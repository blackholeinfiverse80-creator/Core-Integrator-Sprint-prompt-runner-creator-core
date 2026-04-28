"""
BHIV Pipeline Startup Script
===========================
Launches all components of the integrated pipeline in correct order.

Components:
1. Prompt Runner (Port 8003)
2. Creator Core (Port 8000) 
3. BHIV Core (Port 8001)
4. Integration Bridge (Port 8004)
5. Bucket (Port 8005)
"""

import subprocess
import time
import sys
import os
from pathlib import Path


def start_component(name: str, command: list, cwd: str = None, port: int = None):
    """Start a pipeline component"""
    print(f"🚀 Starting {name}...")
    
    try:
        if cwd and not os.path.exists(cwd):
            print(f"❌ Directory not found: {cwd}")
            return None
            
        process = subprocess.Popen(
            command,
            cwd=cwd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            creationflags=subprocess.CREATE_NEW_CONSOLE if sys.platform == "win32" else 0
        )
        
        if port:
            print(f"   Port: {port}")
        print(f"   PID: {process.pid}")
        
        # Give component time to start
        time.sleep(3)
        
        return process
        
    except Exception as e:
        print(f"❌ Failed to start {name}: {str(e)}")
        return None


def main():
    """Start all BHIV pipeline components"""
    
    print("🌟 BHIV Full Integration Pipeline Startup")
    print("=" * 50)
    
    base_path = Path(__file__).parent
    processes = []
    
    # Component 1: Prompt Runner
    prompt_runner_path = base_path / "prompt-runner01"
    if prompt_runner_path.exists():
        process = start_component(
            "Prompt Runner",
            [sys.executable, "run_server.py", "8003"],
            str(prompt_runner_path),
            8003
        )
        if process:
            processes.append(("Prompt Runner", process))
    else:
        print("❌ Prompt Runner directory not found")
    
    # Component 2: Creator Core
    creator_core_path = base_path / "creator-core" / "Core-Integrator-Sprint-1.1"
    if creator_core_path.exists():
        process = start_component(
            "Creator Core",
            [sys.executable, "main.py"],
            str(creator_core_path),
            8000
        )
        if process:
            processes.append(("Creator Core", process))
    else:
        print("❌ Creator Core directory not found")
    
    # Component 3: BHIV Core (using same as Creator Core for now)
    process = start_component(
        "BHIV Core",
        [sys.executable, "-m", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8001"],
        str(creator_core_path),
        8001
    )
    if process:
        processes.append(("BHIV Core", process))
    
    # Component 4: Integration Bridge
    process = start_component(
        "Integration Bridge",
        [sys.executable, "integration_bridge.py"],
        str(base_path),
        8004
    )
    if process:
        processes.append(("Integration Bridge", process))
    
    # Component 5: Bucket
    process = start_component(
        "BHIV Bucket",
        [sys.executable, "bhiv_bucket.py"],
        str(base_path),
        8005
    )
    if process:
        processes.append(("BHIV Bucket", process))
    
    print("\n✅ All components started!")
    print("\n📋 Component Status:")
    for name, process in processes:
        status = "Running" if process.poll() is None else "Stopped"
        print(f"   {name}: {status} (PID: {process.pid})")
    
    print("\n🔗 Integration Endpoints:")
    print("   Pipeline Execute: http://localhost:8004/pipeline/execute")
    print("   Pipeline Health:  http://localhost:8004/pipeline/health")
    print("   Bucket Stats:     http://localhost:8005/bucket/stats")
    
    print("\n🧪 Test the pipeline:")
    print('   curl -X POST http://localhost:8004/pipeline/execute \\')
    print('     -H "Content-Type: application/json" \\')
    print('     -d \'{"prompt": "Design a residential building for Mumbai"}\'')
    
    print("\n📊 Run validation:")
    print("   python validate_full_integration.py")
    
    print(f"\n🎯 Total processes started: {len(processes)}")
    
    # Keep script running
    try:
        print("\n⏳ Press Ctrl+C to stop all components...")
        while True:
            time.sleep(1)
            # Check if any process died
            for name, process in processes:
                if process.poll() is not None:
                    print(f"⚠️  {name} stopped unexpectedly")
    except KeyboardInterrupt:
        print("\n🛑 Stopping all components...")
        for name, process in processes:
            try:
                process.terminate()
                print(f"   Stopped {name}")
            except:
                pass
        print("✅ All components stopped")


if __name__ == "__main__":
    main()