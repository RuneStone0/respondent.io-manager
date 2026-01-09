"""
Cloud Function for scheduled cache refresh
Automatically scheduled by Firebase (runs daily at 6:00 AM)
"""

import os
import sys
from pathlib import Path

# Add parent directory to path
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from firebase_functions import scheduler_fn
from web.cache_refresh import refresh_stale_caches


@scheduler_fn.on_schedule(schedule="every day 06:00", timezone="America/New_York")
def scheduled_cache_refresh(event: scheduler_fn.ScheduledEvent) -> None:
    """
    Refresh stale project caches by fetching fresh data from Respondent.io API.
    Runs daily at 6:00 AM to keep caches up to date.
    """
    try:
        # Refresh stale caches (default max age: 24 hours)
        refresh_stale_caches(max_age_hours=24)
        print("[Cache Refresh] Scheduled task completed successfully")
    except Exception as e:
        print(f"[Cache Refresh] Error in scheduled task: {e}")
        import traceback
        print(traceback.format_exc())
        raise
