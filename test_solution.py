#!/usr/bin/env python3
"""
Test script for Adobe India Hackathon 2025 Solution
Validates both Challenge 1a and Challenge 1b implementations
"""

import os
import json
import time
import subprocess
import sys
from pathlib import Path
from typing import Dict, Any, List

def test_challenge_1a():
    """Test Challenge 1a implementation."""
    print("🧪 Testing Challenge 1a: PDF Processing Solution")
    print("=" * 50)
    
    # Check if Docker is available
    try:
        subprocess.run(["docker", "--version"], check=True, capture_output=True)
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("❌ Docker not available. Skipping Challenge 1a tests.")
        return False
    
    # Check if Challenge 1a files exist
    challenge_1a_path = Path("Challenge_1a")
    if not challenge_1a_path.exists():
        print("❌ Challenge_1a directory not found.")
        return False
    
    required_files = [
        "process_pdfs.py",
        "requirements.txt", 
        "Dockerfile",
        "sample_dataset/pdfs",
        "sample_dataset/schema/output_schema.json"
    ]
    
    for file_path in required_files:
        full_path = challenge_1a_path / file_path
        if not full_path.exists():
            print(f"❌ Required file not found: {file_path}")
            return False
    
    print("✅ All required files found")
    
    # Test Docker build
    print("\n🔨 Testing Docker build...")
    try:
        build_cmd = [
            "docker", "build", 
            "--platform", "linux/amd64", 
            "-t", "test-pdf-processor", 
            str(challenge_1a_path)
        ]
        result = subprocess.run(build_cmd, capture_output=True, text=True)
        
        if result.returncode != 0:
            print(f"❌ Docker build failed: {result.stderr}")
            return False
        
        print("✅ Docker build successful")
        
    except Exception as e:
        print(f"❌ Docker build error: {e}")
        return False
    
    # Test Docker run
    print("\n🚀 Testing Docker run...")
    try:
        # Create temporary output directory
        temp_output = Path("temp_output")
        temp_output.mkdir(exist_ok=True)
        
        run_cmd = [
            "docker", "run", "--rm",
            "-v", f"{challenge_1a_path}/sample_dataset/pdfs:/app/input:ro",
            "-v", f"{temp_output.absolute()}:/app/output",
            "--network", "none",
            "test-pdf-processor"
        ]
        
        start_time = time.time()
        result = subprocess.run(run_cmd, capture_output=True, text=True)
        processing_time = time.time() - start_time
        
        if result.returncode != 0:
            print(f"❌ Docker run failed: {result.stderr}")
            return False
        
        print(f"✅ Docker run successful (took {processing_time:.2f} seconds)")
        
        # Check output files
        output_files = list(temp_output.glob("*.json"))
        if not output_files:
            print("❌ No output files generated")
            return False
        
        print(f"✅ Generated {len(output_files)} output files")
        
        # Validate JSON schema
        schema_file = challenge_1a_path / "sample_dataset/schema/output_schema.json"
        with open(schema_file, 'r') as f:
            schema = json.load(f)
        
        for output_file in output_files:
            try:
                with open(output_file, 'r') as f:
                    data = json.load(f)
                
                # Basic schema validation
                if "title" not in data or "outline" not in data:
                    print(f"❌ Invalid JSON structure in {output_file.name}")
                    return False
                
                if not isinstance(data["outline"], list):
                    print(f"❌ Outline must be a list in {output_file.name}")
                    return False
                
                print(f"✅ {output_file.name} - Title: {data['title']}, Outline items: {len(data['outline'])}")
                
            except json.JSONDecodeError:
                print(f"❌ Invalid JSON in {output_file.name}")
                return False
        
        # Cleanup
        import shutil
        shutil.rmtree(temp_output)
        
        # Performance check
        if processing_time > 10:
            print(f"⚠️  Warning: Processing took {processing_time:.2f} seconds (should be < 10s)")
        else:
            print(f"✅ Performance check passed ({processing_time:.2f}s < 10s)")
        
        print("\n✅ Challenge 1a tests passed!")
        return True
        
    except Exception as e:
        print(f"❌ Docker run error: {e}")
        return False

def test_challenge_1b():
    """Test Challenge 1b implementation."""
    print("\n🧪 Testing Challenge 1b: Multi-Collection PDF Analysis")
    print("=" * 50)
    
    # Check if Challenge 1b files exist
    challenge_1b_path = Path("Challenge_1b")
    if not challenge_1b_path.exists():
        print("❌ Challenge_1b directory not found.")
        return False
    
    required_files = [
        "process_collections.py",
        "requirements.txt",
        "Dockerfile",
        "Collection 1/challenge1b_input.json",
        "Collection 2/challenge1b_input.json", 
        "Collection 3/challenge1b_input.json"
    ]
    
    for file_path in required_files:
        full_path = challenge_1b_path / file_path
        if not full_path.exists():
            print(f"❌ Required file not found: {file_path}")
            return False
    
    print("✅ All required files found")
    
    # Test input JSON structure
    print("\n📋 Testing input JSON structure...")
    for i in range(1, 4):
        input_file = challenge_1b_path / f"Collection {i}" / "challenge1b_input.json"
        try:
            with open(input_file, 'r') as f:
                data = json.load(f)
            
            required_fields = ["challenge_info", "documents", "persona", "job_to_be_done"]
            for field in required_fields:
                if field not in data:
                    print(f"❌ Missing field '{field}' in Collection {i}")
                    return False
            
            print(f"✅ Collection {i} input JSON valid")
            
        except json.JSONDecodeError:
            print(f"❌ Invalid JSON in Collection {i}")
            return False
    
    # Test Python script directly
    print("\n🐍 Testing Python script...")
    try:
        script_path = challenge_1b_path / "process_collections.py"
        
        # Change to Challenge_1b directory
        original_cwd = os.getcwd()
        os.chdir(challenge_1b_path)
        
        # Run the script
        start_time = time.time()
        result = subprocess.run([sys.executable, "process_collections.py"], 
                              capture_output=True, text=True, timeout=300)
        processing_time = time.time() - start_time
        
        # Change back to original directory
        os.chdir(original_cwd)
        
        if result.returncode != 0:
            print(f"❌ Script execution failed: {result.stderr}")
            return False
        
        print(f"✅ Script execution successful (took {processing_time:.2f} seconds)")
        
        # Check output files
        for i in range(1, 4):
            output_file = challenge_1b_path / f"Collection {i}" / "challenge1b_output.json"
            if not output_file.exists():
                print(f"❌ Output file not generated for Collection {i}")
                return False
            
            try:
                with open(output_file, 'r') as f:
                    data = json.load(f)
                
                # Validate output structure
                required_fields = ["metadata", "extracted_sections", "subsection_analysis"]
                for field in required_fields:
                    if field not in data:
                        print(f"❌ Missing field '{field}' in Collection {i} output")
                        return False
                
                print(f"✅ Collection {i} output valid - "
                      f"Sections: {len(data['extracted_sections'])}, "
                      f"Analysis: {len(data['subsection_analysis'])}")
                
            except json.JSONDecodeError:
                print(f"❌ Invalid JSON in Collection {i} output")
                return False
        
        print("\n✅ Challenge 1b tests passed!")
        return True
        
    except subprocess.TimeoutExpired:
        print("❌ Script execution timed out (5 minutes)")
        return False
    except Exception as e:
        print(f"❌ Script execution error: {e}")
        return False

def test_docker_build_1b():
    """Test Challenge 1b Docker build."""
    print("\n🔨 Testing Challenge 1b Docker build...")
    
    challenge_1b_path = Path("Challenge_1b")
    
    try:
        build_cmd = [
            "docker", "build", 
            "--platform", "linux/amd64", 
            "-t", "test-collection-processor", 
            str(challenge_1b_path)
        ]
        result = subprocess.run(build_cmd, capture_output=True, text=True)
        
        if result.returncode != 0:
            print(f"❌ Docker build failed: {result.stderr}")
            return False
        
        print("✅ Challenge 1b Docker build successful")
        return True
        
    except Exception as e:
        print(f"❌ Docker build error: {e}")
        return False

def main():
    """Run all tests."""
    print("🚀 Adobe India Hackathon 2025 - Solution Validation")
    print("=" * 60)
    
    results = []
    
    # Test Challenge 1a
    results.append(("Challenge 1a", test_challenge_1a()))
    
    # Test Challenge 1b
    results.append(("Challenge 1b", test_challenge_1b()))
    
    # Test Challenge 1b Docker build
    results.append(("Challenge 1b Docker", test_docker_build_1b()))
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 Test Results Summary")
    print("=" * 60)
    
    passed = 0
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{test_name:<25} {status}")
        if result:
            passed += 1
    
    print(f"\nOverall: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! Solution is ready for submission.")
        return 0
    else:
        print("⚠️  Some tests failed. Please review the implementation.")
        return 1

if __name__ == "__main__":
    sys.exit(main()) 