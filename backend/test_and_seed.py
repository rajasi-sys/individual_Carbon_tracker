"""
EcoQuest Database Seeder & End-to-End API Tester
------------------------------------------------
Seeds demo users into the SQLite database and executes
HTTP requests against the running FastAPI application.
"""

import sys
import time
import requests
from passlib.context import CryptContext

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")

# Import SQLAlchemy setup and security helpers
from app.database import SessionLocal, engine, Base
from app.models import UserModel
from app.security import get_password_hash, pwd_context

API_BASE_URL = "http://127.0.0.1:8000"


def seed_demo_users():
    print("🌱 Seeding Demo Users into SQLite database...")
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    
    demo_users_data = [
        {"name": "Aarohi", "email": "aarohi@demo.com", "city": "Mumbai", "xp": 2400, "stage": 5, "level": 5, "streak": 12},
        {"name": "Ishwari", "email": "ishwari@demo.com", "city": "Delhi", "xp": 1500, "stage": 4, "level": 4, "streak": 8},
        {"name": "Samrudhi", "email": "samrudhi@demo.com", "city": "London", "xp": 800, "stage": 3, "level": 2, "streak": 5},
        {"name": "Rajasi", "email": "rajasi@demo.com", "city": "Mumbai", "xp": 300, "stage": 2, "level": 1, "streak": 3},
        {"name": "Demo User", "email": "demo@demo.com", "city": "New York", "xp": 100, "stage": 1, "level": 1, "streak": 1},
    ]

    for data in demo_users_data:
        existing = db.query(UserModel).filter(UserModel.email == data["email"]).first()
        if not existing:
            user = UserModel(
                email=data["email"],
                hashed_password=get_password_hash("password123"),
                name=data["name"],
                city=data["city"],
                eco_points=data["xp"],
                tree_stage=data["stage"],
                level=data["level"],
                streak_count=data["streak"]
            )
            db.add(user)
    
    db.commit()
    db.close()
    print("✅ Demo Users seeded successfully.\n")


def run_tests():
    print("🚀 Starting End-to-End API Tests...")
    
    test_user_email = f"test_{int(time.time())}@ecoquest.com"
    test_user_pwd = "TestPassword123!"
    
    results = []
    
    def log_result(test_name: str, passed: bool, info: str = ""):
        status = "✅ PASS" if passed else "❌ FAIL"
        results.append(f"{status} | {test_name} {info}")
        print(results[-1])

    try:
        # Test 1: Register
        res1 = requests.post(f"{API_BASE_URL}/api/v1/auth/register", json={
            "email": test_user_email,
            "password": test_user_pwd
        })
        log_result("Test 1: POST /api/v1/auth/register", res1.status_code in (200, 201))
        
        # Test 2: Login
        res2 = requests.post(f"{API_BASE_URL}/api/v1/auth/login", data={
            "username": test_user_email,
            "password": test_user_pwd
        })
        passed_login = res2.status_code == 200 and "access_token" in res2.json()
        log_result("Test 2: POST /api/v1/auth/login", passed_login)
        
        token = res2.json().get("access_token", "") if passed_login else ""
        headers = {"Authorization": f"Bearer {token}"}
        
        # Test 3: Profile Update
        res3 = requests.post(f"{API_BASE_URL}/api/v1/user/profile", headers=headers, json={
            "name": "API Tester",
            "age": 20,
            "gender": "Not Specified",
            "city": "Mumbai",
            "household_size": 2
        })
        log_result("Test 3: POST /api/v1/user/profile", res3.status_code == 200)

        # Test 4: Lock Daily Emissions
        res4 = requests.post(f"{API_BASE_URL}/api/v1/emissions/lock-daily", headers=headers, json={
            "electricity_kwh": 10.0,
            "petrol_car_km": 20.0
        })
        log_result("Test 4: POST /api/v1/emissions/lock-daily", res4.status_code == 200)

        # Test 5: Zero Emission
        res5 = requests.post(f"{API_BASE_URL}/api/v1/emissions/lock-daily", headers=headers, json={
            "is_zero_emission": True
        })
        log_result("Test 5: POST /api/v1/emissions/lock-daily (Zero Toggle)", res5.status_code == 200)

        # Test 6: Leaderboard
        res6 = requests.get(f"{API_BASE_URL}/api/v1/leaderboard")
        passed_lb = res6.status_code == 200 and len(res6.json()) > 0
        log_result("Test 6: GET /api/v1/leaderboard", passed_lb)

        # Test 7: User Stats
        res7 = requests.get(f"{API_BASE_URL}/api/v1/user/stats", headers=headers)
        passed_stats = res7.status_code == 200 and "xp" in res7.json()
        log_result("Test 7: GET /api/v1/user/stats", passed_stats)

    except requests.exceptions.ConnectionError:
        print("\n❌ CRITICAL: Could not connect to API at", API_BASE_URL)
        print("Please ensure the FastAPI server is running (`uvicorn app.main:app --reload`).")
        sys.exit(1)

    print("\n" + "="*50)
    print("📊 TEST SUMMARY")
    print("="*50)
    for r in results:
        print(r)
    print("="*50)


if __name__ == "__main__":
    seed_demo_users()
    run_tests()
