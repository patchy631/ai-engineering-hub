import os
import requests
from dotenv import load_dotenv

load_dotenv()


class ScriptGenerator:
    def __init__(self):
        self.api_key = os.getenv('OPENROUTER_API_KEY')
        self.api_url = "https://openrouter.ai/api/v1/chat/completions"
    
    def generate(self, content: str) -> str:
        """Generate podcast script from content using Minimax-M2."""
        prompt = self._create_prompt(content)
        
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": "minimax/minimax-m2.1",
            "messages": [
                {"role": "user", "content": prompt}
            ]
        }
        
        try:
            response = requests.post(self.api_url, json=payload, headers=headers)
            response.raise_for_status()
            
            result = response.json()
            script = result['choices'][0]['message']['content']
            return script
        except Exception as e:
            raise Exception(f"Script generation failed: {str(e)}")
    
    def _create_prompt(self, content: str) -> str:
        return f"""Convert the following content into an engaging podcast script between two hosts.

Format the script as a natural conversation with:
- Host 1 (Male): A curious and enthusiastic interviewer
- Host 2 (Female): A knowledgeable expert on the topic

Requirements:
- Break down complex topics into digestible segments
- Use conversational language
- Include natural transitions and reactions
- Keep it engaging, informative and concise. 
- Format each line as "Host 1:" or "Host 2:" followed by their dialogue

Content to convert:
{content}

Generate the podcast script now:"""