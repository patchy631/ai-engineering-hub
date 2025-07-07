import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class Config:
    def __init__(self):
        self.openai = {
            'api_key': os.getenv('OPENAI_API_KEY'),
            'model': 'gpt-4o'
        }
        
        self.firecrawl = {
            'api_key': os.getenv('FIRECRAWL_API_KEY')
        }
        
        self.motia = {
            'port': int(os.getenv('MOTIA_PORT', 3000))
        }
        
        self.typefully = {
            'api_key': os.getenv('TYPEFULLY_API_KEY')
        }
        
        self.validate()
    
    def validate(self):
        """Validate that all required environment variables are present"""
        required = ['OPENAI_API_KEY', 'FIRECRAWL_API_KEY', 'TYPEFULLY_API_KEY']
        missing = [key for key in required if not os.getenv(key)]
        
        if missing:
            raise ValueError(f"Missing required environment variables: {', '.join(missing)}")

# Create a global config instance
config = Config()

