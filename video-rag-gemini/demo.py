#!/usr/bin/env python3
"""
Demo script for Video RAG with Gemini
This script demonstrates how to use the Gemini API for video understanding
"""

import google.generativeai as genai
import os
from dotenv import load_dotenv

load_dotenv()

def demo_video_chat():
    """Simple demo of video chat functionality"""
    
    # Configure API
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        print("❌ Please set GEMINI_API_KEY in your .env file")
        return
    
    genai.configure(api_key=api_key)
    
    # Initialize model
    model = genai.GenerativeModel('gemini-1.5-pro')
    
    print("🎬 Video RAG Demo")
    print("================")
    print("This demo shows how to upload a video and chat with it using Gemini API")
    print()
    
    # Get video file path
    video_path = input("Enter path to your video file: ").strip()
    
    if not os.path.exists(video_path):
        print(f"❌ File not found: {video_path}")
        return
    
    try:
        print("📤 Uploading video...")
        video_file = genai.upload_file(path=video_path, display_name="demo_video")
        
        print("⏳ Processing video...")
        while video_file.state.name == "PROCESSING":
            print("   Still processing...")
            import time
            time.sleep(5)
            video_file = genai.get_file(video_file.name)
        
        if video_file.state.name == "FAILED":
            print("❌ Video processing failed")
            return
        
        print("✅ Video processed successfully!")
        print()
        
        # Interactive chat loop
        print("💬 You can now chat with your video. Type 'quit' to exit.")
        print("   Example questions:")
        print("   - What is happening in this video?")
        print("   - Describe the main events")
        print("   - Who are the people in this video?")
        print()
        
        while True:
            user_input = input("You: ").strip()
            
            if user_input.lower() in ['quit', 'exit', 'q']:
                break
            
            if not user_input:
                continue
            
            try:
                print("🤖 Thinking...")
                response = model.generate_content([video_file, user_input])
                print(f"AI: {response.text}")
                print()
            except Exception as e:
                print(f"❌ Error generating response: {e}")
        
        # Cleanup
        print("🧹 Cleaning up...")
        genai.delete_file(video_file.name)
        print("✅ Demo completed!")
        
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    demo_video_chat()

