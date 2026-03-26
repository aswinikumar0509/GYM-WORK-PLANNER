# from database import init_db, add_user, get_user

# init_db()

# add_user("JohnDoe", 28, "Beginner", "Weight Loss", "Bodyweight")

# user = get_user("JohnDoe")
# if user:
#     print(f"✅ Found user: {user.name}, Age: {user.age}, Goal: {user.goal}, Equipment: {user.equipment}")
# else:
#     print("❌ User not found.")

import secrets
print(secrets.token_hex(32))