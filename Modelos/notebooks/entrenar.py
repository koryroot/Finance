# modelos/entrenar.py

import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier # O el que estés usando
import joblib # <--- PARA GUARDAR EL MODELO
import os

def entrenar_modelo():
    # 1. Cargar datos (Usando rutas relativas seguras)
    base_dir = os.path.dirname(os.path.abspath(__file__))
    csv_path = os.path.join(base_dir, 'data', 'DATA(operaciones_historico_clientes).csv')
    
    df = pd.read_csv(csv_path, delimiter=';') # Ojo con el delimitador

    # ... (AQUÍ VA TUE LÓGICA DE LIMPIEZA Y ENTRENAMIENTO ACTUAL) ...
    # ... X = variables, y = objetivo ...
    # model.fit(X, y)

    # 2. Guardar el modelo entrenado
    model_path = os.path.join(base_dir, 'binarios', 'modelo_riesgo_v1.pkl')
    joblib.dump(model, model_path)
    print(f"Modelo entrenado y guardado en: {model_path}")

if __name__ == "__main__":
    entrenar_modelo()