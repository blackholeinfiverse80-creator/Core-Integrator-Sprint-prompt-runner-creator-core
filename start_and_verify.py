"""
BHIV Services Startup & Verification
===================================
Starts all services and verifies connectivity.
"""

import subprocess
import time
import sys
import os
from pathlib import Path


def start_service(name: str, command: list, cwd: str = None, wait_time: int = 3):
    """Start a service and wait for it to initialize"""
    
    print(f"🚀 Starting {name}...")
    
    try:
        if cwd and not os.path.exists(cwd):
            print(f"❌ Directory not found: {cwd}")
            return None
        
        # Start process in new window (Windows) or background (Linux/Mac)
        if sys.platform == "win32":
            process = subprocess.Popen(
                command,
                cwd=cwd,
                creationflags=subprocess.CREATE_NEW_CONSOLE
            )
        else:
            process = subprocess.Popen(
                command,
                cwd=cwd,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL
            )
        
        print(f"   ✅ {name} started (PID: {process.pid})")
        
        # Wait for service to initialize
        time.sleep(wait_time)
        
        return process
        
    except Exception as e:
        print(f"❌ Failed to start {name}: {str(e)}")
        return None


def main():
    """Start all BHIV services and verify connectivity"""
    
    print("🌟 BHIV Integration Startup & Verification")
    print("=" * 50)
    
    base_path = Path(__file__).parent
    processes = []
    
    # Service 1: Prompt Runner
    print("\n📡 Starting Prompt Runner (Port 8003)...")
    prompt_runner_path = base_path / "prompt-runner01"
    if prompt_runner_path.exists():
        process = start_service(
            "Prompt Runner",
            [sys.executable, "run_server.py", "8003"],
            str(prompt_runner_path),
            5  # Extra time for Groq initialization
        )
        if process:
            processes.append(("Prompt Runner", process))
    else:
        print("❌ Prompt Runner directory not found")
    
    # Service 2: Creator Core
    print("\n🔧 Starting Creator Core (Port 8000)...")
    creator_core_path = base_path / "creator-core" / "Core-Integrator-Sprint-1.1"
    if creator_core_path.exists():
        process = start_service(
            "Creator Core",
            [sys.executable, "main.py"],
            str(creator_core_path),
            4
        )
        if process:
            processes.append(("Creator Core", process))
    else:
        print("❌ Creator Core directory not found")
    
    # Service 3: BHIV Core
    print("\n⚙️  Starting BHIV Core (Port 8001)...")
    process = start_service(
        "BHIV Core",
        [sys.executable, "-m", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8001"],
        str(creator_core_path),
        4
    )
    if process:
        processes.append(("BHIV Core", process))
    
    # Service 4: Simple Orchestrator
    print("\n🎯 Starting Simple Orchestrator (Port 8004)...")
    process = start_service(
        "Simple Orchestrator",
        [sys.executable, "simple_orchestrator.py"],
        str(base_path),
        3
    )
    if process:
        processes.append(("Simple Orchestrator", process))
    
    # Service 5: Bucket (Optional)
    print("\n🗄️  Starting Bucket (Port 8005)...")
    process = start_service(
        "Bucket",
        [sys.executable, "bhiv_bucket.py"],
        str(base_path),
        3
    )
    if process:
        processes.append(("Bucket", process))
    
    print(f"\n✅ Started {len(processes)} services!")
    
    # Wait a bit more for all services to fully initialize
    print("\n⏳ Waiting for services to fully initialize...")
    time.sleep(5)
    
    # Run connectivity check
    print("\n🔍 Running connectivity verification...")
    try:
        result = subprocess.run([sys.executable, "check_connectivity.py"], 
                              capture_output=True, text=True, timeout=60)
        
        print(result.stdout)
        
        if result.returncode == 0:
            print("\n🎉 ALL SYSTEMS VERIFIED AND WORKING!")
            print("\n🚀 Ready to use:")
            print("   curl -X POST http://localhost:8004/execute \\")
            print("     -H \"Content-Type: application/json\" \\")
            print("     -d '{\"prompt\": \"Design a building for Mumbai\"}'")
        else:
            print("\n⚠️  Some issues detected. Check the connectivity report.")
            
    except Exception as e:
        print(f"\n❌ Connectivity check failed: {str(e)}")
    
    # Keep services running
    try:
        print(f"\n⏳ Services running. Press Ctrl+C to stop all...")
        while True:
            time.sleep(1)
            # Check if any process died
            for name, process in processes:
                if process.poll() is not None:
                    print(f"⚠️  {name} stopped unexpectedly")
                    
    except KeyboardInterrupt:
        print(f"\n🛑 Stopping all services...")
        for name, process in processes:
            try:
                process.terminate()
                print(f"   Stopped {name}")
            except:
                pass
        print("✅ All services stopped")


if __name__ == "__main__":
    main()