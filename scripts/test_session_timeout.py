#!/usr/bin/env python3
"""
Session Timeout Test Script

Tests cookie session timeout by repeatedly sending GET requests with
cumulative 4-hour delays until the session expires.
"""
import requests
import time
from datetime import datetime, timedelta


# Configuration
URL = "https://app.respondent.io/api/v4/profiles/user/691f593aabd77eb5a29c7b35"
COOKIE_VALUE = "s%3AHDaelXTCj8EtHCKj7_hPwUspdBfa1cUJ.lUppS7cuJuJ4NmB%2BsuIydZiN9XwTCo9uLfKae2C7Gpc"
DELAY_INCREMENT_HOURS = 4

# Headers
headers = {
    "Cookie": f"respondent.session.sid={COOKIE_VALUE}",
    "X-Requested-With": "XMLHttpRequest",
    "Accept": "application/json, text/plain, */*",
    "Sec-Fetch-Site": "same-origin"
}


def format_time_delta(hours):
    """Format time delta in hours to a human-readable string."""
    if hours < 24:
        return f"{hours:.1f} hours"
    else:
        days = hours / 24
        return f"{days:.2f} days"


def main():
    """Main function to test session timeout."""
    print("=" * 80)
    print("Session Timeout Test Script")
    print("=" * 80)
    print(f"Target URL: {URL}")
    print(f"Starting delay increment: {DELAY_INCREMENT_HOURS} hours")
    print("=" * 80)
    print()

    request_count = 0
    delay_hours = 0
    start_time = datetime.now()
    last_request_time = None
    total_elapsed = timedelta(0)

    try:
        while True:
            request_count += 1
            current_time = datetime.now()
            
            # Calculate time since last request
            if last_request_time:
                time_since_last = current_time - last_request_time
                time_since_last_hours = time_since_last.total_seconds() / 3600
                time_since_last_str = format_time_delta(time_since_last_hours)
            else:
                time_since_last_str = "N/A (first request)"
            
            # Log request timestamp and time since last request
            print(f"[Request #{request_count}]")
            print(f"  Timestamp: {current_time.strftime('%Y-%m-%d %H:%M:%S')}")
            print(f"  Time since last request: {time_since_last_str}")
            print(f"  Current delay: {delay_hours} hours")
            print(f"  Sending request...", end=" ", flush=True)
            
            # Send GET request
            try:
                response = requests.get(URL, headers=headers, timeout=30)
                print(f"Status: {response.status_code}")
                
                # Check if session expired (non-200 response)
                if response.status_code != 200:
                    print()
                    print("=" * 80)
                    print("SESSION TIMEOUT DETECTED")
                    print("=" * 80)
                    print()
                    
                    # Full HTTP response
                    print("Full HTTP Response:")
                    print("-" * 80)
                    print(f"Status Code: {response.status_code}")
                    print(f"Status Reason: {response.reason}")
                    print()
                    print("Response Headers:")
                    for key, value in response.headers.items():
                        print(f"  {key}: {value}")
                    print()
                    print("Response Body:")
                    print("-" * 80)
                    try:
                        # Try to decode as JSON first
                        print(response.json())
                    except:
                        # Fall back to text
                        print(response.text)
                    print("-" * 80)
                    print()
                    
                    # Summary
                    total_elapsed = current_time - start_time
                    total_elapsed_hours = total_elapsed.total_seconds() / 3600
                    
                    print("Summary:")
                    print("-" * 80)
                    print(f"Total requests made: {request_count}")
                    print(f"Total time elapsed: {format_time_delta(total_elapsed_hours)}")
                    print(f"Delay before timeout: {format_time_delta(delay_hours)}")
                    print(f"Start time: {start_time.strftime('%Y-%m-%d %H:%M:%S')}")
                    print(f"Timeout detected at: {current_time.strftime('%Y-%m-%d %H:%M:%S')}")
                    print("=" * 80)
                    break
                
            except requests.exceptions.RequestException as e:
                print(f"ERROR: {e}")
                print("Retrying in 60 seconds...")
                time.sleep(60)
                continue
            
            # Update last request time
            last_request_time = current_time
            
            # Calculate next delay (cumulative: 0h, 4h, 8h, 12h, 16h, etc.)
            delay_hours += DELAY_INCREMENT_HOURS
            delay_seconds = delay_hours * 3600
            
            print(f"  Waiting {format_time_delta(delay_hours)} before next request...")
            print()
            
            # Sleep for the delay
            time.sleep(delay_seconds)
            
    except KeyboardInterrupt:
        print()
        print("=" * 80)
        print("Test interrupted by user")
        print("=" * 80)
        if request_count > 0:
            total_elapsed = datetime.now() - start_time
            total_elapsed_hours = total_elapsed.total_seconds() / 3600
            print(f"Total requests made: {request_count}")
            print(f"Total time elapsed: {format_time_delta(total_elapsed_hours)}")
            print(f"Last delay was: {format_time_delta(delay_hours)}")
        print("=" * 80)


if __name__ == "__main__":
    main()
