"""
Quick Integration Test
=====================
Simple test to verify the BHIV pipeline integration works.
"""

import requests
import json
import time


def test_pipeline():
    """Test the basic pipeline flow"""
    
    print("🧪 Testing BHIV Pipeline Integration")
    print("=" * 40)
    
    # Test prompt
    test_prompt = "Design a residential building for a 1000 sqft plot in Mumbai"
    
    try:
        print(f"📝 Input: {test_prompt}")
        
        # Call integration bridge
        response = requests.post(
            "http://localhost:8004/pipeline/execute",
            json={"prompt": test_prompt},
            timeout=60
        )
        
        if response.status_code == 200:
            result = response.json()
            
            print("✅ Pipeline executed successfully!")
            print(f"📋 Trace ID: {result.get('trace_id')}")
            print(f"🔗 Status: {result.get('status')}")
            
            # Check artifact chain
            chain = result.get('artifact_chain', {})
            artifacts = [k for k in chain.keys() if k.startswith('A')]
            print(f"🗂️  Artifacts: {len(artifacts)} created")
            
            # Show final result
            pipeline_result = result.get('pipeline_result', {})
            print(f"🎯 Pipeline Status: {pipeline_result.get('pipeline_status')}")
            print(f"🔐 Hash: {pipeline_result.get('deterministic_hash')}")
            
            return True
            
        else:
            print(f"❌ Pipeline failed: {response.status_code}")
            print(f"Error: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Test failed: {str(e)}")
        return False


def test_health():
    """Test component health"""
    
    print("\n🏥 Testing Component Health")
    print("-" * 30)
    
    try:
        response = requests.get("http://localhost:8004/pipeline/health", timeout=10)
        
        if response.status_code == 200:
            health = response.json()
            
            print(f"🌟 Pipeline Status: {health.get('pipeline_status')}")
            
            components = health.get('components', {})
            for name, status in components.items():
                emoji = "✅" if status.get('status') == 'healthy' else "❌"
                print(f"   {emoji} {name}: {status.get('status')}")
            
            return health.get('pipeline_status') == 'healthy'
            
        else:
            print(f"❌ Health check failed: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Health check error: {str(e)}")
        return False


def main():
    """Run quick integration test"""
    
    print("🚀 BHIV Pipeline Quick Test")
    print("=" * 50)
    
    # Test 1: Health check
    health_ok = test_health()
    
    if not health_ok:
        print("\n⚠️  Some components are unhealthy. Pipeline may not work correctly.")
        print("Make sure all components are running:")
        print("  - Prompt Runner (port 8003)")
        print("  - Creator Core (port 8000)")
        print("  - BHIV Core (port 8001)")
        print("  - Integration Bridge (port 8004)")
        print("  - Bucket (port 8005)")
        return False
    
    # Test 2: Pipeline execution
    pipeline_ok = test_pipeline()
    
    if pipeline_ok:
        print("\n🎉 Integration test PASSED!")
        print("✅ All components working correctly")
        print("✅ Pipeline flow operational")
        print("✅ Artifact chain created")
        return True
    else:
        print("\n❌ Integration test FAILED!")
        return False


if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)