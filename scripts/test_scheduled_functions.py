#!/usr/bin/env python3
"""
Test script for scheduled functions
Run individual scheduled functions locally for testing

Usage:
    python scripts/test_scheduled_functions.py [--function FUNCTION_NAME]
    
Examples:
    python scripts/test_scheduled_functions.py --function notifications
    python scripts/test_scheduled_functions.py --function cache-refresh
    python scripts/test_scheduled_functions.py --function session-keepalive
    python scripts/test_scheduled_functions.py  # Runs all functions
"""

import os
import sys
from pathlib import Path
from datetime import datetime, timezone
from typing import Optional

# Add project root to path
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

# Try to load environment variables from .env
try:
    from dotenv import load_dotenv
    load_dotenv(PROJECT_ROOT / '.env')
except ImportError:
    pass

# Set up environment variables if not already set
if not os.environ.get('PROJECT_ID'):
    project_id = (
        os.environ.get('GCP_PROJECT') or
        os.environ.get('GCLOUD_PROJECT') or
        os.environ.get('PROJECT_ID') or
        'respondentpro'  # Default fallback
    )
    os.environ['PROJECT_ID'] = project_id


def test_notifications():
    """Test the notifications scheduled function"""
    print("=" * 80)
    print("Testing scheduled_notifications")
    print("=" * 80)
    
    try:
        # For local testing, call the underlying functions directly
        # The scheduler wrapper is just for deployment - the actual logic is in these functions
        from web.notification_scheduler import (
            check_and_send_weekly_notifications,
            check_and_send_token_expiration_notifications
        )
        
        print("Calling check_and_send_weekly_notifications()...")
        check_and_send_weekly_notifications()
        
        print("Calling check_and_send_token_expiration_notifications()...")
        check_and_send_token_expiration_notifications()
        
        print("\n✓ Notifications test completed successfully")
        return True
    except ImportError as e:
        print(f"\n✗ Import error: {e}")
        import traceback
        traceback.print_exc()
        return False
    except Exception as e:
        print(f"\n✗ Notifications test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_cache_refresh():
    """Test the cache refresh scheduled function"""
    print("=" * 80)
    print("Testing scheduled_cache_refresh")
    print("=" * 80)
    
    try:
        # For local testing, call the underlying function directly
        from web.cache_refresh import refresh_stale_caches
        
        print("Calling refresh_stale_caches(max_age_hours=24)...")
        refresh_stale_caches(max_age_hours=24)
        
        print("\n✓ Cache refresh test completed successfully")
        return True
    except ImportError as e:
        print(f"\n✗ Import error: {e}")
        import traceback
        traceback.print_exc()
        return False
    except Exception as e:
        print(f"\n✗ Cache refresh test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_session_keepalive():
    """Test the session keep-alive scheduled function"""
    print("=" * 80)
    print("Testing scheduled_session_keepalive")
    print("=" * 80)
    
    try:
        # For local testing, call the underlying function directly
        from web.cache_refresh import keep_sessions_alive
        
        print("Calling keep_sessions_alive()...")
        keep_sessions_alive()
        
        print("\n✓ Session keep-alive test completed successfully")
        return True
    except ImportError as e:
        print(f"\n✗ Import error: {e}")
        import traceback
        traceback.print_exc()
        return False
    except Exception as e:
        print(f"\n✗ Session keep-alive test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Main function to run tests"""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Test scheduled functions locally",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python scripts/test_scheduled_functions.py --function notifications
  python scripts/test_scheduled_functions.py --function cache-refresh
  python scripts/test_scheduled_functions.py --function session-keepalive
  python scripts/test_scheduled_functions.py  # Runs all functions
        """
    )
    
    parser.add_argument(
        "--function",
        choices=["notifications", "cache-refresh", "session-keepalive", "all"],
        default="all",
        help="Which function to test (default: all)"
    )
    
    args = parser.parse_args()
    
    print("=" * 80)
    print("Scheduled Functions Local Test")
    print("=" * 80)
    print(f"Project ID: {os.environ.get('PROJECT_ID', 'not set')}")
    print(f"Testing: {args.function}")
    print("=" * 80)
    print()
    
    results = {}
    
    if args.function == "notifications" or args.function == "all":
        results["notifications"] = test_notifications()
        print()
    
    if args.function == "cache-refresh" or args.function == "all":
        results["cache-refresh"] = test_cache_refresh()
        print()
    
    if args.function == "session-keepalive" or args.function == "all":
        results["session-keepalive"] = test_session_keepalive()
        print()
    
    # Summary
    print("=" * 80)
    print("Test Summary")
    print("=" * 80)
    for name, success in results.items():
        status = "✓ PASSED" if success else "✗ FAILED"
        print(f"{name:30} {status}")
    print("=" * 80)
    
    # Exit with error code if any test failed
    if not all(results.values()):
        sys.exit(1)


if __name__ == "__main__":
    main()
