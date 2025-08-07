"""
Modern AI Newsletter Generator with Categorized Summaries
This version uses advanced NLP analysis and creates categorized newsletters.
"""

import sys
import json
from datetime import datetime

print("Loading newsletter generator...")

# Try to import our custom modules
try:
    from src.core import config
    from src.newsletter_generator.scraper import get_all_articles
    from src.newsletter_generator.simple_categorized_summarizer import run_categorized_summarization
    from src.utils.utils import ensure_directory_exists
    print("All modules loaded successfully!")
    
except ImportError as e:
    print(f"Error loading modules: {e}")
    print("Make sure you're in the right directory and all files are present!")
    sys.exit(1)


def show_help():
    """Show help information"""
    print("""
AI Newsletter Generator - Categorized Edition
=============================================

This program creates categorized newsletters from news websites using AI and NLP.

USAGE:
  python main.py          # Make a categorized newsletter
  python main.py --help   # Get help

WHAT IT DOES:
1. Gets articles from news websites
2. Uses NLP to analyze content quality and classify articles
3. Uses AI to create category-based summaries  
4. Creates both JSON and HTML newsletter files
5. Saves detailed analysis data for transparency

FILES CREATED:
• {config.INPUT_FOLDER}/detailed_articles_with_nlp_*.json    # Articles with full NLP analysis
• {config.OUTPUT_FOLDER}/categorized_summaries_*.json       # Newsletter data in JSON format
• {config.OUTPUT_FOLDER}/categorized_summaries_*.html       # Your finished newsletter

FEATURES:
• Smart content quality filtering
• Automatic article categorization
• AI-powered category summaries
• Professional HTML newsletter layout

NEED HELP?
• Make sure your .env file has your MISTRAL_API_KEY
• Check that all Python packages are installed (pip install -r requirements.txt)

Enjoy your modern, intelligent newsletter!
    """)


def print_step(number, description):
    """Print a numbered step in the process"""
    print(f"\n=== STEP {number}: {description} ===")


def make_newsletter():
    """
    Modern newsletter creation function using categorized AI summarization.
    """
    print("\n=== Modern Categorized Newsletter Generator ===")
    print("Creating your intelligent newsletter!")
    
    # Step 1: Check setup
    print_step(1, "Checking setup")
    
    if not config.OUTPUT_FOLDER:
        print("Output folder not configured")
        return None
    
    print(f"Output folder ready: {config.OUTPUT_FOLDER}")
    
    # Ensure directories exist
    ensure_directory_exists(config.INPUT_FOLDER)
    ensure_directory_exists(config.OUTPUT_FOLDER)
    
    print("Configuration check passed - ready to generate newsletters!")
    
    # Step 2: Get articles with NLP analysis
    print_step(2, "Scraping articles with NLP analysis")
    
    articles = get_all_articles()
    
    if not articles:
        print("No articles found! Try again later.")
        return None

    # Apply MAX_ARTICLES limit if configured
    if config.MAX_ARTICLES > 0 and len(articles) > config.MAX_ARTICLES:
        print(f"Found {len(articles)} articles, limiting to {config.MAX_ARTICLES} based on MAX_ARTICLES setting")
        articles = articles[:config.MAX_ARTICLES]
    
    print(f"Found {len(articles)} quality articles with NLP analysis!")
    
    # Step 3: Save detailed articles with NLP analysis
    print_step(3, "Saving detailed analysis data")
    
    # Create detailed articles file for transparency and debugging
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    detailed_file = f"{config.INPUT_FOLDER}/detailed_articles_with_nlp_{timestamp}.json"
    
    detailed_data = {
        'collection_timestamp': datetime.now().isoformat(),
        'total_articles': len(articles),
        'articles': articles
    }
    
    try:
        with open(detailed_file, 'w', encoding='utf-8') as f:
            json.dump(detailed_data, f, indent=2, ensure_ascii=False)
        print(f"Saved detailed analysis: {detailed_file}")
    except Exception as e:
        print(f"Warning: Could not save detailed file: {e}")
    
    # Step 4: Generate categorized newsletter
    print_step(4, "Creating categorized newsletter with AI")
    
    result = run_categorized_summarization(detailed_file)
    
    if not result:
        print("Failed to generate categorized newsletter")
        return None
    
    # Step 5: Display results
    print_step(5, "Newsletter completed!")
    
    newsletter = result['newsletter']
    print("\nNewsletter Statistics:")
    print(f"   Title: {newsletter['title']}")
    print(f"   Total Articles Analyzed: {newsletter['total_articles']}")  
    print(f"   Categories Generated: {newsletter['categories_count']}")

    print("\nCategories in Newsletter:")
    for category, summary in newsletter['category_summaries'].items():
        print(f"   • {summary['category_title']}: {summary['article_count']} articles")
    
    print("\nFiles Generated:")
    print(f"   JSON: {result['json_path']}")
    print(f"   HTML: {result['html_path']}")
    print(f"   Analysis: {detailed_file}")
    
    return result['html_path']


def main():
    """
    Main function - starts here when you run the program
    """
    # Show help if requested
    if len(sys.argv) > 1 and sys.argv[1] in ['-h', '--help', 'help']:
        show_help()
        return
    
    print("Starting modern newsletter generator...")
    
    try:
        # Make the newsletter
        result = make_newsletter()
        
        if result:
            print("\nSUCCESS! Your categorized newsletter is ready!")
            print(f"Open this file in your browser: {result}")
            print("\nFeatures in your newsletter:")
            print("   • Smart content quality filtering") 
            print("   • Automatic article categorization")
            print("   • AI-powered category summaries")
            print("   • Professional layout design")
        else:
            print("\nSomething went wrong - try again!")
            
    except KeyboardInterrupt:
        print("\n🛑 You stopped the program!")
        
    except Exception as error:
        print(f"\n💥 Unexpected error: {error}")
        print("Don't panic! This can happen sometimes.")
        print("Try running the program again, or check your API key and internet connection.")


print("Modern newsletter generator loaded and ready!")

# Start the program when file is run directly
if __name__ == "__main__":
    main()
