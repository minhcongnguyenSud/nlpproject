#!/usr/bin/env python3
"""
Test script for Categorized Newsletter Generation

This script processes the collected articles with NLP analysis and creates
categorized summaries using Mistral AI.
"""

import sys
import glob
from pathlib import Path

# Add src to path
sys.path.append('src')

def main():
    print("Categorized Newsletter Generator")
    print("=" * 60)
    
    # Find the most recent detailed articles file
    input_files = glob.glob("input/detailed_articles_with_nlp_*.json")
    
    if not input_files:
        print("No detailed articles file found.")
        print("Please run the scraper first to collect articles with NLP analysis.")
        return
    
    # Use the most recent file
    latest_file = max(input_files, key=lambda f: Path(f).stat().st_mtime)
    print(f"Using articles file: {latest_file}")
    
    try:
        from src.newsletter_generator.simple_categorized_summarizer import run_categorized_summarization
        
        print("\\n[1/2] Processing articles and organizing by categories...")
        result = run_categorized_summarization(latest_file)
        
        if result:
            print("\\n[2/2] Newsletter generation complete!")
            print("\\nResults:")
            newsletter = result['newsletter']
            print(f"   Title: {newsletter['title']}")
            print(f"   Total Articles: {newsletter['total_articles']}")
            print(f"   Categories: {newsletter['categories_count']}")
            
            print("\\nCategories Generated:")
            for category, summary in newsletter['category_summaries'].items():
                print(f"   • {summary['category_title']}: {summary['article_count']} articles")
            
            print(f"\\nFiles Generated:")
            print(f"   JSON: {result['json_path']}")
            print(f"   HTML: {result['html_path']}")
            
            print("\\nCategorized newsletter generation successful!")
            
        else:
            print("Newsletter generation failed.")
            
    except ImportError as e:
        print(f"Import error: {e}")
        print("Make sure all dependencies are installed.")
    except Exception as e:
        print(f"Error: {e}")


if __name__ == "__main__":
    main()
