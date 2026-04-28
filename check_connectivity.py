"""
BHIV Services Connectivity Checker
=================================
Verifies all services are running and can communicate.
"""

import requests
import json
import time
from typing import Dict, Any


class ConnectivityChecker:
    """Check connectivity of all BHIV services"""
    
    def __init__(self):
        self.services = {
            "Prompt Runner": "http://127.0.0.1:8003/health",
            "Creator Core": "http://127.0.0.1:8000/",
            "BHIV Core": "http://127.0.0.1:8001/",
            "Simple Orchestrator": "http://127.0.0.1:8004/health",
            "Bucket": "http://127.0.0.1:8005/bucket/stats"
        }
    
    def check_all_services(self) -> Dict[str, Any]:
        """Check all services are running"""
        
        print("🔍 BHIV Services Connectivity Check")
        print("=" * 50)
        
        results = {}
        all_healthy = True
        
        for name, url in self.services.items():
            print(f"\n📡 Checking {name}...")
            
            try:
                response = requests.get(url, timeout=5)
                
                if response.status_code == 200:
                    print(f"   ✅ {name}: ONLINE (Status: {response.status_code})")
                    results[name] = {"status": "online", "code": response.status_code}
                else:
                    print(f"   ⚠️  {name}: RESPONDING but status {response.status_code}")
                    results[name] = {"status": "warning", "code": response.status_code}
                    
            except requests.exceptions.ConnectionError:
                print(f"   ❌ {name}: OFFLINE (Connection refused)")
                results[name] = {"status": "offline", "error": "Connection refused"}
                all_healthy = False
                
            except requests.exceptions.Timeout:
                print(f"   ❌ {name}: TIMEOUT")
                results[name] = {"status": "timeout", "error": "Request timeout"}
                all_healthy = False
                
            except Exception as e:
                print(f"   ❌ {name}: ERROR - {str(e)}")
                results[name] = {"status": "error", "error": str(e)}
                all_healthy = False
        
        return {
            "all_healthy": all_healthy,
            "services": results,
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
        }
    
    def test_integration_flow(self) -> bool:
        """Test the complete integration flow"""
        
        print(f"\n🔄 Testing Integration Flow")
        print("-" * 30)
        
        test_prompt = "Design a residential building for Mumbai"
        
        try:
            print(f"📝 Input: {test_prompt}")
            
            # Test simple orchestrator
            response = requests.post(
                "http://127.0.0.1:8004/execute",
                json={"prompt": test_prompt},
                timeout=60
            )
            
            if response.status_code == 200:
                result = response.json()
                
                print("✅ Integration flow SUCCESS!")
                print(f"   📋 Instruction: {result.get('instruction', {}).get('module', 'N/A')}")
                print(f"   🔧 Blueprint: {result.get('blueprint', {}).get('status', 'N/A')}")
                print(f"   🎯 Result: {result.get('result', {}).get('status', 'N/A')}")
                
                return True
            else:
                print(f"❌ Integration flow FAILED: {response.status_code}")
                print(f"   Error: {response.text}")
                return False
                
        except Exception as e:
            print(f"❌ Integration flow ERROR: {str(e)}")
            return False
    
    def test_individual_components(self) -> Dict[str, bool]:
        """Test each component individually"""
        
        print(f"\n🧪 Testing Individual Components")
        print("-" * 35)
        
        tests = {}
        
        # Test 1: Prompt Runner
        try:
            response = requests.post(
                "http://127.0.0.1:8003/generate",
                json={"prompt": "Test prompt"},
                timeout=10
            )
            tests["Prompt Runner"] = response.status_code == 200
            print(f"   {'✅' if tests['Prompt Runner'] else '❌'} Prompt Runner: {'PASS' if tests['Prompt Runner'] else 'FAIL'}")
        except:
            tests["Prompt Runner"] = False
            print(f"   ❌ Prompt Runner: FAIL")
        
        # Test 2: Creator Core
        try:
            test_instruction = {
                "prompt": "Test",
                "module": "creator", 
                "intent": "generate",
                "topic": "test",
                "tasks": ["test"],
                "output_format": "guide",
                "product_context": "creator_core"
            }
            response = requests.post(
                "http://127.0.0.1:8000/creator-core/generate-blueprint",
                json=test_instruction,
                timeout=10
            )
            tests["Creator Core"] = response.status_code == 200
            print(f"   {'✅' if tests['Creator Core'] else '❌'} Creator Core: {'PASS' if tests['Creator Core'] else 'FAIL'}")
        except:
            tests["Creator Core"] = False
            print(f"   ❌ Creator Core: FAIL")
        
        # Test 3: BHIV Core
        try:
            test_core_request = {
                "module": "creator",
                "intent": "generate", 
                "user_id": "test",
                "data": {"test": "data"}
            }
            response = requests.post(
                "http://127.0.0.1:8001/core",
                json=test_core_request,
                timeout=10
            )
            tests["BHIV Core"] = response.status_code == 200
            print(f"   {'✅' if tests['BHIV Core'] else '❌'} BHIV Core: {'PASS' if tests['BHIV Core'] else 'FAIL'}")
        except:
            tests["BHIV Core"] = False
            print(f"   ❌ BHIV Core: FAIL")
        
        return tests
    
    def generate_report(self) -> Dict[str, Any]:
        """Generate complete connectivity report"""
        
        print("\n" + "=" * 60)
        print("📊 BHIV INTEGRATION CONNECTIVITY REPORT")
        print("=" * 60)
        
        # Check services
        service_check = self.check_all_services()
        
        # Test components
        component_tests = self.test_individual_components()
        
        # Test integration
        integration_works = self.test_integration_flow()
        
        # Summary
        services_online = sum(1 for s in service_check["services"].values() if s.get("status") == "online")
        total_services = len(service_check["services"])
        
        components_working = sum(1 for t in component_tests.values() if t)
        total_components = len(component_tests)
        
        print(f"\n📋 SUMMARY:")
        print(f"   Services Online: {services_online}/{total_services}")
        print(f"   Components Working: {components_working}/{total_components}")
        print(f"   Integration Flow: {'✅ WORKING' if integration_works else '❌ BROKEN'}")
        
        overall_status = (
            service_check["all_healthy"] and 
            all(component_tests.values()) and 
            integration_works
        )
        
        print(f"\n🎯 OVERALL STATUS: {'✅ ALL SYSTEMS GO' if overall_status else '❌ ISSUES DETECTED'}")
        
        if not overall_status:
            print(f"\n🔧 TROUBLESHOOTING:")
            if not service_check["all_healthy"]:
                print(f"   - Some services are offline. Check startup logs.")
            if not all(component_tests.values()):
                print(f"   - Some components failing. Check individual service logs.")
            if not integration_works:
                print(f"   - Integration broken. Check orchestrator logs.")
        
        return {
            "overall_status": overall_status,
            "services": service_check,
            "components": component_tests,
            "integration": integration_works,
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
        }


def main():
    """Run connectivity check"""
    checker = ConnectivityChecker()
    report = checker.generate_report()
    
    # Save report
    with open("connectivity_report.json", "w") as f:
        json.dump(report, f, indent=2)
    
    print(f"\n📄 Full report saved to: connectivity_report.json")
    
    return report["overall_status"]


if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)