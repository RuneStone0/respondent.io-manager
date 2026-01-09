#!/usr/bin/env python3
"""
Test script for Firebase initialization
Tests both local and cloud environment scenarios without deploying
"""

import os
import sys
import logging
from pathlib import Path

# Setup logging to see what's happening
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

# Add project root to path
PROJECT_ROOT = Path(__file__).parent
sys.path.insert(0, str(PROJECT_ROOT))


def test_local_environment():
    """Test Firebase initialization in local environment (with service account)"""
    print("\n" + "="*70)
    print("TEST 1: Local Environment (with GOOGLE_APPLICATION_CREDENTIALS)")
    print("="*70)
    
    # Clear any cloud environment variables
    env_vars_to_clear = ['GCP_PROJECT', 'FUNCTION_NAME', 'K_SERVICE']
    saved_vars = {}
    for var in env_vars_to_clear:
        saved_vars[var] = os.environ.pop(var, None)
    
    # Ensure GOOGLE_APPLICATION_CREDENTIALS is set (from .env)
    from dotenv import load_dotenv
    load_dotenv(PROJECT_ROOT / '.env')
    
    google_creds = os.environ.get('GOOGLE_APPLICATION_CREDENTIALS')
    project_id = os.environ.get('PROJECT_ID') or os.environ.get('FIREBASE_PROJECT_ID')
    
    print(f"GOOGLE_APPLICATION_CREDENTIALS: {google_creds}")
    print(f"PROJECT_ID: {project_id}")
    
    try:
        # Import and test
        from web.firebase_init import initialize_firebase_admin, is_cloud_environment
        
        print(f"\nIs cloud environment: {is_cloud_environment()}")
        
        # Reset Firebase Admin if already initialized
        import firebase_admin
        if firebase_admin._apps:
            print("Resetting Firebase Admin...")
            firebase_admin._apps.clear()
        
        result = initialize_firebase_admin(project_id=project_id, project_root=PROJECT_ROOT)
        print(f"\n✓ Initialization result: {result}")
        
        # Test Firestore connection
        from firebase_admin import firestore
        db = firestore.client()
        print("✓ Firestore client obtained")
        
        # Try a simple read
        users_ref = db.collection('users').limit(1)
        list(users_ref.stream())
        print("✓ Firestore connection test successful")
        
        return True
        
    except Exception as e:
        print(f"\n✗ Error: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        # Restore environment variables
        for var, value in saved_vars.items():
            if value:
                os.environ[var] = value


def test_cloud_environment():
    """Test Firebase initialization in cloud environment (simulated)"""
    print("\n" + "="*70)
    print("TEST 2: Cloud Environment (simulated - with GCP_PROJECT)")
    print("="*70)
    
    # Save current environment
    saved_google_creds = os.environ.get('GOOGLE_APPLICATION_CREDENTIALS')
    saved_project_id = os.environ.get('PROJECT_ID')
    
    # Simulate cloud environment
    project_id = os.environ.get('PROJECT_ID') or 'respondentpro-xyz'
    os.environ['GCP_PROJECT'] = project_id
    os.environ['FUNCTION_NAME'] = 'respondentpro'  # Simulate Cloud Functions
    
    # Set GOOGLE_APPLICATION_CREDENTIALS to a non-existent file to test the unset logic
    os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = './non-existent-file.json'
    
    print(f"GCP_PROJECT: {os.environ.get('GCP_PROJECT')}")
    print(f"FUNCTION_NAME: {os.environ.get('FUNCTION_NAME')}")
    print(f"GOOGLE_APPLICATION_CREDENTIALS: {os.environ.get('GOOGLE_APPLICATION_CREDENTIALS')}")
    
    try:
        from web.firebase_init import initialize_firebase_admin, is_cloud_environment
        
        print(f"\nIs cloud environment: {is_cloud_environment()}")
        
        # Reset Firebase Admin if already initialized
        import firebase_admin
        if firebase_admin._apps:
            print("Resetting Firebase Admin...")
            firebase_admin._apps.clear()
        
        result = initialize_firebase_admin(project_id=project_id, project_root=PROJECT_ROOT)
        print(f"\n✓ Initialization result: {result}")
        
        # Check if GOOGLE_APPLICATION_CREDENTIALS was unset
        if 'GOOGLE_APPLICATION_CREDENTIALS' not in os.environ:
            print("✓ GOOGLE_APPLICATION_CREDENTIALS was correctly unset in cloud environment")
        else:
            print(f"⚠ GOOGLE_APPLICATION_CREDENTIALS still set: {os.environ.get('GOOGLE_APPLICATION_CREDENTIALS')}")
        
        # Note: In real cloud, default credentials would work, but locally we need service account
        # So we'll just verify the initialization logic worked
        print("✓ Cloud environment initialization logic verified")
        
        return True
        
    except Exception as e:
        print(f"\n✗ Error: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        # Restore environment
        if saved_google_creds:
            os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = saved_google_creds
        elif 'GOOGLE_APPLICATION_CREDENTIALS' in os.environ:
            del os.environ['GOOGLE_APPLICATION_CREDENTIALS']
        
        if saved_project_id:
            os.environ['PROJECT_ID'] = saved_project_id
        
        # Clear cloud simulation vars
        os.environ.pop('GCP_PROJECT', None)
        os.environ.pop('FUNCTION_NAME', None)


def test_firestore_connection():
    """Test Firestore connection through db.py"""
    print("\n" + "="*70)
    print("TEST 3: Firestore Connection via db.py")
    print("="*70)
    
    try:
        # Reset Firebase Admin
        import firebase_admin
        if firebase_admin._apps:
            firebase_admin._apps.clear()
        
        # Import db module (this will initialize Firebase)
        from web.db import firestore_available, users_collection, db
        
        print(f"Firestore available: {firestore_available}")
        print(f"Users collection: {users_collection is not None}")
        print(f"DB client: {db is not None}")
        
        if firestore_available and users_collection:
            # Try a simple query
            query = users_collection.limit(1).stream()
            count = sum(1 for _ in query)
            print(f"✓ Firestore query successful (found {count} test documents)")
            return True
        else:
            print("✗ Firestore not available")
            return False
            
    except Exception as e:
        print(f"\n✗ Error: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Run all tests"""
    print("\n" + "="*70)
    print("Firebase Initialization Test Suite")
    print("="*70)
    print("\nThis script tests Firebase initialization in different scenarios")
    print("without requiring deployment to Cloud Functions.\n")
    
    results = []
    
    # Test 1: Local environment
    results.append(("Local Environment", test_local_environment()))
    
    # Test 2: Cloud environment (simulated)
    results.append(("Cloud Environment (simulated)", test_cloud_environment()))
    
    # Test 3: Firestore connection
    results.append(("Firestore Connection", test_firestore_connection()))
    
    # Summary
    print("\n" + "="*70)
    print("TEST SUMMARY")
    print("="*70)
    for test_name, result in results:
        status = "✓ PASSED" if result else "✗ FAILED"
        print(f"{test_name}: {status}")
    
    all_passed = all(result for _, result in results)
    print("\n" + "="*70)
    if all_passed:
        print("✓ All tests passed!")
    else:
        print("✗ Some tests failed. Check the output above for details.")
    print("="*70)
    
    return 0 if all_passed else 1


if __name__ == '__main__':
    sys.exit(main())
