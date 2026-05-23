from typing import Optional
import firebase_admin
from firebase_admin import auth
from app.db.firebase import get_firestore_db

def decode_access_token(token: str) -> Optional[dict]:
    # Ensure Firebase is initialized
    get_firestore_db()
    try:
        decoded_token = auth.verify_id_token(token)
        # Firebase token contains 'uid', we'll map it to 'sub' for compatibility with existing code
        decoded_token['sub'] = decoded_token.get('email') or decoded_token.get('uid')
        return decoded_token
    except Exception as e:
        import logging
        logging.error(f"Error verifying Firebase token: {e}")
        return None
