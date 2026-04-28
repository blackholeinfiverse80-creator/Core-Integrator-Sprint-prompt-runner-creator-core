# Core Integrator Sprint - Prompt Runner & Creator Core Integration

**Repository**: https://github.com/blackholeinfiverse80-creator/Core-Integrator-Sprint-prompt-runner-creator-core.git

## 🚀 BHIV Full Integration Pipeline - Production Ready

This repository contains the complete BHIV integration pipeline that unifies separate working components into ONE production-ready system. The pipeline provides deterministic, plug-and-play infrastructure usable across TTG, TTV, and all BHIV products.

## 📋 Repository Contents

### Core Components
- **Prompt Runner** (Port 8003) - Converts prompts to structured instructions
- **Creator Core** (Port 8000) - Generates blueprints from instructions  
- **BHIV Core** (Port 8001) - Executes blueprints through modules
- **Integration Bridge** (Port 8004) - Orchestrates full pipeline
- **BHIV Bucket** (Port 8005) - Stores and retrieves artifacts

### Key Features
✅ **Deterministic Processing** - Same input always produces same hash  
✅ **Artifact Traceability** - Complete A1→A4 chain with trace_id  
✅ **Replay & Reconstruction** - Replay pipeline from any trace_id  
✅ **Health Monitoring** - Component status checking  
✅ **TTG/TTV Integration** - Plug-and-play module design  

## 🏗️ Architecture Flow

```
User Prompt 
    ↓
Prompt Runner (8003) ──→ Structured Instruction (A1)
    ↓
Creator Core (8000) ──→ Blueprint Envelope (A2)
    ↓
BHIV Core (8001) ──→ Execution Result (A3)
    ↓
Integration Bridge (8004) ──→ Final Result (A4)
    ↓
Bucket (8005) ──→ Stored Artifacts
```

## 🚀 Quick Start

### 1. Clone Repository
```bash
git clone https://github.com/blackholeinfiverse80-creator/Core-Integrator-Sprint-prompt-runner-creator-core.git
cd Core-Integrator-Sprint-prompt-runner-creator-core
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Start Pipeline
```bash
# Option A: Automated startup (recommended)
python start_bhiv_pipeline.py

# Option B: Manual startup (5 terminals)
# Terminal 1: Prompt Runner
cd prompt-runner01
python run_server.py 8003

# Terminal 2: Creator Core  
cd creator-core/Core-Integrator-Sprint-1.1
python main.py

# Terminal 3: BHIV Core
python -m uvicorn main:app --host 0.0.0.0 --port 8001

# Terminal 4: Integration Bridge
python integration_bridge.py

# Terminal 5: Bucket
python bhiv_bucket.py
```

### 4. Test Integration
```bash
# Quick test
python test_integration.py

# Full validation
python validate_full_integration.py

# Manual API test
curl -X POST http://localhost:8004/pipeline/execute \
  -H "Content-Type: application/json" \
  -d '{"prompt": "Design a residential building for Mumbai"}'
```

## 📁 Directory Structure

```
Core-Integrator-Sprint-prompt-runner-creator-core/
├── prompt-runner01/              # Prompt Runner component
├── creator-core/                 # Creator Core component  
├── src/                         # BHIV Core modules & agents
├── integration_bridge.py        # Main pipeline orchestrator
├── bhiv_bucket.py               # Artifact storage system
├── validate_full_integration.py # Comprehensive validation
├── start_bhiv_pipeline.py       # Component startup script
├── bhiv_config.py               # Configuration management
├── review_packets/              # Documentation & review packets
└── README.md                    # Main documentation
```

## 🔧 API Endpoints

### Integration Bridge (Port 8004)
- `POST /pipeline/execute` - Execute full pipeline
- `GET /pipeline/health` - Check all component health
- `GET /pipeline/replay/{trace_id}` - Replay from trace ID

### BHIV Bucket (Port 8005)  
- `POST /bucket/store` - Store artifact
- `GET /bucket/artifact/{artifact_id}` - Get artifact by ID
- `GET /bucket/trace/{trace_id}` - Get all artifacts for trace
- `GET /bucket/stats` - Get bucket statistics

## 📊 Pipeline Input/Output

### Input
```json
{
  "prompt": "Design a residential building for a 1000 sqft plot in Mumbai"
}
```

### Output
```json
{
  "status": "success",
  "trace_id": "trace_abc123def456",
  "artifact_chain": {
    "A1_instruction": "instruction_12345678",
    "A2_blueprint": "blueprint_87654321", 
    "A3_execution": "execution_11223344",
    "A4_result": "result_55667788"
  },
  "pipeline_result": {
    "original_prompt": "Design a residential building...",
    "pipeline_status": "completed",
    "deterministic_hash": "a1b2c3d4e5f67890"
  }
}
```

## 🔍 Artifact Chain (A1 → A4)

| Artifact | Type | Description |
|----------|------|-------------|
| **A1** | Instruction | Structured instruction from Prompt Runner |
| **A2** | Blueprint | Blueprint envelope from Creator Core |
| **A3** | Execution | Execution result from BHIV Core |
| **A4** | Result | Final assembled result |

## ✅ Validation & Testing

The system includes comprehensive validation:

```bash
python validate_full_integration.py
```

**Validation Tests:**
1. ✅ Component Health Check
2. ✅ End-to-End Flow Proof  
3. ✅ Artifact Chain Validation (A1→A4)
4. ✅ Replay & Reconstruction Proof
5. ✅ Determinism Validation
6. ✅ TTG/TTV Integration Proof

## 🛠️ Configuration

Environment variables can be set in `.env` file:

```bash
# Component URLs
PROMPT_RUNNER_URL=http://127.0.0.1:8003
CREATOR_CORE_URL=http://127.0.0.1:8000
BHIV_CORE_URL=http://127.0.0.1:8001

# Timeouts
REQUEST_TIMEOUT=30
PIPELINE_TIMEOUT=60
```

## 🔧 Troubleshooting

### Common Issues

1. **Port Conflicts**
   ```bash
   netstat -an | findstr "8003 8000 8001 8004 8005"
   ```

2. **Component Health Check**
   ```bash
   curl http://localhost:8004/pipeline/health
   ```

3. **Individual Component Status**
   - Prompt Runner: `http://localhost:8003/health`
   - Creator Core: `http://localhost:8000/health`
   - BHIV Core: `http://localhost:8001/health`

## 📈 Production Deployment

### Requirements
- Python 3.8+
- All component dependencies installed
- Network connectivity between components
- Sufficient storage for artifact bucket

### Scaling Considerations
- Components can be deployed on separate servers
- Update URLs in configuration for distributed deployment
- Consider load balancing for high-traffic scenarios
- Monitor bucket storage growth

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Run validation tests
5. Submit a pull request

## 📄 License

This integration is part of the BHIV infrastructure system.

## 📞 Support

For issues or questions:
1. Check the troubleshooting section
2. Review component logs  
3. Run validation tests
4. Check the review packets for detailed documentation

---

**🎯 Integration Status**: COMPLETED ✅  
**🚀 Production Ready**: YES ✅  
**🔗 Pipeline Operational**: YES ✅  
**📊 All Tests Passing**: YES ✅

**Repository**: https://github.com/blackholeinfiverse80-creator/Core-Integrator-Sprint-prompt-runner-creator-core.git