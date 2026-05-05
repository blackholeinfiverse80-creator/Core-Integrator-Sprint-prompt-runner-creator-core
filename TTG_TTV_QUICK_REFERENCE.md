# TTG/TTV Integration - Quick Reference

## 🚀 Quick Start

### Start All Services (One Command)
```bash
start_ttg_ttv_integration.bat
```

This will:
1. Start all 5 services
2. Wait for initialization
3. Run integration tests automatically

---

## 📡 Service Endpoints

| Service | Port | URL |
|---------|------|-----|
| Prompt Runner | 8003 | http://localhost:8003 |
| Creator Core | 8000 | http://localhost:8000 |
| BHIV Core | 8001 | http://localhost:8001 |
| Bucket | 8005 | http://localhost:8005 |
| TTG/TTV API | 8006 | http://localhost:8006 |

---

## 🎮 TTG Integration

### Generate Game Content
```bash
curl -X POST http://localhost:8006/ttg/generate \
  -H "Content-Type: application/json" \
  -d '{
    "game_type": "adventure",
    "theme": "fantasy",
    "difficulty": "medium",
    "player_count": 2,
    "description": "Create a dungeon crawler game"
  }'
```

### TTG Request Fields
- `game_type` (required): adventure, puzzle, rpg, strategy, etc.
- `theme` (optional): fantasy, sci-fi, horror, etc.
- `difficulty` (optional): easy, medium, hard
- `player_count` (optional): number of players
- `description` (optional): detailed game description

---

## 🎬 TTV Integration

### Generate Video Content
```bash
curl -X POST http://localhost:8006/ttv/generate \
  -H "Content-Type: application/json" \
  -d '{
    "video_type": "tutorial",
    "topic": "Python programming",
    "duration": "5min",
    "style": "animated",
    "voice": "professional",
    "description": "Create a Python basics tutorial"
  }'
```

### TTV Request Fields
- `video_type` (required): tutorial, explainer, demo, etc.
- `topic` (optional): video subject
- `duration` (optional): 1min, 5min, 10min, etc.
- `style` (optional): animated, live-action, whiteboard, etc.
- `voice` (optional): professional, casual, neutral, etc.

---

## ✅ Validation

### Check TANTRA Compliance
```bash
curl http://localhost:8006/tantra/validate
```

Expected Response:
```json
{
  "tantra_compliant": true,
  "system_boundaries": "enforced",
  "component_checks": {
    "prompt_runner_accessible": true,
    "creator_core_accessible": true,
    "bhiv_core_accessible": true,
    "bucket_accessible": true
  }
}
```

---

## 🧪 Testing

### Run Complete Test Suite
```bash
python test_ttg_ttv_integration.py
```

Tests:
1. ✅ TTG Integration
2. ✅ TTV Integration
3. ✅ Artifact Chain Validation
4. ✅ System Boundary Enforcement

---

## 📊 Pipeline Flow

```
TTG/TTV Input
    ↓
Input Normalizer (converts to prompt)
    ↓
Prompt Runner (structured instruction)
    ↓
Creator Core (blueprint generation)
    ↓
BHIV Core (execution - ONLY authority)
    ↓
Output Adapter (product-specific format)
    ↓
TTG/TTV Output
```

---

## 🔍 Artifact Chain

Every request generates:
- `execution_id`: Unique execution identifier
- `input_hash`: Deterministic input hash
- `output_hash`: Deterministic output hash
- `semantic_hash`: Content-based hash
- `trace_id`: Full pipeline trace

---

## 🛡️ TANTRA Principles

✅ Core is ONLY execution authority  
✅ NO direct execution from Creator Core  
✅ NO bypass of pipeline  
✅ Adapters are THIN transformation layers  
✅ System boundaries enforced  

---

## 📁 File Structure

```
src/adapters/
├── __init__.py
├── ttg_input_normalizer.py    # TTG → Prompt
├── ttv_input_normalizer.py    # TTV → Prompt
├── ttg_output_adapter.py      # Core → TTG
├── ttv_output_adapter.py      # Core → TTV
└── tantra_bridge.py           # Pipeline enforcement

ttg_ttv_api.py                 # FastAPI endpoints
test_ttg_ttv_integration.py    # Test suite
start_ttg_ttv_integration.bat  # Startup script
```

---

## 🚨 Troubleshooting

### Service Not Starting
```bash
# Check if port is in use
netstat -ano | findstr "8006"

# Kill process if needed
taskkill /PID <process_id> /F
```

### Integration Test Failing
1. Ensure all 5 services are running
2. Check service health endpoints
3. Review logs in each terminal
4. Verify .env.local files exist

### TANTRA Validation Failing
- One or more pipeline components unavailable
- Check each service individually
- Restart services in order

---

## 📝 Review Packet

Complete documentation: `review_packets/ttg_ttv_integration_v1.md`

Includes:
- Architecture overview
- Live flow examples
- Test results
- Proof of integration
- Deployment guide

---

**Status**: ✅ Production Ready  
**TANTRA Compliance**: ✅ Certified  
**Integration**: ✅ Operational
