#!/usr/bin/env python3
"""
Test script for Zero-Shot Classification in SmartContentAnalyzer
"""

from src.newsletter_generator.smart_analyzer import SmartContentAnalyzer

def test_zero_shot_classification():
    """Test the Zero-Shot classification functionality"""
    print("🧪 Testing Zero-Shot Classification...")
    
    # Initialize analyzer
    analyzer = SmartContentAnalyzer()
    
    # Test articles with different categories
    test_articles = [
        {
            'title': 'City Council Approves New Budget for Municipal Services',
            'content': 'The Greater Sudbury City Council voted unanimously yesterday to approve a $50 million budget increase for municipal services. Mayor Jane Smith announced that the funding will go toward infrastructure improvements and public services. The decision came after extensive deliberations by elected officials and input from city administrators.'
        },
        {
            'title': 'Local Hospital Introduces New Heart Surgery Program',
            'content': 'Health Sciences North announced the launch of a new cardiac surgery program that will serve patients across Northern Ontario. The medical facility has recruited specialist doctors and invested in advanced surgical equipment. This healthcare initiative is expected to reduce wait times for heart procedures.'
        },
        {
            'title': 'Sudbury Wolves Win Championship Game',
            'content': 'The Sudbury Wolves hockey team defeated their rivals 4-2 in an exciting championship game last night. Team captain Mike Johnson scored the winning goal in the final period. The sports victory brings the first championship trophy to the city in five years.'
        },
        {
            'title': 'New Tech Company Opens Downtown Office',
            'content': 'InnovateTech Solutions has opened a new office in downtown Sudbury, creating 75 local jobs in the technology sector. The company specializes in software development and artificial intelligence. This business expansion represents a significant economic development for the region.'
        },
        {
            'title': 'Summer Music Festival Draws Large Crowds',
            'content': 'The annual Northern Lights Music Festival attracted over 10,000 visitors to Bell Park this weekend. Local and international artists performed on three stages. Community volunteers helped organize the cultural event, which featured food vendors and family activities.'
        }
    ]
    
    print(f"\n🔍 Testing {len(test_articles)} articles...")
    
    for i, article in enumerate(test_articles, 1):
        print(f"\n--- Test Article {i} ---")
        print(f"Title: {article['title']}")
        
        # Classify the article
        result = analyzer.classify_article(article)
        
        print(f"Classification Results:")
        print(f"   Primary Category: {result['primary_category']}")
        print(f"   Confidence: {result['confidence']}%")
        print(f"   Method Used: {result['method']}")
        print(f"   Secondary Categories: {result.get('secondary_categories', [])}")
        
        if 'all_scores' in result:
            print(f"   All Scores: {result['all_scores']}")
    
    print(f"\nZero-Shot Classification test completed!")

if __name__ == "__main__":
    test_zero_shot_classification()
