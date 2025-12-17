# modelos/entrenar.py
import pandas as pd
import numpy as np
import joblib
import os
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import LabelEncoder

def limpiar_numero(valor):
    """Convierte '1.250.000,01' a 1250000.01"""
    if isinstance(valor, str):
        valor = valor.replace('.', '').replace(',', '.')
    return float(valor)

def entrenar():
    print("⏳ Cargando datos...")
    # Rutas dinámicas para que funcione en cualquier PC
    base_dir = os.path.dirname(os.path.abspath(__file__))
    csv_path = os.path.join(base_dir, 'data', 'DATA(operaciones_historico_clientes).csv')
    
    # Leemos con encoding latin1 y separador ;
    df = pd.read_csv(csv_path, sep=';', encoding='latin1')

    # --- 1. PREPROCESAMIENTO ---
    print("🧹 Limpiando datos...")
    
    # Seleccionamos las columnas que usaremos para predecir (Features)
    # Objetivo (Target): 'perfil_inversionista'
    features = ['edad', 'sexo', 'nacionalidad', 'promedio_ingresos_anuales', 
               'conocimiento_inversionista', 'estado_laboral']
    target = 'perfil_inversionista'
    
    df_clean = df[features + [target]].dropna()

    # Convertir texto a números (Encoding)
    encoders = {}
    for col in features:
        if df_clean[col].dtype == 'object':
            le = LabelEncoder()
            df_clean[col] = le.fit_transform(df_clean[col].astype(str))
            encoders[col] = le # Guardamos el traductor para usarlo luego
    
    # Separar X (Datos) e y (Objetivo)
    X = df_clean[features]
    y = df_clean[target]

    # --- 2. ENTRENAMIENTO ---
    print("🧠 Entrenando modelo (Random Forest)...")
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    
    modelo = RandomForestClassifier(n_estimators=100, random_state=42)
    modelo.fit(X_train, y_train)
    
    score = modelo.score(X_test, y_test)
    print(f"✅ Modelo entrenado con éxito. Precisión: {score:.2%}")

    # --- 3. GUARDADO ---
    binarios_dir = os.path.join(base_dir, 'binarios')
    os.makedirs(binarios_dir, exist_ok=True)
    
    joblib.dump(modelo, os.path.join(binarios_dir, 'modelo_perfil.pkl'))
    joblib.dump(encoders, os.path.join(binarios_dir, 'encoders.pkl'))
    print("💾 Archivos .pkl guardados en /modelos/binarios/")

if __name__ == "__main__":
    entrenar()