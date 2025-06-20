"""
Test script for Simple AI Newsletter Generator

This script helps junior developers test if everything is working
before running the main newsletter generator.
"""

import asyncio
import os
from datetime import datetime

# Test imports
try:
    from playwright.async_api import async_playwright
    from mistralai.client import MistralClient
    from mistralai.models.chat_completion import ChatMessage
    from bs4 import BeautifulSoup
    import config
    print("✓ All imports successful")
except ImportError as e:
    print(f"✗ Import error: {e}")
    print("Please run: pip install -r requirements.txt")
    exit(1)

def test_config():
    """Test if configuration is set up correctly."""
    print("\n=== Testing Configuration ===")
    
    # Test API key
    if config.MISTRAL_API_KEY and config.MISTRAL_API_KEY != 'your_api_key_here':
        print("✓ API key is configured")
    else:
        print("✗ API key not configured in .env file")
        return False
    
    # Test output folder
    if os.path.exists(config.OUTPUT_FOLDER):
        print(f"✓ Output folder exists: {config.OUTPUT_FOLDER}")
    else:
        print(f"✗ Output folder missing: {config.OUTPUT_FOLDER}")
        return False
    
    # Test websites list
    if config.WEBSITES:
        print(f"✓ {len(config.WEBSITES)} websites configured")
    else:
        print("✗ No websites configured")
        return False
    
    return True

async def test_browser():
    """Test if Playwright browser works."""
    print("\n=== Testing Web Browser ===")
    
    try:
        async with async_playwright() as p:
            print("Starting browser...")
            browser = await p.chromium.launch(headless=True)
            page = await browser.new_page()
            
            # Test basic navigation
            await page.goto('https://www.google.com')
            title = await page.title()
            print(f"✓ Browser working - visited Google, title: {title}")
            
            await browser.close()
            return True
            
    except Exception as e:
        print(f"✗ Browser test failed: {e}")
        print("Try running: playwright install chromium")
        return False

def test_ai_connection():
    """Test if Mistral AI connection works."""
    print("\n=== Testing AI Connection ===")
    
    try:
        # Create client
        client = MistralClient(api_key=config.MISTRAL_API_KEY)
        
        # Test with a simple request
        messages = [ChatMessage(role="user", content="Say hello in one word.")]
        
        response = client.chat(
            model="mistral-small-latest",
            messages=messages,
            max_tokens=10,
        )
        
        result = response.choices[0].message.content.strip()
        print(f"✓ AI connection working - Response: {result}")
        return True
        
    except Exception as e:
        print(f"✗ AI connection failed: {e}")
        print("Check your API key and internet connection")
        return False

async def test_simple_scrape():
    """Test scraping a simple website."""
    print("\n=== Testing Web Scraping ===")
    
    try:
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            page = await browser.new_page()
            
            # Test scraping a simple, reliable website
            await page.goto('https://example.com')
            content = await page.content()
            
            # Parse with BeautifulSoup
            soup = BeautifulSoup(content, 'html.parser')
            title = soup.find('title')
            
            if title:
                print(f"✓ Web scraping working - Found title: {title.get_text()}")
                await browser.close()
                return True
            else:
                print("✗ Could not extract title from webpage")
                await browser.close()
                return False
                
    except Exception as e:
        print(f"✗ Web scraping test failed: {e}")
        return False

def test_html_creation():
    """Test HTML newsletter creation."""
    print("\n=== Testing HTML Creation ===")
    
    try:
        # Create a simple test newsletter
        test_html = f"""
<!DOCTYPE html>
<html>
<head>
    <title>Test Newsletter</title>
</head>
<body>
    <h1>Test Newsletter</h1>
    <p>This is a test created on {datetime.now()}</p>
</body>
</html>
"""
        
        # Try to save it
        test_file = os.path.join(config.OUTPUT_FOLDER, 'test_newsletter.html')
        with open(test_file, 'w', encoding='utf-8') as f:
            f.write(test_html)
        
        if os.path.exists(test_file):
            print(f"✓ HTML creation working - Test file saved: {test_file}")
            # Clean up test file
            os.remove(test_file)
            return True
        else:
            print("✗ Could not save HTML file")
            return False
            
    except Exception as e:
        print(f"✗ HTML creation test failed: {e}")
        return False

async def run_all_tests():
    """Run all tests and report results."""
    print("=== SIMPLE NEWSLETTER GENERATOR - SYSTEM TEST ===")
    print("This will test if everything is set up correctly.\n")
    
    tests = [
        ("Configuration", test_config()),
        ("Browser", await test_browser()),
        ("AI Connection", test_ai_connection()),
        ("Web Scraping", await test_simple_scrape()),
        ("HTML Creation", test_html_creation()),
    ]
    
    passed_tests = sum(1 for name, result in tests if result)
    total_tests = len(tests)
    
    print(f"\n=== TEST RESULTS ===")
    print(f"Passed: {passed_tests}/{total_tests} tests")
    
    if passed_tests == total_tests:
        print("\n🎉 All tests passed! Your system is ready!")
        print("You can now run: python main.py")
    else:
        print("\n⚠ Some tests failed. Please fix the issues above.")
        print("\nCommon solutions:")
        print("- Check your .env file has the correct API key")
        print("- Run: playwright install chromium")
        print("- Check your internet connection")
        print("- Make sure all packages are installed")

def main():
    """Main function to run tests."""
    asyncio.run(run_all_tests())

if __name__ == "__main__":
    main()