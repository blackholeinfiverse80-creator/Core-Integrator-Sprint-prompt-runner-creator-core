"""InsightFlow telemetry payload generator

Produces deterministic, structured events suitable for InsightFlow ingestion and offline testing.
Enhanced with deep linking for instruction → execution → artifact traceability.
"""
from datetime import datetime, timezone
from typing import Dict, Any, List, Optional

INSIGHTFLOW_VERSION = "1.0.0"


def timestamp_iso(ts: Optional[datetime] = None) -> str:
    return (ts or datetime.now(timezone.utc)).isoformat()


def make_event(event_type: str, component: str, status: str, details: Dict[str, Any] = None,
               integration_score: Optional[float] = None, failing_components: Optional[List[str]] = None,
               timestamp: Optional[datetime] = None) -> Dict[str, Any]:
    payload = {
        "insightflow_version": INSIGHTFLOW_VERSION,
        "event_type": event_type,
        "component": component,
        "status": status,
        "details": details or {},
        "timestamp": timestamp_iso(timestamp)
    }
    if integration_score is not None:
        payload["integration_score"] = float(integration_score)
    if failing_components is not None:
        payload["failing_components"] = list(failing_components)
    return payload


def make_lineage_event(
    event_type: str,
    instruction_id: str,
    execution_id: str,
    artifact_hash: Optional[str] = None,
    component: str = "core_integrator",
    status: str = "success",
    details: Dict[str, Any] = None,
    timestamp: Optional[datetime] = None
) -> Dict[str, Any]:
    """
    Create InsightFlow event with deep linking for lineage traceability
    
    Args:
        event_type: Type of event (instruction.received, execution.started, etc.)
        instruction_id: Creator Core instruction ID
        execution_id: Execution ID from routing engine
        artifact_hash: Hash of associated artifact
        component: Component generating the event
        status: Event status
        details: Additional event details
        timestamp: Event timestamp
        
    Returns:
        InsightFlow event with lineage linking
    """
    event_details = details or {}
    
    # Add mandatory lineage fields
    event_details.update({
        "instruction_id": instruction_id,
        "execution_id": execution_id
    })
    
    # Add artifact hash if provided
    if artifact_hash:
        event_details["artifact_hash"] = artifact_hash
    
    # Add trace context for full lineage
    event_details["trace_context"] = {
        "instruction_id": instruction_id,
        "execution_id": execution_id,
        "artifact_hash": artifact_hash,
        "event_sequence": event_type
    }
    
    return make_event(
        event_type=event_type,
        component=component,
        status=status,
        details=event_details,
        timestamp=timestamp
    )


def make_artifact_event(
    artifact_id: str,
    artifact_type: str,
    instruction_id: str,
    execution_id: str,
    artifact_hash: str,
    parent_hash: Optional[str] = None,
    lineage_depth: int = 0,
    status: str = "created",
    details: Dict[str, Any] = None,
    timestamp: Optional[datetime] = None
) -> Dict[str, Any]:
    """
    Create InsightFlow event for artifact creation with full lineage context
    
    Args:
        artifact_id: Unique artifact identifier
        artifact_type: Type of artifact (blueprint, execution, result)
        instruction_id: Creator Core instruction ID
        execution_id: Execution ID
        artifact_hash: Artifact hash
        parent_hash: Parent artifact hash for lineage
        lineage_depth: Depth in lineage chain
        status: Artifact status
        details: Additional details
        timestamp: Event timestamp
        
    Returns:
        InsightFlow event for artifact with lineage
    """
    event_details = details or {}
    
    # Add artifact-specific fields
    event_details.update({
        "artifact_id": artifact_id,
        "artifact_type": artifact_type,
        "artifact_hash": artifact_hash,
        "lineage_depth": lineage_depth
    })
    
    # Add parent relationship if exists
    if parent_hash:
        event_details["parent_hash"] = parent_hash
    
    # Add full lineage context
    event_details["lineage_context"] = {
        "instruction_id": instruction_id,
        "execution_id": execution_id,
        "artifact_chain": {
            "current_hash": artifact_hash,
            "parent_hash": parent_hash,
            "depth": lineage_depth
        }
    }
    
    return make_lineage_event(
        event_type="artifact.created",
        instruction_id=instruction_id,
        execution_id=execution_id,
        artifact_hash=artifact_hash,
        component="bucket_system",
        status=status,
        details=event_details,
        timestamp=timestamp
    )
