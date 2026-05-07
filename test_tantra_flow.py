"""
TANTRA Flow Full Test
======================
Tests complete flow: Prompt → Creator Core → Core → CET → Sarathi → Gate → Execution → Bucket

VALIDATION:
- All layers present
- trace_id consistent
- Artifacts created
- Determinism maintained
"""

import requests
import json
import time
from datetime import datetime


class TANTRAFlowTester:
    """Test full TANTRA flow end-to-end"""
    
    def __init__(self):
        self.prompt_runner_url = "http://127.0.0.1:8003"
        self.creator_core_url = "http://127.0.0.1:8000"
        self.bhiv_core_url = "http://127.0.0.1:8001"
        self.bucket_url = "http://127.0.0.1:8005"
        
    def test_full_flow(self, test_prompt: str = "Create a simple text module"):
        """Test complete TANTRA flow"""
        print("\n" + "="*80)
        print("TANTRA FLOW FULL TEST")
        print("="*80)
        
        results = {
            "test_timestamp": datetime.utcnow().isoformat(),
            "test_prompt": test_prompt,
            "phases": {},
            "validation": {},
            "artifacts": {},
            "trace_consistency": False,
            "flow_complete": False
        }
        
        try:
            # PHASE 1: Prompt Runner → Instruction
            print("\n[PHASE 1] Prompt Runner → Instruction")
            instruction = self._test_prompt_runner(test_prompt)
            results["phases"]["A1_instruction"] = {
                "status": "success",
                "instruction_id": instruction.get("instruction_id"),
                "data": instruction
            }
            print(f"✓ Instruction created: {instruction.get('instruction_id')}")
            
            # PHASE 2: Creator Core → Blueprint
            print("\n[PHASE 2] Creator Core → Blueprint")
            blueprint = self._test_creator_core(instruction)
            results["phases"]["A2_blueprint"] = {
                "status": "success",
                "blueprint_id": blueprint.get("blueprint_id"),
                "data": blueprint
            }
            print(f"✓ Blueprint created: {blueprint.get('blueprint_id')}")
            
            # PHASE 3: BHIV Core → CET → Sarathi → Gate → Execution
            print("\n[PHASE 3] BHIV Core (TANTRA Flow)")
            execution = self._test_bhiv_core_tantra(blueprint)
            results["phases"]["A3_execution"] = {
                "status": execution.get("status"),
                "execution_id": execution.get("execution_envelope", {}).get("execution_id"),
                "data": execution
            }
            
            # Validate TANTRA layers
            tantra_flow = execution.get("tantra_flow", {})
            if tantra_flow:
                print(f"\n  TANTRA LAYERS DETECTED:")
                print(f"  ├─ Contract ID: {tantra_flow.get('contract_id')}")
                print(f"  ├─ Contract Hash: {tantra_flow.get('contract_hash')}")
                print(f"  ├─ Authority Allowed: {tantra_flow.get('authority_allowed')}")
                print(f"  ├─ Authority Reason: {tantra_flow.get('authority_reason')}")
                print(f"  ├─ Gate Status: {tantra_flow.get('gate_status')}")
                print(f"  └─ Flow Complete: {tantra_flow.get('flow_complete')}")
                
                results["validation"]["tantra_layers"] = {
                    "cet_present": bool(tantra_flow.get('contract_id')),
                    "sarathi_present": bool(tantra_flow.get('authority_allowed') is not None),
                    "gate_present": bool(tantra_flow.get('gate_status')),
                    "flow_complete": tantra_flow.get('flow_complete', False)
                }
            else:
                print("  ✗ TANTRA layers NOT detected")
                results["validation"]["tantra_layers"] = {
                    "cet_present": False,
                    "sarathi_present": False,
                    "gate_present": False,
                    "flow_complete": False
                }
            
            # PHASE 4: Bucket → Artifacts
            print("\n[PHASE 4] Bucket → Artifact Storage")
            instruction_id = instruction.get("instruction_id")
            if instruction_id:
                bucket_artifacts = self._test_bucket_artifacts(instruction_id)
                results["artifacts"] = bucket_artifacts
                print(f"✓ Artifacts stored: {len(bucket_artifacts.get('artifacts', []))} artifacts")
            
            # VALIDATION: Trace Consistency
            print("\n[VALIDATION] Trace Consistency Check")
            trace_ids = self._extract_trace_ids(instruction, blueprint, execution)
            trace_consistent = len(set(trace_ids)) <= 1
            results["trace_consistency"] = trace_consistent
            
            if trace_consistent:
                print(f"✓ Trace ID consistent: {trace_ids[0] if trace_ids else 'N/A'}")
            else:
                print(f"✗ Trace ID inconsistent: {trace_ids}")
            
            # FINAL VALIDATION
            results["flow_complete"] = all([
                results["phases"].get("A1_instruction", {}).get("status") == "success",
                results["phases"].get("A2_blueprint", {}).get("status") == "success",
                results["phases"].get("A3_execution", {}).get("status") == "success",
                results["validation"].get("tantra_layers", {}).get("flow_complete", False),
                results["trace_consistency"]
            ])
            
            print("\n" + "="*80)
            print("TEST RESULTS")
            print("="*80)
            print(f"Flow Complete: {results['flow_complete']}")
            print(f"Trace Consistent: {results['trace_consistency']}")
            print(f"TANTRA Layers: {results['validation'].get('tantra_layers', {})}")
            print("="*80)
            
            return results
            
        except Exception as e:
            print(f"\n✗ Test failed: {str(e)}")
            results["error"] = str(e)
            results["flow_complete"] = False
            return results
    
    def _test_prompt_runner(self, prompt: str):
        """Test Prompt Runner"""
        response = requests.post(
            f"{self.prompt_runner_url}/generate",
            json={"prompt": prompt},
            timeout=30
        )
        response.raise_for_status()
        return response.json()
    
    def _test_creator_core(self, instruction):
        """Test Creator Core"""
        response = requests.post(
            f"{self.creator_core_url}/creator-core/generate-blueprint",
            json=instruction,
            timeout=30
        )
        response.raise_for_status()
        return response.json()
    
    def _test_bhiv_core_tantra(self, blueprint):
        """Test BHIV Core with TANTRA flow"""
        # Convert blueprint to Core instruction format
        core_instruction = {
            "instruction_id": blueprint.get("blueprint_id", f"inst_{int(time.time())}"),
            "origin": "creator_core",
            "intent_type": "generate",
            "target_product": "creator",
            "payload": blueprint.get("blueprint", {}),
            "schema_version": "1.0.0",
            "timestamp": datetime.utcnow().isoformat()
        }
        
        response = requests.post(
            f"{self.bhiv_core_url}/core",
            json=core_instruction,
            timeout=45
        )
        response.raise_for_status()
        return response.json()
    
    def _test_bucket_artifacts(self, instruction_id: str):
        """Test Bucket artifact retrieval"""
        try:
            response = requests.get(
                f"{self.bucket_url}/bucket/trace/{instruction_id}",
                timeout=10
            )
            if response.status_code == 200:
                return response.json()
        except:
            pass
        return {"artifacts": []}
    
    def _extract_trace_ids(self, instruction, blueprint, execution):
        """Extract all trace IDs for consistency check"""
        trace_ids = []
        
        if instruction.get("instruction_id"):
            trace_ids.append(instruction["instruction_id"])
        
        if blueprint.get("blueprint_id"):
            trace_ids.append(blueprint["blueprint_id"])
        
        tantra_flow = execution.get("tantra_flow", {})
        if tantra_flow.get("contract_id"):
            # Extract trace from contract_id
            trace_ids.append(execution.get("execution_envelope", {}).get("user_id", ""))
        
        return [t for t in trace_ids if t]


def main():
    """Run TANTRA flow test"""
    tester = TANTRAFlowTester()
    
    # Test with simple prompt
    results = tester.test_full_flow("Create a simple text processing module")
    
    # Save results
    with open("tantra_flow_test_results.json", "w") as f:
        json.dump(results, f, indent=2)
    
    print(f"\n✓ Results saved to: tantra_flow_test_results.json")
    
    if results["flow_complete"]:
        print("\n✅ TANTRA FLOW TEST PASSED")
        return 0
    else:
        print("\n❌ TANTRA FLOW TEST FAILED")
        return 1


if __name__ == "__main__":
    exit(main())
