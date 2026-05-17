"""
Add is_active column to users table
"""

from sqlalchemy import create_engine, text

DATABASE_URL = "postgresql+psycopg2://postgres:postgres@localhost:5432/medilife"

def add_is_active_column():
    """Add is_active column if it doesn't exist"""
    print("\n" + "="*60)
    print("UPDATING DATABASE SCHEMA")
    print("="*60 + "\n")
    
    try:
        engine = create_engine(DATABASE_URL, isolation_level="AUTOCOMMIT")
        connection = engine.connect()
        
        print("✓ Connected to database")
        
        # Check if column exists
        result = connection.execute(
            text("""
                SELECT EXISTS (
                    SELECT 1 FROM information_schema.columns 
                    WHERE table_name = 'users' AND column_name = 'is_active'
                )
            """)
        )
        
        column_exists = result.scalar()
        
        if column_exists:
            print("✓ Column 'is_active' already exists")
        else:
            # Add the column
            connection.execute(
                text("""
                    ALTER TABLE users 
                    ADD COLUMN is_active BOOLEAN DEFAULT TRUE NOT NULL
                """)
            )
            print("✓ Column 'is_active' added to users table")
        
        connection.close()
        engine.dispose()
        
        print("\n" + "="*60)
        print("✓ DATABASE SCHEMA UPDATED")
        print("="*60 + "\n")
        
        return True
        
    except Exception as e:
        print(f"✗ Error: {e}")
        return False

if __name__ == "__main__":
    add_is_active_column()
