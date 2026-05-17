"""
Database Initialization Script
Creates the medilife database and all required tables
"""

import os
import sys
from sqlalchemy import create_engine, text
from sqlalchemy.exc import ProgrammingError

# Database connection details
POSTGRES_USER = "postgres"
POSTGRES_PASSWORD = "postgres"
POSTGRES_HOST = "localhost"
POSTGRES_PORT = 5432
DB_NAME = "medilife"

# Connection strings
DEFAULT_DB_URI = f"postgresql+psycopg2://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_HOST}:{POSTGRES_PORT}/postgres"
TARGET_DB_URI = f"postgresql+psycopg2://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_HOST}:{POSTGRES_PORT}/{DB_NAME}"

def create_database():
    """Create the medilife database"""
    try:
        # Connect to default postgres database
        engine = create_engine(DEFAULT_DB_URI, isolation_level="AUTOCOMMIT")
        connection = engine.connect()
        
        print(f"✓ Connected to PostgreSQL server")
        
        # Check if database exists
        result = connection.execute(
            text(f"SELECT 1 FROM pg_database WHERE datname = '{DB_NAME}'")
        )
        
        if result.fetchone():
            print(f"✓ Database '{DB_NAME}' already exists")
        else:
            # Create database
            connection.execute(text(f"CREATE DATABASE {DB_NAME}"))
            print(f"✓ Database '{DB_NAME}' created successfully")
        
        connection.close()
        engine.dispose()
        return True
        
    except ProgrammingError as e:
        print(f"✗ Database error: {e}")
        return False
    except Exception as e:
        print(f"✗ Connection error: {e}")
        print(f"  Make sure PostgreSQL is running on {POSTGRES_HOST}:{POSTGRES_PORT}")
        return False

def create_tables():
    """Create all required tables"""
    try:
        # Import app and models
        from app import app
        from db import db
        
        print(f"✓ Flask app imported successfully")
        
        # Create all tables
        with app.app_context():
            db.create_all()
            print(f"✓ All tables created successfully")
        
        return True
        
    except ImportError as e:
        print(f"✗ Import error: {e}")
        print(f"  Make sure you're in the correct project directory")
        return False
    except Exception as e:
        print(f"✗ Table creation error: {e}")
        return False

def main():
    """Main initialization function"""
    print("=" * 60)
    print("MEDILIFE DATABASE INITIALIZATION")
    print("=" * 60)
    print()
    
    # Step 1: Create database
    print("Step 1: Creating database...")
    if not create_database():
        print("\n✗ Failed to create database")
        sys.exit(1)
    
    print()
    
    # Step 2: Create tables
    print("Step 2: Creating tables...")
    if not create_tables():
        print("\n✗ Failed to create tables")
        sys.exit(1)
    
    print()
    print("=" * 60)
    print("✓ DATABASE INITIALIZATION COMPLETE")
    print("=" * 60)
    print()
    print("You can now run: python app.py")
    print()

if __name__ == "__main__":
    main()
