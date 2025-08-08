"""
Simple HTTP server to serve newsletter files
"""

import threading
import http.server
import socketserver
from pathlib import Path
import time
import socket


class NewsletterHandler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        # Set the directory to serve files from
        output_dir = Path(__file__).parent / "output"
        if not output_dir.exists():
            output_dir.mkdir(exist_ok=True)
        super().__init__(*args, directory=str(output_dir), **kwargs)
    
    def log_message(self, fmt, *args):
        # Suppress default logging to reduce noise
        pass


class ReuseAddressTCPServer(socketserver.TCPServer):
    allow_reuse_address = True


def start_newsletter_server(port=8503):
    """Start a simple HTTP server to serve newsletter files"""
    handler = NewsletterHandler
    
    try:
        with ReuseAddressTCPServer(("", port), handler) as httpd:
            print(f"Newsletter server running on http://localhost:{port}")
            httpd.serve_forever()
    except OSError as e:
        print(f"Error starting server on port {port}: {e}")
        raise


def start_server_thread(port=8503):
    """Start the newsletter server in a background thread"""
    # Check if port is available
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.bind(('localhost', port))
    except OSError:
        print(f"Port {port} is already in use, but continuing...")
        return port
    
    server_thread = threading.Thread(target=start_newsletter_server, args=(port,), daemon=True)
    server_thread.start()
    time.sleep(1)  # Give server time to start
    return port


if __name__ == "__main__":
    start_newsletter_server()
