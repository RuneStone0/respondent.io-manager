#!/usr/bin/env python3
"""
Entry point for Respondent.io Web UI
"""
import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from .env file in project root
load_dotenv(Path(__file__).parent / '.env')

from web.app import app

if __name__ == '__main__':
    host = os.environ.get('HOST', '0.0.0.0')
    port = int(os.environ.get('PORT', 5000))
    debug = os.environ.get('FLASK_DEBUG', 'False').lower() == 'true'
    
    # Check for SSL certificates for HTTPS support
    ssl_context = None
    cert_file = Path(__file__).parent / 'certs' / 'dev.respondentpro.xyz.crt'
    key_file = Path(__file__).parent / 'certs' / 'dev.respondentpro.xyz.key'
    
    # Note: Flask's development server has known SSL issues (connection hangs)
    # For HTTPS, use: ./run_dev_https.sh (uses gunicorn which handles SSL properly)
    # For HTTP (localhost only), just run: python web.py
    ssl_context = None
    if cert_file.exists() and key_file.exists():
        print("Note: SSL certificates found, but Flask dev server has SSL issues.")
        print("For HTTPS with dev.respondentpro.xyz, use: ./run_dev_https.sh")
        print("Running in HTTP mode (localhost only) - WebAuthn will not work.")
    elif os.environ.get('SSL_CERT') and os.environ.get('SSL_KEY'):
        # Allow SSL via env vars if explicitly set
        ssl_context = (os.environ.get('SSL_CERT'), os.environ.get('SSL_KEY'))
        print("SSL enabled: Using certificates from environment variables")
    
    app.run(debug=debug, host=host, port=port, ssl_context=ssl_context)

