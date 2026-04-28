"""
BHIV Full Integration Validation
===============================
Tests the complete pipeline: Prompt Runner → Creator Core → BHIV Core → Bucket

This validates:
1. End-to-end flow proof (input → output JSON)
2. Artifact chain example (A1 → A4) 
3. Replay + reconstruction proof
4. TTG/TTV integration proof
5. Determinism validation
"""

import json
import time
import requests
from typing import Dict, Any


class BHIVIntegrationValidator:
    """Validates the complete BHIV integration pipeline"""
    
    def __init__(self):
        self.prompt_runner_url = "http://127.0.0.1:8003"
        self.creator_core_url = "http://127.0.0.1:8000" 
        self.bhiv_core_url = "http://127.0.0.1:8001"
        self.integration_bridge_url = "http://127.0.0.1:8004"
        self.bucket_url = "http://127.0.0.1:8005"
        
        self.test_results = []
    
    def run_full_validation(self) -> Dict[str, Any]:
        """Run complete validation suite"""
        
        print("🚀 Starting BHIV Full Integration Validation...")
        print("=" * 60)
        
        # Test 1: Component Health Check
        self._test_component_health()
        
        # Test 2: End-to-End Flow Proof
        self._test_end_to_end_flow()
        
        # Test 3: Artifact Chain Validation
        self._test_artifact_chain()
        
        # Test 4: Replay & Reconstruction
        self._test_replay_reconstruction()
        
        # Test 5: Determinism Validation
        self._test_determinism()
        
        # Test 6: TTG/TTV Integration Proof
        self._test_ttg_ttv_integration()
        
        return self._generate_validation_report()
    
    def _test_component_health(self):
        """Test 1: Verify all components are healthy"""
        print("\n📋 Test 1: Component Health Check")
        
        components = {
            "Prompt Runner": f"{self.prompt_runner_url}/health",
            "Creator Core": f"{self.creator_core_url}/",
            "BHIV Core": f"{self.bhiv_core_url}/",
            "Integration Bridge": f"{self.integration_bridge_url}/pipeline/health",
            "Bucket": f"{self.bucket_url}/bucket/stats"
        }
        
        health_results = {}
        for name, url in components.items():
            try:
                response = requests.get(url, timeout=5)
                health_results[name] = {
                    "status": "healthy" if response.status_code == 200 else "unhealthy",
                    "code": response.status_code
                }
                print(f"  ✅ {name}: {response.status_code}")
            except Exception as e:
                health_results[name] = {"status": "unhealthy", "error": str(e)}
                print(f"  ❌ {name}: {str(e)}")
        
        self.test_results.append({
            "test": "component_health",
            "results": health_results,
            "passed": all(r["status"] == "healthy" for r in health_results.values())
        })
    
    def _test_end_to_end_flow(self):
        """Test 2: End-to-End Flow Proof"""
        print("\n🔄 Test 2: End-to-End Flow Proof")
        
        test_prompt = "Design a residential building for a 1000 sqft plot in Mumbai"
        
        try:
            # Execute full pipeline
            response = requests.post(
                f"{self.integration_bridge_url}/pipeline/execute",
                json={"prompt": test_prompt},
                timeout=60
            )
            
            if response.status_code == 200:
                result = response.json()
                print(f"  ✅ Pipeline executed successfully")
                print(f"  📋 Trace ID: {result.get('trace_id')}")
                print(f"  🔗 Artifact Chain: {len(result.get('artifact_chain', {}))} artifacts")
                
                self.test_results.append({
                    "test": "end_to_end_flow",
                    "input": test_prompt,
                    "output": result,
                    "passed": True,
                    "trace_id": result.get("trace_id")
                })
            else:
                print(f"  ❌ Pipeline failed: {response.status_code}")
                self.test_results.append({
                    "test": "end_to_end_flow", 
                    "passed": False,
                    "error": response.text
                })
                
        except Exception as e:
            print(f"  ❌ Pipeline error: {str(e)}")
            self.test_results.append({
                "test": "end_to_end_flow",
                "passed": False, 
                "error": str(e)
            })
    
    def _test_artifact_chain(self):
        """Test 3: Artifact Chain Validation (A1 → A4)"""
        print("\n🔗 Test 3: Artifact Chain Validation")
        
        # Get the trace_id from previous test
        end_to_end_result = next((r for r in self.test_results if r["test"] == "end_to_end_flow"), None)
        
        if not end_to_end_result or not end_to_end_result.get("passed"):
            print("  ❌ Cannot test artifact chain - end-to-end test failed")
            self.test_results.append({"test": "artifact_chain", "passed": False, "error": "No trace_id"})
            return
        
        trace_id = end_to_end_result.get("trace_id")
        
        try:
            # Retrieve artifacts from bucket
            response = requests.get(f"{self.bucket_url}/bucket/trace/{trace_id}", timeout=10)
            
            if response.status_code == 200:
                trace_data = response.json()
                artifacts = trace_data.get("artifacts", [])
                
                # Validate artifact chain A1 → A2 → A3 → A4
                artifact_types = [a.get("artifact_type") for a in artifacts]
                expected_types = ["instruction", "blueprint", "execution", "result"]
                
                chain_valid = all(t in artifact_types for t in expected_types)
                
                print(f"  📋 Found {len(artifacts)} artifacts")
                print(f"  🔗 Chain: {' → '.join(artifact_types)}")
                print(f"  ✅ Chain valid: {chain_valid}")
                
                self.test_results.append({
                    "test": "artifact_chain",
                    "trace_id": trace_id,
                    "artifacts": artifacts,
                    "chain_valid": chain_valid,
                    "passed": chain_valid
                })
            else:
                print(f"  ❌ Failed to retrieve artifacts: {response.status_code}")
                self.test_results.append({
                    "test": "artifact_chain",
                    "passed": False,
                    "error": f"HTTP {response.status_code}"
                })
                
        except Exception as e:
            print(f"  ❌ Artifact chain error: {str(e)}")
            self.test_results.append({
                "test": "artifact_chain",
                "passed": False,
                "error": str(e)
            })
    
    def _test_replay_reconstruction(self):
        """Test 4: Replay & Reconstruction Proof"""
        print("\n🔄 Test 4: Replay & Reconstruction Proof")
        
        # Get trace_id from artifact chain test
        chain_result = next((r for r in self.test_results if r["test"] == "artifact_chain"), None)
        
        if not chain_result or not chain_result.get("passed"):
            print("  ❌ Cannot test replay - artifact chain test failed")
            self.test_results.append({"test": "replay_reconstruction", "passed": False, "error": "No valid chain"})
            return
        
        trace_id = chain_result.get("trace_id")
        
        try:
            # Test replay from trace_id
            response = requests.get(f"{self.integration_bridge_url}/pipeline/replay/{trace_id}", timeout=10)
            
            if response.status_code == 200:
                replay_data = response.json()
                print(f"  ✅ Replay successful for trace: {trace_id}")
                print(f"  📋 Replay timestamp: {replay_data.get('replay_timestamp')}")
                
                self.test_results.append({
                    "test": "replay_reconstruction",
                    "trace_id": trace_id,
                    "replay_data": replay_data,
                    "passed": True
                })
            else:
                print(f"  ❌ Replay failed: {response.status_code}")
                self.test_results.append({
                    "test": "replay_reconstruction",
                    "passed": False,
                    "error": f"HTTP {response.status_code}"
                })
                
        except Exception as e:
            print(f"  ❌ Replay error: {str(e)}")
            self.test_results.append({
                "test": "replay_reconstruction",
                "passed": False,
                "error": str(e)
            })
    
    def _test_determinism(self):
        """Test 5: Determinism Validation"""
        print("\n🎯 Test 5: Determinism Validation")
        
        test_prompt = "Calculate ROI for a 50 lakh investment over 5 years"
        
        try:
            # Execute same prompt twice
            results = []
            for i in range(2):
                response = requests.post(
                    f"{self.integration_bridge_url}/pipeline/execute",
                    json={"prompt": test_prompt},
                    timeout=60
                )
                if response.status_code == 200:
                    results.append(response.json())
                    time.sleep(1)  # Small delay between requests
            
            if len(results) == 2:
                # Compare deterministic hashes
                hash1 = results[0].get("pipeline_result", {}).get("deterministic_hash")
                hash2 = results[1].get("pipeline_result", {}).get("deterministic_hash")
                
                deterministic = hash1 == hash2 and hash1 is not None
                
                print(f"  📋 Hash 1: {hash1}")
                print(f"  📋 Hash 2: {hash2}")
                print(f"  ✅ Deterministic: {deterministic}")
                
                self.test_results.append({
                    "test": "determinism",
                    "hash1": hash1,
                    "hash2": hash2,
                    "deterministic": deterministic,
                    "passed": deterministic
                })
            else:
                print("  ❌ Failed to execute both requests")
                self.test_results.append({
                    "test": "determinism",
                    "passed": False,
                    "error": "Incomplete execution"
                })
                
        except Exception as e:
            print(f"  ❌ Determinism error: {str(e)}")
            self.test_results.append({
                "test": "determinism",
                "passed": False,
                "error": str(e)
            })
    
    def _test_ttg_ttv_integration(self):
        """Test 6: TTG/TTV Integration Proof"""
        print("\n🔌 Test 6: TTG/TTV Integration Proof")
        
        # Test TTG-style input
        ttg_prompt = "Create a blog post about AI in healthcare"
        
        # Test TTV-style input  
        ttv_prompt = "Generate a video script for product demo"
        
        ttg_ttv_results = {}
        
        for name, prompt in [("TTG", ttg_prompt), ("TTV", ttv_prompt)]:
            try:
                response = requests.post(
                    f"{self.integration_bridge_url}/pipeline/execute",
                    json={"prompt": prompt},
                    timeout=60
                )
                
                if response.status_code == 200:
                    result = response.json()
                    ttg_ttv_results[name] = {
                        "status": "success",
                        "trace_id": result.get("trace_id"),
                        "target_product": result.get("pipeline_result", {}).get("blueprint_envelope", {}).get("target_product")
                    }
                    print(f"  ✅ {name} integration successful")
                else:
                    ttg_ttv_results[name] = {"status": "failed", "error": response.text}
                    print(f"  ❌ {name} integration failed")
                    
            except Exception as e:
                ttg_ttv_results[name] = {"status": "error", "error": str(e)}
                print(f"  ❌ {name} integration error: {str(e)}")
        
        integration_success = all(r["status"] == "success" for r in ttg_ttv_results.values())
        
        self.test_results.append({
            "test": "ttg_ttv_integration",
            "results": ttg_ttv_results,
            "passed": integration_success
        })
    
    def _generate_validation_report(self) -> Dict[str, Any]:
        """Generate final validation report"""
        
        passed_tests = sum(1 for r in self.test_results if r.get("passed", False))
        total_tests = len(self.test_results)
        
        report = {
            "validation_summary": {
                "total_tests": total_tests,
                "passed_tests": passed_tests,
                "failed_tests": total_tests - passed_tests,
                "success_rate": f"{(passed_tests/total_tests)*100:.1f}%" if total_tests > 0 else "0%",
                "overall_status": "PASSED" if passed_tests == total_tests else "FAILED"
            },
            "test_results": self.test_results,
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
        }
        
        print("\n" + "=" * 60)
        print("📊 VALIDATION SUMMARY")
        print("=" * 60)
        print(f"Total Tests: {total_tests}")
        print(f"Passed: {passed_tests}")
        print(f"Failed: {total_tests - passed_tests}")
        print(f"Success Rate: {report['validation_summary']['success_rate']}")
        print(f"Overall Status: {report['validation_summary']['overall_status']}")
        
        return report


def main():
    """Run the full integration validation"""
    validator = BHIVIntegrationValidator()
    report = validator.run_full_validation()
    
    # Save report to file
    with open("bhiv_integration_validation_report.json", "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2, ensure_ascii=False)
    
    print(f"\n📄 Full report saved to: bhiv_integration_validation_report.json")
    
    return report["validation_summary"]["overall_status"] == "PASSED"


if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)