"""Data models for the meeting notes generator."""

from dataclasses import dataclass
from typing import List, Optional
from datetime import datetime


@dataclass(frozen=False)
class Speaker:
    """Represents a speaker in a meeting."""
    id: str
    name: str
    speaking_time: int = 0  # seconds
    word_count: int = 0


@dataclass(frozen=False)
class TranscriptSegment:
    """A segment of transcribed speech."""
    start_time: int  # milliseconds
    end_time: int    # milliseconds
    speaker_id: str
    text: str
    confidence: float = 0.8


@dataclass(frozen=False)
class ActionItem:
    """A task or action item from the meeting."""
    description: str
    assignee: Optional[str] = None
    due_date: Optional[str] = None
    priority: str = "medium"


@dataclass(frozen=False)
class MeetingResult:
    """Complete meeting analysis result."""
    title: str
    summary: str
    speakers: List[Speaker]
    segments: List[TranscriptSegment]
    action_items: List[ActionItem]
    language: str
    duration: int  # seconds
    processed_at: datetime
    
    @property
    def total_words(self) -> int:
        """Calculate total words in transcript."""
        return sum(len(segment.text.split()) for segment in self.segments)
    
    @property
    def avg_confidence(self) -> float:
        """Calculate average confidence score."""
        if not self.segments:
            return 0.0
        return sum(segment.confidence for segment in self.segments) / len(self.segments)
    
    @property
    def unique_speakers_count(self) -> int:
        """Get count of unique speakers."""
        return len(set(segment.speaker_id for segment in self.segments))