"""
Cloud Function for scheduled notifications
Automatically scheduled by Firebase (runs every Friday morning at 9:00 AM)
"""

# Initialize Firebase Admin
from firebase_admin import initialize_app
initialize_app()

from firebase_functions import scheduler_fn
from web.notification_scheduler import check_and_send_weekly_notifications, check_and_send_token_expiration_notifications


@scheduler_fn.on_schedule(schedule="every friday 09:00", timezone="America/New_York")
def scheduled_notifications(event: scheduler_fn.ScheduledEvent) -> None:
    """
    Check and send weekly project summary notifications and token expiration notifications.
    Runs every Friday morning at 9:00 AM to check for users who need notifications.
    """
    try:
        # Check weekly notifications
        check_and_send_weekly_notifications()
        
        # Check token expiration notifications
        check_and_send_token_expiration_notifications()
        
        print("[Notifications] Scheduled task completed successfully")
    except Exception as e:
        print(f"[Notifications] Error in scheduled task: {e}")
        import traceback
        print(traceback.format_exc())
        raise
