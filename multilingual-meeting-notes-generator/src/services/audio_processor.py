"""Main processing service that orchestrates the meeting workflow."""

from datetime import datetime
from src.services.transcriber import AudioTranscriber
from src.services.text_analyzer import TextAnalyzer
from src.data.data_models import MeetingResult


class MeetingProcessor:
    """Main service that orchestrates the meeting processing workflow."""
    
    def __init__(self, assemblyai_api_key: str, openai_api_key: str) -> None:
        """Initialize with API keys."""
        self.transcriber = AudioTranscriber(assemblyai_api_key)
        self.analyzer = TextAnalyzer(openai_api_key)
    
    
    def process_meeting_audio(self, audio_file_path: str) -> MeetingResult:
        """Process a meeting audio file and generate comprehensive meeting notes."""
        
        try:
            full_transcript, segments, speakers, language = self.transcriber.transcribe_audio(
                audio_file_path
            )
            
            if not full_transcript or len(full_transcript.strip()) < 10:
                raise Exception("Transcription produced insufficient content")
            
            if not segments:
                raise Exception("No transcript segments were generated")
            
        except Exception as e:
            raise Exception(f"Audio transcription failed: {str(e)}")
        
        # Identify speaker names using LLM analysis
        try:
            speakers = self.analyzer.identify_speaker_names(full_transcript, speakers)
            print(f"Successfully identified speaker names: {[s.name for s in speakers]}")
        except Exception as e:
            print(f"Warning: Speaker name identification failed: {e}")
            # Keep original speakers with IDs if identification fails
        
        try:
            summary = self.analyzer.generate_meeting_summary(full_transcript)
            if not summary or "failed" in summary.lower():
                summary = "Summary generation failed. Please review the transcript manually."
        except Exception as e:
            print(f"Warning: Summary generation failed: {e}")
            summary = "Summary generation failed. Please review the transcript manually."
        
        try:
            action_items = self.analyzer.extract_action_items(full_transcript)
        except Exception as e:
            print(f"Warning: Action item extraction failed: {e}")
            action_items = []
        
        try:
            title = self.analyzer.generate_meeting_title(full_transcript)
            if not title or "failed" in title.lower():
                title = f"Meeting - {datetime.now().strftime('%B %d, %Y')}"
        except Exception as e:
            print(f"Warning: Title generation failed: {e}")
            title = f"Meeting - {datetime.now().strftime('%B %d, %Y')}"
        
        duration = self.transcriber.get_transcript_duration()
        if duration == 0:
            duration = self._get_meeting_duration(segments)
        result = MeetingResult(
            title=title,
            summary=summary,
            speakers=speakers,
            segments=segments,
            action_items=action_items,
            language=language,
            duration=duration,
            processed_at=datetime.now()
        )
        
        return result
    
    def _get_meeting_duration(self, segments: list) -> int:
        """Calculate meeting duration from transcript segments."""
        if not segments:
            return 0
        
        last_segment_end = max(segment.end_time for segment in segments)
        return last_segment_end // 1000  # Convert milliseconds to seconds
