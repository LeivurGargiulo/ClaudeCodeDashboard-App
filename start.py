#!/usr/bin/env python3
"""
Universal Claude Code Dashboard Launcher

Cross-platform one-click launcher that works on both Windows and Linux.
Automatically sets up everything and starts the dashboard.

Usage: python start.py
"""

import os
import sys
import subprocess
import webbrowser
import time
import threading
import platform
from pathlib import Path


def is_windows():
    """Check if running on Windows."""
    return platform.system() == "Windows"


def print_status(message, status="info"):
    """Print status messages with icons."""
    icons = {
        "success": "✅",
        "error": "❌", 
        "warning": "⚠️",
        "info": "🔧"
    }
    icon = icons.get(status, "📦")
    print(f"{icon} {message}")


def run_command(cmd, cwd=None, shell=None, capture_output=False, timeout=300):
    """Run command with cross-platform compatibility."""
    if shell is None:
        shell = is_windows()
    
    try:
        result = subprocess.run(
            cmd, 
            cwd=cwd, 
            shell=shell, 
            capture_output=capture_output, 
            text=True,
            timeout=timeout
        )
        if capture_output:
            return result.returncode == 0, result.stdout.strip()
        return result.returncode == 0, ""
    except subprocess.TimeoutExpired:
        return False, "Command timed out"
    except Exception as e:
        return False, str(e)


def check_dependencies():
    """Check all required dependencies."""
    print_status("Checking dependencies...")
    
    # Check Python version
    if sys.version_info < (3, 11):
        print_status(f"Python 3.11+ required. Current: {sys.version.split()[0]}", "error")
        return False
    print_status(f"Python {sys.version.split()[0]}", "success")
    
    # Check Node.js
    success, version = run_command("node --version", capture_output=True)
    if not success:
        print_status("Node.js not found. Install from https://nodejs.org/", "error")
        return False
    
    try:
        major_version = int(version[1:].split('.')[0])
        if major_version < 18:
            print_status(f"Node.js 18+ required. Current: {version}", "error")
            return False
    except:
        print_status(f"Could not parse Node.js version: {version}", "error")
        return False
    
    print_status(f"Node.js {version}", "success")
    
    # Check npm
    success, npm_version = run_command("npm --version", capture_output=True)
    if not success:
        print_status("npm not found", "error")
        return False
    
    print_status(f"npm {npm_version}", "success")
    return True


def setup_backend():
    """Set up backend environment."""
    print_status("Setting up backend...")
    
    root_dir = Path(__file__).parent
    backend_dir = root_dir / "backend"
    
    if not backend_dir.exists():
        print_status("Backend directory not found", "error")
        return False
    
    # Virtual environment setup
    venv_dir = backend_dir / "venv"
    if not venv_dir.exists():
        print_status("Creating virtual environment...")
        success, error = run_command([sys.executable, "-m", "venv", "venv"], cwd=backend_dir)
        if not success:
            print_status(f"Failed to create virtual environment: {error}", "error")
            return False
    
    # Get paths for virtual environment
    if is_windows():
        python_exe = venv_dir / "Scripts" / "python.exe"
        pip_exe = venv_dir / "Scripts" / "pip.exe"
    else:
        python_exe = venv_dir / "bin" / "python"
        pip_exe = venv_dir / "bin" / "pip"
    
    # Install dependencies
    requirements_file = backend_dir / "requirements.txt"
    if requirements_file.exists():
        print_status("Installing Python dependencies...")
        success, error = run_command([str(pip_exe), "install", "-r", "requirements.txt"], cwd=backend_dir)
        if not success:
            print_status("Python dependencies may already be installed", "warning")
    
    # Create .env file
    env_file = backend_dir / ".env"
    if not env_file.exists():
        print_status("Creating configuration file...")
        env_content = """HOST=0.0.0.0
PORT=8000
DISABLE_AUTH=true
SECRET_KEY=development-secret-key
DASHBOARD_USERNAME=admin
DASHBOARD_PASSWORD=admin
LOG_LEVEL=INFO"""
        env_file.write_text(env_content)
    
    print_status("Backend setup complete", "success")
    return True


def setup_frontend():
    """Set up frontend environment."""
    print_status("Setting up frontend...")
    
    root_dir = Path(__file__).parent
    frontend_dir = root_dir / "frontend"
    
    if not frontend_dir.exists():
        print_status("Frontend directory not found", "error")
        return False
    
    # Install npm dependencies
    package_json = frontend_dir / "package.json"
    node_modules = frontend_dir / "node_modules"
    
    if package_json.exists() and not node_modules.exists():
        print_status("Installing Node.js dependencies...")
        success, error = run_command("npm install", cwd=frontend_dir)
        if not success:
            print_status("Node.js dependencies may already be installed", "warning")
    
    print_status("Frontend setup complete", "success")
    return True


def wait_for_server(url, timeout=30, name="server"):
    """Wait for server to become available."""
    print_status(f"Waiting for {name} to start...")
    
    # Try using curl first, then Python requests as fallback
    for attempt in range(timeout):
        time.sleep(1)
        
        # Try curl first (faster)
        success, _ = run_command(f"curl -s {url}", capture_output=True)
        if success:
            print_status(f"{name.title()} started successfully", "success")
            return True
        
        # Fallback to Python requests
        try:
            import urllib.request
            urllib.request.urlopen(url, timeout=2)
            print_status(f"{name.title()} started successfully", "success")
            return True
        except:
            continue
    
    print_status(f"{name.title()} may still be starting...", "warning")
    return True


def start_backend():
    """Start the backend server."""
    root_dir = Path(__file__).parent
    backend_dir = root_dir / "backend"
    
    if is_windows():
        python_exe = backend_dir / "venv" / "Scripts" / "python.exe"
    else:
        python_exe = backend_dir / "venv" / "bin" / "python"
    
    def run_backend():
        """Run backend in separate thread."""
        try:
            os.chdir(backend_dir)
            subprocess.call([str(python_exe), "main.py"])
        except Exception as e:
            print_status(f"Backend error: {e}", "error")
    
    print_status("Starting backend server...")
    backend_thread = threading.Thread(target=run_backend, daemon=True)
    backend_thread.start()
    
    return wait_for_server("http://localhost:8000/api/health", name="backend")


def start_frontend():
    """Start the frontend server."""
    root_dir = Path(__file__).parent
    frontend_dir = root_dir / "frontend"
    
    def run_frontend():
        """Run frontend in separate thread."""
        try:
            os.chdir(frontend_dir)
            subprocess.call(["npm", "run", "dev"], shell=is_windows())
        except Exception as e:
            print_status(f"Frontend error: {e}", "error")
    
    print_status("Starting frontend server...")
    frontend_thread = threading.Thread(target=run_frontend, daemon=True)
    frontend_thread.start()
    
    # Frontend takes longer to start
    time.sleep(8)
    print_status("Frontend started successfully", "success")
    return True


def main():
    """Main launcher function."""
    print("🤖 Claude Code Dashboard - Universal Launcher")
    print("=" * 50)
    print(f"Platform: {platform.system()} {platform.release()}")
    print()
    
    # Check dependencies
    if not check_dependencies():
        print_status("Please install missing dependencies and try again", "error")
        if is_windows():
            input("Press Enter to exit...")
        return 1
    
    # Setup environments
    if not setup_backend():
        print_status("Backend setup failed", "error")
        return 1
    
    if not setup_frontend():
        print_status("Frontend setup failed", "error")
        return 1
    
    print("\n🚀 Starting Claude Code Dashboard...")
    print("-" * 40)
    
    # Start servers
    if not start_backend():
        print_status("Failed to start backend", "error")
        return 1
    
    if not start_frontend():
        print_status("Failed to start frontend", "error")
        return 1
    
    # Open browser
    print_status("Opening browser...")
    time.sleep(2)
    webbrowser.open("http://localhost:3000")
    
    print("\n" + "=" * 50)
    print_status("Dashboard is running!", "success")
    print()
    print("   🌐 Frontend: http://localhost:3000")
    print("   🔧 Backend:  http://localhost:8000")
    print("   📚 API Docs: http://localhost:8000/docs")
    print()
    print("📝 Default credentials:")
    print("   Username: admin")
    print("   Password: admin")
    print()
    print("🛑 Press Ctrl+C to stop all servers")
    print("=" * 50)
    
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n🛑 Stopping servers...")
        print_status("Servers stopped", "success")
        return 0


if __name__ == "__main__":
    try:
        exit_code = main()
        sys.exit(exit_code or 0)
    except KeyboardInterrupt:
        print("\n🛑 Interrupted by user")
        sys.exit(0)
    except Exception as e:
        print_status(f"Unexpected error: {e}", "error")
        if is_windows():
            input("Press Enter to exit...")
        sys.exit(1)