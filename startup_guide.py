"""
BHIV Services Startup Guide - Fixed Ports
=========================================
Starts all services on available ports to avoid conflicts.
"""

print("🚀 BHIV Integration Startup Guide")
print("=" * 40)

print("\n📋 Start services in this order:")

print("\n1️⃣  Prompt Runner (Port 8003)")
print("   Terminal 1:")
print("   cd prompt-runner01")
print("   python run_server.py 8003")

print("\n2️⃣  Creator Core (Port 8000)")  
print("   Terminal 2:")
print("   cd creator-core\\Core-Integrator-Sprint-1.1")
print("   python main.py")

print("\n3️⃣  BHIV Core (Port 8002) - Different port to avoid conflict")
print("   Terminal 3:")
print("   cd creator-core\\Core-Integrator-Sprint-1.1")
print("   python -m uvicorn main:app --host 0.0.0.0 --port 8002")

print("\n4️⃣  Simple Orchestrator (Port 8004)")
print("   Terminal 4:")
print("   cd C:\\Aman\\Core-Integrator-Sprint-1.1-")
print("   python simple_orchestrator.py")

print("\n5️⃣  Bucket (Port 8005) - Optional")
print("   Terminal 5:")
print("   cd C:\\Aman\\Core-Integrator-Sprint-1.1-")
print("   python bhiv_bucket.py")

print("\n✅ After all services are running:")
print("   python test_simple.py")

print("\n🧪 Test the integration:")
print('   curl -X POST http://localhost:8004/execute \\')
print('     -H "Content-Type: application/json" \\')
print('     -d \'{"prompt": "Design a building for Mumbai"}\'')

print("\n📊 Check connectivity:")
print("   python check_connectivity.py")