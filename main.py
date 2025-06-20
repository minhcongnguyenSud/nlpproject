"""
Simple AI Newsletter Generator - Main Script

This is the main program that creates newsletters automatically.
It scrapes news websites, summarizes articles with AI, and creates an HTML newsletter.

"""

import asyncio
import os
import time
from datetime import datetime
from playwright.async_api import async_playwright
from mistralai.client import MistralClient
from mistralai.models.chat_completion import ChatMessage
from bs4 import BeautifulSoup

# Import our configuration settings
import config

def print_step(step_number, description):
    """
    Print a numbered step to show progress to the user.
    
    This helps users understand what the program is doing at each stage.
    
    Args:
        step_number (int): The step number (1, 2, 3, etc.)
        description (str): What this step does
    """
    print(f"\n=== STEP {step_number}: {description} ===")

async def scrape_website(page, url):
    """
    Scrape articles from a single website.
    
    This function opens a website and finds news articles on it.
    It looks for headlines and article text that we can summarize.
    
    Args:
        page: The browser page object from Playwright
        url (str): The website URL to scrape
        
    Returns:
        list: A list of articles found on the website
    """
    articles = []
    
    try:
        print(f"Visiting website: {url}")
        
        # Navigate to the website and wait for it to load
        await page.goto(url, wait_until='networkidle')
        
        # Wait a bit more for any dynamic content to load
        await page.wait_for_timeout(3000)  # Wait 3 seconds
        
        # Get the HTML content of the page
        html_content = await page.content()
        
        # Use BeautifulSoup to parse the HTML and find articles
        soup = BeautifulSoup(html_content, 'html.parser')
        
        # Look for common article elements on news websites
        # These are typical HTML tags that contain news articles
        article_elements = soup.find_all(['article', 'div'], class_=['post', 'article', 'news', 'story'])
        
        # If we didn't find articles with those tags, try a broader search
        if not article_elements:
            # Look for any links that might be article headlines
            article_elements = soup.find_all('a', href=True)
        
        print(f"Found {len(article_elements)} potential articles")
        
        # Process each article element we found
        for element in article_elements[:config.MAX_ARTICLES]:  # Only take the first few
            try:
                # Try to extract the article title
                title = ""
                if element.name == 'a':
                    # If it's a link, the text is probably the title
                    title = element.get_text(strip=True)
                else:
                    # Look for heading tags inside the article
                    heading = element.find(['h1', 'h2', 'h3', 'h4'])
                    if heading:
                        title = heading.get_text(strip=True)
                
                # Try to extract article content or summary
                content = ""
                # Look for paragraph tags or content divs
                content_elements = element.find_all(['p', 'div'], class_=['content', 'summary', 'excerpt'])
                if content_elements:
                    content = ' '.join([p.get_text(strip=True) for p in content_elements])
                else:
                    # If no specific content found, just get all text
                    content = element.get_text(strip=True)
                
                # Only keep articles that have both a title and some content
                if title and content and len(title) > 10 and len(content) > 50:
                    article = {
                        'title': title,
                        'content': content,
                        'source': url,
                        'scraped_time': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                    }
                    articles.append(article)
                    print(f"Found article: {title[:50]}...")
                
            except Exception as e:
                # If we can't process this article, skip it and continue
                print(f"Skipping article due to error: {e}")
                continue
        
        print(f"Successfully scraped {len(articles)} articles from {url}")
        
    except Exception as e:
        print(f"Error scraping {url}: {e}")
    
    return articles

async def scrape_all_websites():
    """
    Scrape articles from all configured websites.
    
    This function opens a web browser and visits each news website
    to collect articles for our newsletter.
    
    Returns:
        list: All articles found across all websites
    """
    all_articles = []
    
    # Start Playwright browser
    async with async_playwright() as p:
        print("Starting web browser...")
        
        # Launch browser (headless=False means you can see the browser window)
        # Change to headless=True if you don't want to see the browser
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        
        # Visit each website and scrape articles
        for website_url in config.WEBSITES:
            website_articles = await scrape_website(page, website_url)
            all_articles.extend(website_articles)
            
            # Wait between websites to be polite
            await page.wait_for_timeout(2000)  # Wait 2 seconds
        
        # Close the browser
        await browser.close()
        print("Browser closed")
    
    return all_articles

def summarize_article(client, article):
    """
    Use Mistral AI to create a summary of an article.
    
    This function sends the article to Mistral AI and asks it to create
    a short, easy-to-read summary.
    
    Args:
        client: The Mistral AI client object
        article (dict): The article data to summarize
        
    Returns:
        str: A short summary of the article
    """
    try:
        print(f"Summarizing: {article['title'][:50]}...")
        
        # Create a prompt that tells the AI what we want
        prompt = f"""
Please write a short summary of this news article in 2-3 sentences.
Keep it simple and easy to understand.

Article Title: {article['title']}

Article Content: {article['content']}

Summary:"""
        
        # Send the request to Mistral AI
        messages = [ChatMessage(role="user", content=prompt)]
        
        response = client.chat(
            model="mistral-small-latest",  # Use the basic model for cost efficiency
            messages=messages,
            max_tokens=150,  # Limit the response length
            temperature=0.3,  # Low temperature for consistent, factual summaries
        )
        
        # Extract the summary from the AI response
        summary = response.choices[0].message.content.strip()
        
        # Make sure we got a valid summary
        if summary and len(summary) > 10:
            print(f"Summary created: {summary[:50]}...")
            return summary
        else:
            print("AI returned empty summary, using original content")
            return article['content'][:200] + "..."
            
    except Exception as e:
        print(f"Error summarizing article: {e}")
        # If AI fails, use first part of original content
        return article['content'][:200] + "..."

def summarize_all_articles(articles):
    """
    Create summaries for all articles using Mistral AI.
    
    This function goes through each article and creates a short summary
    that will be easier to read in the newsletter.
    
    Args:
        articles (list): List of articles to summarize
        
    Returns:
        list: Articles with summaries added
    """
    if not articles:
        print("No articles to summarize")
        return []
    
    # Initialize Mistral AI client
    try:
        client = MistralClient(api_key=config.MISTRAL_API_KEY)
        print("Connected to Mistral AI")
    except Exception as e:
        print(f"Error connecting to Mistral AI: {e}")
        return articles
    
    # Summarize each article
    for i, article in enumerate(articles, 1):
        print(f"Processing article {i}/{len(articles)}")
        
        summary = summarize_article(client, article)
        article['summary'] = summary
        
        # Wait a bit between API calls to avoid rate limits
        time.sleep(1)
    
    print(f"Finished summarizing {len(articles)} articles")
    return articles

def create_html_newsletter(articles):
    """
    Create an HTML newsletter from the summarized articles.
    
    This function takes all our articles and puts them into a nice-looking
    HTML page that can be opened in a web browser.
    
    Args:
        articles (list): List of articles with summaries
        
    Returns:
        str: Complete HTML content for the newsletter
    """
    # Start building the HTML
    # This is the basic structure every HTML page needs
    html_content = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{config.NEWSLETTER_TITLE}</title>
    <style>
        /* CSS styles to make our newsletter look good */
        body {{
            font-family: Arial, sans-serif;
            max-width: 800px;
            margin: 0 auto;
            padding: 20px;
            background-color: #f5f5f5;
        }}
        
        .newsletter {{
            background-color: white;
            padding: 30px;
            border-radius: 10px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }}
        
        .header {{
            text-align: center;
            border-bottom: 3px solid #007acc;
            padding-bottom: 20px;
            margin-bottom: 30px;
        }}
        
        .title {{
            color: #007acc;
            font-size: 2.5em;
            margin: 0;
        }}
        
        .subtitle {{
            color: #666;
            font-size: 1.2em;
            margin: 10px 0;
        }}
        
        .date {{
            color: #999;
            font-size: 1em;
        }}
        
        .article {{
            margin-bottom: 30px;
            padding-bottom: 20px;
            border-bottom: 1px solid #eee;
        }}
        
        .article-title {{
            color: #333;
            font-size: 1.4em;
            margin-bottom: 10px;
            font-weight: bold;
        }}
        
        .article-summary {{
            color: #555;
            line-height: 1.6;
            margin-bottom: 10px;
        }}
        
        .article-source {{
            color: #007acc;
            font-size: 0.9em;
            font-weight: bold;
        }}
        
        .footer {{
            text-align: center;
            margin-top: 40px;
            padding-top: 20px;
            border-top: 1px solid #eee;
            color: #999;
            font-size: 0.9em;
        }}
    </style>
</head>
<body>
    <div class="newsletter">
        <div class="header">
            <h1 class="title">{config.NEWSLETTER_TITLE}</h1>
            <p class="subtitle">AI-Generated Local News Summary</p>
            <p class="date">Generated on {datetime.now().strftime('%B %d, %Y at %I:%M %p')}</p>
        </div>
        
        <div class="content">
"""
    
    # Add each article to the HTML
    if articles:
        for i, article in enumerate(articles, 1):
            html_content += f"""
            <div class="article">
                <h2 class="article-title">{i}. {article['title']}</h2>
                <p class="article-summary">{article['summary']}</p>
                <p class="article-source">Source: {article['source']}</p>
            </div>
"""
    else:
        # If no articles, show a message
        html_content += """
            <div class="article">
                <h2 class="article-title">No Articles Found</h2>
                <p class="article-summary">Sorry, we couldn't find any news articles today. Please try again later.</p>
            </div>
"""
    
    # Close the HTML structure
    html_content += f"""
        </div>
        
        <div class="footer">
            <p>This newsletter was automatically generated using AI technology.</p>
            <p>Total articles: {len(articles)}</p>
        </div>
    </div>
</body>
</html>
"""
    
    return html_content

def save_newsletter(html_content):
    """
    Save the HTML newsletter to a file.
    
    This function writes our newsletter to an HTML file that can be
    opened in any web browser.
    
    Args:
        html_content (str): The complete HTML content
        
    Returns:
        str: The filename where the newsletter was saved
    """
    # Create a filename with the current date and time
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    filename = f"newsletter_{timestamp}.html"
    filepath = os.path.join(config.OUTPUT_FOLDER, filename)
    
    try:
        # Write the HTML content to the file
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        print(f"Newsletter saved to: {filepath}")
        return filepath
        
    except Exception as e:
        print(f"Error saving newsletter: {e}")
        return None

async def main():
    """
    Main function that runs the complete newsletter generation process.
    
    This is the main program that coordinates all the steps:
    1. Check configuration
    2. Scrape articles from websites
    3. Summarize articles with AI
    4. Create HTML newsletter
    5. Save the newsletter file
    """
    print("=== AI NEWSLETTER GENERATOR ===")
    print("Welcome! This program will create a newsletter automatically.")
    print("Let's get started...")
    
    # Step 1: Check if everything is set up correctly
    print_step(1, "Checking Configuration")
    if not config.check_config():
        print("Please fix the configuration issues and try again.")
        return
    
    # Step 2: Scrape articles from news websites
    print_step(2, "Scraping Articles from Websites")
    articles = await scrape_all_websites()
    
    if not articles:
        print("No articles were found. Please check your internet connection and try again.")
        return
    
    print(f"Successfully collected {len(articles)} articles!")
    
    # Step 3: Summarize articles using AI
    print_step(3, "Creating AI Summaries")
    articles_with_summaries = summarize_all_articles(articles)
    
    # Step 4: Create HTML newsletter
    print_step(4, "Building Newsletter")
    html_newsletter = create_html_newsletter(articles_with_summaries)
    
    # Step 5: Save the newsletter
    print_step(5, "Saving Newsletter")
    saved_file = save_newsletter(html_newsletter)
    
    if saved_file:
        print("\n=== SUCCESS! ===")
        print(f"Your newsletter has been created: {saved_file}")
        print("You can open this file in your web browser to read it.")
        print("Thank you for using the AI Newsletter Generator!")
    else:
        print("There was an error saving the newsletter.")

# This is how Python knows to run the main function when the script starts
if __name__ == "__main__":
    # Run the main function
    # asyncio.run is needed because we use async/await for web scraping
    asyncio.run(main())