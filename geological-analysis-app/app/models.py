from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

# We'll define db later in __init__.py to avoid circular imports

class User(UserMixin):
    def __init__(self, id, username, password_hash=None):
        self.id = id
        self.username = username
        self.password_hash = password_hash

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

# For now, let's use in-memory user storage for simplicity
# This can be replaced with proper database later
USERS = {
    1: User(1, 'admin', generate_password_hash('password123')),
    2: User(2, 'user', generate_password_hash('user123'))
}

def get_user(user_id):
    return USERS.get(int(user_id))

def get_user_by_username(username):
    for user in USERS.values():
        if user.username == username:
            return user
    return None
