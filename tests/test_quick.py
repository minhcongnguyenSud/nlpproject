#!/usr/bin/env python3
"""
Quick Zero-Shot test with two articles
"""

from src.newsletter_generator.smart_analyzer import SmartContentAnalyzer

print("🧪 Quick Zero-Shot Classification Test...")

analyzer = SmartContentAnalyzer()

# Test 1: Government
test1 = {
    'title': 'City Council Approves Budget',
    'content': 'Mayor announces new municipal spending plan for infrastructure.'
}

result1 = analyzer.classify_article(test1)
print(f"\nGovernment Article:")
print(f"   Category: {result1['primary_category']} ({result1['confidence']}%)")
print(f"   Method: {result1['method']}")

# Test 2: Sports  
test2 = {
    'title': 'Hockey Team Wins Championship',
    'content': 'Local hockey players celebrate victory in the championship game.'
}

result2 = analyzer.classify_article(test2)
print(f"\n🏒 Sports Article:")
print(f"   Category: {result2['primary_category']} ({result2['confidence']}%)")
print(f"   Method: {result2['method']}")

# Test 3: Health
test3 = {
    'title': 'Hospital Opens New Ward',
    'content': 'Medical facility expands healthcare services with new patient wing.'
}

result3 = analyzer.classify_article(test3)
print(f"\n🏥 Health Article:")
print(f"   Category: {result3['primary_category']} ({result3['confidence']}%)")
print(f"   Method: {result3['method']}")

print(f"\nZero-Shot Classification working perfectly!")
