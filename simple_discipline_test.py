#!/usr/bin/env python3
"""
Simple test for execution discipline components
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.core.registry_validation_logic import RegistryValidator
from src.core.execution_envelope import ExecutionEnvelopeManager
from src.core.hash_generation import ExecutionHashGenerator
import json

def main():
    print("Core Integrator Execution Discipline Test")
    print("=" * 50)
    
    # Test registry validation
    print("Testing registry validation...")
    validator = RegistryValidator()
    result = validator.validate_execution_request("sample_text", "generate", {"text": "test"})
    print(f"Valid module test: {result['valid']}")
    
    # Test execution envelope
    print("Testing execution envelope...")
    manager = ExecutionEnvelopeManager()
    envelope = manager.create_immediate_envelope(
        module_id="sample_text",
        intent="generate", 
        user_id="test_user",
        input_data={"text": "test"},
        output_data={"status": "success", "result": {"processed": True}},
        execution_duration_ms=100.0
    )
    print(f"Envelope generated: {envelope.execution_id}")
    
    # Test hash generation
    print("Testing hash generation...")
    generator = ExecutionHashGenerator()
    fingerprint = generator.generate_execution_fingerprint(
        module_id="sample_text",
        intent="generate",
        user_id="test_user", 
        input_data={"text": "test"},
        output_data={"status": "success", "result": {"processed": True}}
    )
    print(f"Hash fingerprint generated: {len(fingerprint)} hashes")
    
    print("=" * 50)
    print("All tests completed successfully!")

if __name__ == "__main__":
    main()