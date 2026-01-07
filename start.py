#!/usr/bin/env python3
"""
Start script for MOJO AEO GEO CHECKER
Runs both the backend and frontend servers
"""

import subprocess
import sys
import time
import os
from threading import Thread

def run_backend():
    """Run the FastAPI backend server"""
    print("🚀 Starting Backend Server on http://localhost:8000")
    subprocess.run([sys.executable, "server.py"])

def run_frontend():
    """Run the Vite frontend development server"""
    print("🎨 Starting Frontend Server...")
    time.sleep(2)  # Wait for backend to start
    os.chdir("ui")
    subprocess.run(["npm", "run", "dev"])

if __name__ == "__main__":
    print("=" * 60)
    print("MOJO AEO GEO CHECKER")
    print("=" * 60)
    print()
    
    # Check if node_modules exists
    if not os.path.exists("ui/node_modules"):
        print("⚠️  node_modules not found. Installing dependencies...")
        os.chdir("ui")
        subprocess.run(["npm", "install"])
        os.chdir("..")
    
    # Start backend in a separate thread
    backend_thread = Thread(target=run_backend, daemon=True)
    backend_thread.start()
    
    # Give backend time to start
    time.sleep(3)
    
    # Start frontend in main thread
    try:
        run_frontend()
    except KeyboardInterrupt:
        print("\n\n👋 Shutting down servers...")
        sys.exit(0)
