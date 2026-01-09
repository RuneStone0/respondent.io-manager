"""
Cloud Function for scheduled session keep-alive
Automatically scheduled by Firebase (runs every 8 hours)
"""

import os
import sys
from pathlib import Path

# Add parent directory to path
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

# Initialize Firebase Admin (if not already initialized)
try:
    import firebase_admin
    from firebase_admin import initialize_app
    if not firebase_admin._apps:
        project_id = os.environ.get('GCP_PROJECT') or os.environ.get('PROJECT_ID', 'respondentpro')
        os.environ['PROJECT_ID'] = project_id
        initialize_app()
except (ValueError, ImportError):
    # Already initialized or firebase_admin not available
    pass

from firebase_functions import scheduler_fn
from web.cache_refresh import keep_sessions_alive


@scheduler_fn.on_schedule(schedule="0 */8 * * *", timezone="America/New_York")
def scheduled_session_keepalive(event: scheduler_fn.ScheduledEvent) -> None:
    """
    Keep all user sessions alive by checking Respondent.io profile endpoints.
    Runs every 8 hours to prevent session expiration.
    """
    try:
        # Keep all sessions alive by checking profile endpoints
        keep_sessions_alive()
        print("[Session Keep-Alive] Scheduled task completed successfully")
    except Exception as e:
        print(f"[Session Keep-Alive] Error in scheduled task: {e}")
        import traceback
        print(traceback.format_exc())
        raise
