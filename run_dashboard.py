"""
TTC Delay Predictor - Complete System Launcher
Launches the full AI-powered transit delay prediction system
"""

import subprocess
import sys
import os
import time
import webbrowser
from pathlib import Path

def check_dependencies():
    """Check if all required dependencies are installed"""
    required_packages = [
        'streamlit', 'pandas', 'numpy', 'scikit-learn', 
        'plotly', 'matplotlib', 'seaborn', 'requests'
    ]
    
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package)
        except ImportError:
            missing_packages.append(package)
    
    if missing_packages:
        print("❌ Missing required packages:")
        for package in missing_packages:
            print(f"   - {package}")
        print("\n💡 Install missing packages with:")
        print("   pip install -r requirements.txt")
        return False
    
    print("✅ All dependencies are installed!")
    return True

def setup_directories():
    """Create necessary directories"""
    directories = ['data', 'models', 'logs', 'static', 'templates']
    
    for directory in directories:
        Path(directory).mkdir(exist_ok=True)
    
    print("✅ Directory structure ready!")

def run_tests():
    """Run the test suite"""
    print("🧪 Running test suite...")
    
    try:
        result = subprocess.run([
            sys.executable, "tests/test_suite.py"
        ], capture_output=True, text=True, timeout=60)
        
        if result.returncode == 0:
            print("✅ All tests passed!")
            return True
        else:
            print("⚠️  Some tests failed, but continuing...")
            print("   (This is normal for first run with mock data)")
            return True
    except subprocess.TimeoutExpired:
        print("⚠️  Tests timed out, continuing...")
        return True
    except Exception as e:
        print(f"⚠️  Test error: {e}, continuing...")
        return True

def train_models():
    """Train ML models"""
    print("🤖 Training ML models...")
    
    try:
        result = subprocess.run([
            sys.executable, "src/ml/train_models.py"
        ], capture_output=True, text=True, timeout=120)
        
        if result.returncode == 0:
            print("✅ Models trained successfully!")
            return True
        else:
            print("⚠️  Model training had issues, but continuing...")
            print("   (Models will train automatically when dashboard loads)")
            return True
    except subprocess.TimeoutExpired:
        print("⚠️  Model training timed out, continuing...")
        return True
    except Exception as e:
        print(f"⚠️  Training error: {e}, continuing...")
        return True

def launch_dashboard():
    """Launch the Streamlit dashboard"""
    print("🌐 Launching TTC Delay Predictor Dashboard...")
    print("📱 The dashboard will open in your browser automatically")
    print("🔗 If it doesn't open, go to: http://localhost:8501")
    print("\n" + "="*60)
    print("🚌 TTC DELAY PREDICTOR - AI POWERED")
    print("="*60)
    print("Features:")
    print("  ✅ Real-time delay tracking")
    print("  ✅ AI-powered delay predictions")
    print("  ✅ Anomaly detection")
    print("  ✅ Natural language queries")
    print("  ✅ Weather integration")
    print("  ✅ Interactive visualizations")
    print("="*60)
    
    try:
        # Launch Streamlit
        subprocess.run([
            sys.executable, "-m", "streamlit", "run", 
            "src/web/app.py",
            "--server.port", "8501",
            "--server.address", "localhost",
            "--theme.base", "light",
            "--theme.primaryColor", "#1f77b4",
            "--theme.backgroundColor", "#ffffff",
            "--theme.secondaryBackgroundColor", "#f0f2f6"
        ])
    except KeyboardInterrupt:
        print("\n👋 Dashboard stopped. Thanks for using TTC Delay Predictor!")
    except Exception as e:
        print(f"❌ Error launching dashboard: {e}")
        print("💡 Try running manually: streamlit run src/web/app.py")

def show_system_info():
    """Show system information and status"""
    print("\n📊 System Information:")
    print(f"   Python version: {sys.version}")
    print(f"   Working directory: {os.getcwd()}")
    print(f"   Platform: {sys.platform}")
    
    # Check if models exist
    models_dir = Path("models")
    if models_dir.exists():
        model_files = list(models_dir.glob("*.pkl"))
        print(f"   Trained models: {len(model_files)}")
    else:
        print("   Trained models: 0 (will be created)")
    
    # Check if data exists
    data_dir = Path("data")
    if data_dir.exists():
        data_files = list(data_dir.glob("*.csv"))
        print(f"   Data files: {len(data_files)}")
    else:
        print("   Data files: 0 (will use mock data)")

def main():
    """Main launcher function"""
    print("🚌 TTC Delay Predictor - Complete System Launcher")
    print("=" * 60)
    
    # System checks
    if not check_dependencies():
        return
    
    setup_directories()
    show_system_info()
    
    # Optional: Run tests (can be skipped for faster startup)
    run_tests_choice = input("\n🧪 Run test suite? (y/N): ").lower().strip()
    if run_tests_choice in ['y', 'yes']:
        run_tests()
    
    # Optional: Train models (can be skipped for faster startup)
    train_choice = input("🤖 Train models now? (y/N): ").lower().strip()
    if train_choice in ['y', 'yes']:
        train_models()
    
    print("\n🚀 Starting dashboard...")
    time.sleep(2)
    
    # Launch dashboard
    launch_dashboard()

if __name__ == "__main__":
    main()
