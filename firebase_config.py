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

# Cargar variables de entorno local (.env)
load_dotenv()

def initialize_firebase():
    """
    Inicializa Firebase de forma inteligente para Local o Render.
    """
    try:
        # 1. Intentar modo Producción (Render)
        # Asegúrate de llamar a la variable igual en el panel de Render
        creds_json_str = os.getenv("FIREBASE_CREDENTIALS_JSON")
        
        if creds_json_str:
            creds_dict = json.loads(creds_json_str)
            cred = credentials.Certificate(creds_dict)
            print("Conectado: Modo Producción (Render).")
        else:
            # 2. Intentar modo Local
            cred_path = os.getenv("FIREBASE_CREDENTIALS_PATH")
            if not cred_path:
                raise ValueError("Faltan variables: FIREBASE_CREDENTIALS_JSON o FIREBASE_CREDENTIALS_PATH")
            
            cred = credentials.Certificate(cred_path)
            print("Conectado: Modo Local (PC).")

        # Inicializar solo si no existe una app activa
        if not firebase_admin._apps:
            firebase_admin.initialize_app(cred)
            print("Firebase App inicializada con éxito.")

    except Exception as e:
        print(f"ERROR CRÍTICO: No se pudo conectar a Firebase: {e}")

# Ejecutar inicialización
initialize_firebase()

# Exportar herramientas (Firestore y Auth)
db = firestore.client()
firebase_auth = auth

