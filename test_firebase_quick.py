#!/usr/bin/env python3
"""
Quick test for Firebase initialization
Usage:
  python test_firebase_quick.py                    # Test local environment
  python test_firebase_quick.py --cloud            # Test cloud environment (simulated)
  python test_firebase_quick.py --cloud --creds     # Test cloud with GOOGLE_APPLICATION_CREDENTIALS set
"""

import os
import sys
import logging
import argparse
from pathlib import Path

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(levelname)s - %(message)s'
)

# Add project root to path
PROJECT_ROOT = Path(__file__).parent
sys.path.insert(0, str(PROJECT_ROOT))


def main():
    parser = argparse.ArgumentParser(description='Test Firebase initialization')
    parser.add_argument('--cloud', action='store_true', 
                       help='Simulate cloud environment (sets GCP_PROJECT)')
    parser.add_argument('--creds', action='store_true',
                       help='Set GOOGLE_APPLICATION_CREDENTIALS to non-existent file (to test unset logic)')
    parser.add_argument('--debug', action='store_true',
                       help='Enable debug logging')
    
    args = parser.parse_args()
    
    if args.debug:
        logging.getLogger().setLevel(logging.DEBUG)
    
    # Save original environment
    original_env = {}
    env_vars_to_save = ['GCP_PROJECT', 'FUNCTION_NAME', 'K_SERVICE', 
                       'GOOGLE_APPLICATION_CREDENTIALS', 'PROJECT_ID']
    for var in env_vars_to_save:
        original_env[var] = os.environ.get(var)
    
    try:
        # Setup environment based on arguments
        if args.cloud:
            print("🌩️  Simulating Cloud Functions environment...")
            project_id = os.environ.get('PROJECT_ID') or 'respondentpro-xyz'
            os.environ['GCP_PROJECT'] = project_id
            os.environ['FUNCTION_NAME'] = 'respondentpro'
            
            if args.creds:
                os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = './non-existent-file.json'
                print(f"  Set GOOGLE_APPLICATION_CREDENTIALS to non-existent file (to test unset logic)")
            
            print(f"  GCP_PROJECT: {os.environ.get('GCP_PROJECT')}")
            print(f"  FUNCTION_NAME: {os.environ.get('FUNCTION_NAME')}")
        else:
            print("💻 Testing local environment...")
            # Load .env file
            from dotenv import load_dotenv
            load_dotenv(PROJECT_ROOT / '.env')
            # Clear cloud vars
            os.environ.pop('GCP_PROJECT', None)
            os.environ.pop('FUNCTION_NAME', None)
            os.environ.pop('K_SERVICE', None)
        
        # Reset Firebase Admin
        import firebase_admin
        if firebase_admin._apps:
            print("  Resetting Firebase Admin...")
            firebase_admin._apps.clear()
        
        # Test initialization
        from web.firebase_init import initialize_firebase_admin, is_cloud_environment
        
        print(f"\n  Is cloud environment: {is_cloud_environment()}")
        print(f"  GOOGLE_APPLICATION_CREDENTIALS: {os.environ.get('GOOGLE_APPLICATION_CREDENTIALS', 'Not set')}")
        
        project_id = os.environ.get('GCP_PROJECT') or os.environ.get('PROJECT_ID')
        result = initialize_firebase_admin(project_id=project_id, project_root=PROJECT_ROOT)
        
        if result:
            print("\n✅ Firebase Admin initialized successfully!")
            
            # Check if GOOGLE_APPLICATION_CREDENTIALS was handled correctly
            if args.cloud and args.creds:
                if 'GOOGLE_APPLICATION_CREDENTIALS' not in os.environ:
                    print("✅ GOOGLE_APPLICATION_CREDENTIALS was correctly unset in cloud environment")
                else:
                    print(f"⚠️  GOOGLE_APPLICATION_CREDENTIALS still set: {os.environ.get('GOOGLE_APPLICATION_CREDENTIALS')}")
            
            # Test Firestore connection
            try:
                from firebase_admin import firestore
                db = firestore.client()
                print("✅ Firestore client obtained")
                
                # Try a simple query (only if not in cloud simulation)
                if not args.cloud or os.environ.get('GOOGLE_APPLICATION_CREDENTIALS'):
                    users_ref = db.collection('users').limit(1)
                    docs = list(users_ref.stream())
                    print(f"✅ Firestore query successful (tested connection)")
            except Exception as e:
                if args.cloud and not args.creds:
                    print(f"⚠️  Firestore query failed (expected in cloud simulation without real credentials): {e}")
                else:
                    print(f"❌ Firestore query failed: {e}")
                    raise
            
            return 0
        else:
            print("\n❌ Firebase Admin initialization failed!")
            return 1
            
    except Exception as e:
        print(f"\n❌ Error: {e}")
        if args.debug:
            import traceback
            traceback.print_exc()
        return 1
    finally:
        # Restore original environment
        for var, value in original_env.items():
            if value is None:
                os.environ.pop(var, None)
            else:
                os.environ[var] = value


if __name__ == '__main__':
    sys.exit(main())
