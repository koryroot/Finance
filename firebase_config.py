# # firebase_config.py
# config = {
#     "apiKey": "AIzaSyC_RbyMkEhwK3T5_Hpl05mJnQQYCuunBj4",
#     "authDomain": "billetera-inteligente-app.firebaseapp.com",
#     "projectId": "billetera-inteligente-app",
#     "storageBucket": "billetera-inteligente-app.firebasestorage.app",
#     "messagingSenderId": "818140911365",
#     "appId": "1:818140911365:web:1f620869505658fa68896c",
#     "databaseURL": ""
# }

# /firebase_config.py

import firebase_admin
from firebase_admin import credentials, auth, firestore
import os
import json
from dotenv import load_dotenv

# Cargar variables de entorno desde el archivo .env (esto solo funcionará localmente)
load_dotenv()

def initialize_firebase():
    """
    Inicializa la conexión con Firebase Admin SDK de forma inteligente.
    Primero, intenta usar las credenciales desde una variable de entorno (para Heroku).
    Si no la encuentra, recurre a la ruta del archivo (para desarrollo local).
    """
    try:
        # MÉTODO PARA HEROKU: Leer las credenciales desde una variable de entorno
        creds_json_str = os.getenv("FIREBASE_CREDENTIALS_JSON")
        if creds_json_str:
            creds_dict = json.loads(creds_json_str)
            cred = credentials.Certificate(creds_dict)
            print("Firebase inicializado desde variable de entorno (modo Heroku).")
        else:
            # MÉTODO LOCAL: Leer las credenciales desde una ruta de archivo
            cred_path = os.getenv("FIREBASE_CREDENTIALS_PATH")
            if not cred_path:
                raise ValueError("No se encontró FIREBASE_CREDENTIALS_JSON ni FIREBASE_CREDENTIALS_PATH.")
            cred = credentials.Certificate(cred_path)
            print("Firebase inicializado desde ruta de archivo (modo local).")

        # Prevenir la reinicialización de la app de Firebase
        if not firebase_admin._apps:
            firebase_admin.initialize_app(cred)
        
        print("Firebase App inicializada exitosamente.")

    except Exception as e:
        print(f"Error CRÍTICO al inicializar Firebase: {e}")

# Llama a la función para asegurar que Firebase se inicialice al importar este módulo.
initialize_firebase()

# Exporta los clientes de auth y firestore para usarlos en otras partes de la app
db = firestore.client()
firebase_auth = auth

