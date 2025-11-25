"""Text analysis service using OpenAI."""

import json
from typing import List
from openai import OpenAI
from src.data.data_models import ActionItem, Speaker


class TextAnalyzer:
    """Analyzes transcribed text to extract insights and generate summaries."""
    
    def __init__(self, api_key: str):
        """Initialize with API key."""
        self.client = OpenAI(api_key=api_key)
        self.model = "gpt-4o"
    
    def generate_meeting_summary(self, transcript_text: str) -> str:
        """Generate a comprehensive summary of the meeting in bullet point format."""
        truncated_text = transcript_text[:3000]
        
        prompt = f"""
        Analyze this meeting transcript and provide a structured summary in English.
        
        IMPORTANT: Write the entire summary in English, regardless of the language of the original transcript.
        
        Provide your response in this EXACT JSON format:
        {{
            "topics_discussed": [
                "First main topic discussed",
                "Second main topic discussed", 
                "Third main topic discussed"
            ],
            "key_decisions": [
                "First important decision made",
                "Second important decision made"
            ],
            "next_steps": [
                "First next step to take",
                "Second next step to take"
            ]
        }}
        
        Guidelines:
        - Keep each item concise but informative
        - Focus on the most important information
        - Do NOT include specific action items or task assignments
        - Do NOT mention "Juan will work on...", "Ana needs to...", etc.
        - Return ONLY the JSON object, no additional text
        
        Meeting Transcript:
        {truncated_text}
        """
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a meeting summarizer. Return ONLY valid JSON in the exact format requested."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=800,
                temperature=0.1
            )
            
            response_text = response.choices[0].message.content.strip()
            
            # Clean markdown code blocks
            if response_text.startswith('```json'):
                response_text = response_text.replace('```json', '').replace('```', '').strip()
            elif response_text.startswith('```'):
                response_text = response_text.replace('```', '').strip()
            
            # Parse JSON response
            import json
            try:
                summary_data = json.loads(response_text)
            except json.JSONDecodeError as e:
                print(f"JSON parsing error: {e}")
                print(f"Response text: {response_text}")
                # Fallback: try to extract JSON using regex
                import re
                json_match = re.search(r'\{[^}]*\}', response_text)
                if json_match:
                    summary_data = json.loads(json_match.group())
                else:
                    return "Summary generation failed. Please review the transcript manually."
            
            # Convert JSON to formatted summary
            formatted_summary = "**Topics Discussed:**\n"
            for topic in summary_data.get("topics_discussed", []):
                formatted_summary += f"• {topic}\n"
            
            formatted_summary += "\n**Key Decisions:**\n"
            for decision in summary_data.get("key_decisions", []):
                formatted_summary += f"• {decision}\n"
            
            formatted_summary += "\n**Next Steps:**\n"
            for step in summary_data.get("next_steps", []):
                formatted_summary += f"• {step}\n"
            
            return formatted_summary
            
        except Exception as e:
            return f"Summary generation failed: {str(e)}"
    
    def extract_action_items(self, transcript_text: str) -> List[ActionItem]:
        """Extract action items and tasks from the meeting transcript."""
        truncated_text = transcript_text[:2000]
        
        prompt = f"""
        Extract all action items, tasks, and commitments from this meeting transcript.
        
        CRITICAL LANGUAGE REQUIREMENT: 
        - ALL action item descriptions MUST be written in English
        - This applies regardless of the original transcript language (Spanish, French, etc.)
        - Do NOT translate names of people - keep original names
        - Do NOT translate company names or technical terms - keep original names
        - ONLY translate the action descriptions to English
        
        Return the results as a JSON array with this exact format:
        [
            {{
                "description": "Clear, specific description of what needs to be done",
                "assignee": "Person responsible (if mentioned, otherwise null)",
                "due_date": "Due date or timeline (if mentioned, otherwise null)",
                "priority": "high/medium/low based on urgency and importance"
            }}
        ]
        
        Look for:
        - Tasks assigned to specific people ("John will...", "Sarah needs to...")
        - Follow-up actions ("We need to...", "Next steps include...")
        - Deadlines or due dates ("by Friday", "next week", "before the end of the month")
        - Commitments made by participants ("I'll handle...", "We'll work on...")
        - Decisions that require follow-up action
        - Items that need to be completed before the next meeting
        
        Be thorough and extract all actionable items, even if they seem minor. 
        
        FINAL REMINDER: All action item descriptions must be in English, regardless of the original transcript language.
        
        Meeting Transcript:
        {truncated_text}
        """
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                max_tokens=500,
                temperature=0.2
            )
            
            response_text = response.choices[0].message.content.strip()
            
            # Clean markdown code blocks
            if response_text.startswith('```json'):
                response_text = response_text.replace('```json', '').replace('```', '').strip()
            elif response_text.startswith('```'):
                response_text = response_text.replace('```', '').strip()
            
            action_items_data = json.loads(response_text)
            
            action_items = []
            for item_data in action_items_data:
                action_item = ActionItem(
                    description=item_data.get("description", ""),
                    assignee=item_data.get("assignee"),
                    due_date=item_data.get("due_date"),
                    priority=item_data.get("priority", "medium")
                )
                action_items.append(action_item)
            
            return action_items
            
        except Exception as e:
            print(f"Action item extraction failed: {e}")
            return []
    
    def identify_speaker_names(self, transcript_text: str, speakers: List[Speaker]) -> List[Speaker]:
        """Identify actual names of speakers from the transcript."""
        # Handle edge cases
        if not speakers:
            return []
        
        truncated_text = transcript_text[:1500]
        
        prompt = f"""
        You are an expert meeting analyst. Analyze this transcript to identify who each speaker is by their real names.
        
        The transcript shows speaker IDs like **A**, **B**, **C**, etc. You need to map these to actual names.
        
        CRITICAL ANALYSIS STEPS:
        1. **Find the facilitator/coordinator**: Look for someone who:
           - Opens/closes the meeting
           - Calls out other people's names ("Juan, sigues tú", "Ana, te toca", etc.)
           - Coordinates the discussion
           - Often speaks first and last
        
        2. **Identify named individuals**: Look for:
           - Direct name mentions when people are called upon
           - Names mentioned in context ("Juan terminé...", "Ana finalicé...")
           - Names in third person references
        
        3. **Match speakers to names**: Use this logic:
           - If someone says "Juan, sigues tú" and then **A** speaks, **A** is likely Juan
           - If someone says "Ana, te toca" and then **B** speaks, **B** is likely Ana
           - The person calling names is usually the facilitator/coordinator
        
        4. **Pattern recognition**: Look for:
           - Sequential name calling followed by responses
           - Self-referential statements ("Ayer terminé...", "Hoy voy a...")
           - Context clues about roles and responsibilities
        
        IMPORTANT RULES:
        - Be very careful with the mapping - one wrong assignment affects everything
        - If a speaker mentions their own name or is clearly identified, use that name
        - If you're uncertain about any mapping, use "Speaker X" for that ID
        - The facilitator might be called "Facilitator", "Coordinator", or their actual name
        
        Return ONLY a JSON object mapping speaker IDs to names.
        Use these speaker IDs: {[speaker.id for speaker in speakers]}
        
        Example format: {{"A": "Juan", "B": "Ana", "C": "Facilitator", "D": "Sofia", "E": "Pedro", "F": "Leo"}}
        
        Meeting Transcript:
        {truncated_text}
        """
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                max_tokens=300,
                temperature=0.1
            )
            
            response_text = response.choices[0].message.content.strip()
            
            # Clean markdown code blocks
            if response_text.startswith('```json'):
                response_text = response_text.replace('```json', '').replace('```', '').strip()
            elif response_text.startswith('```'):
                response_text = response_text.replace('```', '').strip()
            
            # Parse JSON response with robust error handling
            try:
                name_mapping = json.loads(response_text)
            except json.JSONDecodeError as e:
                print(f"JSON parsing error: {e}")
                print(f"Response text: {response_text}")
                # Try to extract JSON object from the text using regex
                import re
                json_match = re.search(r'\{[^}]*\}', response_text)
                if json_match:
                    name_mapping = json.loads(json_match.group())
                else:
                    # Fallback: return speakers with default names
                    return speakers
            
            # Update speaker names using the mapping
            updated_speakers = []
            for speaker in speakers:
                name = name_mapping.get(speaker.id, f"Speaker {speaker.id}")
                updated_speaker = Speaker(
                    id=speaker.id,
                    name=name,
                    speaking_time=speaker.speaking_time,
                    word_count=speaker.word_count
                )
                updated_speakers.append(updated_speaker)
            
            return updated_speakers
            
        except Exception as e:
            print(f"Speaker name identification failed: {e}")
            return speakers
    
    
    # Removed unused detect_segment_language method - no longer needed
    
    def generate_meeting_title(self, transcript_text: str) -> str:
        """Generate a descriptive title for the meeting based on content."""
        truncated_text = transcript_text[:1000]  # Use first part for title generation
        
        prompt = f"""
        Generate a concise, descriptive title for this meeting based on its content.
        
        IMPORTANT: 
        - Return ONLY the title, no additional text
        - Make it 3-8 words maximum
        - Focus on the main topic or purpose
        - Use title case (Capitalize Important Words)
        - Examples: "Weekly Team Standup", "Project Planning Session", "Client Requirements Review"
        
        Meeting Transcript:
        {truncated_text}
        """
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                max_tokens=20,
                temperature=0.3
            )
            
            title = response.choices[0].message.content.strip()
            # Clean up any quotes or extra formatting
            title = title.strip('"\'')
            return title
            
        except Exception as e:
            print(f"Title generation failed: {e}")
            # Fallback to generic title
            from datetime import datetime
            return f"Meeting - {datetime.now().strftime('%B %d, %Y')}"
    
