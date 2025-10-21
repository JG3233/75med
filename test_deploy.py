#!/usr/bin/env python3

"""
Test deployment script for macOS - same as deploy but without system packages
"""

import os
import sys
from pathlib import Path

def main():
    print("🧪 Testing 75 Hard Challenge Tracker deployment...")

    # Create data directory for SQLite
    print("\n💾 Creating data directories...")
    os.makedirs("instance", exist_ok=True)
    print("✓ Created instance/ directory for SQLite database")

    # Test that the app can import
    print("\n🧪 Testing application...")
    try:
        import flask
        import sqlalchemy
        import flask_login
        print("✓ All Python dependencies available")

        # Try importing our app
        old_path = sys.path
        sys.path.insert(0, os.getcwd())
        try:
            from app import app, db
            print("✓ Flask application imported successfully")
            print(f"✓ Templates found: {app.jinja_env.list_templates()}")

            with app.app_context():
                # Test database creation
                db.create_all()
                print("✓ Database tables created successfully")

                # Test that we can create a test user
                from models import User
                test_user = User.query.filter_by(username='testuser').first()
                if not test_user:
                    test_user = User(username='testuser')
                    test_user.set_password('testpass')
                    db.session.add(test_user)
                    db.session.commit()
                    print("✓ Test user created successfully")
                else:
                    print("✓ Test user already exists")

        except Exception as e:
            print(f"✗ Application test failed: {e}")
            return False
        finally:
            sys.path = old_path

    except ImportError as e:
        print(f"✗ Import error: {e}")
        return False

    print("\n🎉 App ready for deployment!")
    print(f"📁 Project location: {os.getcwd()}")
    print("📄 Files created:")
    print("  - instance/ (SQLite database directory)")
    print("  - app.py (Flask application)")
    print("  - models.py, config.py (configuration)")
    print("  - templates/ (HTML templates)")
    print("  - static/css/ (stylesheets)")
    print("  - requirements.txt (dependencies)")
    print("\n🚀 Ready to transfer to Raspberry Pi!")

    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
