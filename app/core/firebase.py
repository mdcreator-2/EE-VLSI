import firebase_admin
from firebase_admin import credentials
from app.config import Settings

settings = Settings()

def initialize_firebase():
    cred = credentials.Certificate(settings.FIREBASE_SERVICE_ACCOUNT_PATH)
    try:
        firebase_admin.initialize_app(cred,
            {
                "storageBucket":settings.FIREBASE_STORAGE_BUCKET
            }
        )
        print("Firebase Initialized Successfully")
    except ValueError:
        pass