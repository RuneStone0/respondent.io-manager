#!/usr/bin/env python3
"""
Background notification scheduler for sending email notifications
"""

import threading
import time
from datetime import datetime

# Import services
try:
    from .services.notification_service import (
        load_notification_preferences, should_send_weekly_notification,
        should_send_token_expiration_notification, get_visible_projects_count,
        mark_weekly_notification_sent, mark_token_expiration_notification_sent
    )
    from .services.email_service import send_weekly_summary_email, send_session_token_expired_email
    from .services.user_service import get_email_by_user_id
except ImportError:
    from services.notification_service import (
        load_notification_preferences, should_send_weekly_notification,
        should_send_token_expiration_notification, get_visible_projects_count,
        mark_weekly_notification_sent, mark_token_expiration_notification_sent
    )
    from services.email_service import send_weekly_summary_email, send_session_token_expired_email
    from services.user_service import get_email_by_user_id


def start_notification_scheduler(db, check_interval_hours: int = 1, token_check_interval_hours: int = 12):
    """
    Start background thread to send notifications
    
    Args:
        db: MongoDB database object
        check_interval_hours: How often to check for weekly notifications (default: 1 hour)
        token_check_interval_hours: How often to check for token expiration (default: 12 hours)
    """
    last_token_check = datetime.utcnow()
    
    def notification_loop():
        nonlocal last_token_check
        while True:
            try:
                # Always check weekly notifications
                check_and_send_weekly_notifications(db)
                
                # Check token expiration only if enough time has passed
                time_since_last_token_check = (datetime.utcnow() - last_token_check).total_seconds() / 3600
                if time_since_last_token_check >= token_check_interval_hours:
                    check_and_send_token_expiration_notifications(db)
                    last_token_check = datetime.utcnow()
            except Exception as e:
                print(f"Error in notification scheduler: {e}")
                import traceback
                print(traceback.format_exc())
            
            # Sleep for check_interval_hours
            time.sleep(check_interval_hours * 3600)
    
    thread = threading.Thread(target=notification_loop, daemon=True)
    thread.start()
    return thread


def check_and_send_weekly_notifications(db):
    """
    Check and send weekly project summary notifications
    
    Args:
        db: MongoDB database object
    """
    try:
        users_collection = db['users']
        
        # Get all users (not just those with notification preferences)
        # This ensures new users get default preferences created
        users = users_collection.find({}, {'_id': 1})
        
        for user_doc in users:
            user_id = str(user_doc.get('_id'))
            if not user_id:
                continue
            
            try:
                # Load preferences (this will auto-create defaults if they don't exist)
                load_notification_preferences(user_id, auto_create=True)
                
                # Check if notification should be sent
                if should_send_weekly_notification(user_id):
                    # Get user email
                    email = get_email_by_user_id(user_id)
                    if not email:
                        print(f"[Notifications] Skipping user {user_id}: no email found")
                        continue
                    
                    # Get visible projects count
                    project_count = get_visible_projects_count(user_id)
                    
                    # Send email
                    try:
                        send_weekly_summary_email(email, project_count)
                        print(f"[Notifications] Sent weekly summary to {email} ({project_count} projects)")
                        
                        # Mark as sent
                        mark_weekly_notification_sent(user_id)
                    except Exception as e:
                        print(f"[Notifications] Failed to send weekly summary to {email}: {e}")
                        # Don't mark as sent if email failed
                        
            except Exception as e:
                print(f"[Notifications] Error processing weekly notification for user {user_id}: {e}")
                # Continue with next user
                continue
                
    except Exception as e:
        print(f"[Notifications] Error checking weekly notifications: {e}")
        import traceback
        print(traceback.format_exc())


def check_and_send_token_expiration_notifications(db):
    """
    Check and send session token expiration notifications
    
    Args:
        db: MongoDB database object
    """
    try:
        users_collection = db['users']
        
        # Get all users (not just those with notification preferences)
        # This ensures new users get default preferences created
        users = users_collection.find({}, {'_id': 1})
        
        for user_doc in users:
            user_id = str(user_doc.get('_id'))
            if not user_id:
                continue
            
            try:
                # Load preferences (this will auto-create defaults if they don't exist)
                load_notification_preferences(user_id, auto_create=True)
                
                # Check if notification should be sent
                if should_send_token_expiration_notification(user_id):
                    # Get user email
                    email = get_email_by_user_id(user_id)
                    if not email:
                        print(f"[Notifications] Skipping user {user_id}: no email found")
                        continue
                    
                    # Send email
                    try:
                        send_session_token_expired_email(email)
                        print(f"[Notifications] Sent token expiration notification to {email}")
                        
                        # Mark as sent
                        mark_token_expiration_notification_sent(user_id)
                    except Exception as e:
                        print(f"[Notifications] Failed to send token expiration notification to {email}: {e}")
                        # Don't mark as sent if email failed
                        
            except Exception as e:
                print(f"[Notifications] Error processing token expiration notification for user {user_id}: {e}")
                # Continue with next user
                continue
                
    except Exception as e:
        print(f"[Notifications] Error checking token expiration notifications: {e}")
        import traceback
        print(traceback.format_exc())
