#!/usr/bin/env python3
"""
MUFG Financial Assistant API Startup Script
"""

import os
import sys
import subprocess
from pathlib import Path

def install_dependencies():
    """Install required dependencies"""
    print("📦 Installing dependencies...")
    
    try:
        subprocess.run([
            sys.executable, "-m", "pip", "install", "-r", "requirements.txt"
        ], check=True)
        print("✅ Dependencies installed successfully!")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to install dependencies: {e}")
        return False

def setup_environment():
    """Setup environment variables"""
    print("🔧 Setting up environment...")
    
    env_file = Path(".env")
    if not env_file.exists():
        print("Creating .env file...")
        env_content = """# Database Configuration
DATABASE_URL=sqlite:///./mufg_financial.db

# API Keys
OPENAI_API_KEY=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

# Application Settings
APP_NAME=MUFG Financial Assistant
APP_VERSION=1.0.0
DEBUG=True

# Vector Database Settings
VECTOR_DB_PATH=./vector_db
EMBEDDING_MODEL=all-MiniLM-L6-v2

# Chat Settings
MAX_CHAT_HISTORY=50
DEFAULT_SESSION_TIMEOUT=3600

# Stock Prediction Settings
MODEL_PATH=../Share_Prediction.h5
LOOKBACK_PERIOD=60
TRADING_DAYS_PER_YEAR=252
"""
        env_file.write_text(env_content)
        print("✅ .env file created")
    else:
        print("✅ .env file already exists")
    
    return True

def initialize_database():
    """Initialize the database"""
    print("🗄️  Initializing database...")
    
    try:
        from database import init_db
        init_db()
        print("✅ Database initialized successfully!")
        return True
    except Exception as e:
        print(f"❌ Failed to initialize database: {e}")
        return False

def run_tests():
    """Run API tests"""
    print("🧪 Running tests...")
    
    try:
        result = subprocess.run([sys.executable, "test_api.py"], 
                              capture_output=True, text=True)
        
        print(result.stdout)
        if result.stderr:
            print("Warnings/Errors:")
            print(result.stderr)
        
        return result.returncode == 0
    except Exception as e:
        print(f"❌ Failed to run tests: {e}")
        return False

def start_server(port=8000, reload=True):
    """Start the FastAPI server"""
    print(f"🚀 Starting MUFG Financial Assistant API on port {port}...")
    
    try:
        cmd = [
            "uvicorn", "main:app", 
            "--host", "0.0.0.0", 
            "--port", str(port)
        ]
        
        if reload:
            cmd.append("--reload")
        
        print(f"Command: {' '.join(cmd)}")
        print("\n" + "="*60)
        print("🌟 MUFG Financial Assistant API")
        print("="*60)
        print(f"📡 Server: http://localhost:{port}")
        print(f"📚 Docs: http://localhost:{port}/docs")
        print(f"🔍 Health: http://localhost:{port}/api/health")
        print("="*60)
        print("Press Ctrl+C to stop the server")
        print("="*60 + "\n")
        
        subprocess.run(cmd)
        
    except KeyboardInterrupt:
        print("\n👋 Server stopped by user")
    except Exception as e:
        print(f"❌ Failed to start server: {e}")

def main():
    """Main startup function"""
    print("🚀 MUFG Financial Assistant API Startup")
    print("=" * 50)
    
    # Check if we're in the right directory
    if not Path("main.py").exists():
        print("❌ main.py not found. Make sure you're in the correct directory.")
        return False
    
    # Setup steps
    steps = [
        ("Install Dependencies", install_dependencies),
        ("Setup Environment", setup_environment),
        ("Initialize Database", initialize_database),
    ]
    
    for step_name, step_func in steps:
        print(f"\n📋 {step_name}...")
        if not step_func():
            print(f"❌ {step_name} failed. Stopping.")
            return False
    
    print("\n✅ Setup completed successfully!")
    
    # Ask user what to do next
    while True:
        print("\n🔧 What would you like to do?")
        print("1. Run tests")
        print("2. Start server")
        print("3. Start server with auto-reload (development)")
        print("4. Exit")
        
        choice = input("Enter your choice (1-4): ").strip()
        
        if choice == "1":
            run_tests()
        elif choice == "2":
            start_server(reload=False)
            break
        elif choice == "3":
            start_server(reload=True)
            break
        elif choice == "4":
            print("👋 Goodbye!")
            break
        else:
            print("❌ Invalid choice. Please try again.")
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
