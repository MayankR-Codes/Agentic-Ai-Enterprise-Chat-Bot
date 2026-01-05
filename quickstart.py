#!/usr/bin/env python3
"""
🚀 QUICK START GUIDE
Run this file to get started immediately
"""

import os
import sys
import subprocess

def print_header(text):
    print("\n" + "="*60)
    print(f"  {text}")
    print("="*60)

def check_python():
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 10):
        print(f"❌ Python 3.10+ required. You have {version.major}.{version.minor}")
        return False
    print(f"✅ Python {version.major}.{version.minor}")
    return True

def check_venv():
    if hasattr(sys, 'real_prefix') or (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix):
        print("✅ Virtual environment detected")
        return True
    print("⚠️ No virtual environment. Create one: python -m venv venv")
    return False

def check_env_file():
    if os.path.exists(".env"):
        print("✅ .env file found")
        return True
    print("❌ .env file not found")
    print("   Create .env with:")
    print("   GOOGLE_API_KEY=your_key_here")
    return False

def run_tests():
    print("\nRunning component tests...")
    result = subprocess.run([sys.executable, "test_components.py"], capture_output=False)
    return result.returncode == 0

def main():
    print_header("🤖 HCLTech Enterprise Assistant - Quick Start")
    
    print("\n📋 Pre-Flight Checks:")
    print("-" * 60)
    
    checks = {
        "Python Version": check_python(),
        "Virtual Env": check_venv(),
        ".env File": check_env_file(),
    }
    
    print("\n" + "="*60)
    print("  TEST RESULTS")
    print("="*60)
    
    for check, passed in checks.items():
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{status}: {check}")
    
    if not all(checks.values()):
        print("\n⚠️ Please fix the above issues before continuing.")
        return 1
    
    print("\n📝 Checking dependencies...")
    result = subprocess.run(
        [sys.executable, "-m", "pip", "list"],
        capture_output=True,
        text=True
    )
    
    required_packages = [
        "langchain",
        "streamlit",
        "faiss-cpu",
        "langchain-google-genai"
    ]
    
    installed = [pkg.lower() in result.stdout.lower() for pkg in required_packages]
    
    if not all(installed):
        print("⚠️ Missing packages. Install with:")
        print("   pip install -r requirement.txt")
        return 1
    
    print("✅ All dependencies installed")
    
    # Run tests
    print("\n🧪 Running component tests...")
    print("-" * 60)
    
    if not run_tests():
        print("\n❌ Tests failed. Check output above.")
        return 1
    
    print("\n" + "="*60)
    print("  🎉 ALL CHECKS PASSED!")
    print("="*60)
    
    print("\n🚀 To start the chatbot, run:")
    print("   streamlit run app.py")
    
    print("\n📚 For more info:")
    print("   - README.md (overview)")
    print("   - CODE_REVIEW_SUMMARY.md (improvements)")
    print("   - DEPLOYMENT_GUIDE.md (production)")
    
    print("\n💡 Test scenarios:")
    print("   1. Chat Mode: 'What was the revenue?'")
    print("   2. Issue Mode: 'My computer crashed'")
    print("   3. Knowledge: Check sidebar dashboard")
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
