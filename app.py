# /app.py

from flask import Flask, session, redirect, url_for, render_template
from dotenv import load_dotenv
import os
import locale

# Carga las variables de entorno desde el archivo .env
load_dotenv()

# Importa el módulo de configuración para inicializar Firebase al arrancar.
import firebase_config

# Importa los blueprints que contienen las rutas de la aplicación.
from blueprints.auth import auth_bp
from blueprints.main import main_bp
from blueprints.income import income_bp  
from blueprints.expenses import expenses_bp     
from blueprints.budget import budget_bp
from blueprints.learning import learning_bp

# Inicializa la aplicación Flask
app = Flask(__name__)

# Configura la llave secreta desde las variables de entorno para la seguridad de las sesiones.
app.secret_key = os.getenv("FLASK_SECRET_KEY")

# --- CONFIGURACIONES GLOBALES ---

# Configura el locale para que las fechas se muestren en español (ajustado para Render/Linux)
try:
    locale.setlocale(locale.LC_TIME, 'es_ES.UTF-8')
except locale.Error:
    try:
        locale.setlocale(locale.LC_TIME, 'Spanish')
    except:
        pass

# Registra un filtro de plantilla personalizado para formatear números como moneda.
@app.template_filter('number_format')
def number_format(value):
    try:
        return "{:,.2f}".format(float(value))
    except (ValueError, TypeError):
        return value

# --- REGISTRO DE BLUEPRINTS ---

app.register_blueprint(auth_bp, url_prefix='/auth')
app.register_blueprint(income_bp, url_prefix='/income')
app.register_blueprint(expenses_bp, url_prefix='/expenses')
app.register_blueprint(budget_bp, url_prefix='/budget')
app.register_blueprint(learning_bp, url_prefix='/learning') 
app.register_blueprint(main_bp, url_prefix='/')


# --- RUTA PRINCIPAL ---

@app.route('/')
def index():
    """
    Ruta principal que redirige al dashboard si el usuario ya ha iniciado sesión.
    """
    if 'user' in session:
        return redirect(url_for('main.dashboard'))
    return render_template('landing.html')


if __name__ == '__main__':
    # Render usará Gunicorn, pero esto te permite seguir probando en tu PC en el puerto 5001.
    app.run(debug=True, port=5001)

# --- FIN DEL ARCHIVO app.py ---
