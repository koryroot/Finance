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

import firebase_admin
from firebase_admin import credentials, auth, firestore
import os
import json
from dotenv import load_dotenv

# Cargar variables locales
load_dotenv()

def get_firebase_creds():
    """Obtiene las credenciales ya sea de Render o de Local."""
    # 1. Intentar Render (Variable de entorno)
    creds_json_str = os.getenv("FIREBASE_CREDENTIALS_JSON")
    if creds_json_str:
        try:
            return credentials.Certificate(json.loads(creds_json_str))
        except Exception as e:
            print(f"Error parseando JSON de Render: {e}")

    # 2. Intentar Local (Ruta de archivo)
    cred_path = os.getenv("FIREBASE_CREDENTIALS_PATH")
    if cred_path and os.path.exists(cred_path):
        return credentials.Certificate(cred_path)
    
    return None

# --- LÓGICA DE INICIALIZACIÓN CRÍTICA ---
if not firebase_admin._apps:
    cred = get_firebase_creds()
    if cred:
        firebase_admin.initialize_app(cred)
        print("Firebase inicializado con éxito.")
    else:
        print("ADVERTENCIA: No se pudieron obtener credenciales de Firebase.")

# Exportar los clientes DESPUÉS de asegurar la inicialización
# Usamos get_app() para forzar que Firestore espere a la app por defecto
try:
    default_app = firebase_admin.get_app()
    db = firestore.client(app=default_app)
    firebase_auth = auth
except ValueError:
    print("Error: La app de Firebase no se inicializó correctamente.")
    db = None
    firebase_auth = None
