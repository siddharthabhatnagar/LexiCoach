import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore
import json
import os

_db = None

def get_firestore_db():
    global _db
    if _db is not None:
        return _db
    
    if not firebase_admin._apps:
        # Check if FIREBASE_CREDENTIALS env var contains the JSON string
        cred_json = os.environ.get("FIREBASE_CREDENTIALS")
        if cred_json:
            cred_dict = json.loads(cred_json)
            cred = credentials.Certificate(cred_dict)
            firebase_admin.initialize_app(cred)
        else:
            # Fallback to default application credentials
            firebase_admin.initialize_app()
    
    _db = firestore.client()
    return _db
