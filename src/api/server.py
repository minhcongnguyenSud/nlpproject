"""
Simple Web Server for Newsletter Dashboard
This creates a web page where students can generate newsletters easily!

What this does:
- Creates a web server (like a mini website)
- Students can visit it in their browser
- Click a button to generate newsletters
- View old newsletters they created
"""

import os
import json
import asyncio
from datetime import datetime
from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import urlparse

from ..core import config

class NewsletterHandler(BaseHTTPRequestHandler):
    """HTTP request handler for the newsletter dashboard"""
    
    def _set_headers(self, status_code=200, content_type='text/html'):
        """Set the headers for the response"""
        self.send_response(status_code)
        self.send_header('Content-type', content_type)
        self.end_headers()
    
    def do_GET(self):
        """Handle GET requests"""
        # Parse the URL path
        parsed_url = urlparse(self.path)
        path = parsed_url.path
        
        # Serve the dashboard HTML
        if path == '/' or path == '/dashboard' or path == '/dashboard.html':
            self._serve_file('dashboard.html')
        # List newsletters API
        elif path == '/list_newsletters':
            self._list_newsletters()
        # Serve a specific newsletter file
        elif path.startswith(f'/{config.OUTPUT_FOLDER}/'):
            self._serve_file(path[1:])  # Remove the leading slash
        # Handle 404 for any other path
        else:
            self._set_headers(404, 'text/plain')
            self.wfile.write(b'404 Not Found')
    
    def do_POST(self):
        """Handle POST requests"""
        # Generate new newsletter API
        if self.path == '/generate_newsletter':
            self._generate_newsletter()
        # Handle 404 for any other path
        else:
            self._set_headers(404, 'text/plain')
            self.wfile.write(b'404 Not Found')
    
    def _serve_file(self, file_path):
        """Serve a static file"""
        try:
            with open(file_path, 'rb') as f:
                content = f.read()
                
            # Set the appropriate content type based on file extension
            if file_path.endswith('.html'):
                content_type = 'text/html'
            elif file_path.endswith('.css'):
                content_type = 'text/css'
            elif file_path.endswith('.js'):
                content_type = 'text/javascript'
            else:
                content_type = 'text/plain'
                
            self._set_headers(200, content_type)
            self.wfile.write(content)
        except FileNotFoundError:
            self._set_headers(404, 'text/plain')
            self.wfile.write(b'404 Not Found')
    
    def _list_newsletters(self):
        """API endpoint to list all generated newsletters"""
        try:
            import os
            from pathlib import Path
            
            # Get list of newsletter HTML files from the configured output directory
            output_path = Path(config.OUTPUT_FOLDER)
            if not output_path.exists():
                output_path.mkdir(exist_ok=True)
            
            newsletter_files = list(output_path.glob('*.html'))
            
            # Get detailed info for each newsletter
            newsletters = []
            for filepath in newsletter_files:
                stat = filepath.stat()
                newsletters.append({
                    'file_path': f'/{config.OUTPUT_FOLDER}/{filepath.name}',  # URL path
                    'filename': filepath.name,
                    'date': datetime.fromtimestamp(stat.st_mtime).isoformat(),
                    'size': stat.st_size
                })
            
            # Sort by date (newest first)
            newsletters.sort(key=lambda x: x['date'], reverse=True)
            
            # Return JSON response
            self._set_headers(200, 'application/json')
            self.wfile.write(json.dumps({'newsletters': newsletters}).encode('utf-8'))
        except Exception as e:
            # Log the exception for debugging
            print(f"Error listing newsletters: {e}")
            self._set_headers(500, 'application/json')
            self.wfile.write(json.dumps({'error': "Failed to list newsletters"}).encode('utf-8'))
    
    def _generate_newsletter(self):
        """API endpoint to generate a new newsletter"""
        try:
            # Run the newsletter generation process
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            file_path = loop.run_until_complete(self._run_newsletter_generator())
            loop.close()
            
            if file_path:
                # Return success response
                self._set_headers(200, 'application/json')
                self.wfile.write(json.dumps({
                    'success': True,
                    'file_path': '/' + file_path
                }).encode('utf-8'))
            else:
                # Return error response
                self._set_headers(500, 'application/json')
                self.wfile.write(json.dumps({
                    'success': False,
                    'error': 'Failed to generate newsletter'
                }).encode('utf-8'))
        except (asyncio.TimeoutError, ConnectionError) as e:
            # Network related errors
            self._set_headers(500, 'application/json')
            self.wfile.write(json.dumps({
                'success': False,
                'error': f"Network error: {str(e)}"
            }).encode('utf-8'))
        except Exception as e:
            # Log the exception for debugging but provide a generic message to user
            print(f"Unexpected error in _generate_newsletter: {str(e)}")
            self._set_headers(500, 'application/json')
            self.wfile.write(json.dumps({
                'success': False,
                'error': "An unexpected error occurred while generating the newsletter"
            }).encode('utf-8'))
    
    async    def _run_newsletter_generator(self):
        """Run the newsletter generation process using modern categorized approach"""
        try:
            # Import required components
            import sys
            import os
            import json
            from datetime import datetime
            sys.path.append(os.path.join(os.path.dirname(__file__), '../..'))
            
            from src.core import config
            from src.utils.utils import ensure_directory_exists
            from src.newsletter_generator.scraper import get_all_articles
            from src.newsletter_generator.simple_categorized_summarizer import run_categorized_summarization
            
            # Replicate the modern newsletter generation logic
            print("=== Modern Categorized Newsletter Generator ===")
            print("Generating newsletter via web interface...")
            
            # Check setup
            if not ensure_directory_exists(config.INPUT_FOLDER):
                print(f"Failed to create {config.INPUT_FOLDER} folder.")
                return None
                
            if not ensure_directory_exists(config.OUTPUT_FOLDER):
                print(f"Failed to create {config.OUTPUT_FOLDER} folder.")
                return None
            
            # Get articles with NLP analysis
            articles = get_all_articles()
            if not articles:
                print("No articles were scraped.")
                return None
            
            print(f"Found {len(articles)} quality articles with NLP analysis!")
            
            # Save detailed articles with NLP analysis
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
            except Exception as e:
                print(f"Warning: Could not save detailed file: {e}")
            
            # Generate categorized newsletter
            result = run_categorized_summarization(detailed_file)
            
            if result:
                print(f"Newsletter generated successfully!")
                return result['html_path']
            else:
                print("Failed to generate newsletter")
                return None
            
        except Exception as e:
            print(f"Error running newsletter generator: {e}")
            return None

def run_server(port=None):
    """Run the web server"""
    if port is None:
        port = int(os.environ.get('PORT', 8080))
    
    server_address = ('', port)
    httpd = HTTPServer(server_address, NewsletterHandler)
    print(f"Server running at http://0.0.0.0:{port}")
    print(f"Access the dashboard at: http://localhost:{port}")
    print("Press Ctrl+C to stop the server")
    httpd.serve_forever()

if __name__ == '__main__':
    run_server()
