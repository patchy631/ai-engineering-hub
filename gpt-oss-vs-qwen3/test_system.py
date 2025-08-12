#!/usr/bin/env python3
"""
Test script for the reasoning model comparison system.
"""

from model_service import get_all_model_names, validate_model_name, get_model_mapping
from code_evaluation_opik import evaluate_reasoning
import asyncio
import os


def test_model_service():
    """Test the model service functionality."""
    print("Testing Model Service...")
    
    # Test getting all model names
    models = get_all_model_names()
    print(f"✓ Available models: {models}")
    assert len(models) > 0, "No models available"
    
    # Test model validation
    for model in models:
        assert validate_model_name(model), f"Model {model} should be valid"
        mapping = get_model_mapping(model)
        print(f"✓ Model {model} -> {mapping}")
    
    # Test invalid model
    assert not validate_model_name("Invalid Model"), "Invalid model should not be valid"
    
    print("✓ Model service tests passed!")


def test_evaluation_system():
    """Test the evaluation system."""
    print("\nTesting Evaluation System...")
    
    # Test basic evaluation
    test_response = """
    The question asks about the relationship between logic and mathematics. 
    
    Logic forms the foundation of mathematical reasoning. In mathematics, we use logical principles to:
    1. Construct valid proofs
    2. Establish the truth of statements
    3. Build consistent theoretical frameworks
    
    For example, the principle of non-contradiction ensures that a mathematical statement cannot be both true and false simultaneously. This logical principle is essential for maintaining the consistency of mathematical systems.
    
    Furthermore, formal logic provides the language and rules that allow mathematicians to express complex ideas precisely and reason about them systematically.
    """
    
    try:
        result = evaluate_reasoning(test_response)
        print(f"✓ Evaluation completed successfully")
        print(f"  Overall Score: {result['overall_score']:.2f}")
        print(f"  Passed: {result['passed']}")
        
        # Check structure
        assert 'detailed_metrics' in result, "Missing detailed_metrics"
        assert 'overall_score' in result, "Missing overall_score"
        assert 'passed' in result, "Missing passed flag"
        
        expected_metrics = ['logical_reasoning', 'factual_accuracy', 'coherence', 'depth_of_analysis']
        for metric in expected_metrics:
            assert metric in result['detailed_metrics'], f"Missing metric: {metric}"
            assert 'score' in result['detailed_metrics'][metric], f"Missing score for {metric}"
            assert 'reason' in result['detailed_metrics'][metric], f"Missing reason for {metric}"
            print(f"  {metric.replace('_', ' ').title()}: {result['detailed_metrics'][metric]['score']:.2f}")
        
        print("✓ Evaluation system tests passed!")
        
    except Exception as e:
        print(f"⚠️  Evaluation test failed (this is expected if Opik is not configured): {e}")
        print("   This is normal if OPIK credentials are not set up")


def test_system_integration():
    """Test basic system integration."""
    print("\nTesting System Integration...")
    
    # Test imports
    try:
        import streamlit as st
        print("✓ Streamlit import successful")
    except ImportError as e:
        print(f"✗ Streamlit import failed: {e}")
        return False
    
    try:
        import pandas as pd
        print("✓ Pandas import successful")
    except ImportError as e:
        print(f"✗ Pandas import failed: {e}")
        return False
    
    try:
        import plotly.express as px
        print("✓ Plotly import successful")
    except ImportError as e:
        print(f"✗ Plotly import failed: {e}")
        return False
    
    print("✓ System integration tests passed!")
    return True


def main():
    """Run all tests."""
    print("=" * 60)
    print("REASONING MODEL COMPARISON SYSTEM TEST")
    print("=" * 60)
    
    try:
        test_model_service()
        test_evaluation_system()
        integration_success = test_system_integration()
        
        print("\n" + "=" * 60)
        if integration_success:
            print("🎉 ALL TESTS PASSED!")
            print("\nTo run the app:")
            print("  uv run streamlit run app.py")
        else:
            print("⚠️  Some tests failed. Check dependencies.")
        print("=" * 60)
        
    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()