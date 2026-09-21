from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

class ResearchData(BaseModel):
    title: str
    content: str
    source_url: str
    credibility_score: float
    date_published: Optional[str] = None

class NewsSection(BaseModel):
    heading: str
    content: str
    sources: List[str] = []

class NewsArticle(BaseModel):
    title: str
    introduction: str
    sections: List[NewsSection] = []
    conclusion: str
    references: List[str] = []
    word_count: int = 0

class ResearchReport(BaseModel):
    executive_summary: str
    key_findings: List[str] = []
    research_data: List[ResearchData] = []
    verified_facts: List[str] = []
    main_themes: List[str] = []
    sources: List[str] = []

class ContentDraft(BaseModel):
    raw_content: str
    sections: List[NewsSection] = []
    sources_used: List[str] = []
    
class EditedContent(BaseModel):
    final_content: str
    improvements_made: List[str] = []
    readability_score: float = 0.0
    word_count: int = 0

class NewsGeneratorState(BaseModel):
    topic: str = ""
    temperature: float = 0.7
    max_sources: int = 10
    
    # Research phase
    research_report: Optional[ResearchReport] = None
    research_completed: bool = False
    
    # Content creation phase  
    content_draft: Optional[ContentDraft] = None
    content_completed: bool = False
    
    # Editing phase
    edited_content: Optional[EditedContent] = None
    editing_completed: bool = False
    
    # Final output
    final_article: Optional[NewsArticle] = None
    generation_completed: bool = False
    
    # Metadata
    start_time: datetime = datetime.now()
    end_time: Optional[datetime] = None
    processing_duration: Optional[float] = None