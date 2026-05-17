#!/usr/bin/env python
"""Test script to check database and app initialization"""

import os
import sys

print("=" * 60)
print("CHECKING MEDILIFE APP INITIALIZATION")
print("=" * 60)

# Test 1: Check environment
print("\n1. Environment Check:")
print(f"   Current directory: {os.getcwd()}")
print(f"   Python version: {sys.version}")

# Test 2: Check imports
print("\n2. Checking Critical Imports:")
try:
    from flask import Flask
    print("   [OK] Flask imported")
except Exception as e:
    print(f"   [ERROR] Flask error: {e}")

try:
    from flask_sqlalchemy import SQLAlchemy
    print("   [OK] Flask-SQLAlchemy imported")
except Exception as e:
    print(f"   [ERROR] Flask-SQLAlchemy error: {e}")

try:
    from flask_login import LoginManager
    print("   [OK] Flask-Login imported")
except Exception as e:
    print(f"   [ERROR] Flask-Login error: {e}")

# Test 3: Check database configuration
print("\n3. Database Configuration:")
try:
    from db import db, init_db
    print("   [OK] DB module imported")
except Exception as e:
    print(f"   [ERROR] DB module error: {e}")
    sys.exit(1)

# Test 4: Initialize app and db
print("\n4. App and Database Initialization:")
try:
    from app import app
    print("   [OK] App created")
    print(f"   - Database URI: {app.config.get('SQLALCHEMY_DATABASE_URI', 'NOT SET')}")
    print(f"   - Debug mode: {app.debug}")
except Exception as e:
    print(f"   [ERROR] App initialization error: {e}")
    sys.exit(1)

# Test 5: Check auth setup
print("\n5. Authentication Setup:")
try:
    from auth import login_manager, init_auth
    print("   [OK] Auth module imported")
except Exception as e:
    print(f"   [ERROR] Auth error: {e}")

# Test 6: Check registered blueprints
print("\n6. Registered Blueprints:")
with app.app_context():
    for name, bp in app.blueprints.items():
        print(f"   [OK] {name}: {bp}")

# Test 7: Check models
print("\n7. Models and Tables:")
try:
    with app.app_context():
        from models import User, DiseasePrediction, ChatbotHistory, Report
        from db import db
        
        # Try to get table names
        inspector = db.inspect(db.engine)
        existing_tables = inspector.get_table_names()
        
        print(f"   Existing tables in DB: {existing_tables if existing_tables else 'NONE'}")
        
        # Show what models are available
        print(f"   Models defined: User, DiseasePrediction, ChatbotHistory, Report")
        
except Exception as e:
    print(f"   [ERROR] Model error: {e}")

# Test 8: Check routes
print("\n8. Registered Routes:")
with app.app_context():
    routes = []
    for rule in app.url_map.iter_rules():
        if rule.endpoint != 'static':
            routes.append(f"{rule.endpoint}: {rule.rule}")
    
    # Show some key routes
    key_routes = [r for r in routes if any(x in r for x in ['login', 'register', 'dashboard', 'admin', 'predict'])]
    for route in sorted(key_routes)[:10]:
        print(f"   {route}")
    
    if len(key_routes) > 10:
        print(f"   ... and {len(key_routes) - 10} more")

print("\n" + "=" * 60)
print("INITIALIZATION CHECK COMPLETE")
print("=" * 60)
