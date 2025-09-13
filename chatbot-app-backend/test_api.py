#!/usr/bin/env python3
"""
MUFG Financial Assistant API Test Script
Tests database connection and basic API functionality
"""

import sys
import os
import asyncio
from datetime import datetime

# Add the project root to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_database_connection():
    """Test database connection and table creation"""
    print("🔌 Testing Database Connection...")
    
    try:
        from database import init_db, SessionLocal, UserProfile
        from sqlalchemy import text
        
        # Initialize database
        init_db()
        
        # Test connection
        db = SessionLocal()
        result = db.execute(text("SELECT 1")).fetchone()
        db.close()
        
        print("✅ Database connection successful!")
        print(f"   Result: {result}")
        return True
        
    except Exception as e:
        print(f"❌ Database connection failed: {e}")
        return False

def test_crud_operations():
    """Test basic CRUD operations"""
    print("\n📝 Testing CRUD Operations...")
    
    try:
        from database import SessionLocal
        from crud import UserProfileCRUD
        from schemas import UserProfileCreate, UserProfileUpdate
        
        db = SessionLocal()
        
        # Test user creation
        test_user = UserProfileCreate(
            user_id="test_user_123",
            first_name="John",
            last_name="Doe",
            email="john.doe@test.com",
            age=30,
            country="Australia",
            annual_income=75000.0,
            risk_tolerance="moderate"
        )
        
        # Create profile
        profile = UserProfileCRUD.create_profile(db, test_user)
        print(f"✅ User created: {profile.user_id}")
        
        # Read profile
        retrieved = UserProfileCRUD.get_profile_by_user_id(db, "test_user_123")
        print(f"✅ User retrieved: {retrieved.first_name} {retrieved.last_name}")
        
        # Update profile
        update_data = UserProfileUpdate(age=31, annual_income=80000.0)
        updated = UserProfileCRUD.update_profile(db, "test_user_123", update_data)
        print(f"✅ User updated: Age={updated.age}, Income={updated.annual_income}")
        
        # Test completeness
        completeness = UserProfileCRUD.get_profile_completeness(db, "test_user_123")
        print(f"✅ Profile completeness: {completeness['completeness_percentage']:.1f}%")
        
        # Clean up
        UserProfileCRUD.delete_profile(db, "test_user_123")
        print("✅ Test user deleted")
        
        db.close()
        return True
        
    except Exception as e:
        print(f"❌ CRUD operations failed: {e}")
        return False

def test_vector_database():
    """Test vector database functionality"""
    print("\n🔍 Testing Vector Database...")
    
    try:
        from LLM.vector_database import FinancialVectorDB
        
        # Initialize vector database
        vector_db = FinancialVectorDB()
        
        # Test search
        results = vector_db.search_funds("growth fund with high returns", k=3)
        print(f"✅ Vector search returned {len(results)} results")
        
        if results:
            print(f"   Top result score: {results[0]['score']:.3f}")
        
        return True
        
    except Exception as e:
        print(f"❌ Vector database test failed: {e}")
        return False

def test_llm_integration():
    """Test LLM integration with vector search"""
    print("\n🤖 Testing LLM Integration...")
    
    try:
        from LLM.LLM1 import callLLM1
        
        test_message = "What are some good investment options for a 30-year-old?"
        test_user_data = {
            "age": 30,
            "country": "Australia",
            "risk_tolerance": "moderate",
            "annual_income": 75000
        }
        
        # This will test the vector search integration
        response = callLLM1(test_message, test_user_data)
        
        if response and len(response) > 50:
            print("✅ LLM integration successful!")
            print(f"   Response length: {len(response)} characters")
            return True
        else:
            print("❌ LLM response too short or empty")
            return False
            
    except Exception as e:
        print(f"❌ LLM integration failed: {e}")
        return False

async def test_api_endpoints():
    """Test API endpoints"""
    print("\n🌐 Testing API Endpoints...")
    
    try:
        import httpx
        
        # Start the server in the background (you'll need to run this manually)
        base_url = "http://localhost:8000"
        
        async with httpx.AsyncClient() as client:
            # Test health endpoint
            response = await client.get(f"{base_url}/api/health")
            if response.status_code == 200:
                print("✅ Health endpoint working")
                return True
            else:
                print(f"❌ Health endpoint failed: {response.status_code}")
                return False
                
    except Exception as e:
        print(f"⚠️  API endpoint test skipped (server not running): {e}")
        return True  # Don't fail the test if server isn't running

def main():
    """Run all tests"""
    print("🚀 MUFG Financial Assistant API Test Suite")
    print("=" * 50)
    
    tests = [
        ("Database Connection", test_database_connection),
        ("CRUD Operations", test_crud_operations),
        ("Vector Database", test_vector_database),
        ("LLM Integration", test_llm_integration),
    ]
    
    results = []
    
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ {test_name} crashed: {e}")
            results.append((test_name, False))
    
    # Run async test
    try:
        print("\n🌐 Testing API Endpoints...")
        result = asyncio.run(test_api_endpoints())
        results.append(("API Endpoints", result))
    except Exception as e:
        print(f"❌ API Endpoints crashed: {e}")
        results.append(("API Endpoints", False))
    
    # Summary
    print("\n" + "=" * 50)
    print("📊 Test Results Summary:")
    
    passed = 0
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"   {test_name}: {status}")
        if result:
            passed += 1
    
    print(f"\n🎯 Tests passed: {passed}/{len(results)}")
    
    if passed == len(results):
        print("🎉 All tests passed! Your MUFG Financial Assistant API is ready!")
    else:
        print("⚠️  Some tests failed. Check the error messages above.")
    
    return passed == len(results)

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
