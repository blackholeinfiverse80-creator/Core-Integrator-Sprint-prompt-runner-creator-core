"""
TTG/TTV Integration API
======================
FastAPI endpoints for TTG and TTV system integration.

TANTRA-compliant endpoints that enforce pipeline flow.
"""

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Dict, Any, Optional

from src.adapters.tantra_bridge import TANTRAIntegrationBridge

app = FastAPI(
    title="TTG/TTV Integration API",
    description="TANTRA-compliant integration for Text-to-Game and Text-to-Video systems",
    version="1.0.0"
)

bridge = TANTRAIntegrationBridge()


class TTGRequest(BaseModel):
    """TTG request model"""
    game_type: str
    theme: Optional[str] = ""
    difficulty: Optional[str] = "medium"
    player_count: Optional[int] = 1
    description: Optional[str] = ""


class TTVRequest(BaseModel):
    """TTV request model"""
    video_type: str
    topic: Optional[str] = ""
    duration: Optional[str] = "5min"
    style: Optional[str] = "standard"
    voice: Optional[str] = "neutral"
    description: Optional[str] = ""


@app.post("/ttg/generate")
async def generate_ttg(request: TTGRequest):
    """
    Generate game content through TTG pipeline
    
    Flow: TTG Input → Normalizer → Prompt Runner → Creator Core → BHIV Core → Adapter → TTG Output
    """
    try:
        result = bridge.process_ttg_request(request.dict())
        
        if result["status"] == "error":
            raise HTTPException(status_code=500, detail=result["error"])
        
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/ttv/generate")
async def generate_ttv(request: TTVRequest):
    """
    Generate video content through TTV pipeline
    
    Flow: TTV Input → Normalizer → Prompt Runner → Creator Core → BHIV Core → Adapter → TTV Output
    """
    try:
        result = bridge.process_ttv_request(request.dict())
        
        if result["status"] == "error":
            raise HTTPException(status_code=500, detail=result["error"])
        
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/tantra/validate")
async def validate_tantra():
    """
    Validate TANTRA system boundaries
    
    Ensures:
    - TTG cannot execute without Core
    - TTV cannot execute without Core
    - Creator Core cannot bypass Core
    """
    return bridge.validate_system_boundaries()


@app.get("/health")
async def health_check():
    """Health check for TTG/TTV integration"""
    return {
        "status": "healthy",
        "service": "ttg_ttv_integration",
        "version": "1.0.0"
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8006)
