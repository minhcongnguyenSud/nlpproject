"""
Smart Web Scraper for Newsletter Generator

This scraper finds high-quality news articles from various news websites using
advanced NLP techniques for content analysis and automatic classification.
It's designed to be comprehensive, intelligent, and easy to understand.
"""

import requests
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
import re
from dateutil import parser as date_parser

from ..core import config
from ..utils.utils import clean_text
from .smart_analyzer import SmartContentAnalyzer

# Global analyzer instance to avoid reloading the model
_analyzer = None

def get_analyzer():
    """Get or create the global analyzer instance"""
    global _analyzer
    if _analyzer is None:
        _analyzer = SmartContentAnalyzer()
    return _analyzer


def is_article_recent(article_date_text, max_days_old=None):
    """
    Check if an article is recent enough (within the last N days).
    
    Args:
        article_date_text (str): Date text from the article
        max_days_old (int): Maximum age in days (defaults to config value)
        
    Returns:
        bool: True if article is recent enough
    """
    if max_days_old is None:
        max_days_old = config.MAX_ARTICLE_AGE_DAYS
    
    if not article_date_text:
        return True  # If no date found, include article
    
    try:
        # Parse the date using dateutil parser (handles many formats)
        article_date = date_parser.parse(article_date_text, fuzzy=True)
        
        # Get current date and calculate cutoff
        now = datetime.now(article_date.tzinfo or datetime.now().astimezone().tzinfo)
        cutoff_date = now - timedelta(days=max_days_old)
        
        return article_date >= cutoff_date
        
    except (ValueError, TypeError):
        # If date parsing fails, include article
        return True


def extract_date_from_article(soup, url):
    """
    Extract publication date from article HTML using various methods.
    
    Args:
        soup (BeautifulSoup): Parsed HTML of the article
        url (str): Article URL
        
    Returns:
        str: Date text if found, None otherwise
    """
    # Common date selectors and patterns
    date_selectors = [
        'time',
        '.article-date',
        '.published-date', 
        '.date',
        '.post-date',
        '.entry-date',
        '[datetime]',
        '[data-date]',
        '.byline time',
        '.article-meta time'
    ]
    
    # Try structured data (JSON-LD, microdata)
    for script in soup.find_all('script', {'type': 'application/ld+json'}):
        try:
            import json
            data = json.loads(script.string)
            if isinstance(data, dict):
                date_published = data.get('datePublished') or data.get('dateCreated')
                if date_published:
                    return date_published
        except (json.JSONDecodeError, AttributeError):
            continue
    
    # Try meta tags
    meta_selectors = [
        'meta[property="article:published_time"]',
        'meta[name="publishdate"]',
        'meta[name="date"]',
        'meta[property="og:updated_time"]'
    ]
    
    for selector in meta_selectors:
        meta_tag = soup.select_one(selector)
        if meta_tag:
            content = meta_tag.get('content')
            if content:
                return content
    
    # Try common date elements
    for selector in date_selectors:
        date_elem = soup.select_one(selector)
        if date_elem:
            # Check for datetime attribute first
            datetime_attr = date_elem.get('datetime')
            if datetime_attr:
                return datetime_attr
            
            # Then check text content
            date_text = date_elem.get_text(strip=True)
            if date_text and re.search(r'\d{4}|\d{1,2}/\d{1,2}', date_text):
                return date_text
    
    return None


def remove_duplicate_articles(articles):
    """
    Remove duplicate articles based on title similarity and URL.
    
    Args:
        articles (list): List of articles to deduplicate
        
    Returns:
        list: Articles with duplicates removed
    """
    seen_titles = set()
    seen_urls = set()
    unique_articles = []
    
    for article in articles:
        title = article.get('title', '').strip().lower()
        url = article.get('source_url', '').strip()
        
        # Create a normalized title for comparison (remove extra spaces, punctuation)
        normalized_title = ''.join(c for c in title if c.isalnum() or c.isspace()).strip()
        normalized_title = ' '.join(normalized_title.split())  # Normalize whitespace
        
        # Check for exact URL duplicates first
        if url and url in seen_urls:
            continue
            
        # Check for very similar titles (likely duplicates)
        is_duplicate = False
        for seen_title in seen_titles:
            # If titles are very similar (same after normalization), consider duplicate
            if normalized_title == seen_title or (
                len(normalized_title) > 20 and  # Only for longer titles
                (normalized_title in seen_title or seen_title in normalized_title)
            ):
                is_duplicate = True
                break
        
        if not is_duplicate:
            unique_articles.append(article)
            seen_titles.add(normalized_title)
            if url:
                seen_urls.add(url)
    
    return unique_articles


def get_all_articles():
    """
    Get high-quality articles from all news websites using NLP analysis.
    
    Returns:
        list: All quality articles found and analyzed
    """
    print("Getting articles from news websites...")
    
    all_articles = []
    
    for website in config.WEBSITES:
        print(f"\nChecking: {website}")
        
        try:
            articles = get_articles_from_website(website)
            
            if articles:
                print(f"Found {len(articles)} good articles!")
                all_articles.extend(articles)
            else:
                print("No articles found on this site")
                
        except requests.RequestException as error:
            print(f"Network error with {website}: {error}")
        except Exception as error:
            print(f"Unexpected error with {website}: {error}")
    
    print(f"\nTotal articles found: {len(all_articles)}")
    
    # Remove duplicate articles
    deduplicated_articles = remove_duplicate_articles(all_articles)
    removed_count = len(all_articles) - len(deduplicated_articles)
    
    if removed_count > 0:
        print(f"Removed {removed_count} duplicate articles")
        print(f"Final article count: {len(deduplicated_articles)}")
    
    return deduplicated_articles


def get_articles_from_website(website_url):
    """
    Get quality articles from one website using NLP-based filtering.
    
    Args:
        website_url (str): The website to scrape
        
    Returns:
        list: Quality articles from this website
    """
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    
    print("  → Downloading page...")
    response = requests.get(website_url, headers=headers, timeout=15)
    response.raise_for_status()  # Raises exception for bad status codes
    
    soup = BeautifulSoup(response.text, 'html.parser')
    
    # Remove unwanted elements that might confuse us
    for unwanted in soup.find_all(['script', 'style', 'nav', 'footer', 'header']):
        unwanted.decompose()
    
    articles = find_articles_on_page(soup, website_url)
    
    # Filter for good articles only
    good_articles = [article for article in articles if is_good_article(article)]
    
    return good_articles


def find_articles_on_page(soup, website_url):
    """
    Find articles on any webpage using a simple, unified approach.
    
    Args:
        soup: The parsed HTML
        website_url (str): The website we're scraping
        
    Returns:
        list: Articles found on the page
    """
    articles = []
    
    # Strategy 1: Look for actual article tags
    for article_tag in soup.find_all('article'):
        article = extract_article_from_element(article_tag, website_url)
        if article:
            articles.append(article)
    
    # Strategy 2: Look for links that might lead to full articles
    for link in soup.find_all('a', href=True):
        title = clean_text(link.get_text())
        href = link.get('href')
        
        # Skip if title too short or looks like navigation
        if len(title) < 15 or is_navigation_link(title):
            continue
            
        # Make full URL
        if href.startswith('/'):
            if 'globalnews.ca' in website_url:
                article_url = 'https://globalnews.ca' + href
            elif 'thesudburystar.com' in website_url:
                article_url = 'https://www.thesudburystar.com' + href
            else:
                article_url = website_url.rstrip('/') + href
        elif href.startswith('http'):
            article_url = href
        else:
            continue
        
        # Only process if it looks like a news article URL
        if is_news_article_url(article_url, website_url):
            print(f"    → Getting article: {title[:50]}...")
            content = get_full_article_content(article_url)
            
            if content and len(content) > 100:
                # Get the article's HTML to extract date
                try:
                    response = requests.get(article_url, timeout=10, headers={
                        'User-Agent': 'Mozilla/5.0 (compatible; NewsBot/1.0)'
                    })
                    article_soup = BeautifulSoup(response.content, 'html.parser')
                    article_date = extract_date_from_article(article_soup, article_url)
                    
                    # Check if article is recent enough
                    if not is_article_recent(article_date):
                        print(f"    Article too old ({article_date}), skipping...")
                        continue
                        
                except (requests.RequestException, Exception):
                    # If date extraction fails, continue with article (don't filter out)
                    article_date = None
                
                # Clean up the title from link text
                clean_title = title
                
                # Remove view counts, read indicators, etc.
                clean_title = re.sub(r'\d+[\,\d]*\s+(views?|reads?|shares?)\s*$', '', clean_title, flags=re.IGNORECASE).strip()
                # Remove "Read more", "Continue reading", etc.
                clean_title = re.sub(r'\s*(read\s+more|continue\s+reading|full\s+story).*$', '', clean_title, flags=re.IGNORECASE).strip()
                # Remove multimedia indicators
                clean_title = re.sub(r':\s*(watch\s+video|view\s+gallery|see\s+photos|listen|audio).*$', '', clean_title, flags=re.IGNORECASE).strip()
                
                # Limit title length absolutely - if too long, truncate at sentence boundary
                if len(clean_title) > 200:
                    # Try to find a sentence boundary
                    sentences = clean_title.split('. ')
                    if len(sentences) > 1 and len(sentences[0]) > 10:
                        clean_title = sentences[0] + "."
                    else:
                        # Fallback to word boundary
                        clean_title = clean_title[:200].rsplit(' ', 1)[0] + "..."
                
                article = {
                    'title': clean_title,
                    'content': content,
                    'source': website_url,
                    'source_url': article_url,
                    'publication_date': article_date,
                    'scraped_time': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                }
                
                if is_good_article(article):
                    articles.append(article)
                    print(f"    Added article: {title[:30]}...")
    
    # Strategy 3: Look for content already on the page (for sites that show full articles)
    for element in soup.find_all(['div', 'section'], class_=lambda x: x and 
                                 any(word in str(x).lower() for word in ['article', 'post', 'news', 'story'])):
        article = extract_article_from_element(element, website_url)
        if article:
            articles.append(article)
    
    print(f"  → Found {len(articles)} good articles from {website_url}")
    return articles


def is_navigation_link(text):
    """Check if a link text looks like navigation rather than an article title."""
    nav_words = ['home', 'menu', 'search', 'subscribe', 'login', 'sign up', 'more stories', 
                 'contact', 'about', 'privacy', 'terms', 'epaper', 'newsletter signup']
    text_lower = text.lower()
    return any(word in text_lower for word in nav_words)


def is_news_article_url(url, _):
    """Check if a URL looks like it leads to a news article."""
    url_lower = url.lower()
    
    # Must be from the same domain or a known news domain
    if not any(domain in url_lower for domain in ['globalnews.ca', 'thesudburystar.com', 'greatersudbury.ca', 'ctvnews.ca']):
        return False
    
    # Should have article-like path patterns
    article_patterns = ['/news/', '/article/', '/story/', '/local/', '/politics/', '/sports/', 
                       '/business/', '/entertainment/', '/health/', '/opinion/', '/city-hall/']
    
    # For globalnews.ca and thesudburystar.com, be more specific
    if 'globalnews.ca' in url_lower:
        return '/news/' in url_lower or '/local/' in url_lower
    elif 'thesudburystar.com' in url_lower:
        return any(pattern in url_lower for pattern in article_patterns) and not url_lower.endswith('.com/')
    
    return any(pattern in url_lower for pattern in article_patterns)


def extract_article_from_element(element, website_url):
    """
    Extract article information from an HTML element.
    
    Args:
        element: HTML element that might contain article content
        website_url (str): The source website
        
    Returns:
        dict or None: Article info if found
    """
    try:
        # Find title - prioritize proper heading tags first
        title = ""
        
        # First try proper heading tags
        for tag in element.find_all(['h1', 'h2', 'h3', 'h4', 'h5']):
            text = clean_text(tag.get_text())
            if 10 < len(text) < 200:  # Reasonable title length
                title = text
                break
        
        # If no heading found, try other elements but with stricter limits
        if not title:
            for tag in element.find_all(['strong', 'a']):
                text = clean_text(tag.get_text())
                if 10 < len(text) < 150:  # Even stricter for non-heading elements
                    title = text
                    break
        
        # Clean up common title issues
        if title:
            # Remove view counts, read indicators, etc.
            title = re.sub(r'\d+[\,\d]*\s+(views?|reads?|shares?)\s*$', '', title, flags=re.IGNORECASE).strip()
            # Remove "Read more", "Continue reading", etc.
            title = re.sub(r'\s*(read\s+more|continue\s+reading|full\s+story).*$', '', title, flags=re.IGNORECASE).strip()
            # Limit title length absolutely
            if len(title) > 200:
                title = title[:200].rsplit(' ', 1)[0] + "..."
        
        if not title or len(title) < 10:
            return None
        
        # Find content
        content = ""
        paragraphs = element.find_all('p')
        if paragraphs:
            content = '\n\n'.join([clean_text(p.get_text()) for p in paragraphs if len(clean_text(p.get_text())) > 20])
        
        if not content:
            content = clean_text(element.get_text())
        
        # Find URL
        article_url = website_url
        link = element.find('a', href=True)
        if link:
            href = link['href']
            if href.startswith('http'):
                article_url = href
            elif href.startswith('/'):
                article_url = website_url.rstrip('/') + href
        
        if len(title) < 10 or len(content) < 50:
            return None

        # Try to extract publication date from the element's parent page
        publication_date = None
        try:
            # Look for date in the element itself or nearby elements
            date_element = element.find('time') or element.find(class_=lambda x: x and 'date' in str(x).lower())
            if date_element:
                date_text = date_element.get('datetime') or date_element.get_text()
                if date_text:
                    publication_date = date_text.strip()
        except:
            pass

        return {
            'title': title,
            'content': content,
            'source': website_url,
            'source_url': article_url,
            'publication_date': publication_date,
            'scraped_time': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
        
    except Exception:
        return None


def get_full_article_content(article_url):
    """
    Get the full content from an individual article page.
    
    Args:
        article_url (str): URL of the article
        
    Returns:
        str: Full article content or empty string
    """
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        
        response = requests.get(article_url, headers=headers, timeout=15)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Remove unwanted elements
        for unwanted in soup.find_all(['script', 'style', 'nav', 'footer', 'header', 'aside']):
            unwanted.decompose()
        
        # Try different strategies to find the main content
        content_areas = [
            # Common article content classes
            soup.find('div', class_=lambda x: x and 'article-content' in str(x).lower()),
            soup.find('div', class_=lambda x: x and 'story-content' in str(x).lower()),
            soup.find('div', class_=lambda x: x and 'entry-content' in str(x).lower()),
            soup.find('div', class_=lambda x: x and 'post-content' in str(x).lower()),
            # Try article tag
            soup.find('article'),
            # Try main tag
            soup.find('main'),
            # Last resort - any div with 'content' in the class
            soup.find('div', class_=lambda x: x and 'content' in str(x).lower()),
        ]
        
        for area in content_areas:
            if area:
                paragraphs = area.find_all('p')
                if paragraphs:
                    content = '\n\n'.join([clean_text(p.get_text()) for p in paragraphs if len(clean_text(p.get_text())) > 20])
                    if len(content) > 100:  # Must have substantial content
                        return content
        
        return ""
        
    except requests.RequestException:
        return ""
    except Exception:
        return ""


def is_good_article(article):
    """
    Advanced article quality assessment using NLP techniques.
    
    This function now uses smart content analysis instead of simple keyword filtering.
    It evaluates:
    - Content quality and structure
    - Language quality and readability  
    - News-worthiness indicators
    - Automatic content classification
    
    Args:
        article (dict): Article to evaluate
        
    Returns:
        bool: True if it's a quality news article
    """
    if not article or not isinstance(article, dict):
        return False
    
    title = article.get('title', '').strip()
    content = article.get('content', '').strip()
    
    # Must have both title and content
    if not title or not content:
        return False
    
    # Basic length requirements (still important)
    if len(title) < 10 or len(content) < 100:
        return False
    
    # Use the global analyzer instance (loads model only once)
    analyzer = get_analyzer()
    
    try:
        # Perform comprehensive NLP-based quality analysis
        quality_analysis = analyzer.analyze_content_quality(article)
        
        # Get article classification
        classification = analyzer.classify_article(article)
        
        # Extract key entities and information
        entities = analyzer.extract_key_entities(article)
        
        # Add analysis results to article for later use
        article['nlp_analysis'] = {
            'quality_analysis': quality_analysis,
            'classification': classification,
            'entities': entities,
            'analysis_timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
        
        # Decision: Accept article if it meets quality threshold
        is_quality = quality_analysis.get('is_quality', False)
        quality_score = quality_analysis.get('quality_score', 0)
        
        if is_quality:
            category = classification.get('primary_category', 'general')
            confidence = classification.get('confidence', 0)
            print(f"    Quality article (score: {quality_score}/100, category: {category}, confidence: {confidence}%)")
            print(f"       Reasons: {', '.join(quality_analysis.get('reasons', []))}")
        else:
            print(f"    Low quality article (score: {quality_score}/100)")
            print(f"       Reasons: {', '.join(quality_analysis.get('reasons', []))}")
        
        return is_quality
        
    except Exception as e:
        print(f"    NLP analysis failed: {e}")
        # Fallback to basic quality checks if NLP analysis fails
        return _basic_quality_check(article)


def _basic_quality_check(article):
    """
    Fallback quality check when NLP analysis fails
    
    Args:
        article (dict): Article to evaluate
        
    Returns:
        bool: True if article passes basic quality checks
    """
    title = article.get('title', '').strip()
    content = article.get('content', '').strip()
    
    # Convert to lowercase for checking
    title_lower = title.lower()
    content_lower = content.lower()
    
    # Skip obvious non-articles
    bad_indicators = [
        'advertisement', 'sponsored', 'subscribe', 'newsletter signup', 
        'follow us', 'social media', 'terms of service', 'privacy policy',
        'cookie policy', 'site map', 'contact us', 'about us',
        'lorem ipsum', 'placeholder', 'test content',
        'click here', 'read more', 'view all', 'show more'
    ]
    
    # Check if title contains bad indicators
    for bad_word in bad_indicators:
        if bad_word in title_lower:
            return False
    
    # Basic quality checks
    words = content_lower.split()
    if len(set(words)) < len(words) * 0.5 and len(words) > 20:  # Less than 50% unique words
        return False
    
    # Check for reasonable alphanumeric content
    alphanumeric_chars = sum(1 for c in title if c.isalnum())
    if alphanumeric_chars < len(title) * 0.6:  # Less than 60% alphanumeric
        return False
    
    return True


# Legacy function for compatibility
async def scrape_all_websites():
    """
    Async wrapper for get_all_articles() for compatibility.
    
    Returns:
        list: All articles found
    """
    return get_all_articles()
