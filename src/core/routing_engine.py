"""
Routing Engine
Executes Creator Core instructions through deterministic routing
"""

import time
from typing import Dict, Any
from .creator_core_parser import RoutingDecision
from .execution_envelope import ExecutionEnvelopeManager
from .hash_generation import ExecutionHashGenerator
from ..utils.logger import setup_logger

class RoutingEngine:
    """Executes instructions through deterministic routing"""
    
    def __init__(self, agents: Dict[str, Any], memory):
        self.agents = agents
        self.memory = memory
        self.logger = setup_logger(__name__)
        self.envelope_manager = ExecutionEnvelopeManager()
        self.hash_generator = ExecutionHashGenerator()
    
    def execute_instruction(self, instruction: Dict[str, Any], routing_decision: RoutingDecision, start_time: float) -> Dict[str, Any]:
        """
        Execute instruction through routing decision
        
        Args:
            instruction: Original Creator Core instruction
            routing_decision: Parsed routing decision
            start_time: Execution start time
            
        Returns:
            Execution result with envelope
        """
        instruction_id = instruction.get('instruction_id')
        
        # Log execution started
        self.logger.info(
            "Instruction execution started",
            extra={
                "event_type": "execution.started",
                "instruction_id": instruction_id,
                "target_product": routing_decision.target_product,
                "module_path": routing_decision.module_path,
                "telemetry_target": "insightflow"
            }
        )
        
        try:
            # Execute through module
            execution_result = self._execute_through_module(
                module_name=routing_decision.module_path,
                intent=routing_decision.execution_intent,
                data=routing_decision.execution_data,
                instruction_id=instruction_id
            )
            
            # Calculate execution duration
            execution_duration_ms = (time.time() - start_time) * 1000
            
            # Generate execution envelope
            envelope = self._generate_instruction_envelope(
                instruction=instruction,
                routing_decision=routing_decision,
                execution_result=execution_result,
                execution_duration_ms=execution_duration_ms
            )
            
            # Add envelope to result
            execution_result['execution_envelope'] = self.envelope_manager.generator.envelope_to_dict(envelope)
            
            # Generate hashes
            hash_fingerprint = self.hash_generator.generate_execution_fingerprint(
                module_id=routing_decision.module_path,
                intent=routing_decision.execution_intent,
                user_id=instruction_id,  # Use instruction_id as user_id for tracing
                input_data=routing_decision.execution_data,
                output_data=execution_result
            )
            
            # Add hashes to envelope
            execution_result['execution_envelope'].update(hash_fingerprint)
            
            # Log execution completed
            self.logger.info(
                "Instruction execution completed",
                extra={
                    "event_type": "execution.completed",
                    "instruction_id": instruction_id,
                    "execution_id": envelope.execution_id,
                    "status": execution_result.get('status'),
                    "execution_duration_ms": execution_duration_ms,
                    "telemetry_target": "insightflow"
                }
            )
            
            # Emit to Bucket
            self._emit_to_bucket(instruction, execution_result, envelope)
            
            return execution_result
            
        except Exception as e:
            self.logger.error(f"Instruction execution failed: {e}")
            return {
                "status": "error",
                "message": f"Execution failed: {str(e)}",
                "result": {},
                "instruction_id": instruction_id
            }
    
    def _execute_through_module(self, module_name: str, intent: str, data: Dict[str, Any], instruction_id: str) -> Dict[str, Any]:
        """Execute through specified module"""
        
        if module_name not in self.agents:
            raise ValueError(f"Module {module_name} not found")
        
        agent = self.agents[module_name]
        if agent is None:
            raise ValueError(f"Module {module_name} is invalid or failed to load")
        
        # Get context (empty for instruction-based execution)
        context = []
        
        # Execute through agent
        if hasattr(agent, 'process'):
            # BaseModule interface
            response = agent.process(data, context)
        elif hasattr(agent, 'handle_request'):
            # Agent interface
            response = agent.handle_request(intent, data, context)
        else:
            raise ValueError(f"Module {module_name} has invalid interface")
        
        # Normalize response
        normalized = {
            'status': 'success',
            'message': '',
            'result': {}
        }
        
        if isinstance(response, dict):
            normalized['status'] = response.get('status', 'success')
            normalized['message'] = response.get('message', '')
            if 'result' in response:
                normalized['result'] = response.get('result', {})
            else:
                raw = {k: v for k, v in response.items() if k not in ('status', 'message', 'result')}
                normalized['result'] = raw
        
        return normalized
    
    def _generate_instruction_envelope(self, instruction: Dict[str, Any], routing_decision: RoutingDecision, 
                                     execution_result: Dict[str, Any], execution_duration_ms: float):
        """Generate execution envelope for instruction"""
        
        return self.envelope_manager.create_immediate_envelope(
            module_id=routing_decision.module_path,
            intent=routing_decision.execution_intent,
            user_id=instruction.get('instruction_id'),
            input_data=routing_decision.execution_data,
            output_data=execution_result,
            schema_version=instruction.get('schema_version', '1.0.0'),
            truth_classification_level='unclassified',  # Default for Creator Core instructions
            parent_execution_id=instruction.get('parent_instruction_id'),
            execution_duration_ms=execution_duration_ms,
            instruction_id=instruction.get('instruction_id'),
            parent_instruction_id=instruction.get('parent_instruction_id')
        )
    
    def _emit_to_bucket(self, instruction: Dict[str, Any], execution_result: Dict[str, Any], envelope):
        """Emit execution artifact to Bucket"""
        try:
            bucket_artifact = {
                "artifact_type": "execution_result",
                "source": "core_integrator",
                "instruction_id": instruction.get('instruction_id'),
                "execution_id": envelope.execution_id,
                "target_product": instruction.get('target_product'),
                "payload": execution_result,
                "hash": envelope.output_hash,
                "timestamp": envelope.timestamp_utc
            }
            
            # Log bucket emission (actual bucket integration would go here)
            self.logger.info(
                "Artifact emitted to Bucket",
                extra={
                    "event_type": "bucket.artifact_stored",
                    "instruction_id": instruction.get('instruction_id'),
                    "execution_id": envelope.execution_id,
                    "artifact_type": "execution_result",
                    "telemetry_target": "bucket"
                }
            )
            
        except Exception as e:
            self.logger.error(f"Bucket emission failed: {e}")