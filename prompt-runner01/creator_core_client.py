"""Creator Core integration client

Provides a single function `send_to_creator_core(instruction_json)` that sends
the instruction JSON to Creator Core and returns the blueprint JSON on success
or a structured error on failure.
"""

from typing import Any, Dict
import re
import os

import requests


def _load_local_env(path: str = ".env.local") -> None:
    """Load simple KEY=VALUE lines from a local env file into os.environ.
    This mirrors the loader used in `llm_adapter.py` so env vars in `.env.local`
    are available during module import.
    """
    try:
        base = os.path.dirname(__file__)
        env_path = os.path.join(base, path)
        if not os.path.exists(env_path):
            return
        with open(env_path, "r", encoding="utf-8") as fh:
            for raw in fh:
                line = raw.strip()
                if not line or line.startswith("#"):
                    continue
                if "=" not in line:
                    continue
                k, v = line.split("=", 1)
                k = k.strip()
                v = v.strip().strip('"').strip("'")
                if k and not os.environ.get(k):
                    os.environ[k] = v
    except Exception:
        pass


# Load .env.local early so CREATOR_CORE_URL reads the file value during import
_load_local_env()

CREATOR_CORE_URL = os.getenv("CREATOR_CORE_URL", "http://127.0.0.1:8000/creator-core/generate-blueprint")
REQUEST_TIMEOUT = int(os.getenv("CREATOR_CORE_TIMEOUT", "10"))


def normalize_text(value: str) -> str:
    """Normalize text to deterministic snake_case."""
    if not isinstance(value, str):
        return ""
    value = value.lower()
    value = re.sub(r"[^a-z0-9\s_]", "", value)
    value = re.sub(r"\s+", "_", value.strip())
    value = re.sub(r"_+", "_", value)
    return value.strip("_")


def normalize_instruction(input_json: Dict[str, Any]) -> Dict[str, Any]:
    """Normalize nested or flat instruction JSON into flat Creator Core schema."""
    if not isinstance(input_json, dict):
        return {}

    # Unwrap if instruction is nested under top-level "instruction"
    instruction = input_json.get("instruction") if isinstance(input_json.get("instruction"), dict) else input_json

    data = instruction.get("data") if isinstance(instruction.get("data"), dict) else {}

    prompt = data.get("original_prompt") or instruction.get("prompt") or ""
    topic = data.get("topic") or instruction.get("topic") or ""
    if not topic and prompt:
        topic = normalize_text(prompt)

    tasks_raw = instruction.get("tasks") if isinstance(instruction.get("tasks"), list) else []
    tasks = [normalize_text(t) for t in tasks_raw if isinstance(t, str) and normalize_text(t)]

    normalized = {
        "prompt": prompt,
        "module": instruction.get("module") or "",
        "intent": instruction.get("intent") or "",
        "topic": normalize_text(topic),
        "tasks": tasks,
        "output_format": instruction.get("output_format") or "",
        "product_context": "creator_core",
    }
    return normalized


def _normalize_blueprint_response(response_json: Dict[str, Any], instruction_payload: Dict[str, Any]) -> Dict[str, Any]:
    """Normalize Creator Core blueprint response formatting deterministically."""
    if not isinstance(response_json, dict):
        return {"status": "error", "message": "Creator Core returned non-JSON response"}

    payload = response_json.get("payload") if isinstance(response_json.get("payload"), dict) else {}

    title_source = payload.get("title") or instruction_payload.get("topic") or instruction_payload.get("prompt")
    outline_source = payload.get("outline") if isinstance(payload.get("outline"), list) else instruction_payload.get("tasks", [])
    normalized_outline = [normalize_text(i) for i in outline_source if isinstance(i, str) and normalize_text(i)]

    normalized_payload = {
        "blueprint_type": payload.get("blueprint_type", "content_blueprint"),
        "product_target": payload.get("product_target", response_json.get("target_product", "")),
        "content_type": payload.get("content_type", instruction_payload.get("output_format", "")),
        "title": normalize_text(title_source or ""),
        "outline": normalized_outline,
    }

    response_json["payload"] = normalized_payload
    return response_json


def _validate_instruction_payload(payload: Dict[str, Any]) -> Dict[str, Any]:
    """Return empty dict when valid, otherwise structured error payload."""
    required = [
        "prompt",
        "module",
        "intent",
        "topic",
        "tasks",
        "output_format",
        "product_context",
    ]

    for field in required:
        if field not in payload:
            return {"status": "error", "message": f"Missing or invalid field: {field}"}

    if not isinstance(payload.get("prompt"), str) or not payload["prompt"].strip():
        return {"status": "error", "message": "Missing or invalid field: prompt"}

    if not isinstance(payload.get("module"), str) or not payload["module"].strip():
        return {"status": "error", "message": "Missing or invalid field: module"}

    if not isinstance(payload.get("intent"), str) or not payload["intent"].strip():
        return {"status": "error", "message": "Missing or invalid field: intent"}

    if not isinstance(payload.get("topic"), str) or not payload["topic"].strip():
        return {"status": "error", "message": "Missing or invalid field: topic"}

    if not isinstance(payload.get("tasks"), list) or not all(isinstance(t, str) for t in payload["tasks"]):
        return {"status": "error", "message": "Missing or invalid field: tasks"}

    if not isinstance(payload.get("output_format"), str) or not payload["output_format"].strip():
        return {"status": "error", "message": "Missing or invalid field: output_format"}

    if payload.get("product_context") != "creator_core":
        return {"status": "error", "message": "Missing or invalid field: product_context"}

    return {}


def send_to_creator_core(input_json: Dict[str, Any]) -> Dict[str, Any]:
    """Send the instruction JSON to Creator Core.

    Args:
        instruction_json: The instruction payload (dict).

    Returns:
        On success (HTTP 200) returns Creator Core JSON response (parsed).
        On failure returns a dict: {"status": "error", "message": "Creator Core request failed"}
    """
    normalized_payload = normalize_instruction(input_json)

    validation_error = _validate_instruction_payload(normalized_payload)
    if validation_error:
        return validation_error

    print("FINAL PAYLOAD:", normalized_payload)

    headers = {"Content-Type": "application/json"}
    try:
        resp = requests.post(CREATOR_CORE_URL, json=normalized_payload, headers=headers, timeout=REQUEST_TIMEOUT)
        if resp.status_code == 200:
            try:
                return _normalize_blueprint_response(resp.json(), normalized_payload)
            except Exception:
                return {"status": "error", "message": "Creator Core returned non-JSON response"}
        # non-200
        return {
            "status": "error",
            "message": "Creator Core request failed",
            "http_status": resp.status_code,
            "url": CREATOR_CORE_URL,
            "response_text": (resp.text or "")[:300],
        }
    except requests.RequestException as exc:
        return {
            "status": "error",
            "message": "Creator Core request failed",
            "url": CREATOR_CORE_URL,
            "error": str(exc),
        }
  