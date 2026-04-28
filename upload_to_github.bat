@echo off
echo ========================================
echo BHIV Full Integration - GitHub Upload
echo ========================================

echo.
echo 🔧 Initializing Git repository...
git init

echo.
echo 📝 Adding remote repository...
git remote add origin https://github.com/blackholeinfiverse80-creator/Core-Integrator-Sprint-prompt-runner-creator-core.git

echo.
echo 📦 Adding all files...
git add .

echo.
echo 💾 Creating initial commit...
git commit -m "Initial commit: BHIV Full Integration Pipeline

✅ Complete integration: Prompt Runner → Creator Core → BHIV Core → Bucket
✅ All components operational on ports 8003, 8000, 8002, 8006
✅ Artifact chain A1→A4 with trace IDs
✅ Deterministic processing and replay capability
✅ Production-ready infrastructure module

Components:
- Simple Orchestrator (8006) - Pipeline coordinator
- Prompt Runner (8003) - Natural language to structured instruction
- Creator Core (8000) - Blueprint generation
- BHIV Core (8002) - Module execution engine
- BHIV Bucket (8005) - Artifact storage system

Features:
- End-to-end pipeline validation
- Health monitoring and connectivity checks
- Comprehensive documentation and review packets
- TTG/TTV integration ready"

echo.
echo 🚀 Pushing to GitHub...
git branch -M main
git push -u origin main

echo.
echo ✅ Upload complete!
echo 🔗 Repository: https://github.com/blackholeinfiverse80-creator/Core-Integrator-Sprint-prompt-runner-creator-core.git
echo.
pause