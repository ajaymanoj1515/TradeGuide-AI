from app import create_app, db
from app.models import Admin

# Initialize the app context
app = create_app()

with app.app_context():
    # 1. Choose your Admin Credentials
    username = "admin"
    email = "admin@tradeguide.com"
    password = "admin123"  # Change this to a strong password!

    # 2. Check if Admin already exists
    existing_admin = Admin.query.filter_by(username=username).first()
    
    if existing_admin:
        print(f"⚠️  Admin user '{username}' already exists!")
    else:
        # 3. Create the new Admin
        new_admin = Admin(username=username, email=email)
        new_admin.set_password(password)  # Hashes the password securely
        
        db.session.add(new_admin)
        db.session.commit()
        
        print(f"✅ Success! Admin '{username}' created.")
        print("You can now log in at /login")