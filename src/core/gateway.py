from typing import Dict, Any
from ..agents.finance import FinanceAgent
from ..agents.education import EducationAgent
from ..agents.creator import CreatorAgent
from ..agents.video import VideoAgent
from ..modules.base import BaseModule
from .module_loader import load_modules
from .feedback_models import CanonicalFeedbackSchema
from .registry_validation_logic import RegistryValidator, RegistryValidationError
from .execution_envelope import ExecutionEnvelopeManager
from .hash_generation import ExecutionHashGenerator
from ..db.memory import ContextMemory
from ..db.memory_adapter import SQLiteAdapter, RemoteNoopurAdapter, MONGODB_AVAILABLE
from ..utils.logger import setup_logger
from ..utils.bridge_client import BridgeClient
from ..utils.video_bridge_client import VideoBridgeClient
from config.config import DB_PATH, INTEGRATOR_USE_NOOPUR, USE_MONGODB, MONGODB_CONNECTION_STRING, MONGODB_DATABASE_NAME
from pydantic import ValidationError
import time

if MONGODB_AVAILABLE:
    from ..db.mongodb_adapter import MongoDBAdapter
from creator_routing import CreatorRouter
import json
import os

class Gateway:
    """Central gateway for routing requests to appropriate agents"""
    
    def __init__(self):
        # Initialize logger first
        self.logger = setup_logger(__name__)
        
        # Initialize registry validator for strict execution discipline
        self.registry_validator = RegistryValidator()
        
        # Initialize execution envelope manager for traceability
        self.envelope_manager = ExecutionEnvelopeManager()
        
        # Initialize hash generator for replay validation
        self.hash_generator = ExecutionHashGenerator()
        
        # Initialize BridgeClient as canonical external service interface
        self.bridge_client = BridgeClient()
        
        # Initialize VideoBridgeClient for text-to-video service
        self.video_bridge_client = VideoBridgeClient()
        
        # Built-in agents (non-module agents)
        self.agents = {
            "finance": FinanceAgent(),
            "education": EducationAgent(),
            "creator": CreatorAgent(),
            "video": VideoAgent(),
        }

        # Dynamically load modules from modules/ directory
        loaded_modules, errors = load_modules()
        for name, inst in loaded_modules.items():
            # register module instance under its name
            self.agents[name] = inst
        if errors:
            for e in errors:
                self.logger.warning(f"Module loader issue: {e}")
        
        # Memory adapter: MongoDB > Noopur > SQLite (priority order with fallback)
        if USE_MONGODB and MONGODB_AVAILABLE:
            try:
                self.memory = MongoDBAdapter(MONGODB_CONNECTION_STRING, MONGODB_DATABASE_NAME)
                self.logger.info("Using MongoDB adapter")
            except Exception as e:
                self.logger.warning(f"MongoDB connection failed, falling back to SQLite: {e}")
                self.memory = SQLiteAdapter(DB_PATH)
        elif INTEGRATOR_USE_NOOPUR:
            self.memory = RemoteNoopurAdapter()
        else:
            self.memory = SQLiteAdapter(DB_PATH)
        self.creator_router = CreatorRouter(self.memory)
        # Validate module contracts for any module-like entries (modules under /modules should subclass BaseModule)
        for name, mod in list(self.agents.items()):
            # If the object exposes `process`, expect it to be a BaseModule
            if hasattr(mod, 'process'):
                if not isinstance(mod, BaseModule):
                    # replace with an error responder but do not crash
                    self.logger.error(f"Module '{name}' does not implement BaseModule contract. Marking as invalid.")
                    self.agents[name] = None

    def _load_module_metadata(self, module_name: str) -> Dict[str, Any]:
        """Try to load `modules/<module>/config.json` for metadata (optional)."""
        try:
            cfg_path = os.path.join('src', 'modules', module_name, 'config.json')
            if os.path.exists(cfg_path):
                with open(cfg_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
        except Exception:
            pass
        return {}
    
    def check_external_service_health(self) -> Dict[str, Any]:
        """Check external service health using BridgeClient"""
        try:
            health_result = self.bridge_client.health_check()
            if health_result.get('success') is not False:
                return {"status": "healthy", "details": health_result}
            else:
                return {
                    "status": "unhealthy", 
                    "error_type": health_result.get('error_type'),
                    "details": health_result
                }
        except Exception as e:
            return {"status": "unreachable", "error": str(e)}
    
    def validate_feedback(self, data: Dict[str, Any]) -> CanonicalFeedbackSchema:
        """Validate feedback data against canonical schema"""
        try:
            return CanonicalFeedbackSchema(**data)
        except ValidationError as e:
            self.logger.error(f"Feedback validation failed: {e}")
            raise ValueError(f"Invalid feedback schema: {e}")
    
    def process_request(self, module: str, intent: str, user_id: str, 
                       data: Dict[str, Any]) -> Dict[str, Any]:
        """Process incoming request and route to appropriate agent"""
        
        start_time = time.time()
        
        # PART 1: Registry Validation - Enforce strict execution discipline
        try:
            validation_result = self.registry_validator.validate_execution_request(module, intent, data)
            if not validation_result["valid"]:
                # Reject execution immediately - no fallback permitted
                self.logger.error(f"Registry validation failed for module '{module}': {validation_result['error']}")
                return {
                    "status": "error",
                    "message": f"Registry validation failed: {validation_result['error']}",
                    "result": {},
                    "validation_error": True
                }
            
            registry_entry = validation_result["registry_entry"]
            truth_classification_level = registry_entry.truth_classification_level
            
        except Exception as e:
            self.logger.error(f"Registry validation system error: {e}")
            return {
                "status": "error",
                "message": "Registry validation system error",
                "result": {},
                "validation_error": True
            }
        
        # Special validation for feedback requests
        if module == "creator" and intent == "feedback":
            try:
                validated_feedback = self.validate_feedback(data)
                data = validated_feedback.dict()
                self.logger.info(f"Feedback validated successfully for user: {user_id}")
            except ValueError as e:
                return {
                    "status": "error",
                    "message": str(e),
                    "result": {}
                }
        
        # Get user context (adapter provides get_context)
        context = self.memory.get_context(user_id) if user_id else []
        
        # Log request with execution tracing
        self.logger.info(
            f"Processing request for module: {module}, intent: {intent}",
            extra={
                "user_id": user_id, 
                "request_data": {"module": module, "intent": intent, "data": data},
                "registry_validation": "passed",
                "truth_classification_level": truth_classification_level
            }
        )
        
        # Special handling for creator flows: pre-warm with context from Noopur/local memory
        if module == "creator":
            try:
                data = self.creator_router.prewarm_and_prepare(request=user_id and data or {}, user_id=user_id, input_data=data)
            except Exception:
                # fallback to original data
                pass

        # Route to agent
        if module not in self.agents:
            response = {
                "status": "error",
                "message": f"Unknown module: {module}",
                "result": {}
            }
        elif self.agents[module] is None:
            response = {
                "status": "error",
                "message": f"Module {module} is invalid or failed to load",
                "result": {}
            }
        else:
            agent = self.agents[module]
            try:
                # Check if it's a BaseModule (has process method)
                if isinstance(agent, BaseModule):
                    response = agent.process(data, context)
                # Otherwise it's an agent (has handle_request method)
                elif hasattr(agent, 'handle_request'):
                    response = agent.handle_request(intent, data, context)
                else:
                    response = {
                        "status": "error",
                        "message": f"Module {module} has invalid interface",
                        "result": {}
                    }
            except Exception as e:
                self.logger.exception(f"Agent processing failed for {module}")
                response = {
                    "status": "error",
                    "message": f"Agent processing failed: {str(e)}",
                    "result": {}
                }
        
        # Calculate execution duration
        execution_duration_ms = (time.time() - start_time) * 1000
        
        # Normalize response into standardized CoreResponse shape (do not rely on module to emit full CoreResponse)
        normalized = {
            'status': 'success',
            'message': '',
            'result': {}
        }

        # If module returned a mapping, interpret intelligently
        if isinstance(response, dict):
            # If module returned keys 'status'/'message'/'result', use them; else treat whole dict as result
            normalized['status'] = response.get('status', 'success')
            normalized['message'] = response.get('message', '')
            if 'result' in response:
                normalized['result'] = response.get('result', {})
            else:
                # module returned raw payload -> put under result
                # avoid copying status/message keys into result
                raw = {k: v for k, v in response.items() if k not in ('status', 'message', 'result')}
                normalized['result'] = raw
        
        # PART 2: Generate Execution Envelope - Standardized execution tracing
        try:
            execution_envelope = self.envelope_manager.create_immediate_envelope(
                module_id=module,
                intent=intent,
                user_id=user_id,
                input_data=data,
                output_data=normalized,
                schema_version=registry_entry.schema_version,
                truth_classification_level=truth_classification_level,
                execution_duration_ms=execution_duration_ms
            )
            
            # Add envelope to response for traceability
            normalized['execution_envelope'] = self.envelope_manager.generator.envelope_to_dict(execution_envelope)
            
            # PART 3: Generate Replay Hashes - Deterministic hashing for replay validation
            hash_fingerprint = self.hash_generator.generate_execution_fingerprint(
                module_id=module,
                intent=intent,
                user_id=user_id,
                input_data=data,
                output_data=normalized
            )
            
            # Add hashes to envelope
            normalized['execution_envelope'].update(hash_fingerprint)
            
        except Exception as e:
            self.logger.error(f"Execution envelope generation failed: {e}")
            # Continue execution but log the failure

        # Store interaction
        if user_id:
            request_data = {"module": module, "intent": intent, "user_id": user_id, "data": data}
            try:
                self.memory.store_interaction(user_id, request_data, normalized)
            except Exception:
                self.logger.exception("Failed to store interaction")

        # PART 4: Execution Logging Alignment - Structured log event for telemetry
        try:
            execution_trace_log = {
                "execution_id": normalized.get('execution_envelope', {}).get('execution_id', 'unknown'),
                "module_id": module,
                "intent": intent,
                "user_id": user_id,
                "timestamp": normalized.get('execution_envelope', {}).get('timestamp_utc', ''),
                "input_hash": normalized.get('execution_envelope', {}).get('input_hash', ''),
                "output_hash": normalized.get('execution_envelope', {}).get('output_hash', ''),
                "semantic_hash": normalized.get('execution_envelope', {}).get('semantic_hash', ''),
                "status": normalized.get('status'),
                "execution_duration_ms": execution_duration_ms,
                "truth_classification_level": truth_classification_level
            }
            
            # Emit structured log through InsightFlow telemetry
            self.logger.info(
                "Execution trace event",
                extra={
                    "event_type": "execution_trace",
                    "execution_trace": execution_trace_log,
                    "telemetry_target": "insightflow"
                }
            )
            
        except Exception as e:
            self.logger.error(f"Execution trace logging failed: {e}")

        # Log response with execution envelope metadata
        try:
            self.logger.info(
                f"Request processed with status: {normalized.get('status')}",
                extra={
                    "user_id": user_id, 
                    "response_data": normalized,
                    "execution_envelope_id": normalized.get('execution_envelope', {}).get('execution_id'),
                    "replay_ready": True
                }
            )
        except Exception:
            pass

        return normalized