#!/usr/bin/env python3
"""
Simple test for SmartContentAnalyzer initialization
"""

print("Testing SmartContentAnalyzer initialization...")

try:
    from src.newsletter_generator.smart_analyzer import SmartContentAnalyzer
    print("SmartContentAnalyzer imported successfully")
    
    analyzer = SmartContentAnalyzer()
    print("SmartContentAnalyzer initialized successfully")
    print(f"   Zero-Shot Classifier available: {analyzer.zero_shot_classifier is not None}")
    
    # Test with a simple article
    test_article = {
        'title': 'City Council Meeting',
        'content': 'The city council met to discuss budget issues and municipal services.'
    }
    
    print("\n🧪 Testing classification...")
    result = analyzer.classify_article(test_article)
    print(f"Classification result: {result}")
    
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()
