# modelos/predecir.py
import joblib
import os
import pandas as pd
import numpy as np

class AnalistaIA:
    def __init__(self):
        # Cargar el cerebro al iniciar
        base_dir = os.path.dirname(os.path.abspath(__file__))
        self.model_path = os.path.join(base_dir, 'binarios', 'modelo_perfil.pkl')
        self.encoders_path = os.path.join(base_dir, 'binarios', 'encoders.pkl')
        
        self.modelo = None
        self.encoders = None
        self._cargar()

    def _cargar(self):
        """Carga los archivos .pkl si existen"""
        if os.path.exists(self.model_path):
            self.modelo = joblib.load(self.model_path)
            self.encoders = joblib.load(self.encoders_path)
        else:
            print("⚠️ ADVERTENCIA: No hay cerebro entrenado. Ejecuta entrenar.py")

    def predecir_perfil(self, datos_usuario):
        """
        Recibe un diccionario con los datos del usuario y devuelve el perfil predicho.
        Ejemplo datos_usuario: {'edad': 25, 'sexo': 'Masculino', ...}
        """
        if self.modelo is None:
            return "Desconocido (Modelo no cargado)"

        # 1. Convertir diccionario a DataFrame (como una hoja de excel de 1 fila)
        df_input = pd.DataFrame([datos_usuario])

        # 2. Traducir texto a números usando los diccionarios guardados (Encoders)
        for col, le in self.encoders.items():
            if col in df_input.columns:
                # Truco de seguridad: Si llega un valor que la IA no conoce, usa el primero de la lista (índice 0)
                # para evitar que la app se rompa.
                df_input[col] = df_input[col].apply(lambda x: le.transform([str(x)])[0] if str(x) in le.classes_ else 0)

        # 3. Preguntarle al cerebro
        prediccion = self.modelo.predict(df_input)
        
        # Devolver el resultado (ej. "Agresivo")
        return prediccion[0]