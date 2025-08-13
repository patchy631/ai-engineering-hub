#!/usr/bin/env python
"""
Simple validation script that tests the basic structure without requiring external dependencies
"""

import sys
import importlib.util
from pathlib import Path

def test_file_structure():
    """Test that all required files exist"""
    print("🧪 Testing file structure...")
    
    required_files = [
        "news_flow.py",
        "app_flow.py", 
        "requirements.txt",
        "test_flow.py"
    ]
    
    missing_files = []
    for file in required_files:
        if not Path(file).exists():
            missing_files.append(file)
    
    if missing_files:
        print(f"❌ Missing files: {missing_files}")
        return False
    
    print("✅ All required files exist")
    return True

def test_python_syntax():
    """Test that Python files have valid syntax"""
    print("🧪 Testing Python syntax...")
    
    python_files = ["news_flow.py", "app_flow.py", "test_flow.py"]
    
    for file in python_files:
        try:
            with open(file, 'r') as f:
                content = f.read()
                compile(content, file, 'exec')
            print(f"  ✅ {file} - syntax OK")
        except SyntaxError as e:
            print(f"  ❌ {file} - syntax error: {e}")
            return False
    
    print("✅ All Python files have valid syntax")
    return True

def test_imports_structure():
    """Test that the imports look correct (without actually importing)"""
    print("🧪 Testing import structure...")
    
    with open("news_flow.py", 'r') as f:
        content = f.read()
        
    # Check for key imports
    required_imports = [
        "from crewai.flow.flow import Flow, listen, start",
        "from crewai import Agent, Task, Crew, LLM", 
        "from pydantic import BaseModel, Field"
    ]
    
    for imp in required_imports:
        if imp not in content:
            print(f"❌ Missing import: {imp}")
            return False
    
    print("✅ Import structure looks correct")
    return True

def test_class_definitions():
    """Test that key classes are defined"""
    print("🧪 Testing class definitions...")
    
    with open("news_flow.py", 'r') as f:
        content = f.read()
        
    required_classes = [
        "class ResearchReport(BaseModel):",
        "class BlogPost(BaseModel):",
        "class NewsFlowState(BaseModel):",
        "class AINewsGeneratorFlow(Flow"
    ]
    
    for cls in required_classes:
        if cls not in content:
            print(f"❌ Missing class definition: {cls}")
            return False
    
    print("✅ All required classes are defined")
    return True

def test_flow_decorators():
    """Test that flow decorators are present"""
    print("🧪 Testing flow decorators...")
    
    with open("news_flow.py", 'r') as f:
        content = f.read()
        
    required_decorators = [
        "@start()",
        "@listen(conduct_research)",
        "@listen(generate_content)"
    ]
    
    for decorator in required_decorators:
        if decorator not in content:
            print(f"❌ Missing decorator: {decorator}")
            return False
    
    print("✅ All required flow decorators are present")
    return True

def test_requirements():
    """Test requirements.txt content"""
    print("🧪 Testing requirements.txt...")
    
    with open("requirements.txt", 'r') as f:
        content = f.read()
    
    required_packages = [
        "crewai>=",
        "crewai-tools>=",
        "streamlit>=",
        "python-dotenv>=",
        "pydantic>="
    ]
    
    for package in required_packages:
        if package not in content:
            print(f"❌ Missing package requirement: {package}")
            return False
    
    print("✅ Requirements.txt has all required packages")
    return True

def main():
    """Run all validation tests"""
    print("🔍 AI News Generator Flow - Structure Validation")
    print("=" * 50)
    
    tests = [
        test_file_structure,
        test_python_syntax,
        test_imports_structure, 
        test_class_definitions,
        test_flow_decorators,
        test_requirements
    ]
    
    passed = 0
    failed = 0
    
    for test in tests:
        try:
            if test():
                passed += 1
            else:
                failed += 1
        except Exception as e:
            print(f"❌ {test.__name__} failed with exception: {e}")
            failed += 1
        print()
    
    print("=" * 50)
    print(f"📊 Results: {passed} passed, {failed} failed")
    
    if failed == 0:
        print("🎉 All structure validation tests passed!")
        print("✅ CrewAI flows implementation is structurally sound")
        return True
    else:
        print("❌ Some validation tests failed")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)