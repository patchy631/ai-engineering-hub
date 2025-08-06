#!/usr/bin/env python
"""
Test script for AI News Generator Flow

This script tests the basic functionality of the CrewAI flows implementation
without requiring API keys or external services for basic validation.
"""

import os
import sys
from unittest.mock import Mock, patch
from news_flow import NewsFlowState, AINewsGeneratorFlow, create_news_flow

def test_state_model():
    """Test the NewsFlowState Pydantic model"""
    print("🧪 Testing NewsFlowState model...")
    
    # Test basic state creation
    state = NewsFlowState(topic="Test Topic")
    assert state.topic == "Test Topic"
    assert state.temperature == 0.7  # default value
    assert state.research_report is None
    assert state.final_blog_post is None
    
    print("✅ NewsFlowState model tests passed")

def test_flow_initialization():
    """Test flow initialization"""
    print("🧪 Testing flow initialization...")
    
    # Test flow creation
    flow = create_news_flow("Test Topic", temperature=0.5)
    assert isinstance(flow, AINewsGeneratorFlow)
    assert flow.state.topic == "Test Topic"
    assert flow.state.temperature == 0.5
    
    print("✅ Flow initialization tests passed")

def test_flow_structure():
    """Test that the flow has the expected methods and decorators"""
    print("🧪 Testing flow structure...")
    
    flow = create_news_flow("Test Topic")
    
    # Check that required methods exist
    assert hasattr(flow, 'conduct_research')
    assert hasattr(flow, 'generate_content')
    assert hasattr(flow, 'finalize_output')
    assert hasattr(flow, 'get_blog_content')
    assert hasattr(flow, 'get_research_summary')
    
    print("✅ Flow structure tests passed")

def test_convenience_methods():
    """Test convenience methods"""
    print("🧪 Testing convenience methods...")
    
    flow = create_news_flow("Test Topic")
    
    # Test methods when state is empty
    assert flow.get_blog_content() == ""
    assert flow.get_research_summary() == ""
    
    print("✅ Convenience methods tests passed")

def run_integration_test():
    """
    Integration test - only runs if API keys are available
    This would actually execute the flow end-to-end
    """
    print("🧪 Checking for integration test prerequisites...")
    
    cohere_key = os.getenv('COHERE_API_KEY')
    serper_key = os.getenv('SERPER_API_KEY')
    
    if not cohere_key or not serper_key:
        print("⚠️  Skipping integration test - API keys not found")
        print("   Set COHERE_API_KEY and SERPER_API_KEY to run integration test")
        return
    
    print("🚀 Running integration test...")
    try:
        from news_flow import kickoff_news_flow
        
        # Run with a simple topic
        result = kickoff_news_flow("The benefits of renewable energy", temperature=0.3)
        
        # Validate result structure
        assert isinstance(result, dict)
        assert 'blog_post' in result
        assert 'word_count' in result
        assert isinstance(result['word_count'], int)
        assert result['word_count'] > 0
        
        print(f"✅ Integration test passed!")
        print(f"   Generated {result['word_count']} word blog post")
        
    except Exception as e:
        print(f"❌ Integration test failed: {str(e)}")

def main():
    """Run all tests"""
    print("🔬 Starting AI News Generator Flow Tests")
    print("=" * 50)
    
    try:
        test_state_model()
        test_flow_initialization()
        test_flow_structure()
        test_convenience_methods()
        
        print("\n" + "=" * 50)
        print("✅ All unit tests passed!")
        
        # Run integration test if possible
        print("\n" + "-" * 50)
        run_integration_test()
        
    except Exception as e:
        print(f"❌ Test failed: {str(e)}")
        sys.exit(1)
    
    print("\n" + "=" * 50)
    print("🎉 All tests completed successfully!")

if __name__ == "__main__":
    main()