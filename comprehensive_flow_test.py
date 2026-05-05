"""
Comprehensive Flow Testing - Find Breaking Points
Tests every component, connection, and failure scenario
"""

import requests
import time
import json
from typing import Dict, Any, List, Tuple

class FlowTester:
    def __init__(self):
        self.components = {
            "prompt_runner": "http://127.0.0.1:8003",
            "creator_core": "http://127.0.0.1:8000",
            "bhiv_core": "http://127.0.0.1:8001",
            "integration_bridge": "http://127.0.0.1:8004",
            "bucket": "http://127.0.0.1:8005",
            "ttg_ttv_api": "http://127.0.0.1:8006"
        }
        self.issues = []
        self.passed = []
        
    def log_issue(self, test_name: str, error: str):
        self.issues.append({"test": test_name, "error": error})
        print(f"[FAIL] {test_name} - {error}")
        
    def log_pass(self, test_name: str):
        self.passed.append(test_name)
        print(f"[PASS] {test_name}")
        
    def test_component_health(self) -> bool:
        """Test 1: Component Health Checks"""
        print("\n=== TEST 1: Component Health ===")
        all_healthy = True
        
        for name, url in self.components.items():
            try:
                if name == "prompt_runner":
                    response = requests.get(f"{url}/health", timeout=5)
                elif name == "creator_core":
                    response = requests.get(f"{url}/system/health", timeout=5)
                elif name == "bhiv_core":
                    response = requests.get(f"{url}/health", timeout=5)
                elif name == "integration_bridge":
                    response = requests.get(f"{url}/pipeline/health", timeout=5)
                elif name == "bucket":
                    response = requests.get(f"{url}/bucket/stats", timeout=5)
                elif name == "ttg_ttv_api":
                    response = requests.get(f"{url}/health", timeout=5)
                    
                if response.status_code == 200:
                    self.log_pass(f"{name} health check")
                else:
                    self.log_issue(f"{name} health check", f"Status {response.status_code}")
                    all_healthy = False
            except Exception as e:
                self.log_issue(f"{name} health check", f"Connection failed: {str(e)}")
                all_healthy = False
                
        return all_healthy
        
    def test_prompt_runner_standalone(self) -> Tuple[bool, Dict]:
        """Test 2: Prompt Runner Standalone"""
        print("\n=== TEST 2: Prompt Runner Standalone ===")
        try:
            payload = {
                "prompt": "Design a residential building for Mumbai"
            }
            response = requests.post(
                f"{self.components['prompt_runner']}/process",
                json=payload,
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                if "instruction" in data or "structured_instruction" in data:
                    self.log_pass("Prompt Runner processing")
                    return True, data
                else:
                    self.log_issue("Prompt Runner processing", "Missing instruction in response")
                    return False, data
            else:
                self.log_issue("Prompt Runner processing", f"Status {response.status_code}")
                return False, {}
        except Exception as e:
            self.log_issue("Prompt Runner processing", str(e))
            return False, {}
            
    def test_creator_core_standalone(self) -> Tuple[bool, Dict]:
        """Test 3: Creator Core Standalone"""
        print("\n=== TEST 3: Creator Core Standalone ===")
        try:
            payload = {
                "instruction": "Design a residential building",
                "context": {"location": "Mumbai"}
            }
            response = requests.post(
                f"{self.components['creator_core']}/core",
                json=payload,
                timeout=15
            )
            
            if response.status_code == 200:
                data = response.json()
                if "blueprint" in data or "execution_id" in data:
                    self.log_pass("Creator Core processing")
                    return True, data
                else:
                    self.log_issue("Creator Core processing", "Missing blueprint in response")
                    return False, data
            else:
                self.log_issue("Creator Core processing", f"Status {response.status_code}")
                return False, {}
        except Exception as e:
            self.log_issue("Creator Core processing", str(e))
            return False, {}
            
    def test_bhiv_core_standalone(self) -> Tuple[bool, Dict]:
        """Test 4: BHIV Core Standalone"""
        print("\n=== TEST 4: BHIV Core Standalone ===")
        try:
            payload = {
                "blueprint": {
                    "type": "residential",
                    "location": "Mumbai"
                }
            }
            response = requests.post(
                f"{self.components['bhiv_core']}/execute",
                json=payload,
                timeout=15
            )
            
            if response.status_code == 200:
                data = response.json()
                self.log_pass("BHIV Core execution")
                return True, data
            else:
                self.log_issue("BHIV Core execution", f"Status {response.status_code}")
                return False, {}
        except Exception as e:
            self.log_issue("BHIV Core execution", str(e))
            return False, {}
            
    def test_integration_bridge_pipeline(self) -> Tuple[bool, Dict]:
        """Test 5: Integration Bridge Full Pipeline"""
        print("\n=== TEST 5: Integration Bridge Pipeline ===")
        try:
            payload = {
                "prompt": "Design a residential building for Mumbai"
            }
            response = requests.post(
                f"{self.components['integration_bridge']}/pipeline/execute",
                json=payload,
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                if "trace_id" in data and "artifact_chain" in data:
                    self.log_pass("Integration Bridge pipeline")
                    return True, data
                else:
                    self.log_issue("Integration Bridge pipeline", "Missing trace_id or artifact_chain")
                    return False, data
            else:
                self.log_issue("Integration Bridge pipeline", f"Status {response.status_code}: {response.text}")
                return False, {}
        except Exception as e:
            self.log_issue("Integration Bridge pipeline", str(e))
            return False, {}
            
    def test_ttg_integration(self) -> Tuple[bool, Dict]:
        """Test 6: TTG Integration"""
        print("\n=== TEST 6: TTG Integration ===")
        try:
            payload = {
                "game_type": "puzzle",
                "theme": "ancient_egypt",
                "difficulty": "medium",
                "player_count": 1,
                "description": "A puzzle game set in ancient Egypt"
            }
            response = requests.post(
                f"{self.components['ttg_ttv_api']}/ttg/generate",
                json=payload,
                timeout=45
            )
            
            if response.status_code == 200:
                data = response.json()
                required_fields = ["status", "trace_id", "artifact_chain", "ttg_output"]
                missing = [f for f in required_fields if f not in data]
                
                if not missing:
                    # Check TTG output structure
                    ttg_out = data.get("ttg_output", {})
                    ttg_required = ["game_content", "gameplay_structure", "assets", "metadata"]
                    ttg_missing = [f for f in ttg_required if f not in ttg_out]
                    
                    if not ttg_missing:
                        self.log_pass("TTG integration")
                        return True, data
                    else:
                        self.log_issue("TTG integration", f"Missing TTG fields: {ttg_missing}")
                        return False, data
                else:
                    self.log_issue("TTG integration", f"Missing fields: {missing}")
                    return False, data
            else:
                self.log_issue("TTG integration", f"Status {response.status_code}: {response.text}")
                return False, {}
        except Exception as e:
            self.log_issue("TTG integration", str(e))
            return False, {}
            
    def test_ttv_integration(self) -> Tuple[bool, Dict]:
        """Test 7: TTV Integration"""
        print("\n=== TEST 7: TTV Integration ===")
        try:
            payload = {
                "video_type": "tutorial",
                "topic": "Python programming basics",
                "duration": 300,
                "style": "educational",
                "voice": "professional",
                "description": "Introduction to Python programming"
            }
            response = requests.post(
                f"{self.components['ttg_ttv_api']}/ttv/generate",
                json=payload,
                timeout=45
            )
            
            if response.status_code == 200:
                data = response.json()
                required_fields = ["status", "trace_id", "artifact_chain", "ttv_output"]
                missing = [f for f in required_fields if f not in data]
                
                if not missing:
                    # Check TTV output structure
                    ttv_out = data.get("ttv_output", {})
                    ttv_required = ["video_script", "audio_requirements", "visual_elements", "timeline", "metadata"]
                    ttv_missing = [f for f in ttv_required if f not in ttv_out]
                    
                    if not ttv_missing:
                        self.log_pass("TTV integration")
                        return True, data
                    else:
                        self.log_issue("TTV integration", f"Missing TTV fields: {ttv_missing}")
                        return False, data
                else:
                    self.log_issue("TTV integration", f"Missing fields: {missing}")
                    return False, data
            else:
                self.log_issue("TTV integration", f"Status {response.status_code}: {response.text}")
                return False, {}
        except Exception as e:
            self.log_issue("TTV integration", str(e))
            return False, {}
            
    def test_artifact_storage_retrieval(self, trace_id: str) -> bool:
        """Test 8: Artifact Storage and Retrieval"""
        print("\n=== TEST 8: Artifact Storage & Retrieval ===")
        try:
            response = requests.get(
                f"{self.components['bucket']}/bucket/trace/{trace_id}",
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                if "artifacts" in data and len(data["artifacts"]) > 0:
                    self.log_pass("Artifact retrieval")
                    return True
                else:
                    self.log_issue("Artifact retrieval", "No artifacts found")
                    return False
            else:
                self.log_issue("Artifact retrieval", f"Status {response.status_code}")
                return False
        except Exception as e:
            self.log_issue("Artifact retrieval", str(e))
            return False
            
    def test_replay_capability(self, trace_id: str) -> bool:
        """Test 9: Replay Capability"""
        print("\n=== TEST 9: Replay Capability ===")
        try:
            response = requests.get(
                f"{self.components['integration_bridge']}/pipeline/replay/{trace_id}",
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                if "replayed_result" in data or "status" in data:
                    self.log_pass("Replay capability")
                    return True
                else:
                    self.log_issue("Replay capability", "Invalid replay response")
                    return False
            else:
                self.log_issue("Replay capability", f"Status {response.status_code}")
                return False
        except Exception as e:
            self.log_issue("Replay capability", str(e))
            return False
            
    def test_tantra_validation(self) -> bool:
        """Test 10: TANTRA Boundary Validation"""
        print("\n=== TEST 10: TANTRA Boundary Validation ===")
        try:
            response = requests.get(
                f"{self.components['ttg_ttv_api']}/tantra/validate",
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                if data.get("tantra_compliant") == True:
                    self.log_pass("TANTRA validation")
                    return True
                else:
                    self.log_issue("TANTRA validation", "System not TANTRA compliant")
                    return False
            else:
                self.log_issue("TANTRA validation", f"Status {response.status_code}")
                return False
        except Exception as e:
            self.log_issue("TANTRA validation", str(e))
            return False
            
    def test_error_handling(self) -> bool:
        """Test 11: Error Handling"""
        print("\n=== TEST 11: Error Handling ===")
        all_passed = True
        
        # Test invalid TTG input
        try:
            response = requests.post(
                f"{self.components['ttg_ttv_api']}/ttg/generate",
                json={},
                timeout=10
            )
            if response.status_code in [400, 422]:
                self.log_pass("TTG invalid input handling")
            else:
                self.log_issue("TTG invalid input handling", f"Expected 400/422, got {response.status_code}")
                all_passed = False
        except Exception as e:
            self.log_issue("TTG invalid input handling", str(e))
            all_passed = False
            
        # Test invalid TTV input
        try:
            response = requests.post(
                f"{self.components['ttg_ttv_api']}/ttv/generate",
                json={},
                timeout=10
            )
            if response.status_code in [400, 422]:
                self.log_pass("TTV invalid input handling")
            else:
                self.log_issue("TTV invalid input handling", f"Expected 400/422, got {response.status_code}")
                all_passed = False
        except Exception as e:
            self.log_issue("TTV invalid input handling", str(e))
            all_passed = False
            
        return all_passed
        
    def run_all_tests(self):
        """Run all tests and generate report"""
        print("=" * 60)
        print("COMPREHENSIVE FLOW TESTING - FINDING BREAKING POINTS")
        print("=" * 60)
        
        start_time = time.time()
        
        # Test 1: Component Health
        health_ok = self.test_component_health()
        
        if not health_ok:
            print("\n[WARNING] Some components are not healthy. Continuing with available components...")
        
        # Test 2-4: Individual Components
        self.test_prompt_runner_standalone()
        self.test_creator_core_standalone()
        self.test_bhiv_core_standalone()
        
        # Test 5: Integration Bridge
        bridge_ok, bridge_data = self.test_integration_bridge_pipeline()
        trace_id = bridge_data.get("trace_id") if bridge_ok else None
        
        # Test 6-7: TTG/TTV Integration
        ttg_ok, ttg_data = self.test_ttg_integration()
        ttg_trace_id = ttg_data.get("trace_id") if ttg_ok else None
        
        ttv_ok, ttv_data = self.test_ttv_integration()
        ttv_trace_id = ttv_data.get("trace_id") if ttv_ok else None
        
        # Test 8-9: Artifact Storage and Replay
        if ttg_trace_id:
            self.test_artifact_storage_retrieval(ttg_trace_id)
            self.test_replay_capability(ttg_trace_id)
        
        # Test 10: TANTRA Validation
        self.test_tantra_validation()
        
        # Test 11: Error Handling
        self.test_error_handling()
        
        # Generate Report
        elapsed = time.time() - start_time
        self.generate_report(elapsed)
        
    def generate_report(self, elapsed: float):
        """Generate test report"""
        print("\n" + "=" * 60)
        print("TEST REPORT")
        print("=" * 60)
        
        total_tests = len(self.passed) + len(self.issues)
        pass_rate = (len(self.passed) / total_tests * 100) if total_tests > 0 else 0
        
        print(f"\nTotal Tests: {total_tests}")
        print(f"Passed: {len(self.passed)}")
        print(f"Failed: {len(self.issues)}")
        print(f"Pass Rate: {pass_rate:.1f}%")
        print(f"Time Elapsed: {elapsed:.2f}s")
        
        if self.issues:
            print("\n" + "=" * 60)
            print("ISSUES FOUND (BREAKING POINTS)")
            print("=" * 60)
            for idx, issue in enumerate(self.issues, 1):
                print(f"\n{idx}. {issue['test']}")
                print(f"   Error: {issue['error']}")
                
        print("\n" + "=" * 60)
        
        # Save report to file
        report = {
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
            "total_tests": total_tests,
            "passed": len(self.passed),
            "failed": len(self.issues),
            "pass_rate": pass_rate,
            "elapsed_seconds": elapsed,
            "issues": self.issues,
            "passed_tests": self.passed
        }
        
        with open("test_report.json", "w") as f:
            json.dump(report, f, indent=2)
            
        print(f"Report saved to: test_report.json")
        
        return len(self.issues) == 0

if __name__ == "__main__":
    tester = FlowTester()
    success = tester.run_all_tests()
    
    if success:
        print("\n[SUCCESS] ALL TESTS PASSED - NO BREAKING POINTS FOUND")
        exit(0)
    else:
        print("\n[WARNING] BREAKING POINTS FOUND - SEE REPORT ABOVE")
        exit(1)
