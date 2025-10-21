#!/usr/bin/env python3

"""
Simple Raspberry Pi deployment script for 75 Hard Challenge app.
Run with: python3 deploy_pi.py
"""

import os
import subprocess
import sys
import time
from pathlib import Path

def run_command(cmd, shell=False):
    """Run a command and return success status."""
    try:
        if shell:
            result = subprocess.run(cmd, shell=True, check=True,
                                  capture_output=True, text=True)
        else:
            result = subprocess.run(cmd, check=True,
                                  capture_output=True, text=True)
        print(f"✓ {cmd[0] if not shell else cmd}")
        return True
    except subprocess.CalledProcessError as e:
        print(f"✗ Failed: {' '.join(cmd) if not shell else cmd}")
        print(f"Error: {e.stderr}")
        return False

def main():
    print("🚀 Deploying 75 Hard Challenge Tracker...")

    # Check if we're on Raspberry Pi (optional)
    import platform
    system = platform.system().lower()
    is_pi = False

    try:
        with open('/proc/cpuinfo', 'r') as f:
            cpuinfo = f.read()
        if 'Raspberry Pi' in cpuinfo or 'raspberrypi' in cpuinfo.lower():
            is_pi = True
    except:
        pass

    if not is_pi:
        print("ℹ️  Running on non-Pi system. This will work but won't install system packages.")

    if is_pi:
        print("✅ Detected Raspberry Pi - will install system dependencies.")
    else:
        print("✅ Detected non-Pi system - skipping system package installation.")

    # Install system dependencies (only on Pi)
    if is_pi:
        print("\n📦 Installing system dependencies...")
        system_deps = [
            "python3",
            "python3-pip",
            "python3-dev",
            "build-essential",
        ]

        if run_command(["sudo", "apt-get", "update"]):
            for package in system_deps:
                run_command(["sudo", "apt-get", "install", "-y", package])
    else:
        print(f"\n📦 Skipping system dependencies (detected {system}) - not Raspberry Pi")

    # Install Python dependencies
    print("\n🐍 Installing Python dependencies...")
    if Path("requirements.txt").exists():
        if not run_command([sys.executable, "-m", "pip", "install", "--user", "-r", "requirements.txt"]):
            print("Using --break-system-packages for pip install...")
            run_command([sys.executable, "-m", "pip", "install", "--break-system-packages", "-r", "requirements.txt"])
    else:
        print("✗ requirements.txt not found!")

    # Create data directory for SQLite
    print("\n💾 Creating data directories...")
    os.makedirs("instance", exist_ok=True)
    print("✓ Created instance/ directory for SQLite database")

    # Set database path environment variable
    env_file = ".env"
    with open(env_file, 'w') as f:
        f.write("DATABASE_URL=sqlite:///instance/75hard.db\n")
        f.write("SECRET_KEY=your-secret-key-change-in-production\n")
        f.write("FLASK_ENV=production\n")
    print(f"✓ Created {env_file} with production settings")

    # Test that the app can import
    print("\n🧪 Testing application...")
    try:
        import flask
        import sqlalchemy
        import flask_login
        print("✓ All Python dependencies imported successfully")

        # Try importing our app
        old_path = sys.path
        sys.path.insert(0, os.getcwd())
        try:
            from app import app, db
            print("✓ Flask application imported successfully")
            app.config['TESTING'] = True

            with app.app_context():
                # Test database creation
                db.create_all()
                print("✓ Database tables created successfully")
        finally:
            sys.path = old_path

    except ImportError as e:
        print(f"✗ Import error: {e}")
        return False

    # Create start script
    print("\n📜 Creating start script...")
    start_script = "start_app.sh"
    with open(start_script, 'w') as f:
        f.write("#!/bin/bash\n")
        f.write("# Start 75 Hard Challenge app\n")
        f.write("cd $(dirname $0)\n")
        f.write("python3 app.py\n")
    os.chmod(start_script, 0o755)
    print(f"✓ Created {start_script}")

    # Create systemd service (optional)
    create_service = input("\nDo you want to create a systemd service to auto-start the app? (y/n): ").lower().strip()
    if create_service == 'y':
        print("\n👷 Creating systemd service...")
        service_content = f"""[Unit]
Description=75 Hard Challenge Tracker
After=network.target

[Service]
Type=simple
User={os.getlogin()}
WorkingDirectory={os.getcwd()}
ExecStart={sys.executable} app.py
Restart=always
RestartSec=5
Environment=FLASK_ENV=production

[Install]
WantedBy=multi-user.target
"""

        service_file = "/tmp/75hard.service"
        with open(service_file, 'w') as f:
            f.write(service_content)

        try:
            run_command(["sudo", "cp", service_file, "/etc/systemd/system/75hard.service"])
            run_command(["sudo", "systemctl", "daemon-reload"])
            print("✓ Systemd service created")
            print("  To enable: sudo systemctl enable 75hard")
            print("  To start:  sudo systemctl start 75hard")
            print("  To check:  sudo systemctl status 75hard")
        except:
            print("✗ Failed to create systemd service (you'll need to run manually)")
    else:
        print("✓ Skipping systemd service creation")

    print("\n🎉 Deployment complete!")
    print("\nTo start the app:")
    print(f"  cd {os.getcwd()}")
    print("./start_app.sh")
    print("\nOr run directly:")
    print("python3 app.py")
    print("\nAccess at: http://your-pi-ip:5000")
    print("\nThe app will automatically create the database and default challenge when first run.")

    # Offer to start the app
    start_now = input("\nStart the app now? (y/n): ").lower().strip()
    if start_now == 'y':
        print("\nStarting app...")
        try:
            os.system("./start_app.sh")
        except KeyboardInterrupt:
            print("\nApp stopped.")

if __name__ == "__main__":
    main()
