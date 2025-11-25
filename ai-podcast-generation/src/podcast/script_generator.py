import logging
import json
from typing import List, Dict, Any
from dataclasses import dataclass

from crewai import LLM

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class PodcastScript:
    """Represents a podcast script with metadata"""
    script: List[Dict[str, str]]
    source_document: str
    total_lines: int
    estimated_duration: str

    def get_speaker_lines(self, speaker: str) -> List[str]:
        return [item[speaker] for item in self.script if speaker in item]

    def to_json(self) -> str:
        return json.dumps({
            'script': self.script,
            'metadata': {
                'source_document': self.source_document,
                'total_lines': self.total_lines,
                'estimated_duration': self.estimated_duration
            }
        }, indent=2)


class PodcastScriptGenerator:
    def __init__(self, openai_api_key: str, model_name: str = "gpt-4o-mini"):
        self.llm = LLM(
            model=f"openai/{model_name}",
            temperature=0.7,
            max_tokens=4000
        )
        logger.info(f"Podcast script generator initialized with {model_name}")


    def generate_script_from_text(
        self,
        text_content: str,
        source_name: str = "Text Input",
        podcast_style: str = "conversational",
        target_duration: str = "10 minutes"
    ) -> PodcastScript:

        logger.info("Generating podcast script from text input")

        script_data = self._generate_conversation_script(
            text_content,
            podcast_style,
            target_duration
        )

        podcast_script = PodcastScript(
            script=script_data['script'],
            source_document=source_name,
            total_lines=len(script_data['script']),
            estimated_duration=target_duration
        )

        logger.info(f"Generated script with {podcast_script.total_lines} lines")
        return podcast_script

    def _generate_conversation_script(
        self,
        document_content: str,
        podcast_style: str,
        target_duration: str
    ) -> Dict[str, Any]:

        style_prompts = {
            "conversational": "Create a natural, friendly conversation between two hosts discussing the document. They should build on each other's points and occasionally ask clarifying questions.",
            "educational": "Create an educational discussion where one speaker explains concepts and the other asks thoughtful questions to help clarify complex topics for listeners.",
            "interview": "Create an interview format where Speaker 1 acts as the interviewer asking questions and Speaker 2 provides detailed explanations from the document.",
            "debate": "Create a thoughtful discussion where speakers present different perspectives on the topics, maintaining respect while exploring various viewpoints."
        }

        style_instruction = style_prompts.get(podcast_style, style_prompts["conversational"])

        duration_guidelines = {
            "5 minutes": "Keep the conversation concise, focusing on 3-4 main points with brief explanations.",
            "10 minutes": "Cover the key topics thoroughly with good explanations and examples.",
            "15 minutes": "Provide comprehensive coverage with detailed discussions and multiple examples.",
            "20 minutes": "Create an in-depth exploration with extensive analysis and supporting details."
        }

        duration_guide = duration_guidelines.get(target_duration, duration_guidelines["10 minutes"])

        prompt = f"""Using the following document, create a podcast script for two speakers: 'Speaker 1' and 'Speaker 2'.

STYLE GUIDELINES:
{style_instruction}

DURATION GUIDELINES:
{duration_guide}

CONVERSATION RULES:
1. Each speaker should speak for 2-4 sentences maximum before alternating
2. The conversation should flow naturally with smooth transitions
3. Use engaging, conversational language that's easy to understand
4. Include brief introductions at the start and wrap-up at the end
5. Break down complex concepts into digestible explanations
6. Maintain professional grammar and punctuation throughout
7. Make it engaging for listeners who haven't read the document

RESPONSE FORMAT:
Respond with a valid JSON object containing a 'script' array. Each array element should be an object with either 'Speaker 1' or 'Speaker 2' as the key and their dialogue as the value.

Example format:
{{
  "script": [
    {{"Speaker 1": "Welcome everyone to our podcast! Today we're diving into some fascinating insights from this document..."}},
    {{"Speaker 2": "Thanks for having me! I'm really excited to discuss this topic. The first thing that caught my attention was..."}}
  ]
}}

DOCUMENT CONTENT:
{document_content[:8000]}

Generate an engaging {target_duration} podcast script now:"""

        try:
            response = self.llm.call(prompt)
            script_data = json.loads(response)

            if 'script' not in script_data or not isinstance(script_data['script'], list):
                raise ValueError("Invalid script format returned by LLM")

            validated_script = self._validate_and_clean_script(script_data['script'])

            return {'script': validated_script}

        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse LLM response as JSON: {e}")
            response_clean = response.strip()
            if response_clean.startswith('```json'):
                response_clean = response_clean[7:-3]
            elif response_clean.startswith('```'):
                response_clean = response_clean[3:-3]

            try:
                script_data = json.loads(response_clean)
                validated_script = self._validate_and_clean_script(script_data['script'])
                return {'script': validated_script}
            except:
                raise ValueError(f"Could not parse LLM response as valid JSON: {response}")

        except Exception as e:
            logger.error(f"Error generating script: {str(e)}")
            raise

    def _validate_and_clean_script(self, script: List[Dict[str, str]]) -> List[Dict[str, str]]:
        cleaned_script = []
        expected_speaker = "Speaker 1"
        for item in script:
            if not isinstance(item, dict) or len(item) != 1:
                continue

            speaker, dialogue = next(iter(item.items()))
            speaker = speaker.strip()

            if speaker not in ["Speaker 1", "Speaker 2"]:
                if "1" in speaker or "one" in speaker.lower():
                    speaker = "Speaker 1"
                elif "2" in speaker or "two" in speaker.lower():
                    speaker = "Speaker 2"
                else:
                    speaker = expected_speaker

            dialogue = dialogue.strip()
            if not dialogue:
                continue
            if not dialogue.endswith(('.', '!', '?')):
                dialogue += '.'

            cleaned_script.append({speaker: dialogue})

            expected_speaker = "Speaker 2" if expected_speaker == "Speaker 1" else "Speaker 1"

        if len(cleaned_script) < 2:
            raise ValueError("Generated script is too short or invalid")

        return cleaned_script
