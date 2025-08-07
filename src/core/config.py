"""
Simple configuration file for Newsletter Generator

This file loads settings from the .env file and provides them to other parts of the program.
Everything is kept simple and easy to understand for junior developers.
"""

import os
import re
from dotenv import load_dotenv

# Load environment variables from .env file
# This keeps our API keys secure and separate from our code
load_dotenv()

# API Configuration
# This is your secret key from Mistral AI - never share this publicly
MISTRAL_API_KEY = os.getenv('MISTRAL_API_KEY', '')

# Newsletter Settings
# These control how our newsletter looks and what content it includes
NEWSLETTER_TITLE = os.getenv('NEWSLETTER_TITLE', 'Daily News Digest')
MAX_ARTICLES = int(os.getenv('MAX_ARTICLES', '50'))  # Increased from 30 to 50

# Date Filtering Settings
# Filter articles to only include recent news (within X days)
MAX_ARTICLE_AGE_DAYS = int(os.getenv('MAX_ARTICLE_AGE_DAYS', '3'))  # Only articles from last 3 days

# File and Folder Settings
# Where we save the input data and generated newsletters
INPUT_FOLDER = os.getenv('INPUT_FOLDER', 'input')
OUTPUT_FOLDER = os.getenv('OUTPUT_FOLDER', 'output')

# Website URLs to scrape news from
# These are diverse news sources covering multiple topics and regions
WEBSITES = [
    # Sudbury & Greater Sudbury
  
    'https://globalnews.ca/tag/sudbury-news/',
    'https://www.thesudburystar.com/',
    'https://www.cbc.ca/news/canada/sudbury',
    
    # Northern Ontario Local News
    'https://www.northernnews.ca/',
    'https://www.baytoday.ca/',
    'https://www.sootoday.com/',
    'https://www.timminstoday.com/',
    'https://www.nugget.ca/',
    'https://www.tbnewswatch.com/',
    'https://www.nwonewswatch.com/',
    
    # Business & Regional
    'https://www.northernontariobusiness.com/',
    'https://news.ontario.ca/en',
    
    # National Coverage
    'https://www.ctvnews.ca/northern-ontario',
    'https://www.cbc.ca/news',
    'https://www.thestar.com/',
    'https://nationalpost.com/'
]

def validate_api_key(key):
    """
    Validate API key format without exposing the actual key.
    
    Args:
        key (str): The API key to validate
        
    Returns:
        bool: True if key appears valid, False otherwise
    """
    if not key:
        return False
    
    # Check if it looks like a real API key (basic format validation)
    # Mistral API keys are typically alphanumeric and 20+ characters
    if not re.match(r'^[A-Za-z0-9]{20,}$', key):
        return False
    
    # Additional check: make sure it's not a placeholder
    placeholder_patterns = [
        'your_api_key_here',
        'your_mistral_api_key_here',
        'placeholder',
        'example',
        'test'
    ]
    
    if key.lower() in placeholder_patterns:
        return False
    
    return True

def check_config():
    """
    Check if our configuration is set up correctly.
    
    This function makes sure we have everything we need to run the program.
    It will tell us if something is missing.
    
    Returns:
        bool: True if everything is OK, False if something is missing
    """
    # Check if we have an API key
    if not MISTRAL_API_KEY:
        print("ERROR: MISTRAL_API_KEY is missing from .env file")
        print("Please add your Mistral AI API key to the .env file")
        print("1. Copy .env.example to .env")
        print("2. Get your API key from https://console.mistral.ai/")
        print("3. Replace 'your_mistral_api_key_here' with your actual key")
        return False
    
    # Validate API key format
    if not validate_api_key(MISTRAL_API_KEY):
        print("ERROR: MISTRAL_API_KEY appears to be invalid")
        print("Please check that you've copied the correct API key from Mistral AI")
        print("The key should be alphanumeric and at least 20 characters long")
        return False
    
    # Check if output folder exists, create it if it doesn't
    try:
        os.makedirs(OUTPUT_FOLDER, exist_ok=True)
        print(f"Output folder ready: {OUTPUT_FOLDER}")
    except Exception as e:
        print(f"ERROR: Cannot create output folder: {e}")
        return False
    
    print("Configuration check passed - ready to generate newsletters!")
    return True