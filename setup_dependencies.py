"""
Quick Setup - Install Missing Dependencies
=========================================
"""

import subprocess
import sys


def install_dependencies():
    """Install missing dependencies"""
    
    print("🔧 Installing Missing Dependencies...")
    print("=" * 40)
    
    # Install jsonschema specifically
    print("📦 Installing jsonschema...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "jsonschema>=4.0.0"])
        print("✅ jsonschema installed")
    except Exception as e:
        print(f"❌ Failed to install jsonschema: {e}")
        return False
    
    # Install all requirements
    print("\n📦 Installing all requirements...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        print("✅ All requirements installed")
    except Exception as e:
        print(f"❌ Failed to install requirements: {e}")
        return False
    
    return True


def main():
    """Run setup"""
    
    print("🚀 BHIV Integration Setup")
    print("=" * 30)
    
    if install_dependencies():
        print("\n✅ Setup complete!")
        print("\n🎯 Next steps:")
        print("   1. python start_and_verify.py")
        print("   2. Or manually start services")
        return True
    else:
        print("\n❌ Setup failed!")
        return False


if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)