import logging
import os
import time
from typing import List, Dict, Any, Optional
from dataclasses import dataclass
from pathlib import Path
import json

import assemblyai as aai
from src.document_processing.doc_processor import DocumentChunk

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class SpeakerSegment:
    """Represents a speaker segment with timing and content"""
    speaker: str
    start_time: float
    end_time: float
    text: str
    confidence: float
    
    def get_timestamp_str(self) -> str:
        def format_time(seconds):
            minutes = int(seconds // 60)
            seconds = int(seconds % 60)
            return f"{minutes:02d}:{seconds:02d}"
        
        return f"[{format_time(self.start_time)} - {format_time(self.end_time)}]"


class AudioTranscriber:
    def __init__(self, api_key: str):
        self.api_key = api_key
        aai.settings.api_key = api_key
        
        self.supported_formats = {
            '.mp3', '.wav', '.m4a', '.aac', '.ogg', 
            '.flac', '.wma', '.opus', '.mp4', '.mov', '.avi'
        }
        
        logger.info("AudioTranscriber initialized with AssemblyAI")
    
    def transcribe_audio(
        self,
        audio_path: str,
        enable_speaker_diarization: bool = True,
        enable_auto_punctuation: bool = True,
        audio_language: str = "en",
        chunk_size: int = 1000,
        chunk_overlap: int = 100
    ) -> List[DocumentChunk]:
        
        audio_path = Path(audio_path)
        
        if not audio_path.exists():
            raise FileNotFoundError(f"Audio file not found: {audio_path}")
        if audio_path.suffix.lower() not in self.supported_formats:
            raise ValueError(f"Unsupported audio format: {audio_path.suffix}")
        
        logger.info(f"Starting transcription for: {audio_path.name}")
        
        try:
            config = aai.TranscriptionConfig(
                speaker_labels=enable_speaker_diarization,
                punctuate=enable_auto_punctuation,
                language_code=audio_language,
            )
            
            transcriber = aai.Transcriber(config=config)
            transcript = transcriber.transcribe(str(audio_path))
            
            if transcript.status == aai.TranscriptStatus.error:
                raise Exception(f"Transcription failed: {transcript.error}")
            
            logger.info(f"Transcription completed for: {audio_path.name}")
            
            return self._process_transcript_to_chunks(
                transcript, 
                audio_path.name, 
                chunk_size, 
                chunk_overlap
            )
            
        except Exception as e:
            logger.error(f"Error transcribing audio {audio_path.name}: {str(e)}")
            raise
    
    def _process_transcript_to_chunks(
        self,
        transcript: aai.Transcript,
        source_file: str,
        chunk_size: int,
        chunk_overlap: int
    ) -> List[DocumentChunk]:
        
        chunks = []
        transcript_metadata = {
            'duration_seconds': transcript.audio_duration,
            'confidence': transcript.confidence,
            'audio_url': transcript.audio_url,
            'transcription_id': transcript.id
        }
        
        if hasattr(transcript, 'utterances') and transcript.utterances:
            chunks = self._create_chunks_with_speakers(
                transcript.utterances,
                source_file,
                chunk_size,
                chunk_overlap,
                transcript_metadata
            )
        else:
            chunks = self._create_chunks_without_speakers(
                transcript.text,
                source_file,
                chunk_size,
                chunk_overlap,
                transcript_metadata
            )
        
        logger.info(f"Created {len(chunks)} chunks from transcript")
        return chunks
    
    def _create_chunks_with_speakers(
        self,
        utterances: List[aai.Utterance],
        source_file: str,
        chunk_size: int,
        chunk_overlap: int,
        base_metadata: Dict[str, Any]
    ) -> List[DocumentChunk]:

        chunks = []
        current_text = ""
        current_speakers = []
        current_timestamps = []
        chunk_index = 0
        start_char = 0
        
        for utterance in utterances:
            speaker_label = f"Speaker {utterance.speaker}"
            timestamp_str = f"[{self._format_milliseconds(utterance.start)}]"
            
            speaker_text = f"{timestamp_str} {speaker_label}: {utterance.text}\n"

            if len(current_text + speaker_text) > chunk_size and current_text:
                chunk_metadata = base_metadata.copy()
                chunk_metadata.update({
                    'speakers': list(set(current_speakers)),
                    'start_timestamp': current_timestamps[0] if current_timestamps else None,
                    'end_timestamp': current_timestamps[-1] if current_timestamps else None,
                    'speaker_count': len(set(current_speakers))
                })
                
                chunk = DocumentChunk(
                    content=current_text.strip(),
                    source_file=source_file,
                    source_type='audio',
                    page_number=None,
                    chunk_index=chunk_index,
                    start_char=start_char,
                    end_char=start_char+len(current_text)-1,
                    metadata=chunk_metadata
                )
                chunks.append(chunk)
                
                overlap_text = current_text[-chunk_overlap:] if chunk_overlap > 0 else ""
                current_text = overlap_text + speaker_text
                start_char += len(current_text) - len(overlap_text) - len(speaker_text)
                chunk_index += 1
                
                current_speakers = [speaker_label]
                current_timestamps = [utterance.start, utterance.end]
            else:
                current_text += speaker_text
                current_speakers.append(speaker_label)
                current_timestamps.extend([utterance.start, utterance.end])
        
        if current_text.strip():
            chunk_metadata = base_metadata.copy()
            chunk_metadata.update({
                'speakers': list(set(current_speakers)),
                'start_timestamp': current_timestamps[0] if current_timestamps else None,
                'end_timestamp': current_timestamps[-1] if current_timestamps else None,
                'speaker_count': len(set(current_speakers))
            })
            
            chunk = DocumentChunk(
                content=current_text.strip(),
                source_file=source_file,
                source_type='audio',
                page_number=None,
                chunk_index=chunk_index,
                start_char=start_char,
                end_char=start_char+len(current_text)-1,
                metadata=chunk_metadata
            )
            chunks.append(chunk)
        
        return chunks
    
    # def _create_chunks_without_speakers(
    #     self,
    #     transcript_text: str,
    #     source_file: str,
    #     chunk_size: int,
    #     chunk_overlap: int,
    #     base_metadata: Dict[str, Any]
    # ) -> List[DocumentChunk]:
    #     if not transcript_text.strip():
    #         return []
        
    #     chunks = []
    #     start = 0
    #     chunk_index = 0
        
    #     while start < len(transcript_text):
    #         end = min(start + chunk_size, len(transcript_text))
            
    #         # Try to break at sentence boundary
    #         if end < len(transcript_text):
    #             last_period = transcript_text.rfind('.', start, end)
    #             last_newline = transcript_text.rfind('\n', start, end)
                
    #             boundary = max(last_period, last_newline)
    #             if boundary > start + chunk_size * 0.5:
    #                 end = boundary + 1
            
    #         chunk_text = transcript_text[start:end].strip()
            
    #         if chunk_text:
    #             chunk_metadata = base_metadata.copy()
    #             chunk_metadata.update({
    #                 'speakers': ['Unknown Speaker'],
    #                 'speaker_count': 1
    #             })
                
    #             chunk = DocumentChunk(
    #                 content=chunk_text,
    #                 source_file=source_file,
    #                 source_type='audio',
    #                 page_number=None,
    #                 chunk_index=chunk_index,
    #                 start_char=start,
    #                 end_char=end - 1,
    #                 metadata=chunk_metadata
    #             )
    #             chunks.append(chunk)
    #             chunk_index += 1
            
    #         start = max(start + chunk_size - chunk_overlap, end)
        
    #     return chunks
    
    def _format_milliseconds(self, ms: int) -> str:
        seconds = ms // 1000
        minutes = seconds // 60
        seconds = seconds % 60
        return f"{minutes:02d}:{seconds:02d}"
    
    def get_transcript_summary(self, audio_path: str) -> Dict[str, Any]:
        try:
            config = aai.TranscriptionConfig(
                speaker_labels=True,
                summarization=True
            )
            
            transcriber = aai.Transcriber(config=config)
            transcript = transcriber.transcribe(str(audio_path))
            
            if transcript.status == aai.TranscriptStatus.error:
                return {"error": transcript.error}
            
            summary_info = {
                'id': transcript.id,
                'file_name': Path(audio_path).name,
                'duration_seconds': transcript.audio_duration,
                'confidence': transcript.confidence,
                'word_count': len(transcript.text.split()) if transcript.text else 0,
                'character_count': len(transcript.text) if transcript.text else 0,
                'summary': getattr(transcript, 'summary', 'Not available'),
                'speaker_count': len(set(u.speaker for u in transcript.utterances)) if hasattr(transcript, 'utterances') and transcript.utterances else 1
            }
            
            return summary_info
            
        except Exception as e:
            logger.error(f"Error getting transcript summary: {str(e)}")
            return {"error": str(e)}
    
    def batch_transcribe(self, audio_paths: List[str]) -> List[List[DocumentChunk]]:
        all_chunks = []
        for audio_path in audio_paths:
            try:
                chunks = self.transcribe_audio(audio_path)
                all_chunks.append(chunks)
                logger.info(f"Successfully transcribed {audio_path}: {len(chunks)} chunks")
            except Exception as e:
                logger.error(f"Failed to transcribe {audio_path}: {str(e)}")
                all_chunks.append([])
        
        return all_chunks


if __name__ == "__main__":
    api_key = os.getenv("ASSEMBLYAI_API_KEY")
    if not api_key:
        print("Please set ASSEMBLYAI_API_KEY environment variable")
        exit(1)
    
    transcriber = AudioTranscriber(api_key)
    
    try:
        audio_file = "data/harvard.wav"

        summary = transcriber.get_transcript_summary(audio_file)
        print(f"Transcript Summary: {summary}")
        
        # Full transcription
        chunks = transcriber.transcribe_audio(audio_file)
        
        print(f"\nTranscription Results:")
        print(f"Generated {len(chunks)} chunks")
        
        for i, chunk in enumerate(chunks[:3]):
            print(f"\nChunk {i+1}:")
            print(f"Content: {chunk.content[:200]}...")
            print(f"Speakers: {chunk.metadata.get('speakers', [])}")
            print(f"Citation: Source: {chunk.source_file}, Type: Audio Transcript")
        
    except Exception as e:
        print(f"Error in transcription example: {e}")