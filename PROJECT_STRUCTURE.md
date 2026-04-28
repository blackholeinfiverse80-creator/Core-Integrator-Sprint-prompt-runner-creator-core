# BHIV Full Integration - Project Structure

```
Core-Integrator-Sprint-1.1-/
├── 📋 README.md                           # Main documentation
├── 🔧 requirements.txt                    # Python dependencies
├── ⚙️ .gitignore                         # Git ignore rules
├── 🚀 upload_to_github.bat              # GitHub upload script
├── 📊 PROJECT_STRUCTURE.md               # This file
│
├── 🎯 INTEGRATION FILES (Main Pipeline)
│   ├── simple_orchestrator.py            # Main pipeline orchestrator (Port 8006)
│   ├── integration_bridge.py             # Advanced pipeline with artifact chain
│   ├── bhiv_bucket.py                    # Artifact storage system (Port 8005)
│   ├── bhiv_config.py                    # Configuration management
│   └── start_bhiv_pipeline.py            # Component startup script
│
├── 🧪 TESTING & VALIDATION
│   ├── test_simple.py                    # Quick integration test
│   ├── test_integration.py               # Basic integration test
│   ├── validate_full_integration.py      # Comprehensive validation suite
│   └── check_connectivity.py             # Service connectivity checker
│
├── 📁 COMPONENTS
│   ├── prompt-runner01/                   # Prompt Runner (Port 8003)
│   │   ├── run_server.py
│   │   ├── prompt_processor.py
│   │   └── requirements.txt
│   │
│   ├── creator-core/                      # Creator Core (Port 8000)
│   │   └── Core-Integrator-Sprint-1.1/
│   │       ├── main.py
│   │       ├── creator_core_service.py
│   │       └── requirements.txt
│   │
│   └── [BHIV Core files in root]          # BHIV Core (Port 8002)
│       ├── main.py
│       ├── src/
│       │   ├── core/
│       │   ├── agents/
│       │   ├── modules/
│       │   └── db/
│       └── config/
│
├── 📚 DOCUMENTATION
│   ├── review_packets/
│   │   └── full_integration_v1.md         # Comprehensive review packet
│   ├── startup_guide.md                   # Service startup instructions
│   └── troubleshooting_guide.md           # Common issues and solutions
│
└── 🔧 CONFIGURATION
    ├── .env.example                       # Environment variables template
    └── config/
        └── config.py                      # Main configuration file
```

## Key Files Description

### Integration Core
- **simple_orchestrator.py**: Main pipeline coordinator connecting all components
- **integration_bridge.py**: Advanced orchestrator with artifact chain (A1→A4)
- **bhiv_bucket.py**: Artifact storage with trace ID management

### Components
- **Prompt Runner**: Converts natural language to structured instructions
- **Creator Core**: Generates blueprints from instructions  
- **BHIV Core**: Executes blueprints through modules
- **Integration Bridge**: Orchestrates full pipeline flow

### Testing
- **test_simple.py**: Quick end-to-end test
- **validate_full_integration.py**: Comprehensive validation suite
- **check_connectivity.py**: Health monitoring

### Documentation
- **README.md**: Complete integration documentation
- **review_packets/**: Detailed technical documentation
- **startup_guide.md**: Step-by-step startup instructions

## Port Assignments
- **8003**: Prompt Runner
- **8000**: Creator Core  
- **8002**: BHIV Core
- **8005**: BHIV Bucket
- **8006**: Simple Orchestrator

## Quick Start
1. Run `upload_to_github.bat` to upload to repository
2. Follow README.md for component startup
3. Use `test_simple.py` to validate integration
4. Access pipeline at `http://localhost:8006/execute`