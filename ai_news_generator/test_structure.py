#!/usr/bin/env python3
"""
Basic structure test for AI News Generator with CrewAI Flows
"""

import sys
import os

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

def test_models():
    """Test that models can be imported and instantiated."""
    print("🧪 Testing models...")
    try:
        from ai_news_flow.models import (
            NewsGeneratorState, 
            ResearchReport, 
            NewsArticle, 
            ContentDraft,
            EditedContent
        )
        
        # Test basic instantiation
        state = NewsGeneratorState(topic="Test Topic")
        print(f"  ✅ State created: {state.topic}")
        
        article = NewsArticle(
            title="Test Article",
            introduction="Test intro",
            conclusion="Test conclusion"
        )
        print(f"  ✅ Article created: {article.title}")
        
        print("✅ Models test passed!")
        return True
    except Exception as e:
        print(f"❌ Models test failed: {e}")
        return False

def test_directory_structure():
    """Test that all required directories exist."""
    print("\n🧪 Testing directory structure...")
    
    required_dirs = [
        "src/ai_news_flow",
        "src/ai_news_flow/crews",
        "src/ai_news_flow/crews/research_crew",
        "src/ai_news_flow/crews/content_crew", 
        "src/ai_news_flow/crews/editing_crew",
        "src/ai_news_flow/tools"
    ]
    
    all_exist = True
    for dir_path in required_dirs:
        if os.path.exists(dir_path):
            print(f"  ✅ {dir_path}")
        else:
            print(f"  ❌ {dir_path} - Missing!")
            all_exist = False
    
    if all_exist:
        print("✅ Directory structure test passed!")
    else:
        print("❌ Directory structure test failed!")
    
    return all_exist

def test_config_files():
    """Test that configuration files exist."""
    print("\n🧪 Testing configuration files...")
    
    config_files = [
        "src/ai_news_flow/crews/research_crew/config/agents.yaml",
        "src/ai_news_flow/crews/research_crew/config/tasks.yaml",
        "src/ai_news_flow/crews/content_crew/config/agents.yaml",
        "src/ai_news_flow/crews/content_crew/config/tasks.yaml",
        "src/ai_news_flow/crews/editing_crew/config/agents.yaml",
        "src/ai_news_flow/crews/editing_crew/config/tasks.yaml"
    ]
    
    all_exist = True
    for file_path in config_files:
        if os.path.exists(file_path):
            print(f"  ✅ {file_path}")
        else:
            print(f"  ❌ {file_path} - Missing!")
            all_exist = False
    
    if all_exist:
        print("✅ Configuration files test passed!")
    else:
        print("❌ Configuration files test failed!")
    
    return all_exist

def test_main_files():
    """Test that main files exist."""
    print("\n🧪 Testing main files...")
    
    main_files = [
        "app.py",
        "pyproject.toml", 
        "README.md",
        "src/ai_news_flow/main.py",
        "src/ai_news_flow/models.py"
    ]
    
    all_exist = True
    for file_path in main_files:
        if os.path.exists(file_path):
            print(f"  ✅ {file_path}")
        else:
            print(f"  ❌ {file_path} - Missing!")
            all_exist = False
    
    if all_exist:
        print("✅ Main files test passed!")
    else:
        print("❌ Main files test failed!")
    
    return all_exist

def test_streamlit_app():
    """Test basic Streamlit app structure."""
    print("\n🧪 Testing Streamlit app...")
    
    try:
        with open('app.py', 'r') as f:
            content = f.read()
        
        required_elements = [
            "import streamlit as st",
            "NewsGeneratorFlow", 
            "st.set_page_config",
            "generate_button"
        ]
        
        all_found = True
        for element in required_elements:
            if element in content:
                print(f"  ✅ Found: {element}")
            else:
                print(f"  ❌ Missing: {element}")
                all_found = False
        
        if all_found:
            print("✅ Streamlit app test passed!")
        else:
            print("❌ Streamlit app test failed!")
        
        return all_found
    except Exception as e:
        print(f"❌ Streamlit app test failed: {e}")
        return False

def main():
    """Run all tests."""
    print("🚀 AI News Generator Structure Test")
    print("="*50)
    
    tests = [
        test_directory_structure,
        test_main_files,
        test_config_files,
        test_models,
        test_streamlit_app
    ]
    
    passed = 0
    total = len(tests)
    
    for test_func in tests:
        if test_func():
            passed += 1
    
    print("\n" + "="*50)
    print(f"📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! The CrewAI Flow integration is ready!")
        print("\nNext steps:")
        print("1. Install dependencies: pip install crewai crewai-tools streamlit")
        print("2. Set up API keys (SERPER_API_KEY, COHERE_API_KEY)")
        print("3. Run: streamlit run app.py")
    else:
        print("⚠️  Some tests failed. Please review the issues above.")
    
    return passed == total

if __name__ == "__main__":
    main()