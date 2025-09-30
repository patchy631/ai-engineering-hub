import logging
import os
import soundfile as sf
from typing import List, Dict, Any
from pathlib import Path
from dataclasses import dataclass

try:
    from kokoro import KPipeline
except ImportError:
    print("Kokoro not installed. Install with: pip install kokoro>=0.9.4")
    KPipeline = None

from src.podcast.script_generator import PodcastScript

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class AudioSegment:
    """Represents a single audio segment with metadata"""
    speaker: str
    text: str
    audio_data: Any
    duration: float
    file_path: str


class PodcastTTSGenerator:
    def __init__(self, lang_code: str = 'a', sample_rate: int = 24000):
        if KPipeline is None:
            raise ImportError("Kokoro TTS not available. Install with: pip install kokoro>=0.9.4 soundfile")
        
        self.sample_rate = sample_rate
        self.pipeline = KPipeline(lang_code=lang_code)
        
        self.speaker_voices = {
            "Speaker 1": "af_heart",  # Female voice
            "Speaker 2": "am_liam"    # Male voice
        }
        
        logger.info(f"Kokoro TTS initialized with lang_code='{lang_code}', sample_rate={sample_rate}")
    
    def generate_podcast_audio(
        self, 
        podcast_script: PodcastScript,
        output_dir: str = "outputs/podcast_audio",
        combine_audio: bool = True
    ) -> List[str]:

        Path(output_dir).mkdir(parents=True, exist_ok=True)
        
        logger.info(f"Generating podcast audio for {podcast_script.total_lines} segments")
        logger.info(f"Output directory: {output_dir}")
        
        audio_segments = []
        output_files = []
        
        for i, line_dict in enumerate(podcast_script.script):
            speaker, dialogue = next(iter(line_dict.items()))
            
            logger.info(f"Processing segment {i+1}/{podcast_script.total_lines}: {speaker}")
            
            try:
                segment_audio = self._generate_single_segment(speaker, dialogue)
                segment_filename = f"segment_{i+1:03d}_{speaker.replace(' ', '_').lower()}.wav"
                segment_path = os.path.join(output_dir, segment_filename)
                
                sf.write(segment_path, segment_audio, self.sample_rate)
                output_files.append(segment_path)
                
                if combine_audio:
                    audio_segment = AudioSegment(
                        speaker=speaker,
                        text=dialogue,
                        audio_data=segment_audio,
                        duration=len(segment_audio) / self.sample_rate,
                        file_path=segment_path
                    )
                    audio_segments.append(audio_segment)
                
                logger.info(f"✓ Generated segment {i+1}: {segment_filename}")
                
            except Exception as e:
                logger.error(f"✗ Failed to generate segment {i+1}: {str(e)}")
                continue
        
        if combine_audio and audio_segments:
            combined_path = self._combine_audio_segments(audio_segments, output_dir)
            output_files.append(combined_path)
        
        logger.info(f"Podcast generation complete! Generated {len(output_files)} files")
        return output_files
    
    def _generate_single_segment(self, speaker: str, text: str) -> Any:
        voice = self.speaker_voices.get(speaker, "af_heart")
        clean_text = self._clean_text_for_tts(text)

        generator = self.pipeline(clean_text, voice=voice)
        
        combined_audio = []
        for i, (gs, ps, audio) in enumerate(generator):
            combined_audio.append(audio)
        
        if len(combined_audio) == 1:
            return combined_audio[0]
        else:
            import numpy as np
            return np.concatenate(combined_audio)
    
    def _clean_text_for_tts(self, text: str) -> str:
        clean_text = text.strip()

        clean_text = clean_text.replace("...", ".")
        clean_text = clean_text.replace("!!", "!")
        clean_text = clean_text.replace("??", "?")

        if not clean_text.endswith(('.', '!', '?')):
            clean_text += '.'
        
        return clean_text
    
    def _combine_audio_segments(
        self, 
        segments: List[AudioSegment], 
        output_dir: str
    ) -> str:
        logger.info(f"Combining {len(segments)} audio segments")
        
        try:
            import numpy as np
            
            pause_duration = 0.2  # seconds
            pause_samples = int(pause_duration * self.sample_rate)
            pause_audio = np.zeros(pause_samples, dtype=np.float32)
            
            combined_audio = []
            for i, segment in enumerate(segments):
                combined_audio.append(segment.audio_data)
                
                if i < len(segments) - 1:
                    combined_audio.append(pause_audio)
            
            final_audio = np.concatenate(combined_audio)
            
            combined_filename = "complete_podcast.wav"
            combined_path = os.path.join(output_dir, combined_filename)
            sf.write(combined_path, final_audio, self.sample_rate)
            
            duration = len(final_audio) / self.sample_rate
            logger.info(f"✓ Combined podcast saved: {combined_path} (Duration: {duration:.1f}s)")
            
            return combined_path
            
        except Exception as e:
            logger.error(f"✗ Failed to combine audio segments: {str(e)}")
            raise


if __name__ == "__main__":
    import json
    
    try:
        tts_generator = PodcastTTSGenerator()
        
        sample_script_data = {
            "script": [
                {"Speaker 1": "Welcome everyone to our podcast! Today we're exploring the fascinating world of artificial intelligence."},
                {"Speaker 2": "Thanks for having me! AI is indeed one of the most exciting technological developments of our time."},
                {"Speaker 1": "Let's start with machine learning. Can you explain what makes it so revolutionary?"},
                {"Speaker 2": "Absolutely! Machine learning allows computers to learn from data without being explicitly programmed for every single task."},
                {"Speaker 1": "That's incredible! And deep learning takes this even further, doesn't it?"},
                {"Speaker 2": "Exactly! Deep learning uses neural networks with multiple layers, revolutionizing computer vision and natural language processing."}
            ]
        }
        
        from src.podcast.script_generator import PodcastScript
        test_script = PodcastScript(
            script=sample_script_data["script"],
            source_document="AI Overview Test",
            total_lines=len(sample_script_data["script"]),
            estimated_duration="2 minutes"
        )
        
        print("Generating podcast audio...")
        output_files = tts_generator.generate_podcast_audio(
            test_script,
            output_dir="./podcast_output",
            combine_audio=True
        )
        
        print(f"\nGenerated files:")
        for file_path in output_files:
            print(f"  - {file_path}")
        
        print("\nPodcast TTS test completed successfully!")
        
    except ImportError as e:
        print(f"Import error: {e}")
        print("Please install Kokoro TTS: pip install kokoro>=0.9.4")
    except Exception as e:
        print(f"Error: {e}")