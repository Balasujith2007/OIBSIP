"""
=============================================================================
 Oasis Infobyte SIP — Python Programming Internship
 Task 2: BMI Calculator — Web Server Launcher
=============================================================================
"""

import http.server
import socketserver
import webbrowser
import os
import sys

PORT = 8080
DIRECTORY = os.path.dirname(os.path.abspath(__file__))


class CustomHandler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=DIRECTORY, **kwargs)


def main():
    os.chdir(DIRECTORY)
    url = f"http://localhost:{PORT}/index.html"
    print(f"==================================================")
    print(f" Oasis Infobyte Task 2: ProFit BMI Calculator")
    print(f" Serving live web app at: {url}")
    print(f" Press Ctrl+C to stop the server.")
    print(f"==================================================")
    
    # Open browser automatically
    webbrowser.open(url)
    
    with socketserver.TCPServer(("", PORT), CustomHandler) as httpd:
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\nServer stopped.")


if __name__ == "__main__":
    main()
