"""
Simple Categorized Summarizer for Newsletter Generator

This creates summaries organized by news categories using Mistral AI.
"""

import json
import time
from collections import defaultdict
from datetime import datetime
from pathlib import Path

from mistralai.models.chat_completion import ChatMessage

from ..core import config
from ..utils.mistral_utils import create_mistral_client


def remove_cross_category_duplicates(article_assignments):
    """
    Remove articles that appear in multiple categories, keeping only the one
    with highest confidence score.
    
    Args:
        article_assignments (list): List of article data with categories
        
    Returns:
        list: Articles with cross-category duplicates removed
    """
    # Group articles by normalized title and URL for duplicate detection
    article_groups = defaultdict(list)
    
    for article in article_assignments:
        title = article.get('title', '').strip().lower()
        url = article.get('source_url', '').strip()
        
        # Create a key for grouping (normalized title + URL)
        normalized_title = ''.join(c for c in title if c.isalnum() or c.isspace()).strip()
        normalized_title = ' '.join(normalized_title.split())  # Normalize whitespace
        
        # Use URL as primary key, title as secondary
        key = url if url else normalized_title
        if not key:  # Skip if no title or URL
            continue
            
        article_groups[key].append(article)
    
    # For each group, keep only the article with highest confidence
    unique_articles = []
    duplicate_count = 0
    
    for key, articles in article_groups.items():
        if len(articles) == 1:
            # No duplicates, keep the article
            unique_articles.append(articles[0])
        else:
            # Multiple articles with same key, keep the one with highest confidence
            duplicate_count += len(articles) - 1
            best_article = max(articles, key=lambda x: x.get('confidence', 0))
            unique_articles.append(best_article)
    
    if duplicate_count > 0:
        print(f"Removed {duplicate_count} cross-category duplicate articles")
    
    return unique_articles


def remove_intra_category_duplicates(articles):
    """
    Remove duplicate articles within the same category based on URL and title similarity.
    Also removes articles covering the same story/event.
    
    Args:
        articles (list): List of articles within a single category
        
    Returns:
        list: Articles with intra-category duplicates removed
    """
    if len(articles) <= 1:
        return articles
    
    seen_urls = set()
    seen_stories = []  # Track story keywords to detect same events
    unique_articles = []
    
    for article in articles:
        title = article.get('title', '').strip().lower()
        url = article.get('source_url', '').strip()
        content = article.get('content', '').strip().lower()
        
        # Skip if we've seen this URL
        if url and url in seen_urls:
            continue
        
        # Create normalized title and content for comparison
        normalized_title = ''.join(c for c in title if c.isalnum() or c.isspace()).strip()
        normalized_title = ' '.join(normalized_title.split())  # Normalize whitespace
        
        # Extract key story elements for same-event detection
        story_keywords = extract_story_keywords(title, content)
        
        # Check for exact duplicate titles
        is_duplicate_title = False
        for seen_title in [story['normalized_title'] for story in seen_stories]:
            if normalized_title == seen_title or (
                len(normalized_title) > 20 and  # Only for longer titles
                (normalized_title in seen_title or seen_title in normalized_title)
            ):
                is_duplicate_title = True
                break
        
        # Check for same story/event (e.g., same rescue, same incident)
        is_same_story = False
        for story in seen_stories:
            if is_same_news_event(story_keywords, story['keywords']):
                is_same_story = True
                break
        
        if not is_duplicate_title and not is_same_story:
            unique_articles.append(article)
            if url:
                seen_urls.add(url)
            seen_stories.append({
                'normalized_title': normalized_title,
                'keywords': story_keywords
            })
    
    return unique_articles


def extract_story_keywords(title, content):
    """
    Extract key elements that identify a news story/event.
    
    Args:
        title (str): Article title
        content (str): Article content
        
    Returns:
        set: Set of keywords that identify the story
    """
    text = (title + ' ' + content).lower()
    
    # Common story identifiers
    story_elements = []
    
    # Names and places
    import re
    
    # Look for specific incident types with locations/numbers
    patterns = [
        r'(\d+)\s+miners?\s+(trapped|rescued|safe)',  # Miner rescue stories
        r'fire\s+(kills?|deaths?)\s+(\w+)',  # Fire incidents
        r'(\w+)\s+(charged|arrested|sentenced)',  # Criminal cases
        r'(\w+)\s+(academy|facility|school)',  # Institution stories  
        r'(\d+)\s+(dead|injured|killed)',  # Casualty numbers
        r'(totten|vale|sudbury)\s+mine',  # Specific mine incidents
        r'(opening|ceremonies|games)\s+(\w+)',  # Event stories
    ]
    
    for pattern in patterns:
        matches = re.findall(pattern, text)
        story_elements.extend([' '.join(match) if isinstance(match, tuple) else match for match in matches])
    
    # Add location keywords
    locations = re.findall(r'\b(sudbury|sault|north bay|kirkland|timmins|ontario)\b', text)
    story_elements.extend(locations)
    
    # Add key nouns (simplified)
    key_words = re.findall(r'\b(miners?|rescue|fire|arrest|death|accident|court|trial|ceremony|games|budget|strike)\b', text)
    story_elements.extend(key_words)
    
    return set(story_elements)


def is_same_news_event(keywords1, keywords2):
    """
    Determine if two sets of keywords represent the same news event.
    
    Args:
        keywords1 (set): Keywords from first article
        keywords2 (set): Keywords from second article
        
    Returns:
        bool: True if they appear to be the same story
    """
    if not keywords1 or not keywords2:
        return False
    
    # Calculate overlap
    overlap = keywords1.intersection(keywords2)
    
    # High-confidence same story indicators
    high_confidence_indicators = [
        'miners trapped', 'miners rescued', 'totten mine', 'vale mine',
        'sudbury fire', 'north bay fire', 'venture academy',
        'opening ceremonies', 'summer games'
    ]
    
    # Check if both articles contain specific high-confidence indicators
    for indicator in high_confidence_indicators:
        words = indicator.split()
        if all(word in keywords1 for word in words) and all(word in keywords2 for word in words):
            return True
    
    # General overlap threshold - if they share many keywords, likely same story
    if len(overlap) >= 3 and len(overlap) >= min(len(keywords1), len(keywords2)) * 0.6:
        return True
    
    return False


def organize_by_categories(articles):
    """Organize articles by their NLP-determined categories."""
    categorized = defaultdict(list)
    
    # First, collect all articles with their primary categories
    article_assignments = []
    
    for article in articles:
        nlp_analysis = article.get('nlp_analysis', {})
        classification = nlp_analysis.get('classification', {})
        quality_analysis = nlp_analysis.get('quality_analysis', {})
        
        category = classification.get('primary_category', 'general')
        confidence = classification.get('confidence', 0)
        quality_score = quality_analysis.get('quality_score', 0)
        
        article_data = {
            'title': article.get('title', 'Untitled'),
            'content': article.get('content', ''),
            'source': article.get('source', ''),
            'source_url': article.get('source_url', ''),
            'publication_date': article.get('publication_date'),  # Include publication date
            'quality_score': quality_score,
            'confidence': confidence,
            'nlp_analysis': nlp_analysis,
            'category': category
        }
        
        article_assignments.append(article_data)
    
    # Remove cross-category duplicates - keep article in category with highest confidence
    unique_articles = remove_cross_category_duplicates(article_assignments)
    
    # Now organize into categories
    for article in unique_articles:
        categorized[article['category']].append(article)
    
    # Sort articles within each category by quality score and remove intra-category duplicates
    for category in categorized:
        # Remove duplicates within the same category
        categorized[category] = remove_intra_category_duplicates(categorized[category])
        # Sort by quality score
        categorized[category].sort(key=lambda x: x['quality_score'], reverse=True)
    
    print(f"Organized articles into {len(categorized)} categories:")
    for category, articles_list in categorized.items():
        avg_quality = sum(a['quality_score'] for a in articles_list) / len(articles_list)
        print(f"   {category.replace('_', ' ').title()}: {len(articles_list)} articles (avg quality: {avg_quality:.1f}/100)")
    
    return dict(categorized)


def create_category_summary(client, category, articles):
    """Create an AI summary for a specific category."""
    try:
        print(f"Summarizing {category.replace('_', ' ').title()} ({len(articles)} articles)...")
        
        # Prepare top articles for summarization
        top_articles = articles[:5]  # Use top 5 articles
        articles_text = ""
        
        for i, article in enumerate(top_articles, 1):
            articles_text += f"\\n--- Article {i} ---\\n"
            articles_text += f"Title: {article['title']}\\n"
            articles_text += f"Content: {article['content'][:800]}...\\n"
        
        category_name = category.replace('_', ' ').title()
        prompt = f"""Please create a comprehensive summary for {category_name} news.

Here are the key articles:
{articles_text}

Create a well-structured summary with:
1. Key Highlights (3-4 main points)
2. Major Stories (detailed coverage)  
3. Notable Updates (other important items)

Write in professional news style, focusing on facts and key details.
Aim for 3-4 paragraphs total."""

        messages = [ChatMessage(role="user", content=prompt)]
        
        response = client.chat(
            model="mistral-small-latest",
            messages=messages,
            max_tokens=600,
            temperature=0.3,
        )
        
        if response and response.choices and len(response.choices) > 0:
            summary_text = response.choices[0].message.content.strip()
            
            return {
                'category': category,
                'category_title': category_name,
                'article_count': len(articles),
                'summary': summary_text,
                'generated_at': datetime.now().isoformat(),
                'top_articles': [
                    {
                        'title': article['title'],  # Keep full title instead of truncating
                        'source': article['source'],
                        'source_url': article.get('source_url', ''),  # Include the article URL
                        'quality_score': article['quality_score'],
                        'publication_date': article.get('publication_date')  # Include publication date
                    }
                    for article in articles[:3]
                ]
            }
        
        print(f"Failed to get summary for {category}")
        return None
        
    except Exception as e:
        print(f"Error summarizing {category}: {e}")
        return None


def save_summaries(summaries, total_articles, output_dir=None):
    """Save the categorized summaries."""
    if output_dir is None:
        output_dir = config.OUTPUT_FOLDER
    
    try:
        Path(output_dir).mkdir(exist_ok=True)
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        
        # Create newsletter data
        newsletter = {
            'title': f"{config.NEWSLETTER_TITLE} - {datetime.now().strftime('%B %d, %Y')}",
            'generated_at': datetime.now().isoformat(),
            'total_articles': total_articles,
            'categories_count': len(summaries),
            'category_summaries': summaries
        }
        
        # Save JSON
        json_path = f"{output_dir}/categorized_summaries_{timestamp}.json"
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(newsletter, f, indent=2, ensure_ascii=False)
        
        # Create simple HTML
        html_content = create_html_newsletter(newsletter)
        html_path = f"{output_dir}/categorized_summaries_{timestamp}.html"
        
        with open(html_path, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        print(f"Newsletter saved:")
        print(f"   JSON: {json_path}")
        print(f"   HTML: {html_path}")
        
        return {
            'json_path': json_path,
            'html_path': html_path,
            'newsletter': newsletter
        }
        
    except Exception as e:
        print(f"Error saving newsletter: {e}")
        return None


def create_html_newsletter(newsletter):
    """Generate HTML newsletter."""
    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{newsletter['title']}</title>
    <style>
        body {{ font-family: Arial, sans-serif; line-height: 1.6; margin: 0; padding: 20px; background-color: #f5f5f5; }}
        .container {{ max-width: 1000px; margin: 0 auto; background: white; padding: 30px; border-radius: 10px; box-shadow: 0 0 20px rgba(0,0,0,0.1); }}
        h1 {{ color: #2c3e50; border-bottom: 3px solid #3498db; padding-bottom: 10px; }}
        h2 {{ color: #34495e; border-left: 4px solid #3498db; padding-left: 15px; margin-top: 30px; }}
        .category-section {{ margin: 30px 0; padding: 20px; border: 1px solid #bdc3c7; border-radius: 8px; }}
        .articles-list {{ background: #f8f9fa; padding: 15px; border-radius: 5px; margin-top: 15px; }}
        .article-item {{ padding: 8px 0; border-bottom: 1px solid #dee2e6; }}
        .article-item a {{ color: #2c3e50; text-decoration: none; }}
        .article-item a:hover {{ color: #3498db; text-decoration: underline; }}
        .read-more-link {{ color: #3498db; font-size: 12px; margin-left: 10px; }}
        .read-more-link:hover {{ color: #2980b9; text-decoration: underline; }}
        .quality-score {{ background: #27ae60; color: white; padding: 2px 8px; border-radius: 12px; font-size: 12px; }}
        .stats {{ background: #ecf0f1; padding: 15px; border-radius: 5px; margin: 20px 0; }}
    </style>
</head>
<body>
    <div class="container">
        <h1>{newsletter['title']}</h1>
        
        <div class="stats">
            <strong>Newsletter Statistics:</strong><br>
            Total Articles Analyzed: {newsletter['total_articles']}<br>
            Categories Covered: {newsletter['categories_count']}<br>
            Generated: {datetime.now().strftime('%Y-%m-%d at %H:%M:%S')}
        </div>
"""
    
    # Add category sections
    for category, summary in newsletter['category_summaries'].items():
        html += f"""
        <div class="category-section">
            <h2>{summary['category_title']} ({summary['article_count']} articles)</h2>
            
            <div style="white-space: pre-line; margin-bottom: 15px;">{summary['summary']}</div>
            
            <div class="articles-list">
                <strong>Top Articles:</strong>
"""
        
        for article in summary['top_articles']:
            # Create clickable link if URL is available
            article_title = article['title']
            article_url = article.get('source_url', '')
            
            if article_url:
                title_html = f'<a href="{article_url}" target="_blank">{article_title}</a>'
                read_more = f' <a href="{article_url}" target="_blank" class="read-more-link">[Read Full Article]</a>'
            else:
                title_html = article_title
                read_more = ''
            
            # Format the publication date if available
            date_info = ""
            if article.get('publication_date'):
                try:
                    from dateutil import parser as date_parser
                    
                    # Parse and format the date
                    parsed_date = date_parser.parse(article['publication_date'], fuzzy=True)
                    formatted_date = parsed_date.strftime('%B %d, %Y')
                    date_info = f" | Posted: {formatted_date}"
                except Exception as e:
                    # If date parsing fails, show raw date
                    print(f"    Date parsing failed for {article['title'][:30]}...: {e}")
                    date_info = f" | Posted: {article['publication_date']}"
            
            html += f"""
                <div class="article-item">
                    <strong>{title_html}</strong> 
                    <span class="quality-score">Quality: {article['quality_score']}/100</span>{read_more}<br>
                    <small>Source: {article['source']}{date_info}</small>
                </div>
"""
        
        html += "</div></div>"
    
    html += """
    </div>
</body>
</html>"""
    
    return html


def run_categorized_summarization(articles_filepath):
    """Main function to run categorized summarization."""
    print("Starting categorized newsletter generation...")
    
    # Load articles
    try:
        with open(articles_filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        articles = data.get('articles', [])
        total_articles = len(articles)
        print(f"Loaded {total_articles} articles")
        
    except Exception as e:
        print(f"Error loading articles: {e}")
        return None
    
    if not articles:
        print("No articles found")
        return None
    
    # Create Mistral client
    try:
        client = create_mistral_client()
    except Exception as e:
        print(f"Failed to create Mistral client: {e}")
        return None
    
    # Organize by categories
    categorized_articles = organize_by_categories(articles)
    
    # Create summaries for each category
    summaries = {}
    
    for category, category_articles in categorized_articles.items():
        if len(category_articles) >= 2:  # Only process categories with multiple articles
            summary = create_category_summary(client, category, category_articles)
            if summary:
                summaries[category] = summary
                time.sleep(1)  # Respectful delay between API calls
    
    if not summaries:
        print("No summaries generated")
        return None
    
    # Save results
    result = save_summaries(summaries, total_articles)
    
    if result:
        print(f"Successfully generated newsletter with {len(summaries)} categories!")
        return result
    
    return None
