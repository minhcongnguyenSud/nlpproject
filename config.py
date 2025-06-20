"""
Simple configuration file for Newsletter Generator

This file loads settings from the .env file and provides them to other parts of the program.
Everything is kept simple and easy to understand for junior developers.
"""

import os
from dotenv import load_dotenv

# Load environment variables from .env file
# This keeps our API keys secure and separate from our code
load_dotenv()

# API Configuration
# This is your secret key from Mistral AI - never share this publicly
MISTRAL_API_KEY = os.getenv('MISTRAL_API_KEY', '')

# Newsletter Settings
# These control how our newsletter looks and what content it includes
NEWSLETTER_TITLE = os.getenv('NEWSLETTER_TITLE', 'Sudbury Daily News')
MAX_ARTICLES = int(os.getenv('MAX_ARTICLES', '5'))

# File and Folder Settings
# Where we save the generated newsletters
OUTPUT_FOLDER = os.getenv('OUTPUT_FOLDER', 'output')

# Website URLs to scrape news from
# These are the local Sudbury news sources we will check
WEBSITES = [
    'https://www.sudbury.com/',
    'https://www.greatersudbury.ca/',
    'https://www.ctvnews.ca/northern-ontario'
]

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