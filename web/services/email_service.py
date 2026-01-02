#!/usr/bin/env python3
"""
Email service for sending verification and notification emails
"""

import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from pathlib import Path

# Get the directory where this file is located
BASE_DIR = Path(__file__).parent.parent
TEMPLATES_DIR = BASE_DIR / 'templates' / 'email'


def get_smtp_config():
    """Get SMTP configuration from environment variables"""
    return {
        'host': os.environ.get('SMTP_HOST', 'smtp.mailgun.org'),
        'port': int(os.environ.get('SMTP_PORT', '587')),
        'user': os.environ.get('SMTP_USER'),
        'password': os.environ.get('SMTP_PASSWORD'),
        'from_email': os.environ.get('SMTP_FROM_EMAIL'),
        'app_url': os.environ.get('APP_URL', 'http://localhost:5000')
    }


def send_email(to_email, subject, html_body, text_body=None):
    """Send an email using SMTP"""
    config = get_smtp_config()
    
    if not config['user'] or not config['password']:
        raise Exception("SMTP credentials not configured. Please set SMTP_USER and SMTP_PASSWORD environment variables.")
    
    if not config['from_email']:
        raise Exception("SMTP_FROM_EMAIL not configured.")
    
    try:
        # Create message
        msg = MIMEMultipart('alternative')
        msg['Subject'] = subject
        msg['From'] = config['from_email']
        msg['To'] = to_email
        
        # Add text and HTML parts
        if text_body:
            part1 = MIMEText(text_body, 'plain')
            msg.attach(part1)
        
        part2 = MIMEText(html_body, 'html')
        msg.attach(part2)
        
        # Send email
        with smtplib.SMTP(config['host'], config['port']) as server:
            server.starttls()
            server.login(config['user'], config['password'])
            server.send_message(msg)
        
        return True
    except Exception as e:
        raise Exception(f"Failed to send email: {e}")


def send_verification_email(email, token):
    """Send email verification email"""
    config = get_smtp_config()
    verification_url = f"{config['app_url']}/api/verify-email/{token}"
    
    # Load email template
    template_path = TEMPLATES_DIR / 'verification.html'
    if template_path.exists():
        with open(template_path, 'r', encoding='utf-8') as f:
            html_template = f.read()
    else:
        # Fallback template if file doesn't exist
        html_template = """
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <title>Verify Your Email</title>
        </head>
        <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
            <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
                <h1 style="color: #4CAF50;">Verify Your Email</h1>
                <p>Thank you for signing up for Respondent Pro!</p>
                <p>Please click the button below to verify your email address:</p>
                <p style="text-align: center; margin: 30px 0;">
                    <a href="{verification_url}" style="background-color: #4CAF50; color: white; padding: 12px 24px; text-decoration: none; border-radius: 5px; display: inline-block;">Verify Email</a>
                </p>
                <p>Or copy and paste this link into your browser:</p>
                <p style="word-break: break-all; color: #666;">{verification_url}</p>
                <p>This link will expire in 7 days.</p>
                <p>If you didn't create an account, you can safely ignore this email.</p>
            </div>
        </body>
        </html>
        """
    
    # Render template with variables (simple string replacement)
    html_body = html_template.replace('{verification_url}', verification_url).replace('{email}', email)
    
    # Plain text version
    text_body = f"""Verify Your Email

Thank you for signing up for Respondent Pro!

Please click the link below to verify your email address:
{verification_url}

This link will expire in 7 days.

If you didn't create an account, you can safely ignore this email.
"""
    
    return send_email(
        to_email=email,
        subject="Verify Your Email - Respondent Pro",
        html_body=html_body,
        text_body=text_body
    )


def send_login_email(email, token):
    """Send login link email"""
    config = get_smtp_config()
    login_url = f"{config['app_url']}/api/login/email/{token}"
    
    # Create login email template
    html_template = """
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Login to Respondent Pro</title>
    </head>
    <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333; margin: 0; padding: 0; background-color: #f4f4f4;">
        <div style="max-width: 600px; margin: 0 auto; padding: 20px; background-color: #ffffff;">
            <div style="text-align: center; margin-bottom: 30px;">
                <h1 style="color: #4CAF50; margin: 0;">Respondent Pro</h1>
            </div>
            
            <h2 style="color: #333;">Login to Your Account</h2>
            
            <p>Click the button below to log in to your Respondent Pro account:</p>
            
            <div style="text-align: center; margin: 30px 0;">
                <a href="{login_url}" style="background-color: #4CAF50; color: white; padding: 12px 24px; text-decoration: none; border-radius: 5px; display: inline-block; font-weight: bold;">Log In</a>
            </div>
            
            <p style="color: #666; font-size: 14px;">Or copy and paste this link into your browser:</p>
            <p style="word-break: break-all; color: #666; font-size: 14px; background-color: #f9f9f9; padding: 10px; border-radius: 4px;">{login_url}</p>
            
            <p style="color: #999; font-size: 12px; margin-top: 30px;">This link will expire in 1 hour.</p>
            
            <p style="color: #999; font-size: 12px;">If you didn't request this login link, you can safely ignore this email.</p>
            
            <hr style="border: none; border-top: 1px solid #eee; margin: 30px 0;">
            
            <p style="color: #999; font-size: 12px; text-align: center;">
                © 2024 Respondent Pro. All rights reserved.
            </p>
        </div>
    </body>
    </html>
    """
    
    # Render template with variables
    html_body = html_template.replace('{login_url}', login_url).replace('{email}', email)
    
    # Plain text version
    text_body = f"""Login to Respondent Pro

Click the link below to log in to your account:
{login_url}

This link will expire in 1 hour.

If you didn't request this login link, you can safely ignore this email.
"""
    
    return send_email(
        to_email=email,
        subject="Login to Respondent Pro",
        html_body=html_body,
        text_body=text_body
    )
