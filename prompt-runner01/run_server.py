#!/usr/bin/env python
"""
Start Prompt Runner with proper environment loading.
This script ensures .env.local is loaded before uvicorn starts the app.
"""
import os
import subprocess
import sys

# Load .env.local FIRST
env_path = os.path.join(os.path.dirname(__file__), '.env.local')
if os.path.exists(env_path):
    with open(env_path, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if line and '=' in line and not line.startswith('#'):
                k, v = line.split('=', 1)
                k = k.strip()
                v = v.strip().strip('"').strip("'")
                if k and not os.environ.get(k):
                    os.environ[k] = v
                    print(f"[ENV] {k} loaded from .env.local")

# Now start uvicorn with updated environment
port = sys.argv[1] if len(sys.argv) > 1 else '8003'
print(f"\n[START] Starting Prompt Runner on port {port}")
print(f"[INFO] GROQ_API_KEY is set: {bool(os.environ.get('GROQ_API_KEY'))}")
print(f"[INFO] CREATOR_CORE_URL: {os.environ.get('CREATOR_CORE_URL', 'NOT SET')}")
print()

subprocess.run([sys.executable, '-m', 'uvicorn', 'api:app', '--host', '127.0.0.1', '--port', port], env=os.environ)
