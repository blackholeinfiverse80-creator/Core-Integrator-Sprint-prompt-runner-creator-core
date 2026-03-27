"""
Test Lineage and Replay System
Comprehensive test for the complete deterministic system
"""

import json
import time
from datetime import datetime, timezone
from src.core.gateway import Gateway
from src.core.lineage_manager import LineageManager
from src.core.replay_engine import ReplayEngine
from src.core.bucket_reader import BucketReader
from src.core.routing_engine import RoutingEngine
from src.db.memory_adapter import SQLiteAdapter

def test_complete_lineage_replay_system():
    """Test the complete lineage and replay system"""
    
    print("🚀 Testing Complete Lineage and Replay System")
    print("=" * 60)
    
    # Initialize system components
    memory = SQLiteAdapter("test_lineage.db")
    gateway = Gateway()
    
    # Test Creator Core instruction
    test_instruction = {
        "instruction_id": "test_lineage_001",
        "origin": "creator_core",
        "intent_type": "generate",
        "target_product": "content",
        "payload": {
            "text": "Test lineage and replay system functionality",
            "type": "validation_test"
        },
        "schema_version": "1.0.0",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "parent_instruction_id": None
    }
    
    print(f"📝 Test Instruction: {test_instruction['instruction_id']}")
    print(f"🎯 Target Product: {test_instruction['target_product']}")
    
    # Step 1: Execute instruction and create artifacts
    print("\n🔄 Step 1: Executing instruction...")
    start_time = time.time()
    
    try:
        result = gateway.process_request(
            module="sample_text",  # This will be detected as Creator Core instruction
            intent="generate",
            user_id="test_user",
            data=test_instruction
        )
        
        execution_time = (time.time() - start_time) * 1000
        print(f"✅ Execution completed in {execution_time:.2f}ms")
        print(f"📊 Status: {result.get('status')}")
        
        if result.get('execution_envelope'):
            execution_id = result['execution_envelope']['execution_id']
            print(f"🔗 Execution ID: {execution_id}")
        
    except Exception as e:
        print(f"❌ Execution failed: {e}")
        return False
    
    # Step 2: Verify lineage creation
    print("\n🔍 Step 2: Verifying lineage creation...")
    
    try:
        lineage = gateway.lineage_manager.get_instruction_lineage(test_instruction['instruction_id'])
        
        if lineage['status'] == 'found':
            print(f"✅ Lineage found with {len(lineage['artifacts'])} artifacts")
            print(f"📈 Lineage chain length: {len(lineage['lineage_chain'])}")
            
            # Check for required artifact types
            artifact_types = [a['artifact_type'] for a in lineage['artifacts']]
            required_types = ['blueprint', 'execution', 'result']
            
            for req_type in required_types:
                if req_type in artifact_types:
                    print(f"✅ {req_type.capitalize()} artifact found")
                else:
                    print(f"❌ {req_type.capitalize()} artifact missing")
                    return False
        else:
            print(f"❌ Lineage not found: {lineage}")
            return False
            
    except Exception as e:
        print(f"❌ Lineage verification failed: {e}")
        return False
    
    # Step 3: Test artifact retrieval
    print("\n📦 Step 3: Testing artifact retrieval...")
    
    try:
        artifacts = gateway.bucket_reader.get_artifacts_by_instruction(test_instruction['instruction_id'])
        print(f"✅ Retrieved {len(artifacts)} artifacts")
        
        for artifact in artifacts:
            print(f"  📄 {artifact['artifact_type']}: {artifact['artifact_id']}")
            
            # Verify hash integrity
            expected_hash = gateway.lineage_manager.compute_artifact_hash(artifact['payload'])
            if artifact['artifact_hash'] == expected_hash:
                print(f"    ✅ Hash integrity verified")
            else:
                print(f"    ❌ Hash mismatch!")
                return False
                
    except Exception as e:
        print(f"❌ Artifact retrieval failed: {e}")
        return False
    
    # Step 4: Test replay capability validation
    print("\n🔍 Step 4: Validating replay capability...")
    
    try:
        # Initialize replay engine
        routing_engine = RoutingEngine(gateway.agents, gateway.memory)
        replay_engine = ReplayEngine(gateway.lineage_manager, routing_engine, gateway.memory)
        
        validation = replay_engine.validate_replay_capability(test_instruction['instruction_id'])
        
        if validation['can_replay']:
            print("✅ Instruction is replayable")
            print(f"📊 Artifact count: {validation['artifact_count']}")
            print(f"🔗 Lineage valid: {validation['lineage_valid']}")
        else:
            print(f"❌ Instruction cannot be replayed: {validation['reason']}")
            if validation.get('missing_artifact_types'):
                print(f"   Missing: {validation['missing_artifact_types']}")
            if validation.get('lineage_issues'):
                print(f"   Issues: {validation['lineage_issues']}")
            return False
            
    except Exception as e:
        print(f"❌ Replay validation failed: {e}")
        return False
    
    # Step 5: Execute replay
    print("\n🔄 Step 5: Executing replay...")
    
    try:
        replay_start = time.time()
        replay_result = replay_engine.replay_instruction(test_instruction['instruction_id'])
        replay_time = (time.time() - replay_start) * 1000
        
        if replay_result['replay_status'] == 'completed':
            print(f"✅ Replay completed in {replay_time:.2f}ms")
            print(f"🎯 Hash match: {replay_result['hash_match']}")
            print(f"📊 Determinism score: {replay_result['determinism_score']:.2f}")
            print(f"🔗 Original execution: {replay_result['original_execution_id']}")
            print(f"🔗 Replayed execution: {replay_result['replayed_execution_id']}")
            
            if replay_result['hash_match']:
                print("✅ Replay is deterministic!")
            else:
                print("⚠️  Replay shows differences:")
                for diff in replay_result.get('differences', []):
                    print(f"   - {diff}")
                    
        else:
            print(f"❌ Replay failed: {replay_result.get('message', 'Unknown error')}")
            return False
            
    except Exception as e:
        print(f"❌ Replay execution failed: {e}")
        return False
    
    # Step 6: Test system statistics
    print("\n📊 Step 6: System statistics...")
    
    try:
        bucket_stats = gateway.bucket_reader.get_bucket_statistics()
        replay_stats = replay_engine.get_replay_statistics()
        
        print(f"📦 Bucket Statistics:")
        print(f"   Total instructions: {bucket_stats.get('total_instructions', 0)}")
        print(f"   Total artifacts: {bucket_stats.get('total_artifacts', 0)}")
        print(f"   Max lineage depth: {bucket_stats.get('max_lineage_depth', 0)}")
        
        print(f"🔄 Replay Statistics:")
        print(f"   Replayable instructions: {replay_stats.get('replayable_instructions', 0)}")
        print(f"   Replay readiness rate: {replay_stats.get('replay_readiness_rate', 0):.2f}")
        
    except Exception as e:
        print(f"⚠️  Statistics retrieval failed: {e}")
    
    print("\n🎉 Complete Lineage and Replay System Test: SUCCESS!")
    print("=" * 60)
    
    return True

def create_sample_artifacts():
    """Create sample artifacts for demonstration"""
    
    sample_artifacts = {
        "blueprint_artifact": {
            "artifact_id": "artifact_sample_blueprint",
            "artifact_type": "blueprint",
            "instruction_id": "sample_instruction_001",
            "execution_id": "exec_sample_001",
            "source_module_id": "creator_core",
            "payload": {
                "instruction": {
                    "instruction_id": "sample_instruction_001",
                    "target_product": "content",
                    "intent_type": "generate"
                }
            },
            "artifact_hash": "a1b2c3d4e5f6...",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "lineage_depth": 0
        },
        "execution_artifact": {
            "artifact_id": "artifact_sample_execution",
            "artifact_type": "execution",
            "instruction_id": "sample_instruction_001",
            "execution_id": "exec_sample_001",
            "source_module_id": "sample_text",
            "payload": {
                "execution_envelope": {
                    "execution_id": "exec_sample_001",
                    "input_hash": "input_hash_123",
                    "output_hash": "output_hash_456"
                }
            },
            "artifact_hash": "b2c3d4e5f6g7...",
            "parent_hash": "a1b2c3d4e5f6...",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "lineage_depth": 1
        },
        "result_artifact": {
            "artifact_id": "artifact_sample_result",
            "artifact_type": "result",
            "instruction_id": "sample_instruction_001",
            "execution_id": "exec_sample_001",
            "source_module_id": "sample_text",
            "payload": {
                "status": "success",
                "result": {
                    "generated_text": "Sample generated content for lineage demonstration"
                }
            },
            "artifact_hash": "c3d4e5f6g7h8...",
            "parent_hash": "b2c3d4e5f6g7...",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "lineage_depth": 2
        }
    }
    
    return sample_artifacts

if __name__ == "__main__":
    # Run the complete test
    success = test_complete_lineage_replay_system()
    
    if success:
        print("\n✅ All tests passed! System is ready for deployment.")
    else:
        print("\n❌ Tests failed! System needs fixes before deployment.")
    
    # Create sample artifacts for documentation
    samples = create_sample_artifacts()
    
    print("\n📄 Sample Artifacts Created:")
    for artifact_type, artifact in samples.items():
        print(f"   {artifact_type}: {artifact['artifact_id']}")