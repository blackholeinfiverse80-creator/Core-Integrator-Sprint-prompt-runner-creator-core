"""
Simple Startup - Just run the orchestration
"""

import subprocess
import sys
import time
from pathlib import Path


def start_orchestration():
    """Start just the orchestration service"""
    
    print("🚀 Starting Simple BHIV Orchestration")
    print("=" * 40)
    
    # Assume other components are already running
    print("📋 Prerequisites:")
    print("   - Prompt Runner should be running on port 8003")
    print("   - Creator Core should be running on port 8000") 
    print("   - BHIV Core should be running on port 8001")
    print()
    
    print("🔧 Starting orchestrator on port 8004...")
    
    try:
        # Start the simple orchestrator
        subprocess.run([
            sys.executable, "simple_orchestrator.py"
        ])
    except KeyboardInterrupt:
        print("\n🛑 Orchestrator stopped")


if __name__ == "__main__":
    start_orchestration()