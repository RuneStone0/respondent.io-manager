#!/bin/bash
# Run Flask app in HTTP or HTTPS mode
# Usage: ./run.sh [--http|--https]

CERT_DIR="certs"
DOMAIN="dev.respondentpro.xyz"
CERT_FILE="$CERT_DIR/$DOMAIN.crt"
KEY_FILE="$CERT_DIR/$DOMAIN.key"
PORT=${PORT:-5000}
HOST=${HOST:-0.0.0.0}

# Parse arguments
MODE=""
if [ "$1" == "--http" ]; then
    MODE="http"
elif [ "$1" == "--https" ]; then
    MODE="https"
elif [ "$1" == "--help" ] || [ "$1" == "-h" ]; then
    MODE="help"
elif [ -n "$1" ]; then
    MODE="help"
fi

# Show help if no mode specified or help requested
if [ -z "$MODE" ] || [ "$MODE" == "help" ]; then
    echo "Usage: $0 [--http|--https]"
    echo ""
    echo "Options:"
    echo "  --http    Run in HTTP mode (localhost only, WebAuthn won't work)"
    echo "  --https   Run in HTTPS mode (requires SSL certificates, WebAuthn will work)"
    echo "  --help    Show this help message"
    echo ""
    echo "Examples:"
    echo "  $0 --https    # Start with HTTPS (recommended for passkeys)"
    echo "  $0 --http     # Start with HTTP (quick testing only)"
    exit 0
fi

if [ "$MODE" == "https" ]; then
    # Check if certificates exist
    if [ ! -f "$CERT_FILE" ] || [ ! -f "$KEY_FILE" ]; then
        echo "Error: SSL certificates not found!"
        echo "Please run ./generate_cert.sh first"
        exit 1
    fi

    echo "Starting Flask app with HTTPS on $HOST:$PORT"
    echo "Certificate: $CERT_FILE"
    echo "Private Key: $KEY_FILE"
    echo ""
    echo "Access at: https://dev.respondentpro.xyz:$PORT"
    echo ""

    # Run with gunicorn (better SSL support than Flask dev server)
    # SSL certificate warnings are already suppressed in web/app.py
    # --reload enables auto-reload on code changes (like Flask debug mode)
    gunicorn \
        --bind $HOST:$PORT \
        --workers 1 \
        --threads 8 \
        --timeout 120 \
        --keyfile "$KEY_FILE" \
        --certfile "$CERT_FILE" \
        --access-logfile - \
        --error-logfile - \
        --log-level info \
        --reload \
        web.app:app
else
    echo "Starting Flask app with HTTP on $HOST:$PORT"
    echo ""
    echo "Access at: http://localhost:$PORT"
    echo "Note: WebAuthn requires HTTPS, so passkeys won't work in HTTP mode."
    echo "Use --https for full functionality."
    echo ""

    # Run with Flask development server (HTTP only)
    python web.py
fi
