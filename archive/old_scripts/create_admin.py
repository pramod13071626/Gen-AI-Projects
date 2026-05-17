"""
Create default admin user for Medilife
"""

from app import app
from db import db
from models import User

def create_admin_user():
    """Create default admin user"""
    print("\n" + "="*60)
    print("CREATING DEFAULT ADMIN USER")
    print("="*60 + "\n")
    
    with app.app_context():
        # Check if admin already exists
        admin = User.query.filter_by(email='admin@gmail.com').first()
        
        if admin:
            print("✓ Admin user already exists")
            print(f"  Email: {admin.email}")
            print(f"  Name: {admin.full_name}")
            print(f"  Admin Status: {admin.is_admin}")
        else:
            # Create new admin user
            admin = User(
                full_name="Administrator",
                email="admin@gmail.com",
                age=30,
                gender="Male",
                phone="9999999999",
                is_admin=True,
                is_active=True
            )
            admin.set_password("admin123")
            
            db.session.add(admin)
            db.session.commit()
            
            print("✓ Admin user created successfully!")
            print(f"  Email: {admin.email}")
            print(f"  Password: admin123")
            print(f"  ID: {admin.user_id}")
        
        print("\n" + "="*60)
        print("LOGIN CREDENTIALS")
        print("="*60)
        print(f"Email: admin@gmail.com")
        print(f"Password: admin123")
        print("="*60 + "\n")

if __name__ == "__main__":
    create_admin_user()
