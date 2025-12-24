import os
import time
import requests
from dotenv import load_dotenv

load_dotenv()


class TTSConverter:
    def __init__(self):
        self.api_key = os.getenv('MINIMAX_API_KEY')
        self.base_url = "https://api.minimax.io/v1/t2a_async_v2"
        self.query_url = "https://api.minimax.io/v1/query/t2a_async_query_v2"
        self.file_url = "https://api.minimax.io/v1/files/retrieve_content"
        
        # Voice configurations
        self.voices = {
            "male": "English_Explanatory_Man",
            "female": "English_captivating_female1"
        }
    
    def convert(self, script: str, output_dir: str = "audio_segments") -> list:
        """Convert script to speech using Minimax TTS."""
        segments = self._parse_script(script)
        
        # Create output directory
        os.makedirs(output_dir, exist_ok=True)
        
        audio_files = []
        
        for i, (speaker, text) in enumerate(segments, 1):
            print(f"  Generating segment {i}/{len(segments)} ...")
            voice = self.voices.get(speaker, self.voices["male"])
            audio_file = os.path.join(output_dir, f"segment_{i:03d}.mp3")
            
            self._generate_and_save_speech(text, voice, audio_file)
            audio_files.append((speaker, audio_file))
            print(f"  ✓ Saved to {audio_file}")
        
        return audio_files
    
    def _parse_script(self, script: str) -> list:
        """Parse script into speaker and text segments."""
        segments = []
        lines = script.strip().split('\n')
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            if line.startswith("Host 1:"):
                text = line.replace("Host 1:", "").strip()
                segments.append(("male", text))
            elif line.startswith("Host 2:"):
                text = line.replace("Host 2:", "").strip()
                segments.append(("female", text))
        
        return segments
    
    def _generate_and_save_speech(self, text: str, voice: str, output_file: str):
        """Generate speech for a single text segment and save to file."""
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": "speech-2.6-hd",
            "text": text,
            "voice_setting": {
                "voice_id": voice,
                "speed": 1.0,
                "vol": 1.0,
                "pitch": 0
            },
            "audio_setting": {
                "sample_rate": 32000,
                "bitrate": 128000,
                "format": "mp3"
            }
        }
        
        try:
            # Submit TTS request
            response = requests.post(
                self.base_url,
                json=payload,
                headers=headers,
                timeout=30
            )
            response.raise_for_status()
            
            result = response.json()
            task_id = result.get('task_id')
            
            if not task_id:
                raise Exception("No task_id received")
            
            # Poll for completion and get file_id
            file_id = self._poll_task(task_id)
            
            # Download and save the audio file
            self._download_audio(file_id, output_file)
            
        except Exception as e:
            raise Exception(f"TTS conversion failed: {str(e)}")
    
    def _poll_task(self, task_id: str, max_attempts: int = 60) -> str:
        """Poll task status until completion."""
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        for _ in range(max_attempts):
            response = requests.get(
                f"{self.query_url}?task_id={task_id}",
                headers=headers,
                timeout=15
            )
            response.raise_for_status()
            
            result = response.json()
            status = result.get('status')
            
            if status == 'Success':
                return result.get('file_id')
            elif status == 'Failed':
                error_msg = result.get('error', 'Unknown error')
                raise Exception(f"TTS generation failed: {error_msg}")
            
            time.sleep(2)
        
        raise Exception("TTS generation timeout")
    
    def _download_audio(self, file_id: str, output_file: str):
        """Download audio file from Minimax API."""
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        response = requests.get(
            f"{self.file_url}?file_id={file_id}",
            headers=headers
        )
        response.raise_for_status()
        
        # Write binary content to file
        with open(output_file, 'wb') as f:
            f.write(response.content)


if __name__ == "__main__":
    """Test the TTS functionality."""
    
    # Sample podcast script
    test_script = """Host 1: Hey everyone, welcome back to Tech Talk! Today we're diving into artificial intelligence.
Host 2: Thanks for having me! AI is such an exciting field right now.
Host 1: Absolutely! So let's start with the basics. What exactly is AI?
Host 2: Great question! AI, or artificial intelligence, is the simulation of human intelligence by machines.
Host 1: That's fascinating. Can you give us a real-world example?
Host 2: Sure! Think about voice assistants like Siri or Alexa. They use AI to understand and respond to your questions.
Host 1: Wow, that really puts it in perspective. Thanks for breaking that down for us!
Host 2: My pleasure! There's so much more to explore in this field."""
    
    try:
        print("Testing TTS Converter...")
        print("=" * 50)
        
        converter = TTSConverter()
        audio_files = converter.convert(test_script, output_dir="test_audio")
        
        print("\n" + "=" * 50)
        print("✅ Test completed successfully!")
        print(f"\nGenerated {len(audio_files)} audio files:")
        for speaker, filepath in audio_files:
            print(f"  - {filepath}")
        
    except Exception as e:
        print(f"\n❌ Test failed: {str(e)}")