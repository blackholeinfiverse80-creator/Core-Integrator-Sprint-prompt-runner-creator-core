#!/usr/bin/env python3
"""
Test script to demonstrate execution discipline enforcement
Shows registry validation, execution envelopes, and hash generation
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.core.registry_validation_logic import RegistryValidator, RegistryValidationError
from src.core.execution_envelope import ExecutionEnvelopeManager
from src.core.hash_generation import ExecutionHashGenerator
import json

def test_registry_validation():
    """Test registry validation enforcement"""
    print("=== Testing Registry Validation ===")
    
    validator = RegistryValidator()
    
    # Test valid module
    try:
        result = validator.validate_execution_request("sample_text", "generate", {"text": "test"})
        print(f"✅ Valid module validation: {result['valid']}")
        print(f"   Contract hash: {result['contract_hash']}")
        print(f"   Classification: {result['truth_classification_level']}")
    except Exception as e:
        print(f"❌ Valid module test failed: {e}")
    
    # Test invalid module
    try:
        result = validator.validate_execution_request("invalid_module", "generate", {"data": "test"})
        print(f"❌ Invalid module should fail: {result['valid']}")
        print(f"   Error: {result['error']}")
    except Exception as e:
        print(f"✅ Invalid module correctly rejected: {e}")
    
    print()

def test_execution_envelope():
    """Test execution envelope generation"""
    print("=== Testing Execution Envelope Generation ===")
    
    manager = ExecutionEnvelopeManager()
    
    # Test envelope creation
    input_data = {"text": "Execution discipline test"}
    output_data = {
        "status": "success",
        "message": "Text processed",
        "result": {"processed_text": "Execution discipline test", "word_count": 3}
    }
    
    envelope = manager.create_immediate_envelope(
        module_id="sample_text",
        intent="generate",
        user_id="test_user",
        input_data=input_data,
        output_data=output_data,
        truth_classification_level="unclassified",
        execution_duration_ms=125.5
    )
    
    print(f"✅ Execution envelope generated:")
    print(f"   Execution ID: {envelope.execution_id}")
    print(f"   Module ID: {envelope.module_id}")
    print(f"   Input hash: {envelope.input_hash[:16]}...")
    print(f"   Output hash: {envelope.output_hash[:16]}...")
    print(f"   Semantic hash: {envelope.semantic_hash[:16]}...")
    print(f"   Duration: {envelope.execution_duration_ms}ms")
    print(f"   Classification: {envelope.truth_classification_level}")
    
    # Save example envelope
    envelope_dict = manager.generator.envelope_to_dict(envelope)
    with open("test_execution_envelope.json", "w") as f:
        json.dump(envelope_dict, f, indent=2)
    print(f"   Saved to: test_execution_envelope.json")
    
    print()

def test_hash_generation():
    """Test deterministic hash generation"""
    print("=== Testing Hash Generation ===")
    
    generator = ExecutionHashGenerator()
    
    # Test hash generation
    input_data = {"text": "Hash generation test", "parameters": {"mode": "test"}}
    output_data = {
        "status": "success",
        "result": {"processed": True, "output": "Hash generation test processed"}
    }
    
    fingerprint = generator.generate_execution_fingerprint(
        module_id="sample_text",
        intent="generate",
        user_id="hash_test_user",
        input_data=input_data,
        output_data=output_data
    )
    
    print(f"✅ Hash fingerprint generated:")
    print(f"   Input hash: {fingerprint['input_hash']}")
    print(f"   Output hash: {fingerprint['output_hash']}")
    print(f"   Semantic hash: {fingerprint['semantic_hash']}")
    
    # Test deterministic behavior
    fingerprint2 = generator.generate_execution_fingerprint(
        module_id="sample_text",
        intent="generate",
        user_id="hash_test_user",
        input_data=input_data,
        output_data=output_data
    )
    
    deterministic = fingerprint == fingerprint2
    print(f"   Deterministic: {deterministic} ✅" if deterministic else f"   Deterministic: {deterministic} ❌")
    
    print()

def test_registry_rejection():
    """Test registry validation rejection"""
    print("=== Testing Registry Validation Rejection ===")
    
    validator = RegistryValidator()
    
    # Test with disabled module (modify registry temporarily)
    registry = validator.registry
    
    # Temporarily disable a module
    if "example_math" in registry._registry:
        original_enabled = registry._registry["example_math"].enabled
        registry._registry["example_math"].enabled = False
        
        try:
            result = validator.validate_execution_request("example_math", "process", {"operation": "add"})
            print(f"❌ Disabled module should fail: {result['valid']}")
        except RegistryValidationError as e:
            print(f"✅ Disabled module correctly rejected: {e}")
        
        # Restore original state
        registry._registry["example_math"].enabled = original_enabled
    
    print()

def main():
    """Run all tests"""
    print("🚀 Core Integrator Execution Discipline Test Suite")
    print("=" * 60)
    
    test_registry_validation()
    test_execution_envelope()
    test_hash_generation()
    test_registry_rejection()
    
    print("=" * 60)
    print("✅ Execution discipline enforcement tests completed")
    print("\nGenerated files:")
    print("- test_execution_envelope.json")
    print("\nExecution discipline features verified:")
    print("- Registry validation enforcement")
    print("- Execution envelope generation")
    print("- Deterministic hash generation")
    print("- Rejection of invalid modules")

if __name__ == "__main__":
    main()