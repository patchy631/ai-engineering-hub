try:
    from crewai_tools import BaseTool, SerperDevTool
except ImportError:
    # Fallback for development/testing
    class BaseTool:
        name: str = ""
        description: str = ""
        args_schema = None
        def _run(self, **kwargs): 
            pass
    
    class SerperDevTool:
        def __init__(self, **kwargs): 
            pass
        def _run(self, query: str, **kwargs): 
            return []
from typing import Type, List, Dict, Any
from pydantic import BaseModel, Field
import re
import requests
from datetime import datetime


class SourceCredibilityInput(BaseModel):
    """Input schema for source credibility checker."""
    source_url: str = Field(..., description="The URL of the source to check for credibility")
    content: str = Field(..., description="The content from the source to analyze")


class SourceCredibilityTool(BaseTool):
    name: str = "Source Credibility Checker"
    description: str = (
        "Analyzes the credibility of news sources based on domain reputation, "
        "content quality indicators, and publication patterns. Returns a credibility score from 0-1."
    )
    args_schema: Type[BaseModel] = SourceCredibilityInput

    def _run(self, source_url: str, content: str) -> float:
        """
        Analyze source credibility based on various factors.
        Returns a score from 0.0 (low credibility) to 1.0 (high credibility).
        """
        score = 0.5  # Base score
        
        # Domain-based credibility indicators
        trusted_domains = [
            'reuters.com', 'ap.org', 'bbc.com', 'npr.org', 'wsj.com',
            'nytimes.com', 'washingtonpost.com', 'cnn.com', 'guardian.co.uk',
            'bloomberg.com', 'economist.com', 'nature.com', 'science.org'
        ]
        
        suspicious_domains = [
            'wordpress.com', 'blogspot.com', 'medium.com'
        ]
        
        domain = source_url.split('//')[1].split('/')[0] if '//' in source_url else source_url.split('/')[0]
        domain = domain.replace('www.', '')
        
        # Domain credibility scoring
        if any(trusted in domain for trusted in trusted_domains):
            score += 0.3
        elif any(suspicious in domain for suspicious in suspicious_domains):
            score -= 0.2
            
        # Content quality indicators
        if len(content) > 500:  # Substantial content
            score += 0.1
            
        # Check for citations and references
        if re.search(r'http[s]?://[^\s]+', content):
            score += 0.1
            
        # Check for author information
        if re.search(r'(author|by|written by)', content.lower()):
            score += 0.1
            
        # Ensure score is within bounds
        return max(0.0, min(1.0, score))


class ContentAnalysisInput(BaseModel):
    """Input schema for content analysis."""
    content: str = Field(..., description="The content to analyze for readability and quality")


class ReadabilityAnalyzer(BaseTool):
    name: str = "Readability Analyzer"
    description: str = (
        "Analyzes content for readability metrics including sentence length, "
        "word complexity, and overall readability score."
    )
    args_schema: Type[BaseModel] = ContentAnalysisInput

    def _run(self, content: str) -> Dict[str, Any]:
        """
        Analyze content readability.
        Returns readability metrics and suggestions.
        """
        # Basic readability metrics
        sentences = re.split(r'[.!?]+', content)
        sentences = [s.strip() for s in sentences if s.strip()]
        
        words = content.split()
        
        # Calculate metrics
        avg_sentence_length = len(words) / len(sentences) if sentences else 0
        
        # Simple readability score (Flesch-like approximation)
        # Lower scores = harder to read, higher scores = easier to read
        readability_score = 206.835 - (1.015 * avg_sentence_length)
        readability_score = max(0, min(100, readability_score))  # Bound between 0-100
        
        # Word count
        word_count = len(words)
        
        # Character count
        char_count = len(content)
        
        return {
            "readability_score": readability_score,
            "word_count": word_count,
            "sentence_count": len(sentences),
            "avg_sentence_length": avg_sentence_length,
            "character_count": char_count,
            "reading_level": self._get_reading_level(readability_score)
        }
    
    def _get_reading_level(self, score: float) -> str:
        """Convert readability score to reading level."""
        if score >= 90:
            return "Very Easy"
        elif score >= 80:
            return "Easy"
        elif score >= 70:
            return "Fairly Easy"
        elif score >= 60:
            return "Standard"
        elif score >= 50:
            return "Fairly Difficult"
        elif score >= 30:
            return "Difficult"
        else:
            return "Very Difficult"


class EnhancedSearchTool(SerperDevTool):
    """Enhanced search tool that provides better structured results."""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        
    def _run(self, query: str, **kwargs) -> List[Dict[str, Any]]:
        """
        Enhanced search with better result structuring.
        """
        # Use parent class search functionality
        results = super()._run(query, **kwargs)
        
        # Enhanced result processing would go here
        # For now, return the original results
        return results