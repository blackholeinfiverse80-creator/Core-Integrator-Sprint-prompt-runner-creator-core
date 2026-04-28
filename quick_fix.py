"""
Quick Fix - Install Dependencies and Test
========================================
"""

import subprocess
import sys
import os


def install_missing_deps():
    """Install missing dependencies"""
    
    print("🔧 Installing missing dependencies...")
    
    deps = [
        "jsonschema>=4.0.0",
        "requests>=2.0.0", 
        "fastapi>=0.100.0",
        "uvicorn[standard]>=0.20.0",
        "pydantic>=2.0.0"
    ]
    
    for dep in deps:
        try:
            print(f"📦 Installing {dep}...")
            subprocess.check_call([sys.executable, "-m", "pip", "install", dep], 
                                stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        except:
            print(f"⚠️  Failed to install {dep}")
    
    print("✅ Dependencies installed")


def test_main():
    """Test if main.py works now"""
    
    print("\n🧪 Testing main.py...")
    
    try:
        # Try importing the main modules
        import sys
        sys.path.append("src")
        
        from src.core.gateway import Gateway
        print("✅ Gateway import successful")
        
        return True
        
    except Exception as e:
        print(f"❌ Still failing: {e}")
        return False


def main():
    """Run the fix"""
    
    print("🚀 BHIV Quick Fix")
    print("=" * 20)
    
    install_missing_deps()
    
    if test_main():
        print("\n✅ Fix successful! You can now run:")
        print("   python main.py")
    else:
        print("\n❌ Still having issues. Let's use the Creator Core instead:")
        print("   cd creator-core\\Core-Integrator-Sprint-1.1")
        print("   python main.py")


if __name__ == "__main__":
    main()