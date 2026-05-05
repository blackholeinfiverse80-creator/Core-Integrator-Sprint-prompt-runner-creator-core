"""
TTG/TTV Integration Test
========================
Validates complete TTG/TTV integration through BHIV pipeline.

Tests:
1. TTG integration proof
2. TTV integration proof
3. Artifact chain validation
4. Replay capability
5. System boundary enforcement
"""

import requests
import json
from datetime import datetime


class TTGTTVIntegrationTest:
    """Test suite for TTG/TTV integration"""
    
    def __init__(self):
        self.ttg_ttv_url = "http://127.0.0.1:8006"
        self.bhiv_core_url = "http://127.0.0.1:8001"
        self.results = []
    
    def run_all_tests(self):
        """Run complete test suite"""
        print("=" * 60)
        print("TTG/TTV INTEGRATION TEST SUITE")
        print("=" * 60)
        print()
        
        self.test_ttg_integration()
        self.test_ttv_integration()
        self.test_artifact_chain()
        self.test_system_boundaries()
        
        self.print_summary()
    
    def test_ttg_integration(self):
        """Test TTG integration through pipeline"""
        print("TEST 1: TTG Integration")
        print("-" * 40)
        
        ttg_request = {
            "game_type": "adventure",
            "theme": "fantasy",
            "difficulty": "medium",
            "player_count": 2,
            "description": "Create a dungeon crawler game with magic system"
        }
        
        try:
            response = requests.post(
                f"{self.ttg_ttv_url}/ttg/generate",
                json=ttg_request,
                timeout=60
            )
            
            if response.status_code == 200:
                result = response.json()
                print("✅ TTG Integration: SUCCESS")
                print(f"   Trace ID: {result.get('trace_id')}")
                print(f"   Status: {result.get('status')}")
                print(f"   Artifact Chain: {bool(result.get('artifact_chain'))}")
                
                # Save proof
                self._save_proof("ttg_integration_proof.json", result)
                self.results.append(("TTG Integration", "PASS"))
            else:
                print(f"❌ TTG Integration: FAILED (HTTP {response.status_code})")
                self.results.append(("TTG Integration", "FAIL"))
        
        except Exception as e:
            print(f"❌ TTG Integration: ERROR - {str(e)}")
            self.results.append(("TTG Integration", "ERROR"))
        
        print()
    
    def test_ttv_integration(self):
        """Test TTV integration through pipeline"""
        print("TEST 2: TTV Integration")
        print("-" * 40)
        
        ttv_request = {
            "video_type": "tutorial",
            "topic": "Python programming basics",
            "duration": "5min",
            "style": "animated",
            "voice": "professional",
            "description": "Create a beginner-friendly Python tutorial video"
        }
        
        try:
            response = requests.post(
                f"{self.ttg_ttv_url}/ttv/generate",
                json=ttv_request,
                timeout=60
            )
            
            if response.status_code == 200:
                result = response.json()
                print("✅ TTV Integration: SUCCESS")
                print(f"   Trace ID: {result.get('trace_id')}")
                print(f"   Status: {result.get('status')}")
                print(f"   Artifact Chain: {bool(result.get('artifact_chain'))}")
                
                # Save proof
                self._save_proof("ttv_integration_proof.json", result)
                self.results.append(("TTV Integration", "PASS"))
            else:
                print(f"❌ TTV Integration: FAILED (HTTP {response.status_code})")
                self.results.append(("TTV Integration", "FAIL"))
        
        except Exception as e:
            print(f"❌ TTV Integration: ERROR - {str(e)}")
            self.results.append(("TTV Integration", "ERROR"))
        
        print()
    
    def test_artifact_chain(self):
        """Test artifact chain creation"""
        print("TEST 3: Artifact Chain Validation")
        print("-" * 40)
        
        # Use TTG request to test artifact chain
        ttg_request = {
            "game_type": "puzzle",
            "description": "Create a simple puzzle game"
        }
        
        try:
            response = requests.post(
                f"{self.ttg_ttv_url}/ttg/generate",
                json=ttg_request,
                timeout=60
            )
            
            if response.status_code == 200:
                result = response.json()
                artifact_chain = result.get("artifact_chain", {})
                
                required_artifacts = ["execution_id", "input_hash", "output_hash", "semantic_hash"]
                has_all_artifacts = all(key in artifact_chain for key in required_artifacts)
                
                if has_all_artifacts:
                    print("✅ Artifact Chain: COMPLETE")
                    print(f"   Execution ID: {artifact_chain.get('execution_id')}")
                    print(f"   Input Hash: {artifact_chain.get('input_hash')[:16]}...")
                    print(f"   Output Hash: {artifact_chain.get('output_hash')[:16]}...")
                    self.results.append(("Artifact Chain", "PASS"))
                else:
                    print("❌ Artifact Chain: INCOMPLETE")
                    self.results.append(("Artifact Chain", "FAIL"))
            else:
                print(f"❌ Artifact Chain: FAILED (HTTP {response.status_code})")
                self.results.append(("Artifact Chain", "FAIL"))
        
        except Exception as e:
            print(f"❌ Artifact Chain: ERROR - {str(e)}")
            self.results.append(("Artifact Chain", "ERROR"))
        
        print()
    
    def test_system_boundaries(self):
        """Test TANTRA system boundary enforcement"""
        print("TEST 4: System Boundary Validation")
        print("-" * 40)
        
        try:
            response = requests.get(
                f"{self.ttg_ttv_url}/tantra/validate",
                timeout=10
            )
            
            if response.status_code == 200:
                result = response.json()
                tantra_compliant = result.get("tantra_compliant", False)
                
                if tantra_compliant:
                    print("✅ System Boundaries: ENFORCED")
                    print(f"   TANTRA Compliant: {tantra_compliant}")
                    print(f"   Boundary Status: {result.get('system_boundaries')}")
                    self.results.append(("System Boundaries", "PASS"))
                else:
                    print("❌ System Boundaries: NOT ENFORCED")
                    self.results.append(("System Boundaries", "FAIL"))
            else:
                print(f"❌ System Boundaries: FAILED (HTTP {response.status_code})")
                self.results.append(("System Boundaries", "FAIL"))
        
        except Exception as e:
            print(f"❌ System Boundaries: ERROR - {str(e)}")
            self.results.append(("System Boundaries", "ERROR"))
        
        print()
    
    def _save_proof(self, filename: str, data: Dict):
        """Save integration proof"""
        proof_dir = "review_packets"
        import os
        os.makedirs(proof_dir, exist_ok=True)
        
        filepath = os.path.join(proof_dir, filename)
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2)
        
        print(f"   Proof saved: {filepath}")
    
    def print_summary(self):
        """Print test summary"""
        print("=" * 60)
        print("TEST SUMMARY")
        print("=" * 60)
        
        passed = sum(1 for _, status in self.results if status == "PASS")
        failed = sum(1 for _, status in self.results if status == "FAIL")
        errors = sum(1 for _, status in self.results if status == "ERROR")
        total = len(self.results)
        
        for test_name, status in self.results:
            symbol = "✅" if status == "PASS" else "❌"
            print(f"{symbol} {test_name}: {status}")
        
        print()
        print(f"Total: {total} | Passed: {passed} | Failed: {failed} | Errors: {errors}")
        print("=" * 60)


if __name__ == "__main__":
    tester = TTGTTVIntegrationTest()
    tester.run_all_tests()
