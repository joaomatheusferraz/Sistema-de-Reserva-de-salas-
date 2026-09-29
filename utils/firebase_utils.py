import json 
import os 
from pathlib import Path

import firebase_admin 
from firebase_admin import credentials, firestore

def init_firestore():
    if not firebase_admin._apps:
        service_account_json = os.environ.get(
            "FIREBASE_SERVICE_ACCOUNT_JSON"
        )

        if service_account_json:
            cred_info = json.loads(service_account_json)
            cred = credentials.Certificate(cred_info)
        else:
            cred = credentials.Certificate(str(Path(__file__).resolve().parents[1] / "secrets" / "key.json"))

        firebase_admin.initialize_app(cred)

    return firestore.client()
