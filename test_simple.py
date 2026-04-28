"""
Simple Test - Just verify the orchestration works
"""

import requests
import json


def test_simple_orchestration():
    """Test the basic pipeline integration"""
    
    print("🧪 Testing Simple BHIV Orchestration")
    print("=" * 40)
    
    # Test prompt
    prompt = "Design a residential building for Mumbai"
    
    try:
        print(f"📝 Input: {prompt}")
        
        # Call simple orchestrator
        response = requests.post(
            "http://localhost:8006/execute",
            json={"prompt": prompt},
            timeout=60
        )
        
        if response.status_code == 200:
            result = response.json()
            
            print("✅ Pipeline executed!")
            print(f"📋 Instruction module: {result['instruction'].get('module')}")
            print(f"🔧 Blueprint type: {result['blueprint'].get('blueprint', {}).get('payload', {}).get('blueprint_type')}")
            print(f"🎯 Result status: {result['result'].get('status')}")
            
            return True
        else:
            print(f"❌ Failed: {response.status_code}")
            print(response.text)
            return False
            
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return False


if __name__ == "__main__":
    success = test_simple_orchestration()
    print(f"\n{'✅ SUCCESS' if success else '❌ FAILED'}")