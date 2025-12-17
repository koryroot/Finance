# /blueprints/learning.py

from flask import Blueprint, render_template, abort
from .auth import login_required

learning_bp = Blueprint('learning', __name__, template_folder='../templates')

# --- SIMULACIÓN DE BASE DE DATOS DE CONTENIDO ---
# Usamos un "slug" (identificador de texto) como clave
LESSONS_DB = {
    'fundamentos': {
        'title': 'Fundamentos de Inversión',
        'level': 'Básico',
        'color': 'green',
        'icon': '🌱',
        'content': """
            <p class="mb-4">Invertir no es solo para millonarios. Es la herramienta clave para proteger tu dinero contra la inflación.</p>
            <h3 class="text-xl font-bold text-white mb-2">¿Qué es el interés compuesto?</h3>
            <p class="mb-4">Es el proceso de ganar intereses sobre los intereses que ya has ganado. Es como una bola de nieve.</p>
            <div class="bg-gray-700 p-4 rounded-lg border-l-4 border-green-500 mb-4">
                <p class="font-bold">Regla de Oro:</p>
                <p>El tiempo en el mercado es más importante que intentar adivinar los tiempos del mercado.</p>
            </div>
        """
    },
    'bolsa': {
        'title': 'Bolsa de Valores',
        'level': 'Intermedio',
        'color': 'blue',
        'icon': '📈',
        'content': """
            <p class="mb-4">La bolsa es un mercado donde se compran y venden partes de empresas (acciones).</p>
            <h3 class="text-xl font-bold text-white mb-2">¿Qué es un ETF?</h3>
            <p class="mb-4">Un Exchange Traded Fund (ETF) es una canasta de acciones. Al comprar uno, inviertes en cientos de empresas a la vez, diversificando tu riesgo.</p>
        """
    },
    'cripto': {
        'title': 'Criptomonedas',
        'level': 'Avanzado',
        'color': 'purple',
        'icon': '₿',
        'content': """
            <p class="mb-4">Las criptomonedas son dinero digital descentralizado basado en tecnología Blockchain.</p>
            <p class="mb-4 text-yellow-400">⚠️ Advertencia: Es un mercado altamente volátil.</p>
        """
    },
    'bienes-raices': {
        'title': 'Bienes Raíces',
        'level': 'Intermedio',
        'color': 'yellow',
        'icon': '🏢',
        'content': """
            <p class="mb-4">Invertir en propiedades puede generar ingresos pasivos por alquiler y plusvalía.</p>
        """
    }
}

@learning_bp.route('/')
@login_required
def index():
    # Pasamos el diccionario, pero necesitamos también las claves (slugs) para los enlaces
    # Convertimos el DB a una lista amigable para el template
    modules_list = []
    for slug, data in LESSONS_DB.items():
        data['slug'] = slug # Le inyectamos el ID para poder hacer el link
        modules_list.append(data)
        
    return render_template('learning/index.html', modules=modules_list)

@learning_bp.route('/lesson/<slug>')
@login_required
def lesson_detail(slug):
    # Buscamos la lección en nuestra "Base de Datos"
    lesson = LESSONS_DB.get(slug)
    
    if not lesson:
        # Si escriben una URL que no existe, mostramos error 404
        abort(404)
        
    return render_template('learning/detail.html', lesson=lesson)