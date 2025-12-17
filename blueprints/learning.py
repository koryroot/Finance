# blueprints/learning.py

import pandas as pd
import random
from flask import Blueprint, render_template, request, session, abort
from .auth import login_required

# --- IMPORTACIÓN DE TU CEREBRO IA ---
# Asegúrate de haber creado el archivo modelos/predecir.py
from modelos.predecir import AnalistaIA

learning_bp = Blueprint('learning', __name__, template_folder='../templates')

# INICIALIZAR LA IA (Se carga una sola vez al arrancar)
try:
    ia_bancaria = AnalistaIA()
    print("✅ IA Bancaria cargada correctamente en el servidor.")
except Exception as e:
    print(f"⚠️ Alerta: No se pudo cargar la IA. Error: {e}")
    ia_bancaria = None

# ==========================================
#  SECCIÓN 1: DATOS SIMULADOS (BASE DE DATOS)
# ==========================================

# 1.1 LECCIONES (Escuela)
LESSONS_DB = {
    'fundamentos': {
        'title': 'Fundamentos de Inversión',
        'level': 'Básico',
        'color': 'green',
        'icon': '🌱',
        'content': "<p>Invertir es poner tu dinero a trabajar...</p>" # Resumido para no ocupar espacio
    },
    'bolsa': {
        'title': 'Bolsa de Valores',
        'level': 'Intermedio',
        'color': 'blue',
        'icon': '📈',
        'content': "<p>La bolsa es el mercado de empresas...</p>"
    },
    'cripto': {
        'title': 'Criptomonedas',
        'level': 'Avanzado',
        'color': 'purple',
        'icon': '₿',
        'content': "<p>Activos digitales descentralizados...</p>"
    }
}

# 1.2 ESCENARIOS DE MERCADO (Juego)
MOCK_SCENARIOS = [
    {
        'id': 1,
        'date': '2020-03-16',
        'headline': 'La OMS declara pandemia global. Países cierran fronteras.',
        'sentiment': 0.1, 
        'sentiment_label': 'Miedo Extremo',
        'change_next_day': -12.93,
        'context': 'El inicio del confinamiento global provocó pánico masivo.'
    },
    {
        'id': 2,
        'date': '2020-11-09',
        'headline': 'Pfizer anuncia 90% de efectividad en su vacuna.',
        'sentiment': 0.9,
        'sentiment_label': 'Euforia',
        'change_next_day': 7.5,
        'context': 'La esperanza de la recuperación impulsó los mercados.'
    },
    {
        'id': 3,
        'date': '2022-02-24',
        'headline': 'Tensiones geopolíticas escalan en Europa del Este.',
        'sentiment': 0.3,
        'sentiment_label': 'Incertidumbre',
        'change_next_day': -2.5,
        'context': 'Inicio del conflicto Rusia-Ucrania impactó la energía.'
    }
]

# ==========================================
#  SECCIÓN 2: RUTAS DE LA ESCUELA
# ==========================================

@learning_bp.route('/')
@login_required
def index():
    # Convertimos el diccionario a lista para el template
    modules_list = []
    for slug, data in LESSONS_DB.items():
        data['slug'] = slug
        modules_list.append(data)
    return render_template('learning/index.html', modules=modules_list)

@learning_bp.route('/lesson/<slug>')
@login_required
def lesson_detail(slug):
    lesson = LESSONS_DB.get(slug)
    if not lesson:
        abort(404)
    return render_template('learning/detail.html', lesson=lesson)

# ==========================================
#  SECCIÓN 3: RUTAS DEL SIMULADOR (JUEGO)
# ==========================================

@learning_bp.route('/simulator', methods=['GET', 'POST'])
@login_required
def simulator():
    # Inicializar billetera virtual si no existe
    if 'virtual_wallet' not in session:
        session['virtual_wallet'] = 10000.00

    # LÓGICA DEL JUEGO (POST)
    if request.method == 'POST':
        scenario_id = int(request.form.get('scenario_id'))
        action = request.form.get('action') # 'buy' o 'short'
        
        # Buscar el escenario jugado
        scenario = next((item for item in MOCK_SCENARIOS if item["id"] == scenario_id), None)
        
        if scenario:
            change = scenario['change_next_day']
            profit = 0
            
            # Calcular ganancia/pérdida
            if action == 'buy':
                profit = (session['virtual_wallet'] * (change / 100))
            elif action == 'short':
                profit = (session['virtual_wallet'] * (-change / 100))
            
            # Actualizar saldo y guardar
            session['virtual_wallet'] += profit
            
            result = {
                'profit': profit,
                'actual_change': change,
                'context': scenario['context'],
                'new_balance': session['virtual_wallet']
            }
            return render_template('learning/game_result.html', scenario=scenario, result=result)

    # CARGAR NUEVO ESCENARIO (GET)
    scenario = random.choice(MOCK_SCENARIOS)
    return render_template('learning/game.html', scenario=scenario, wallet=session['virtual_wallet'])

# ==========================================
#  SECCIÓN 4: RUTA DE INTELIGENCIA ARTIFICIAL
# ==========================================

@learning_bp.route('/test-ia', methods=['GET', 'POST'])
@login_required
def test_ia():
    resultado = None
    
    # Opciones para los select del formulario (Deben coincidir con tu CSV original)
    opciones = {
        'sexo': ['Femenino', 'Masculino'],
        'nacionalidad': ['Dominicana', 'Extranjero'], 
        'ingresos': [
            'Menos de DOP 500,000', 
            'Entre DOP 2,000,000 y 3,999,999', 
            'Mas de DOP 25,000,000.00'
        ],
        'conocimiento': ['Ninguno', 'Principiante', 'Intermedio', 'Avanzado'],
        'laboral': ['Empleado', 'Independiente', 'Desempleado', 'Jubilado']
    }

    if request.method == 'POST':
        # 1. Recolectar datos del formulario
        datos_usuario = {
            'edad': request.form['edad'],
            'sexo': request.form['sexo'],
            'nacionalidad': request.form['nacionalidad'],
            'promedio_ingresos_anuales': request.form['ingresos'],
            'conocimiento_inversionista': request.form['conocimiento'],
            'estado_laboral': request.form['laboral']
        }
        
        # 2. Consultar a la IA
        if ia_bancaria:
            try:
                # La IA devuelve la predicción (ej. "Conservador", "Agresivo")
                resultado = ia_bancaria.predecir_perfil(datos_usuario)
            except Exception as e:
                resultado = f"Error en el análisis: {str(e)}"
        else:
            resultado = "Error: El cerebro de la IA no está cargado."

    return render_template('learning/test_ia.html', resultado=resultado, opciones=opciones)