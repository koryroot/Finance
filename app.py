# /app.py

from flask import Flask, session, redirect, url_for, render_template
from dotenv import load_dotenv
import os
import locale

# Carga las variables de entorno desde el archivo .env
load_dotenv()

# Importa el módulo de configuración para inicializar Firebase al arrancar.
# Esta es la única línea necesaria para la conexión.
import firebase_config

# Importa los blueprints que contienen las rutas de la aplicación.
from blueprints.auth import auth_bp
from blueprints.main import main_bp

# Inicializa la aplicación Flask
app = Flask(__name__)

# Configura la llave secreta desde las variables de entorno para la seguridad de las sesiones.
app.secret_key = os.getenv("FLASK_SECRET_KEY")

# --- CONFIGURACIONES GLOBALES ---

# Configura el locale para que las fechas (como los meses) se muestren en español.
try:
    locale.setlocale(locale.LC_TIME, 'es_ES.UTF-8')
except locale.Error:
    locale.setlocale(locale.LC_TIME, 'Spanish')

# Registra un filtro de plantilla personalizado para formatear números como moneda.
# Este filtro estará disponible en todos tus archivos HTML.
@app.template_filter('number_format')
def number_format(value):
    try:
        return "{:,.2f}".format(float(value))
    except (ValueError, TypeError):
        return value

# --- REGISTRO DE BLUEPRINTS ---

# Registra los blueprints en la aplicación, asignando un prefijo a sus URLs.
# Todas las rutas en auth.py comenzarán con /auth
app.register_blueprint(auth_bp, url_prefix='/auth')
# Todas las rutas en main.py estarán en la raíz del sitio.
app.register_blueprint(main_bp, url_prefix='/')


# --- RUTA PRINCIPAL ---

@app.route('/')
def index():
    """
    Ruta principal que redirige al dashboard si el usuario ya ha iniciado sesión,
    o muestra la página de bienvenida (landing) si no lo ha hecho.
    """
    if 'user' in session:
        return redirect(url_for('main.dashboard'))
    return render_template('landing.html')


if __name__ == '__main__':
    # Ejecuta la aplicación en modo debug.
    # El puerto 5001 es útil si ya tienes otro proyecto corriendo en el 5000.
    app.run(debug=True, port=5001)
# --- FIN DEL ARCHIVO app.py ---