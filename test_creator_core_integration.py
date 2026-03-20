#!/usr/bin/env python3
"""
Test Creator Core instruction processing
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.core.gateway import Gateway
import json
from datetime import datetime

def test_creator_core_instruction():
    """Test Creator Core instruction processing"""
    print("Testing Creator Core Instruction Processing")
    print("=" * 50)
    
    # Initialize gateway
    gateway = Gateway()
    
    # Create Creator Core instruction
    creator_core_instruction = {
        "instruction_id": "inst_cc_001",
        "origin": "creator_core",
        "intent_type": "generate",
        "target_product": "content",
        "payload": {
            "blueprint_type": "content_generation",
            "text": "Create engaging content about AI innovation",
            "type": "article",
            "goal": "inform"
        },
        "schema_version": "1.0.0",
        "timestamp": datetime.utcnow().isoformat()
    }
    
    print("1. Testing Creator Core instruction...")
    print(f"   Instruction ID: {creator_core_instruction['instruction_id']}")
    print(f"   Target Product: {creator_core_instruction['target_product']}")
    print(f"   Intent Type: {creator_core_instruction['intent_type']}")
    
    # Process instruction (pass as data parameter)
    response = gateway.process_request(
        module="",  # Not used for Creator Core instructions
        intent="",  # Not used for Creator Core instructions  
        user_id="",  # Not used for Creator Core instructions
        data=creator_core_instruction
    )
    
    print(f"   Status: {response.get('status')}")
    print(f"   Message: {response.get('message', 'No message')}")
    
    # Check execution envelope
    if 'execution_envelope' in response:
        envelope = response['execution_envelope']
        print(f"   Execution ID: {envelope.get('execution_id')}")
        print(f"   Instruction ID: {envelope.get('instruction_id')}")
        print(f"   Module ID: {envelope.get('module_id')}")
        print(f"   Input Hash: {envelope.get('input_hash', '')[:16]}...")
        print(f"   Output Hash: {envelope.get('output_hash', '')[:16]}...")
        
        # Save example
        with open("creator_core_instruction_example.json", "w") as f:
            json.dump(response, f, indent=2)
        print(f"   Saved to: creator_core_instruction_example.json")
    
    print()
    
    # Test invalid instruction
    print("2. Testing invalid Creator Core instruction...")
    invalid_instruction = {
        "instruction_id": "inst_cc_002",
        "origin": "invalid_origin",  # Invalid origin
        "intent_type": "generate",
        "target_product": "content",
        "payload": {"text": "test"},
        "schema_version": "1.0.0",
        "timestamp": datetime.utcnow().isoformat()
    }
    
    invalid_response = gateway.process_request(
        module="", intent="", user_id="", data=invalid_instruction
    )
    
    print(f"   Status: {invalid_response.get('status')}")
    print(f"   Message: {invalid_response.get('message')}")
    print(f"   Instruction Error: {invalid_response.get('instruction_error', False)}")
    
    print()
    
    # Test traditional module request
    print("3. Testing traditional module request...")
    traditional_request = {
        "text": "Traditional module request test"
    }
    
    traditional_response = gateway.process_request(
        module="sample_text",
        intent="generate", 
        user_id="test_user",
        data=traditional_request
    )
    
    print(f"   Status: {traditional_response.get('status')}")
    print(f"   Has Execution Envelope: {'execution_envelope' in traditional_response}")
    
    print()
    print("=" * 50)
    print("Creator Core integration test completed")

if __name__ == "__main__":
    test_creator_core_instruction()