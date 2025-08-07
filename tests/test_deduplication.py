#!/usr/bin/env python3
"""
Test script to verify the deduplication functionality
"""

from src.newsletter_generator.scraper import remove_duplicate_articles

# Test data with duplicates
test_articles = [
    {
        'title': 'Opening Ceremonies Kick Off Sudbury 2025 Ontario 55+ Summer Games with Spirit',
        'source': 'https://www.greatersudbury.ca/',
        'source_url': 'https://www.greatersudbury.ca/news/opening-ceremonies-1',
        'content': 'Test content 1'
    },
    {
        'title': 'Opening Ceremonies Kick Off Sudbury 2025 Ontario 55+ Summer Games with Spirit',  # Exact duplicate
        'source': 'https://www.example.com/',
        'source_url': 'https://www.example.com/news/opening-ceremonies-2',
        'content': 'Test content 2'
    },
    {
        'title': '2025 Civic Holiday Municipal Service Schedule',
        'source': 'https://www.greatersudbury.ca/',
        'source_url': 'https://www.greatersudbury.ca/news/civic-holiday-1',
        'content': 'Test content 3'
    },
    {
        'title': '2025 Civic Holiday Municipal Service Schedule',  # Exact duplicate
        'source': 'https://www.example.com/',
        'source_url': 'https://www.example.com/news/civic-holiday-2',
        'content': 'Test content 4'
    },
    {
        'title': 'Different Article About Local News',
        'source': 'https://www.thesudburystar.com/',
        'source_url': 'https://www.thesudburystar.com/news/different-article',
        'content': 'Test content 5'
    },
    {
        'title': 'Same URL Test',
        'source': 'https://www.example.com/',
        'source_url': 'https://www.example.com/news/same-url',
        'content': 'Test content 6'
    },
    {
        'title': 'Another Same URL Test',  # Same URL should be detected
        'source': 'https://www.different.com/',
        'source_url': 'https://www.example.com/news/same-url',
        'content': 'Test content 7'
    }
]

print("Testing deduplication system...")
print(f"Original articles: {len(test_articles)}")

for i, article in enumerate(test_articles, 1):
    print(f"   {i}. '{article['title'][:50]}...' - {article['source_url']}")

print("\n" + "="*80)

# Test deduplication
deduplicated = remove_duplicate_articles(test_articles)

print(f"After deduplication: {len(deduplicated)}")
print(f"Removed duplicates: {len(test_articles) - len(deduplicated)}")

print("\nRemaining articles:")
for i, article in enumerate(deduplicated, 1):
    print(f"   {i}. '{article['title'][:50]}...' - {article['source_url']}")

print("\nDeduplication test completed!")
