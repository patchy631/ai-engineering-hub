#!/usr/bin/env python3
"""
Sample script demonstrating the CrewAI Agentic Flow

This script shows how to use the ResearchFlow to orchestrate
Researcher and Writer agents for comprehensive query answering.
"""

import os
import sys
from dotenv import load_dotenv

# Add the src directory to Python path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from crewai_agentic_flow.flows import ResearchFlow


def main():
    """Main function to demonstrate the agentic workflow"""
    
    # Load environment variables
    load_dotenv()
    
    print("🚀 CrewAI Agentic Flow Demo")
    print("=" * 50)
    
    # Example queries to demonstrate the workflow
    sample_queries = [
        "What are the latest developments in artificial intelligence and machine learning?",
        "How does blockchain technology work and what are its real-world applications?",
        "What are the benefits and challenges of remote work in 2024?",
        "What is quantum computing and how might it impact cybersecurity?"
    ]
    
    print("\nAvailable sample queries:")
    for i, query in enumerate(sample_queries, 1):
        print(f"{i}. {query}")
    
    print("\nOptions:")
    print("- Enter a number (1-4) to use a sample query")
    print("- Enter your own custom query")
    print("- Press Enter to use the default query")
    
    user_input = input("\nYour choice: ").strip()
    
    # Determine which query to use
    if user_input.isdigit() and 1 <= int(user_input) <= len(sample_queries):
        query = sample_queries[int(user_input) - 1]
    elif user_input:
        query = user_input
    else:
        query = sample_queries[0]  # Default to first sample query
    
    print(f"\n🔍 Processing query: '{query}'")
    print("=" * 50)
    
    try:
        # Create and run the flow
        flow = ResearchFlow()
        results = flow.run_flow(query)
        
        # Display results
        print("\n" + "=" * 50)
        print("📋 FLOW EXECUTION RESULTS")
        print("=" * 50)
        
        print(f"\n📝 Original Query:")
        print(f"{results['query']}")
        
        print(f"\n🔍 Research Findings:")
        print("-" * 30)
        print(results['research_findings'])
        
        print(f"\n📄 Final Answer:")
        print("-" * 30)
        print(results['final_answer'])
        
        print("\n✅ Flow completed successfully!")
        
        # Optional: Save results to file
        save_results = input("\nSave results to file? (y/n): ").strip().lower()
        if save_results == 'y':
            filename = f"flow_results_{hash(query) % 10000}.txt"
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(f"Query: {results['query']}\n\n")
                f.write(f"Research Findings:\n{results['research_findings']}\n\n")
                f.write(f"Final Answer:\n{results['final_answer']}\n")
            print(f"💾 Results saved to {filename}")
        
    except Exception as e:
        print(f"\n❌ Error executing flow: {str(e)}")
        print("\nThis might be due to:")
        print("- Missing API keys (set OPENAI_API_KEY or other LLM provider keys)")
        print("- Network connectivity issues")
        print("- CrewAI configuration problems")
        
        print(f"\nFull error details:")
        import traceback
        traceback.print_exc()


def demo_flow_visualization():
    """Demonstrate flow visualization capabilities"""
    print("\n🔄 Flow Structure Visualization")
    print("-" * 30)
    
    try:
        flow = ResearchFlow()
        # Initialize with a sample query for visualization
        flow.state = flow.FlowState(query="Sample query for visualization")
        
        print("Flow structure:")
        print("1. initialize_research() - @start() decorator")
        print("2. conduct_research() - @listen(initialize_research)")
        print("3. generate_answer() - @listen(conduct_research)")
        
        print("\nData flow:")
        print("Query -> Research Findings -> Final Answer")
        
        # If flow.plot() is available, you could visualize the flow
        # flow.plot()
        
    except Exception as e:
        print(f"Visualization not available: {e}")


if __name__ == "__main__":
    try:
        main()
        
        # Optional demo of flow structure
        show_viz = input("\nShow flow structure? (y/n): ").strip().lower()
        if show_viz == 'y':
            demo_flow_visualization()
            
    except KeyboardInterrupt:
        print("\n\n👋 Demo interrupted by user")
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()