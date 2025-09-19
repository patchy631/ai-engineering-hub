"""Audio transcription service using AssemblyAI."""

import os
import time
from typing import Tuple, List
import assemblyai as aai
from src.data.data_models import Speaker, TranscriptSegment


class AudioTranscriber:
    """Handles audio transcription with speaker diarization."""
    
    def __init__(self, api_key: str) -> None:
        """Initialize with API key."""
        aai.settings.api_key = api_key
        self.client = aai.Transcriber()
    
    def transcribe_audio(self, audio_path: str) -> Tuple[str, List[TranscriptSegment], List[Speaker], str]:
        """Transcribe audio file with speaker diarization and language detection."""
        
        # Configure transcription
        config = aai.TranscriptionConfig(
            speaker_labels=True,
            language_detection=True,
            language_detection_options=aai.LanguageDetectionOptions(
                expected_languages=["en", "es", "fr", "de", "it", "pt", "hi", "zh", "ja", "ko"],
                fallback_language="auto"
            ),
            punctuate=True,
            format_text=True,
            dual_channel=False,
            webhook_url=None
        )
        
        transcript = self.client.transcribe(audio_path, config=config)
        
        # Wait for completion
        max_wait_time = 300
        wait_time = 0
        
        while transcript.status not in [aai.TranscriptStatus.completed, aai.TranscriptStatus.error]:
            if wait_time >= max_wait_time:
                raise Exception("Transcription timeout")
            
            time.sleep(2)
            wait_time += 2
            transcript = self.client.get_transcript(transcript.id)
        
        if transcript.status == aai.TranscriptStatus.error:
            error_msg = f"Transcription failed: {transcript.error}"
            
            if "speaker" in str(transcript.error).lower():
                error_msg += "\n\nSpeaker diarization failed. Check audio quality and speaker separation."
            elif "language" in str(transcript.error).lower():
                error_msg += "\n\nLanguage detection failed. Ensure clear speech in supported language."
            
            raise Exception(error_msg)
        
        # Validate results
        if not transcript.utterances:
            raise Exception("No utterances found. Check audio quality and format.")
        
        if not transcript.text or len(transcript.text.strip()) < 10:
            raise Exception("Insufficient text content. Check audio quality and language support.")
        
        
        full_text = transcript.text
        segments = self._extract_segments(transcript)
        speakers = self._extract_speakers(transcript)
        
        language = self._get_detected_language(transcript)
        self._last_transcript = transcript
        
        return full_text, segments, speakers, language
    
    def get_transcript_duration(self) -> int:
        """Get duration from the last transcript if available."""
        if hasattr(self, '_last_transcript') and self._last_transcript:
            # Try to get duration from transcript object
            if hasattr(self._last_transcript, 'audio_duration'):
                return int(self._last_transcript.audio_duration)
            elif hasattr(self._last_transcript, 'json_response') and self._last_transcript.json_response:
                return int(self._last_transcript.json_response.get("audio_duration", 0))
        return 0
    
    def _extract_segments(self, transcript) -> List[TranscriptSegment]:
        """Extract transcript segments from utterances."""
        utterances = transcript.utterances or []
        
        # Handle case where utterances is empty
        if not utterances:
            return []
        
        # Process each utterance as a transcript segment
        segments = [
            TranscriptSegment(
                start_time=utterance.start,
                end_time=utterance.end,
                speaker_id=utterance.speaker,
                text=utterance.text,
                confidence=utterance.confidence
            )
            for utterance in utterances
        ]
        
        # Sort segments by start time to ensure chronological order
        segments.sort(key=lambda x: x.start_time)
        
        return segments
    
    def _extract_speakers(self, transcript) -> List[Speaker]:
        """Extract speaker information from utterances."""
        utterances = transcript.utterances or []
        
        # Handle case where utterances is empty
        if not utterances:
            return []
            
        speaker_ids = list(set(utterance.speaker for utterance in utterances))
        
        speakers = []
        for speaker_id in speaker_ids:
            # Calculate stats from utterances
            speaker_utterances = [u for u in utterances if u.speaker == speaker_id]
            speaking_time = sum(u.end - u.start for u in speaker_utterances) // 1000
            word_count = sum(len(u.text.split()) for u in speaker_utterances)
            
            speaker = Speaker(
                id=speaker_id,
                name=speaker_id,  # Use raw speaker ID from AssemblyAI
                speaking_time=speaking_time,
                word_count=word_count
            )
            speakers.append(speaker)
        
        return speakers
    
    def _get_detected_language(self, transcript) -> str:
        """Get detected language from transcript response."""
        try:
            if hasattr(transcript, 'json_response') and transcript.json_response:
                language_code = transcript.json_response.get("language_code")
                if language_code:
                    return language_code
            
            if hasattr(transcript, 'language') and transcript.language:
                return transcript.language
                
        except (AttributeError, KeyError, TypeError):
            pass
        
        return "en"
    
