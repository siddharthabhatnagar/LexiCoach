from datetime import datetime
from app.db.firebase import get_firestore_db
import logging

class UserServiceError(Exception):
    pass

class User:
    def __init__(self, id: str, email: str, full_name: str = None, last_active: datetime = None):
        self.id = id
        self.email = email
        self.full_name = full_name
        self.last_active = last_active

class UserService:
    @staticmethod
    async def create_user(email: str, full_name: str | None = None) -> User:
        # User is created via Firebase Auth from the Android app, but we can store profile in Firestore
        try:
            db = get_firestore_db()
            user_ref = db.collection('users').document(email)
            user_data = {
                'email': email,
                'full_name': full_name,
                'last_active': datetime.utcnow()
            }
            user_ref.set(user_data)
            return User(id=email, email=email, full_name=full_name, last_active=user_data['last_active'])
        except Exception as e:
            logging.error(f"Error creating user by email: {e}")
            raise UserServiceError("User profile storage is unavailable") from e

    @staticmethod
    async def get_by_email(email: str) -> User | None:
        try:
            db = get_firestore_db()
            doc_ref = db.collection('users').document(email)
            doc = doc_ref.get()
            if doc.exists:
                data = doc.to_dict()
                return User(id=email, email=data.get('email'), full_name=data.get('full_name'), last_active=data.get('last_active'))
            else:
                return None
        except Exception as e:
            logging.error(f"Error fetching user by email: {e}")
            raise UserServiceError("User profile storage is unavailable") from e

    @staticmethod
    async def get_by_id(user_id: str) -> User | None:
        # id is email in our simplified setup
        return await UserService.get_by_email(email=user_id)

    @staticmethod
    async def update_last_active(user: User) -> None:
        try:
            db = get_firestore_db()
            user_ref = db.collection('users').document(user.email)
            user.last_active = datetime.utcnow()
            user_ref.update({'last_active': user.last_active})
        except Exception as e:
            logging.error(f"Error updating last active: {e}")
