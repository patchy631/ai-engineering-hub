import argparse
import os

import yaml
from crewai import LLM, Agent, Crew, Process, Task
from crewai_tools import ApifyActorsTool
from dotenv import load_dotenv

load_dotenv()

CONFIG_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "config.yaml")

# Keep each transcript within a reasonable prompt size
MAX_CHARS_PER_VIDEO = 30000


def load_llm():
    # To run locally with Ollama instead:
    # return LLM(model="ollama/llama3.2", base_url="http://localhost:11434")
    return LLM(
        model=os.getenv("MODEL", "gpt-4o-mini"),
        api_key=os.getenv("OPENAI_API_KEY"),
    )


def fetch_transcripts(video_urls, language="en"):
    """Fetch transcripts for a list of YouTube URLs in a single Actor run."""
    transcript_tool = ApifyActorsTool(actor_name="johnvc/YoutubeTranscripts")
    items = transcript_tool.run(
        run_input={
            "youtube_url": video_urls,
            "languages": [language],
            "include_metadata": True,
        }
    )

    transcripts = []
    for item in items:
        if not item.get("success") or not item.get("non_timestamped"):
            print(f"Skipping {item.get('url')}: {item.get('error', 'no transcript returned')}")
            continue
        transcripts.append(
            {
                "url": item.get("url"),
                "title": item.get("title") or item.get("video_id"),
                "channel": item.get("channel_name", ""),
                "text": item["non_timestamped"],
            }
        )
    return transcripts


def format_transcripts(transcripts):
    blocks = []
    for i, t in enumerate(transcripts, start=1):
        text = t["text"][:MAX_CHARS_PER_VIDEO]
        blocks.append(
            f"### Video {i}: {t['title']}\n"
            f"Channel: {t['channel']}\nURL: {t['url']}\n\n{text}"
        )
    return "\n\n".join(blocks)


def create_crew():
    with open(CONFIG_PATH, "r") as file:
        config = yaml.safe_load(file)

    llm = load_llm()
    agents_cfg = config["agents"]
    tasks_cfg = config["tasks"]

    transcript_analyst = Agent(
        role=agents_cfg["transcript_analyst"]["role"],
        goal=agents_cfg["transcript_analyst"]["goal"],
        backstory=agents_cfg["transcript_analyst"]["backstory"],
        llm=llm,
        verbose=True,
    )

    research_writer = Agent(
        role=agents_cfg["research_writer"]["role"],
        goal=agents_cfg["research_writer"]["goal"],
        backstory=agents_cfg["research_writer"]["backstory"],
        llm=llm,
        verbose=True,
    )

    summary_task = Task(
        description=tasks_cfg["summary_task"]["description"],
        expected_output=tasks_cfg["summary_task"]["expected_output"],
        agent=transcript_analyst,
    )

    answer_task = Task(
        description=tasks_cfg["answer_task"]["description"],
        expected_output=tasks_cfg["answer_task"]["expected_output"],
        agent=research_writer,
        context=[summary_task],
    )

    return Crew(
        agents=[transcript_analyst, research_writer],
        tasks=[summary_task, answer_task],
        process=Process.sequential,
        verbose=True,
    )


def run_research(video_urls, question, language="en"):
    transcripts = fetch_transcripts(video_urls, language=language)
    if not transcripts:
        raise RuntimeError("No transcripts were returned for the given videos.")

    total_chars = sum(len(t["text"]) for t in transcripts)
    print(f"Fetched {len(transcripts)} transcript(s), {total_chars} characters in total")

    crew = create_crew()
    result = crew.kickoff(
        inputs={
            "question": question,
            "transcripts": format_transcripts(transcripts),
        }
    )
    return result, transcripts


def main():
    parser = argparse.ArgumentParser(description="Research YouTube videos with CrewAI")
    parser.add_argument("urls", nargs="+", help="One or more YouTube video URLs")
    parser.add_argument(
        "-q",
        "--question",
        default="What are the main points made in these videos?",
        help="The research question to answer",
    )
    parser.add_argument("-l", "--language", default="en", help="Transcript language code")
    args = parser.parse_args()

    result, _ = run_research(args.urls, args.question, language=args.language)
    print("\n===== Final answer =====\n")
    print(result.raw)


if __name__ == "__main__":
    main()
