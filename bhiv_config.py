"""
BHIV Pipeline Configuration
==========================
Centralized configuration for all pipeline components.
"""

import os
from typing import Dict, Any


class BHIVConfig:
    """Configuration manager for BHIV pipeline"""
    
    # Component URLs
    PROMPT_RUNNER_URL = os.getenv("PROMPT_RUNNER_URL", "http://127.0.0.1:8003")
    CREATOR_CORE_URL = os.getenv("CREATOR_CORE_URL", "http://127.0.0.1:8000")
    BHIV_CORE_URL = os.getenv("BHIV_CORE_URL", "http://127.0.0.1:8001")
    INTEGRATION_BRIDGE_URL = os.getenv("INTEGRATION_BRIDGE_URL", "http://127.0.0.1:8004")
    BUCKET_URL = os.getenv("BUCKET_URL", "http://127.0.0.1:8005")
    
    # Component Ports
    PROMPT_RUNNER_PORT = int(os.getenv("PROMPT_RUNNER_PORT", "8003"))
    CREATOR_CORE_PORT = int(os.getenv("CREATOR_CORE_PORT", "8000"))
    BHIV_CORE_PORT = int(os.getenv("BHIV_CORE_PORT", "8001"))
    INTEGRATION_BRIDGE_PORT = int(os.getenv("INTEGRATION_BRIDGE_PORT", "8004"))
    BUCKET_PORT = int(os.getenv("BUCKET_PORT", "8005"))
    
    # Timeouts (seconds)
    REQUEST_TIMEOUT = int(os.getenv("REQUEST_TIMEOUT", "30"))
    HEALTH_CHECK_TIMEOUT = int(os.getenv("HEALTH_CHECK_TIMEOUT", "5"))
    PIPELINE_TIMEOUT = int(os.getenv("PIPELINE_TIMEOUT", "60"))
    
    # Storage Configuration
    BUCKET_BASE_PATH = os.getenv("BUCKET_BASE_PATH", "bhiv_bucket")
    ARTIFACT_RETENTION_DAYS = int(os.getenv("ARTIFACT_RETENTION_DAYS", "30"))
    
    # Pipeline Configuration
    MAX_RETRIES = int(os.getenv("MAX_RETRIES", "3"))
    RETRY_DELAY = float(os.getenv("RETRY_DELAY", "1.0"))
    
    # Logging
    LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
    LOG_FILE = os.getenv("LOG_FILE", "bhiv_pipeline.log")
    
    @classmethod
    def get_component_urls(cls) -> Dict[str, str]:
        """Get all component URLs"""
        return {
            "prompt_runner": cls.PROMPT_RUNNER_URL,
            "creator_core": cls.CREATOR_CORE_URL,
            "bhiv_core": cls.BHIV_CORE_URL,
            "integration_bridge": cls.INTEGRATION_BRIDGE_URL,
            "bucket": cls.BUCKET_URL
        }
    
    @classmethod
    def get_component_ports(cls) -> Dict[str, int]:
        """Get all component ports"""
        return {
            "prompt_runner": cls.PROMPT_RUNNER_PORT,
            "creator_core": cls.CREATOR_CORE_PORT,
            "bhiv_core": cls.BHIV_CORE_PORT,
            "integration_bridge": cls.INTEGRATION_BRIDGE_PORT,
            "bucket": cls.BUCKET_PORT
        }
    
    @classmethod
    def validate_config(cls) -> Dict[str, Any]:
        """Validate configuration settings"""
        issues = []
        
        # Check port conflicts
        ports = list(cls.get_component_ports().values())
        if len(ports) != len(set(ports)):
            issues.append("Port conflicts detected")
        
        # Check timeout values
        if cls.REQUEST_TIMEOUT <= 0:
            issues.append("REQUEST_TIMEOUT must be positive")
        
        if cls.PIPELINE_TIMEOUT <= cls.REQUEST_TIMEOUT:
            issues.append("PIPELINE_TIMEOUT should be greater than REQUEST_TIMEOUT")
        
        return {
            "valid": len(issues) == 0,
            "issues": issues,
            "config": {
                "urls": cls.get_component_urls(),
                "ports": cls.get_component_ports(),
                "timeouts": {
                    "request": cls.REQUEST_TIMEOUT,
                    "health_check": cls.HEALTH_CHECK_TIMEOUT,
                    "pipeline": cls.PIPELINE_TIMEOUT
                }
            }
        }


# Environment file template
ENV_TEMPLATE = """
# BHIV Pipeline Configuration
# Copy this to .env and modify as needed

# Component URLs (for external deployment)
PROMPT_RUNNER_URL=http://127.0.0.1:8003
CREATOR_CORE_URL=http://127.0.0.1:8000
BHIV_CORE_URL=http://127.0.0.1:8001
INTEGRATION_BRIDGE_URL=http://127.0.0.1:8004
BUCKET_URL=http://127.0.0.1:8005

# Component Ports (for local development)
PROMPT_RUNNER_PORT=8003
CREATOR_CORE_PORT=8000
BHIV_CORE_PORT=8001
INTEGRATION_BRIDGE_PORT=8004
BUCKET_PORT=8005

# Timeouts (seconds)
REQUEST_TIMEOUT=30
HEALTH_CHECK_TIMEOUT=5
PIPELINE_TIMEOUT=60

# Storage
BUCKET_BASE_PATH=bhiv_bucket
ARTIFACT_RETENTION_DAYS=30

# Pipeline
MAX_RETRIES=3
RETRY_DELAY=1.0

# Logging
LOG_LEVEL=INFO
LOG_FILE=bhiv_pipeline.log
"""


def create_env_file():
    """Create .env template file"""
    with open(".env.template", "w", encoding="utf-8") as f:
        f.write(ENV_TEMPLATE.strip())
    print("✅ Created .env.template file")


if __name__ == "__main__":
    # Validate current configuration
    validation = BHIVConfig.validate_config()
    
    print("🔧 BHIV Pipeline Configuration")
    print("=" * 40)
    
    if validation["valid"]:
        print("✅ Configuration is valid")
    else:
        print("❌ Configuration issues found:")
        for issue in validation["issues"]:
            print(f"   - {issue}")
    
    print("\n📋 Current Configuration:")
    config = validation["config"]
    
    print("\n🌐 Component URLs:")
    for name, url in config["urls"].items():
        print(f"   {name}: {url}")
    
    print("\n🔌 Component Ports:")
    for name, port in config["ports"].items():
        print(f"   {name}: {port}")
    
    print("\n⏱️  Timeouts:")
    for name, timeout in config["timeouts"].items():
        print(f"   {name}: {timeout}s")
    
    # Create environment template
    create_env_file()