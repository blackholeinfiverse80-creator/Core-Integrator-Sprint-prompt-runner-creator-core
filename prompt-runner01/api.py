"""
Prompt Runner - FastAPI Service
================================
Converts any user prompt into a structured JSON instruction using the Groq API.

Required environment variable:
    GROQ_API_KEY=gsk_...   (get yours at console.groq.com)

Start:
    uvicorn api:app --host 0.0.0.0 --port 8001

Endpoints:
    POST /generate   — prompt  structured JSON instruction
    GET  /health     — Groq availability check
    GET  /schema     — JSON Schema for the instruction format
    GET  /models     — list available Groq models
"""

# **IMPORTANT**: Load .env.local FIRST before any other imports
import os
_env_path = os.path.join(os.path.dirname(__file__), '.env.local')
if os.path.exists(_env_path):
    try:
        with open(_env_path, 'r', encoding='utf-8') as _f:
            for _line in _f:
                _line = _line.strip()
                if _line and '=' in _line and not _line.startswith('#'):
                    _k, _v = _line.split('=', 1)
                    _k = _k.strip()
                    _v = _v.strip().strip('"').strip("'")
                    if _k and not os.environ.get(_k):
                        os.environ[_k] = _v
    except Exception:
        pass

from typing import Any, Dict, List, Optional

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from creator_core_client import send_to_creator_core
from llm_adapter import LLMAdapter, DEFAULT_MODEL

# ---------------------------------------------------------------------------
# App
# ---------------------------------------------------------------------------

app = FastAPI(
    title="Prompt Runner API",
    description="Converts any user prompt into a deterministic JSON instruction via Groq API.",
    version="5.0.0",
)



app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---------------------------------------------------------------------------
# JSON Schema (served at /schema)
# ---------------------------------------------------------------------------

INSTRUCTION_SCHEMA: Dict[str, Any] = {
    "$schema": "http://json-schema.org/draft-07/schema#",
    "title": "Prompt Runner Instruction",
    "type": "object",
    "properties": {
        "prompt":          {"type": "string"},
        "module":          {"type": "string"},
        "intent":          {"type": "string"},
        "topic":           {"type": "string"},
        "tasks":           {"type": "array", "items": {"type": "string"}, "minItems": 1},
        "output_format":   {"type": "string"},
        "product_context": {"type": "string", "enum": ["creator_core"]},
    },
    "required": ["prompt", "module", "intent", "topic", "tasks", "output_format", "product_context"],
    "additionalProperties": False,
}

# ---------------------------------------------------------------------------
# Singleton adapter
# ---------------------------------------------------------------------------

_llm: Optional[LLMAdapter] = None


def _get_llm() -> LLMAdapter:
    global _llm
    if _llm is None:
        _llm = LLMAdapter()   # reads GROQ_API_KEY from environment / .env.local
    return _llm


# ---------------------------------------------------------------------------
# Pydantic models
# ---------------------------------------------------------------------------

class PromptRequest(BaseModel):
    prompt: str           = Field(..., min_length=1, description="User prompt to interpret")
    model:  Optional[str] = Field(None, description="Groq model override")


class InstructionResponse(BaseModel):
    prompt:          str
    module:          str
    intent:          str
    topic:           str
    tasks:           List[str]
    output_format:   str
    product_context: str = "creator_core"


class HealthResponse(BaseModel):
    status:         str
    groq_available: bool
    models:         List[str]


class RunRequest(BaseModel):
    prompt: Optional[str] = Field(None, description="User prompt to run end-to-end")


# ---------------------------------------------------------------------------
# Endpoints
# ---------------------------------------------------------------------------

@app.get("/health", response_model=HealthResponse, tags=["system"])
def health_check():
    """Check Groq API availability."""
    llm = _get_llm()
    llm.reset_availability_cache()
    return HealthResponse(
        status         = "healthy",
        groq_available = llm.available,
        models         = llm.client.list_models() if llm.available else [],
    )


@app.post("/generate", response_model=InstructionResponse, tags=["core"])
def generate_instruction(request: PromptRequest):
    """
    Convert a user prompt into a structured JSON instruction via Groq API.

    Output always contains exactly these 6 keys:
    {
        "prompt": "...",
        "module": "...",
        "intent": "...",
        "topic": "...",
        "tasks": ["...", "..."],
        "output_format": "..."
    }
    """
    llm = _get_llm()
    llm.reset_availability_cache()

    if not llm.available:
        raise HTTPException(
            status_code=503,
            detail="GROQ_API_KEY is not configured. Set it as an environment variable.",
        )

    

    if request.model:
        llm.client.model = request.model
        llm.reset_availability_cache()

    try:
        instruction = llm.generate_instruction(request.prompt)
        return InstructionResponse(**instruction)
    except HTTPException as http_exc:
        raise http_exc  # preserve original status code
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))


@app.post("/run", tags=["core"])
def run_prompt(request: RunRequest):
    """Generate instruction and forward it to Creator Core in one request."""
    prompt = (request.prompt or "").strip() if request else ""
    if not prompt:
        # CHANGED: use proper HTTP status code for client input errors
        raise HTTPException(status_code=400, detail="prompt is required")

    llm = _get_llm()
    llm.reset_availability_cache()
    if not llm.available:
        raise HTTPException(
            status_code=503,
            detail="GROQ_API_KEY is not configured. Set it as an environment variable.",
        )

    try:
        print("USER PROMPT:", prompt)
        instruction = llm.generate_instruction(prompt)
        # CHANGED: only set product_context when missing
        if "product_context" not in instruction:
            instruction["product_context"] = "creator_core"

        # CHANGED: strict instruction validation before sending to Creator Core
        required_fields = [
            "prompt",
            "module",
            "intent",
            "topic",
            "tasks",
            "output_format",
        ]
        for field in required_fields:
            if field not in instruction:
                raise HTTPException(status_code=400, detail=f"Missing field: {field}")

        if not isinstance(instruction["tasks"], list):
            raise HTTPException(status_code=400, detail="tasks must be a list")

        if not instruction["prompt"]:
            raise HTTPException(status_code=400, detail="prompt cannot be empty")

        print("INSTRUCTION:", instruction)

        blueprint = send_to_creator_core(instruction)
        print("BLUEPRINT:", blueprint)
        # Persist last blueprint to a local file for debugging when running under uvicorn
        try:
            import json, time, os
            os.makedirs("logs", exist_ok=True)
            with open(os.path.join("logs", f"last_blueprint_{int(time.time())}.json"), "w", encoding="utf-8") as fh:
                json.dump(blueprint, fh, ensure_ascii=False, indent=2)
        except Exception:
            pass

        # CHANGED: propagate Creator Core errors with 502
        if isinstance(blueprint, dict) and blueprint.get("status") == "error":
            raise HTTPException(
                status_code=502,
                detail=blueprint.get("message", "Creator Core failed"),
            )

        # CHANGED: standardized success response wrapper
        return {
            "status": "success",
            "data": {
                "instruction": instruction,
                "blueprint": blueprint,
            },
        }
    except HTTPException as http_exc:
        raise http_exc  # preserve original status code
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))


@app.get("/schema", tags=["system"])
def get_schema():
    """Return the JSON Schema for the instruction output format."""
    return INSTRUCTION_SCHEMA


@app.get("/models", tags=["system"])
def list_models():
    """List available Groq models."""
    llm = _get_llm()
    llm.reset_availability_cache()
    return {
        "groq_available": llm.available,
        "models":         llm.client.list_models() if llm.available else [],
        "default_model":  DEFAULT_MODEL,
    }
    
    
    
    
    