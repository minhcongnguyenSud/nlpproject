#!/usr/bin/env python3
"""
Test the NLP-Enhanced Scraper

This script tests our new smart content analysis and article classification system.
"""

import sys
import json
from datetime import datetime

# Add src to path
sys.path.append('src')

try:
    from src.newsletter_generator.scraper import get_all_articles
    from src.newsletter_generator.smart_analyzer import SmartContentAnalyzer
except ImportError as e:
    print(f"Import error: {e}")
    print("Make sure you're running from the project root directory")
    sys.exit(1)


def test_nlp_scraper():
    """Test the NLP-enhanced scraper"""
    print("Testing NLP-Enhanced Article Scraper")
    print("=" * 60)
    
    print("\n[1/3] Scraping articles with smart NLP analysis...")
    articles = get_all_articles()
    
    if not articles:
        print("No articles found. Check your internet connection or website accessibility.")
        return
    
    print(f"\nFound {len(articles)} quality articles!")
    
    print("\n[2/3] Analyzing article classifications...")
    
    # Analyze classifications
    categories = {}
    quality_scores = []
    
    for article in articles:
        # Get NLP analysis that was added during scraping
        nlp_analysis = article.get('nlp_analysis', {})
        
        if nlp_analysis:
            # Classification analysis
            classification = nlp_analysis.get('classification', {})
            category = classification.get('primary_category', 'unknown')
            confidence = classification.get('confidence', 0)
            
            if category not in categories:
                categories[category] = []
            categories[category].append({
                'title': article['title'][:60] + '...',
                'confidence': confidence
            })
            
            # Quality score analysis
            quality_analysis = nlp_analysis.get('quality_analysis', {})
            quality_score = quality_analysis.get('quality_score', 0)
            quality_scores.append(quality_score)
    
    # Display results
    print(f"\nArticle Classification Results:")
    print("-" * 40)
    
    for category, category_articles in categories.items():
        print(f"\n{category.upper().replace('_', ' ')} ({len(category_articles)} articles)")
        for article in category_articles[:3]:  # Show top 3
            print(f"   • {article['title']} (confidence: {article['confidence']}%)")
        if len(category_articles) > 3:
            print(f"   ... and {len(category_articles) - 3} more")
    
    # Quality score analysis
    if quality_scores:
        avg_quality = sum(quality_scores) / len(quality_scores)
        min_quality = min(quality_scores)
        max_quality = max(quality_scores)
        
        print(f"\nQuality Score Analysis:")
        print(f"   Average Quality Score: {avg_quality:.1f}/100")
        print(f"   Range: {min_quality} - {max_quality}")
    
    print("\n[3/3] Generating detailed analysis report...")
    
    # Generate detailed report
    report_data = {
        'analysis_timestamp': datetime.now().isoformat(),
        'total_articles': len(articles),
        'categories': {cat: len(arts) for cat, arts in categories.items()},
        'quality_statistics': {
            'average_quality': avg_quality if quality_scores else 0,
            'min_quality': min_quality if quality_scores else 0,
            'max_quality': max_quality if quality_scores else 0
        },
        'sample_articles': []
    }
    
    # Add sample articles with full NLP analysis
    for i, article in enumerate(articles[:5]):  # Top 5 articles
        nlp_analysis = article.get('nlp_analysis', {})
        
        sample = {
            'title': article['title'],
            'source': article.get('source', 'unknown'),
            'word_count': len(article.get('content', '').split()),
            'quality_score': nlp_analysis.get('quality_analysis', {}).get('quality_score', 0),
            'category': nlp_analysis.get('classification', {}).get('primary_category', 'unknown'),
            'confidence': nlp_analysis.get('classification', {}).get('confidence', 0),
            'key_entities': nlp_analysis.get('entities', {})
        }
        report_data['sample_articles'].append(sample)
    
    # Save detailed report
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    report_file = f"output/nlp_analysis_report_{timestamp}.json"
    
    with open(report_file, 'w', encoding='utf-8') as f:
        json.dump(report_data, f, indent=2, ensure_ascii=False)
    
    print(f"Detailed report saved to: {report_file}")
    
    print("\n" + "=" * 60)
    print("NLP-Enhanced Scraper Test Complete!")
    print("=" * 60)
    
    print(f"\nSummary:")
    print(f"   • {len(articles)} quality articles found")
    print(f"   • {len(categories)} different categories identified")
    print(f"   • Average quality score: {avg_quality:.1f}/100" if quality_scores else "   • No quality scores available")
    
    print(f"\n💡 Key Improvements:")
    print("   • Removed geographic filtering - now finds articles from all topics")
    print("   • Smart quality analysis using NLP techniques")
    print("   • Automatic article classification into categories")
    print("   • Entity extraction (people, places, organizations)")
    print("   • Detailed quality scoring and reasoning")
    
    return articles, report_data


def test_individual_analyzer():
    """Test the smart analyzer with sample content"""
    print("\n🧪 Testing Smart Content Analyzer individually...")
    
    # Sample articles for testing
    test_articles = [
        {
            'title': 'City Council Approves New Budget for Community Programs',
            'content': 'The Sudbury City Council voted unanimously yesterday to approve a $2.5 million budget increase for community programs. Mayor Johnson announced that the funds will support youth sports, senior services, and local arts initiatives. The budget will be implemented starting next month, according to city officials.'
        },
        {
            'title': 'Local Restaurant Chain Expands with Third Location',
            'content': 'Popular restaurant chain "Northern Eats" announced plans to open their third location in downtown Sudbury. The family-owned business has seen significant growth over the past two years. Construction on the new 4,000 square foot location will begin in September, creating 25 new jobs for the community.'
        },
        {
            'title': 'Click Here for More Info Subscribe Newsletter',
            'content': 'Subscribe to our newsletter for updates. Click here for more information about our services. Follow us on social media for daily updates.'
        }
    ]
    
    analyzer = SmartContentAnalyzer()
    
    for i, article in enumerate(test_articles, 1):
        print(f"\n--- Test Article {i} ---")
        print(f"Title: {article['title'][:50]}...")
        
        # Quality analysis
        quality = analyzer.analyze_content_quality(article)
        print(f"Quality Score: {quality['quality_score']}/100")
        print(f"Is Quality: {quality['is_quality']}")
        print(f"Reasons: {', '.join(quality['reasons'])}")
        
        # Classification
        classification = analyzer.classify_article(article)
        print(f"Category: {classification['primary_category']}")
        print(f"Confidence: {classification['confidence']}%")
        
        # Entities
        entities = analyzer.extract_key_entities(article)
        if entities['people']:
            print(f"People: {', '.join(entities['people'][:3])}")
        if entities['locations']:
            print(f"Locations: {', '.join(entities['locations'][:3])}")
        if entities['key_phrases']:
            print(f"Key Phrases: {', '.join(entities['key_phrases'][:3])}")


def main():
    """Main test function"""
    if len(sys.argv) > 1 and sys.argv[1] == '--analyzer-only':
        test_individual_analyzer()
    else:
        # Run full test
        test_individual_analyzer()
        test_nlp_scraper()


if __name__ == "__main__":
    main()
