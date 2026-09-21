#!/usr/bin/env python
"""
Demo script for AI News Generator Flow

This script demonstrates how to use the CrewAI flows implementation
programmatically, showcasing the agentic workflow capabilities.

Usage:
    python demo_flow.py [topic] [temperature]

Example:
    python demo_flow.py "Latest AI developments" 0.7
"""

import sys
import os
from dotenv import load_dotenv
from news_flow import create_news_flow, kickoff_news_flow

# Load environment variables
load_dotenv()

def check_api_keys():
    """Check if required API keys are available"""
    cohere_key = os.getenv('COHERE_API_KEY')
    serper_key = os.getenv('SERPER_API_KEY')
    
    if not cohere_key:
        print("❌ COHERE_API_KEY not found. Please set it in your .env file.")
        return False
        
    if not serper_key:
        print("❌ SERPER_API_KEY not found. Please set it in your .env file.")
        return False
        
    print("✅ API keys found")
    return True

def demo_simple_usage(topic="The future of renewable energy", temperature=0.7):
    """Demonstrate simple usage of the flow"""
    print("\n" + "="*60)
    print("🚀 SIMPLE USAGE DEMO")
    print("="*60)
    print(f"Topic: {topic}")
    print(f"Temperature: {temperature}")
    print()
    
    try:
        # Simple one-liner execution
        result = kickoff_news_flow(topic, temperature)
        
        print("📊 RESULTS:")
        print(f"  Word count: {result['word_count']}")
        print(f"  Citations: {result['citations_count']}")
        print(f"  Blog post length: {len(result['blog_post'])} characters")
        
        # Save to file
        filename = f"demo_output_{topic.lower().replace(' ', '_')}.md"
        with open(filename, 'w') as f:
            f.write(result['blog_post'])
        print(f"  Saved to: {filename}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def demo_advanced_usage(topic="AI ethics in healthcare", temperature=0.5):
    """Demonstrate advanced flow usage with state inspection"""
    print("\n" + "="*60)
    print("🔬 ADVANCED USAGE DEMO")
    print("="*60)
    print(f"Topic: {topic}")
    print(f"Temperature: {temperature}")
    print()
    
    try:
        # Create flow instance for inspection
        print("🔧 Creating flow instance...")
        flow = create_news_flow(topic, temperature)
        
        # Inspect initial state
        print(f"📋 Initial state:")
        print(f"  Topic: {flow.state.topic}")
        print(f"  Temperature: {flow.state.temperature}")
        print(f"  Research report: {flow.state.research_report}")
        print(f"  Final blog post: {flow.state.final_blog_post}")
        
        # Execute the flow
        print("\n🔄 Executing flow...")
        result = flow.kickoff()
        
        # Inspect final state
        print(f"\n📋 Final state:")
        print(f"  Research report exists: {flow.state.research_report is not None}")
        print(f"  Blog post exists: {flow.state.final_blog_post is not None}")
        
        if flow.state.research_report:
            print(f"  Research citations: {len(flow.state.research_report.citations)}")
            print(f"  Executive summary: {len(flow.state.research_report.executive_summary)} chars")
        
        if flow.state.final_blog_post:
            print(f"  Blog title: {flow.state.final_blog_post.title}")
            print(f"  Blog word count: {flow.state.final_blog_post.word_count}")
        
        # Use convenience methods
        print(f"\n📄 Content preview (first 200 chars):")
        content = flow.get_blog_content()
        print(f"  {content[:200]}...")
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def demo_batch_processing():
    """Demonstrate processing multiple topics"""
    print("\n" + "="*60)
    print("📦 BATCH PROCESSING DEMO")
    print("="*60)
    
    topics = [
        "Quantum computing breakthroughs 2024",
        "Sustainable technology innovations",
        "AI in space exploration"
    ]
    
    results = []
    
    for i, topic in enumerate(topics, 1):
        print(f"\n📝 Processing {i}/{len(topics)}: {topic}")
        
        try:
            # Use lower temperature for consistency in batch processing
            result = kickoff_news_flow(topic, temperature=0.3)
            results.append({
                'topic': topic,
                'word_count': result['word_count'],
                'citations_count': result['citations_count'],
                'success': True
            })
            print(f"  ✅ Success - {result['word_count']} words")
            
        except Exception as e:
            print(f"  ❌ Failed - {e}")
            results.append({
                'topic': topic,
                'success': False,
                'error': str(e)
            })
    
    # Summary
    print(f"\n📊 BATCH RESULTS:")
    successful = sum(1 for r in results if r['success'])
    print(f"  Successful: {successful}/{len(topics)}")
    
    for result in results:
        if result['success']:
            print(f"  ✅ {result['topic']} - {result['word_count']} words")
        else:
            print(f"  ❌ {result['topic']} - {result.get('error', 'Unknown error')}")
    
    return successful > 0

def main():
    """Main demo function"""
    print("🤖 AI News Generator - CrewAI Flows Demo")
    print("GitHub Issue #168 Implementation")
    
    # Check API keys
    if not check_api_keys():
        print("\n💡 To run this demo:")
        print("1. Get API keys from https://serper.dev/ and https://dashboard.cohere.com/")
        print("2. Create a .env file with:")
        print("   COHERE_API_KEY=your_key_here")
        print("   SERPER_API_KEY=your_key_here")
        sys.exit(1)
    
    # Parse command line arguments
    topic = sys.argv[1] if len(sys.argv) > 1 else "The impact of AI on modern journalism"
    temperature = float(sys.argv[2]) if len(sys.argv) > 2 else 0.7
    
    # Run demos
    demos_run = 0
    demos_successful = 0
    
    # Simple usage demo
    demos_run += 1
    if demo_simple_usage(topic, temperature):
        demos_successful += 1
    
    # Advanced usage demo (only if simple demo worked)
    if demos_successful > 0:
        demos_run += 1
        if demo_advanced_usage():
            demos_successful += 1
    
    # Batch processing demo (only if previous demos worked)
    if demos_successful > 1:
        demos_run += 1 
        if demo_batch_processing():
            demos_successful += 1
    
    # Final summary
    print("\n" + "="*60)
    print("🎯 DEMO SUMMARY")
    print("="*60)
    print(f"Demos run: {demos_run}")
    print(f"Demos successful: {demos_successful}")
    
    if demos_successful == demos_run:
        print("🎉 All demos completed successfully!")
        print("✅ CrewAI flows implementation is working correctly")
    else:
        print("⚠️  Some demos failed - check API keys and network connection")
    
    print(f"\n💡 Next steps:")
    print(f"  - Run: streamlit run app_flow.py")
    print(f"  - Or use: from news_flow import kickoff_news_flow")

if __name__ == "__main__":
    main()