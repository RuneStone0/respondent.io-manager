#!/bin/bash
# Generate self-signed SSL certificate for local development

CERT_DIR="certs"
DOMAIN="dev.respondentpro.xyz"
CONFIG_FILE="$CERT_DIR/openssl.conf"

# Create certs directory if it doesn't exist
mkdir -p "$CERT_DIR"

# Generate private key
openssl genrsa -out "$CERT_DIR/$DOMAIN.key" 2048

# Generate self-signed certificate with SANs (valid for 365 days)
openssl req -new -x509 -key "$CERT_DIR/$DOMAIN.key" \
    -out "$CERT_DIR/$DOMAIN.crt" \
    -days 365 \
    -config "$CONFIG_FILE" \
    -extensions v3_req

# Clean up CSR file
rm "$CERT_DIR/$DOMAIN.csr"

# Set appropriate permissions
chmod 644 "$CERT_DIR/$DOMAIN.crt"
chmod 600 "$CERT_DIR/$DOMAIN.key"

echo "Certificate generated successfully!"
echo "Certificate: $CERT_DIR/$DOMAIN.crt"
echo "Private Key: $CERT_DIR/$DOMAIN.key"
echo ""
echo "Note: Browsers will show a security warning for self-signed certificates."
echo "You'll need to click 'Advanced' and 'Proceed to dev.respondentpro.xyz' to continue."
