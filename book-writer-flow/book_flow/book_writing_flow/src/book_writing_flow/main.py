#!/usr/bin/env python
import os
import asyncio

from pydantic import BaseModel

from crewai.flow import Flow, listen, start

from book_writing_flow.crews.Writer_crew.writer_crew import ChapterWriterCrew
from book_writing_flow.crews.Outline_crew.outline_crew import OutlineCrew
from dotenv import load_dotenv

load_dotenv()

class Chapter(BaseModel):
    title: str = ""
    content: str = ""

class BookState(BaseModel):
    topic: str = "Astronomy in 2025"
    total_chapters: int = 0
    titles: list[str] = []
    chapters: list[Chapter] = []


class BookFlow(Flow[BookState]):

    @start()
    def generate_outline(self):
        print("Generating outline")
        outline = OutlineCrew().crew().kickoff(inputs={"topic": self.state.topic})
        self.state.total_chapters = outline.pydantic.total_chapters
        self.state.titles = outline.pydantic.titles

    @listen(generate_outline)
    async def generate_chapters(self):
        print("Generating chapters")
        tasks = []

        async def write_single_chapter(title: str):
            result = (
                ChapterWriterCrew()
                .crew()
                .kickoff(inputs={
                    "title": title,
                    "topic": self.state.topic,
                    "chapters": self.state.titles
                })
            )
            return result.pydantic

        # Create tasks for each chapter
        for i in range(self.state.total_chapters):
            task = asyncio.create_task(
                write_single_chapter(
                    self.state.titles[i]
                )
            )
            tasks.append(task)

        # Wait for all chapters to be generated concurrently
        chapters = await asyncio.gather(*tasks)
        print(f"Generated {len(chapters)} chapters")
        self.state.chapters.extend(chapters)

    @listen(generate_chapters)
    def save_book(self):
        print("Saving book")
        with open("book.md", "w") as f:
            for chapter in self.state.chapters:
                f.write("# " + chapter.title + "\n")
                f.write(chapter.content + "\n")


def kickoff():
    book_flow = BookFlow()
    asyncio.run(book_flow.kickoff_async())


def plot():
    book_flow = BookFlow()
    book_flow.plot()


if __name__ == "__main__":
    kickoff()
