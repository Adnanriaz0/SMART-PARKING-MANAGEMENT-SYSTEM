from app import app, db
from models import Admin

with app.app_context():
    # Delete all existing admins
    Admin.query.delete()
    db.session.commit()
    print("All existing admins deleted.")
    
    # Create new admin
    admin = Admin(email='admin@smartparking.com')
    admin.set_password('admin123')
    db.session.add(admin)
    db.session.commit()
    
    print("New admin created successfully!")
    print("Email: admin@smartparking.com")
    print("Password: admin123")