"""
Simple BHIV Orchestration
=========================
Just connects: Prompt Runner → Creator Core → BHIV Core → Done

No extra features, just integration.
"""

import requests
import json
from datetime import datetime
from typing import Dict, Any


class SimpleOrchestrator:
    """Simple orchestration of existing BHIV components"""
    
    def __init__(self):
        self.prompt_runner_url = "http://127.0.0.1:8003"
        self.creator_core_url = "http://127.0.0.1:8000" 
        self.bhiv_core_url = "http://127.0.0.1:8002"  # Changed to 8002 to avoid conflict
    
    def execute(self, prompt: str) -> Dict[str, Any]:
        """Execute the full pipeline"""
        
        # Step 1: Prompt Runner
        instruction = self._call_prompt_runner(prompt)
        
        # Step 2: Creator Core  
        blueprint = self._call_creator_core(instruction)
        
        # Step 3: BHIV Core
        result = self._call_bhiv_core(blueprint)
        
        return {
            "prompt": prompt,
            "instruction": instruction,
            "blueprint": blueprint,
            "result": result,
            "timestamp": datetime.now().isoformat()
        }
    
    def _call_prompt_runner(self, prompt: str) -> Dict[str, Any]:
        """Call Prompt Runner"""
        response = requests.post(
            f"{self.prompt_runner_url}/generate",
            json={"prompt": prompt}
        )
        return response.json()
    
    def _call_creator_core(self, instruction: Dict[str, Any]) -> Dict[str, Any]:
        """Call Creator Core"""
        response = requests.post(
            f"{self.creator_core_url}/creator-core/generate-blueprint",
            json=instruction
        )
        return response.json()
    
    def _call_bhiv_core(self, blueprint: Dict[str, Any]) -> Dict[str, Any]:
        """Call BHIV Core"""
        # Extract blueprint data
        blueprint_data = blueprint.get("blueprint", blueprint)
        
        # Convert to Core format
        core_request = {
            "module": blueprint_data.get("target_product", "creator"),
            "intent": blueprint_data.get("intent_type", "generate"),
            "user_id": "orchestrator",
            "data": blueprint_data.get("payload", {})
        }
        
        response = requests.post(
            f"{self.bhiv_core_url}/core",
            json=core_request
        )
        return response.json()


# Simple API
from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI(title="BHIV Simple Orchestrator")
orchestrator = SimpleOrchestrator()

class PromptRequest(BaseModel):
    prompt: str

@app.post("/execute")
async def execute_pipeline(request: PromptRequest):
    """Execute the integrated pipeline"""
    return orchestrator.execute(request.prompt)

@app.get("/health")
async def health():
    """Health check"""
    return {"status": "ok"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8006)