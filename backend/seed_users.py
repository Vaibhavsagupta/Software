from database import SessionLocal, engine
from models import User, Base
from auth_utils import hash_password

# Create tables if they don't exist
Base.metadata.create_all(bind=engine)

db = SessionLocal()

def create_user(username, password, role):
    # Check if user exists
    user = db.query(User).filter(User.username == username).first()
    if user:
        print(f"User {username} already exists. Updating password and role.")
        user.password = hash_password(password)
        user.role = role
    else:
        new_user = User(
            username=username,
            password=hash_password(password),
            role=role
        )
        db.add(new_user)
        print(f"User {username} created.")

try:
    create_user("admin", "1234", "admin")
    create_user("staff", "4321", "staff")
    db.commit()
    print("Database seeded successfully.")
except Exception as e:
    print(f"Error seeding database: {e}")
    db.rollback()
finally:
    db.close()
