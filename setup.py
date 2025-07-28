#!/usr/bin/env python3
"""
Setup script for Adobe India Hackathon 2025 Solution
Helps users get started quickly with the implementation
"""

import os
import sys
import subprocess
import platform
from pathlib import Path

def check_python_version():
    """Check if Python version is compatible."""
    print("🐍 Checking Python version...")
    
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 8):
        print(f"❌ Python 3.8+ required. Current version: {version.major}.{version.minor}")
        return False
    
    print(f"✅ Python {version.major}.{version.minor}.{version.micro} - Compatible")
    return True

def check_docker():
    """Check if Docker is available."""
    print("\n🐳 Checking Docker...")
    
    try:
        result = subprocess.run(["docker", "--version"], 
                              capture_output=True, text=True, check=True)
        print(f"✅ Docker available: {result.stdout.strip()}")
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("❌ Docker not found. Please install Docker to run the solution.")
        print("   Download from: https://docs.docker.com/get-docker/")
        return False

def check_system_architecture():
    """Check system architecture."""
    print("\n💻 Checking system architecture...")
    
    arch = platform.machine().lower()
    if arch in ['x86_64', 'amd64']:
        print(f"✅ Architecture: {arch} - Compatible")
        return True
    else:
        print(f"⚠️  Architecture: {arch} - May have compatibility issues")
        print("   The solution is optimized for AMD64 architecture")
        return True

def check_disk_space():
    """Check available disk space."""
    print("\n💾 Checking disk space...")
    
    try:
        import shutil
        total, used, free = shutil.disk_usage(".")
        free_gb = free // (1024**3)
        
        if free_gb > 5:
            print(f"✅ Available disk space: {free_gb} GB - Sufficient")
            return True
        else:
            print(f"⚠️  Available disk space: {free_gb} GB - Low space warning")
            return True
    except:
        print("⚠️  Could not check disk space")
        return True

def check_memory():
    """Check available memory."""
    print("\n🧠 Checking memory...")
    
    try:
        import psutil
        memory = psutil.virtual_memory()
        available_gb = memory.available // (1024**3)
        
        if available_gb > 8:
            print(f"✅ Available memory: {available_gb} GB - Sufficient")
            return True
        else:
            print(f"⚠️  Available memory: {available_gb} GB - Low memory warning")
            return True
    except ImportError:
        print("⚠️  Could not check memory (psutil not installed)")
        return True

def check_project_structure():
    """Check if project structure is correct."""
    print("\n📁 Checking project structure...")
    
    required_dirs = [
        "Challenge_1a",
        "Challenge_1b",
        "Challenge_1a/sample_dataset",
        "Challenge_1a/sample_dataset/pdfs",
        "Challenge_1a/sample_dataset/schema",
        "Challenge_1b/Collection 1",
        "Challenge_1b/Collection 2", 
        "Challenge_1b/Collection 3"
    ]
    
    missing_dirs = []
    for dir_path in required_dirs:
        if not Path(dir_path).exists():
            missing_dirs.append(dir_path)
    
    if missing_dirs:
        print("❌ Missing directories:")
        for dir_path in missing_dirs:
            print(f"   - {dir_path}")
        return False
    
    print("✅ Project structure is correct")
    return True

def show_usage_instructions():
    """Show usage instructions."""
    print("\n" + "="*60)
    print("🚀 USAGE INSTRUCTIONS")
    print("="*60)
    
    print("\n📋 Challenge 1a - PDF Processing:")
    print("1. Build Docker image:")
    print("   cd Challenge_1a")
    print("   docker build --platform linux/amd64 -t pdf-processor .")
    print("\n2. Run with sample data:")
    print("   docker run --rm -v $(pwd)/sample_dataset/pdfs:/app/input:ro \\")
    print("     -v $(pwd)/sample_dataset/outputs:/app/output --network none pdf-processor")
    
    print("\n📋 Challenge 1b - Multi-Collection Analysis:")
    print("1. Build Docker image:")
    print("   cd Challenge_1b")
    print("   docker build --platform linux/amd64 -t collection-processor .")
    print("\n2. Run the analysis:")
    print("   docker run --rm -v $(pwd):/app/data collection-processor")
    
    print("\n📋 Testing the Solution:")
    print("   python test_solution.py")
    
    print("\n📋 For Windows users:")
    print("   Replace $(pwd) with %cd% in the commands above")
    
    print("\n📋 For more details:")
    print("   - Read the README.md file")
    print("   - Check individual challenge README files")
    print("   - Run the test script for validation")

def show_troubleshooting():
    """Show troubleshooting tips."""
    print("\n" + "="*60)
    print("🔧 TROUBLESHOOTING")
    print("="*60)
    
    print("\n❓ Common Issues:")
    print("\n1. Docker build fails:")
    print("   - Ensure Docker is running")
    print("   - Check internet connection")
    print("   - Try: docker system prune -a")
    
    print("\n2. Memory issues:")
    print("   - Close other applications")
    print("   - Increase Docker memory limit")
    print("   - Use smaller test files")
    
    print("\n3. Performance issues:")
    print("   - Ensure AMD64 architecture")
    print("   - Check available CPU cores")
    print("   - Monitor system resources")
    
    print("\n4. Permission errors:")
    print("   - Use sudo (Linux/Mac)")
    print("   - Run as Administrator (Windows)")
    print("   - Check file permissions")

def main():
    """Main setup function."""
    print("🚀 Adobe India Hackathon 2025 - Setup Check")
    print("="*60)
    
    checks = [
        ("Python Version", check_python_version),
        ("Docker", check_docker),
        ("System Architecture", check_system_architecture),
        ("Disk Space", check_disk_space),
        ("Memory", check_memory),
        ("Project Structure", check_project_structure)
    ]
    
    results = []
    for check_name, check_func in checks:
        try:
            result = check_func()
            results.append((check_name, result))
        except Exception as e:
            print(f"❌ {check_name} check failed: {e}")
            results.append((check_name, False))
    
    # Summary
    print("\n" + "="*60)
    print("📊 Setup Check Summary")
    print("="*60)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for check_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{check_name:<20} {status}")
    
    print(f"\nOverall: {passed}/{total} checks passed")
    
    if passed == total:
        print("\n🎉 All checks passed! You're ready to run the solution.")
    else:
        print("\n⚠️  Some checks failed. Please address the issues above.")
    
    # Show instructions
    show_usage_instructions()
    show_troubleshooting()
    
    print("\n" + "="*60)
    print("🎯 Ready to connect the dots? Let's go!")
    print("="*60)

if __name__ == "__main__":
    main() 