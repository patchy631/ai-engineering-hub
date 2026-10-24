#!/usr/bin/env python
import os
import asyncio
from datetime import datetime
from pydantic import BaseModel

from crewai.flow import Flow, listen, start
from crewai import LLM

from ai_news_flow.models import NewsGeneratorState, NewsArticle, NewsSection
from ai_news_flow.crews.research_crew.research_crew import ResearchCrew
from ai_news_flow.crews.content_crew.content_crew import ContentCrew  
from ai_news_flow.crews.editing_crew.editing_crew import EditingCrew

from dotenv import load_dotenv

load_dotenv()


class NewsGeneratorFlow(Flow[NewsGeneratorState]):
    """
    Complete AI News Generator Flow using CrewAI.
    
    This flow orchestrates multiple crews to:
    1. Research the topic comprehensively
    2. Create engaging content from research
    3. Edit and polish the final article
    """

    def __init__(self, topic: str = "", temperature: float = 0.7, max_sources: int = 10):
        """Initialize the flow with topic and configuration."""
        super().__init__()
        
        # Initialize state
        self.state = NewsGeneratorState(
            topic=topic,
            temperature=temperature, 
            max_sources=max_sources
        )
        
        # Initialize LLM for all crews
        self.llm = LLM(model="command-r", temperature=temperature)
        
        # Initialize crews
        self.research_crew = ResearchCrew(llm=self.llm, temperature=temperature)
        self.content_crew = ContentCrew(llm=self.llm, temperature=temperature)
        self.editing_crew = EditingCrew(llm=self.llm, temperature=0.5)  # Lower temp for editing

    @start()
    def research_phase(self):
        """
        Phase 1: Comprehensive research on the topic.
        This includes fact-checking and synthesis of findings.
        """
        print(f"🔍 Starting research phase for topic: {self.state.topic}")
        
        try:
            # Run research crew
            research_result = self.research_crew.crew().kickoff(inputs={
                "topic": self.state.topic,
                "max_sources": self.state.max_sources
            })
            
            # Update state with research results
            self.state.research_report = research_result.pydantic
            self.state.research_completed = True
            
            print("✅ Research phase completed successfully")
            print(f"📊 Found {len(self.state.research_report.research_data)} research sources")
            print(f"🎯 Identified {len(self.state.research_report.main_themes)} main themes")
            
        except Exception as e:
            print(f"❌ Research phase failed: {str(e)}")
            raise

    @listen(research_phase)
    def content_creation_phase(self):
        """
        Phase 2: Create engaging content from research findings.
        This includes content strategy, writing, and SEO optimization.
        """
        print("✍️ Starting content creation phase")
        
        try:
            # Prepare research context for content crew
            research_context = {
                "topic": self.state.topic,
                "research_report": self.state.research_report.dict() if self.state.research_report else {},
                "executive_summary": self.state.research_report.executive_summary if self.state.research_report else "",
                "key_findings": self.state.research_report.key_findings if self.state.research_report else [],
                "sources": self.state.research_report.sources if self.state.research_report else []
            }
            
            # Run content creation crew
            content_result = self.content_crew.crew().kickoff(inputs=research_context)
            
            # Update state with content results
            self.state.content_draft = content_result.pydantic
            self.state.content_completed = True
            
            print("✅ Content creation phase completed successfully")
            print(f"📝 Generated content with {len(self.state.content_draft.sections)} sections")
            
        except Exception as e:
            print(f"❌ Content creation phase failed: {str(e)}")
            raise

    @listen(content_creation_phase)
    def editing_phase(self):
        """
        Phase 3: Edit and polish the content for final publication.
        This includes copy editing, technical review, and final formatting.
        """
        print("📝 Starting editing phase")
        
        try:
            # Prepare content context for editing crew
            editing_context = {
                "topic": self.state.topic,
                "content_draft": self.state.content_draft.dict() if self.state.content_draft else {},
                "raw_content": self.state.content_draft.raw_content if self.state.content_draft else "",
                "sources_used": self.state.content_draft.sources_used if self.state.content_draft else []
            }
            
            # Run editing crew
            editing_result = self.editing_crew.crew().kickoff(inputs=editing_context)
            
            # Update state with editing results
            self.state.edited_content = editing_result.pydantic
            self.state.editing_completed = True
            
            print("✅ Editing phase completed successfully")
            print(f"📊 Readability score: {self.state.edited_content.readability_score}")
            print(f"📄 Final word count: {self.state.edited_content.word_count}")
            
        except Exception as e:
            print(f"❌ Editing phase failed: {str(e)}")
            raise

    @listen(editing_phase)
    def finalization_phase(self):
        """
        Phase 4: Finalize the article and prepare for delivery.
        This creates the final NewsArticle object with all components.
        """
        print("🎯 Starting finalization phase")
        
        try:
            # Parse the final content to create structured article
            final_content = self.state.edited_content.final_content
            
            # Extract sections from the markdown content
            sections = self._parse_content_sections(final_content)
            
            # Create final article
            self.state.final_article = NewsArticle(
                title=self._extract_title(final_content),
                introduction=self._extract_introduction(final_content),
                sections=sections,
                conclusion=self._extract_conclusion(final_content),
                references=self.state.research_report.sources if self.state.research_report else [],
                word_count=self.state.edited_content.word_count
            )
            
            # Update completion status and timing
            self.state.end_time = datetime.now()
            self.state.processing_duration = (
                self.state.end_time - self.state.start_time
            ).total_seconds()
            self.state.generation_completed = True
            
            print("✅ News article generation completed successfully!")
            print(f"⏱️ Total processing time: {self.state.processing_duration:.2f} seconds")
            print(f"📄 Final article: {self.state.final_article.word_count} words")
            
        except Exception as e:
            print(f"❌ Finalization phase failed: {str(e)}")
            raise

    def _parse_content_sections(self, content: str) -> list[NewsSection]:
        """Parse markdown content into structured sections."""
        sections = []
        lines = content.split('\n')
        current_section = None
        current_content = []
        
        for line in lines:
            if line.startswith('### '):  # H3 headings for sections
                if current_section:
                    sections.append(NewsSection(
                        heading=current_section,
                        content='\n'.join(current_content).strip()
                    ))
                current_section = line[4:].strip()
                current_content = []
            elif current_section and line.strip():
                current_content.append(line)
        
        # Add the last section
        if current_section:
            sections.append(NewsSection(
                heading=current_section,
                content='\n'.join(current_content).strip()
            ))
        
        return sections

    def _extract_title(self, content: str) -> str:
        """Extract the main title from markdown content."""
        lines = content.split('\n')
        for line in lines:
            if line.startswith('# '):
                return line[2:].strip()
        return f"Article about {self.state.topic}"

    def _extract_introduction(self, content: str) -> str:
        """Extract the introduction section."""
        lines = content.split('\n')
        intro_lines = []
        capture = False
        
        for line in lines:
            if line.startswith('# '):
                capture = True
                continue
            elif line.startswith('### ') and capture:
                break
            elif capture and line.strip():
                intro_lines.append(line)
        
        return '\n'.join(intro_lines).strip()

    def _extract_conclusion(self, content: str) -> str:
        """Extract the conclusion section."""
        lines = content.split('\n')
        conclusion_lines = []
        capture = False
        
        for line in lines:
            if 'conclusion' in line.lower() and line.startswith('### '):
                capture = True
                continue
            elif line.startswith('### ') and capture:
                break
            elif capture and line.strip():
                conclusion_lines.append(line)
        
        return '\n'.join(conclusion_lines).strip()

    def get_final_content(self) -> str:
        """Get the final content as a string."""
        if self.state.edited_content:
            return self.state.edited_content.final_content
        return ""

    def get_processing_summary(self) -> dict:
        """Get a summary of the processing results."""
        return {
            "topic": self.state.topic,
            "completed": self.state.generation_completed,
            "research_sources": len(self.state.research_report.research_data) if self.state.research_report else 0,
            "word_count": self.state.final_article.word_count if self.state.final_article else 0,
            "processing_time": self.state.processing_duration,
            "readability_score": self.state.edited_content.readability_score if self.state.edited_content else 0
        }


def kickoff(topic: str, temperature: float = 0.7, max_sources: int = 10):
    """Convenience function to run the complete news generation flow."""
    flow = NewsGeneratorFlow(topic=topic, temperature=temperature, max_sources=max_sources)
    result = flow.kickoff()
    return flow


def plot(topic: str = "Sample Topic"):
    """Generate a visual plot of the flow."""
    flow = NewsGeneratorFlow(topic=topic)
    flow.plot()


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        topic = " ".join(sys.argv[1:])
        print(f"🚀 Starting AI News Generator Flow for topic: {topic}")
        flow = kickoff(topic)
        print("\n" + "="*50)
        print("FINAL ARTICLE")
        print("="*50)
        print(flow.get_final_content())
    else:
        print("Usage: python main.py <topic>")
        print("Example: python main.py AI trends in 2025")