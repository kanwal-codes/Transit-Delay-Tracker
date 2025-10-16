"""
Simple validation script to check if all components are properly structured
"""

import os
import sys

def check_file_structure():
    """Check if all required files exist"""
    required_files = [
        "requirements.txt",
        "README.md", 
        "QUICK_START.md",
        "run_dashboard.py",
        "src/data_collection/collector.py",
        "src/ml/predictor.py",
        "src/ml/anomaly_detector.py",
        "src/ml/train_models.py",
        "src/web/app.py"
    ]
    
    missing_files = []
    for file_path in required_files:
        if not os.path.exists(file_path):
            missing_files.append(file_path)
    
    if missing_files:
        print("❌ Missing files:")
        for file_path in missing_files:
            print(f"   - {file_path}")
        return False
    else:
        print("✅ All required files exist!")
        return True

def check_directory_structure():
    """Check if all required directories exist"""
    required_dirs = [
        "src",
        "src/data_collection",
        "src/ml", 
        "src/web",
        "src/utils",
        "data",
        "models",
        "notebooks",
        "static",
        "templates"
    ]
    
    missing_dirs = []
    for dir_path in required_dirs:
        if not os.path.exists(dir_path):
            missing_dirs.append(dir_path)
    
    if missing_dirs:
        print("❌ Missing directories:")
        for dir_path in missing_dirs:
            print(f"   - {dir_path}")
        return False
    else:
        print("✅ All required directories exist!")
        return True

def main():
    print("🚌 TTC Delay Predictor - Structure Validation")
    print("=" * 50)
    
    files_ok = check_file_structure()
    dirs_ok = check_directory_structure()
    
    if files_ok and dirs_ok:
        print("\n🎉 Project structure is complete!")
        print("📋 Next steps:")
        print("   1. Install Python 3.8+ if not already installed")
        print("   2. Run: pip install -r requirements.txt")
        print("   3. Run: python run_dashboard.py")
        print("   4. Open: http://localhost:8501")
    else:
        print("\n❌ Project structure needs fixing")
        print("   Please ensure all files and directories are created")

if __name__ == "__main__":
    main()

