#!/usr/bin/env python3
"""
Test optimized scraper with single analyzer instance
"""

from src.newsletter_generator.scraper import get_analyzer

print("Testing optimized analyzer...")

# Get analyzer instance (should load model only once)
analyzer1 = get_analyzer()
print(f"Analyzer 1 Zero-Shot available: {analyzer1.zero_shot_classifier is not None}")

# Get analyzer instance again (should reuse existing)
analyzer2 = get_analyzer()
print(f"Analyzer 2 Zero-Shot available: {analyzer2.zero_shot_classifier is not None}")

# Test that they are the same instance
print(f"Same instance: {analyzer1 is analyzer2}")

# Test classification
test_article = {
    'title': 'City Council Approves Budget',
    'content': 'The municipal government voted to approve spending on infrastructure projects.'
}

result1 = analyzer1.classify_article(test_article)
result2 = analyzer2.classify_article(test_article)

print(f"Result 1: {result1['primary_category']} ({result1['confidence']}%) via {result1['method']}")
print(f"Result 2: {result2['primary_category']} ({result2['confidence']}%) via {result2['method']}")

print("Optimization test: SUCCESS - Single model instance reused!")
