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
        'content': """<!-- Contenido Principal -->
        <div class="space-y-8">

            <!-- ¿Qué es invertir? -->
            <div class="bg-gradient-to-br from-blue-900/50 to-cyan-900/50 rounded-3xl p-8 border border-blue-500/30 shadow-2xl">
                <div class="flex items-center gap-4 mb-6">
                    <div class="text-4xl bg-blue-500/20 w-16 h-16 flex items-center justify-center rounded-xl">💡</div>
                    <h2 class="text-3xl font-bold text-white">¿Qué es invertir?</h2>
                </div>
                <p class="text-gray-300 text-lg leading-relaxed mb-4">
                    Invertir es destinar dinero a un activo o proyecto con la expectativa de obtener ganancias en el futuro. 
                    A diferencia de ahorrar (guardar dinero sin generar rendimientos significativos), invertir busca que tu dinero crezca con el tiempo.
                </p>
                <div class="bg-blue-950/50 rounded-xl p-5 border border-blue-500/20">
                    <p class="text-blue-200 font-semibold">✨ Ejemplo:</p>
                    <p class="text-gray-300 mt-2">
                        Si compras acciones de una empresa a $100 y en un año valen $120, has obtenido una ganancia de $20 (20% de retorno).
                    </p>
                </div>
            </div>

            <!-- Tipos de inversión -->
            <div class="bg-gray-800 rounded-3xl p-8 border border-gray-700 shadow-2xl">
                <div class="flex items-center gap-4 mb-6">
                    <div class="text-4xl bg-purple-500/20 w-16 h-16 flex items-center justify-center rounded-xl">🎯</div>
                    <h2 class="text-3xl font-bold text-white">Tipos de Inversión</h2>
                </div>
                
                <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
                    
                    <div class="bg-gradient-to-br from-green-900/30 to-emerald-900/30 rounded-2xl p-6 border border-green-500/30">
                        <h3 class="text-xl font-bold text-green-300 mb-3">📈 Acciones</h3>
                        <p class="text-gray-300">
                            Comprar parte de una empresa. Si la empresa crece, el valor de tus acciones aumenta.
                        </p>
                        <span class="inline-block mt-3 text-xs bg-green-500/20 text-green-300 px-3 py-1 rounded-full">
                            Riesgo: Medio-Alto
                        </span>
                    </div>

                    <div class="bg-gradient-to-br from-blue-900/30 to-indigo-900/30 rounded-2xl p-6 border border-blue-500/30">
                        <h3 class="text-xl font-bold text-blue-300 mb-3">🏦 Bonos</h3>
                        <p class="text-gray-300">
                            Préstamos a gobiernos o empresas que te pagan intereses. Más estable que las acciones.
                        </p>
                        <span class="inline-block mt-3 text-xs bg-blue-500/20 text-blue-300 px-3 py-1 rounded-full">
                            Riesgo: Bajo-Medio
                        </span>
                    </div>

                    <div class="bg-gradient-to-br from-purple-900/30 to-pink-900/30 rounded-2xl p-6 border border-purple-500/30">
                        <h3 class="text-xl font-bold text-purple-300 mb-3">🏢 Fondos de Inversión</h3>
                        <p class="text-gray-300">
                            Agrupan dinero de varios inversionistas para comprar una mezcla de activos diversificados.
                        </p>
                        <span class="inline-block mt-3 text-xs bg-purple-500/20 text-purple-300 px-3 py-1 rounded-full">
                            Riesgo: Variable
                        </span>
                    </div>

                    <div class="bg-gradient-to-br from-orange-900/30 to-red-900/30 rounded-2xl p-6 border border-orange-500/30">
                        <h3 class="text-xl font-bold text-orange-300 mb-3">🏠 Bienes Raíces</h3>
                        <p class="text-gray-300">
                            Invertir en propiedades para alquilarlas o venderlas más caras en el futuro.
                        </p>
                        <span class="inline-block mt-3 text-xs bg-orange-500/20 text-orange-300 px-3 py-1 rounded-full">
                            Riesgo: Medio
                        </span>
                    </div>

                </div>
            </div>

            <!-- Conceptos clave -->
            <div class="bg-gradient-to-br from-purple-900/50 to-pink-900/50 rounded-3xl p-8 border border-purple-500/30 shadow-2xl">
                <div class="flex items-center gap-4 mb-6">
                    <div class="text-4xl bg-purple-500/20 w-16 h-16 flex items-center justify-center rounded-xl">🔑</div>
                    <h2 class="text-3xl font-bold text-white">Conceptos Clave</h2>
                </div>

                <div class="space-y-5">
                    
                    <div class="bg-purple-950/40 rounded-xl p-5 border border-purple-500/20">
                        <h3 class="text-lg font-bold text-purple-200 mb-2">⚖️ Riesgo y Retorno</h3>
                        <p class="text-gray-300">
                            Mayor riesgo suele significar mayor potencial de ganancia (pero también de pérdida). Inversiones más seguras dan menores rendimientos.
                        </p>
                    </div>

                    <div class="bg-purple-950/40 rounded-xl p-5 border border-purple-500/20">
                        <h3 class="text-lg font-bold text-purple-200 mb-2">🌐 Diversificación</h3>
                        <p class="text-gray-300">
                            No pongas todo tu dinero en un solo lugar. Distribuye tus inversiones en diferentes activos para reducir el riesgo.
                        </p>
                    </div>

                    <div class="bg-purple-950/40 rounded-xl p-5 border border-purple-500/20">
                        <h3 class="text-lg font-bold text-purple-200 mb-2">⏳ Horizonte de Inversión</h3>
                        <p class="text-gray-300">
                            ¿Cuánto tiempo puedes dejar tu dinero invertido? A largo plazo (5+ años) puedes asumir más riesgo que a corto plazo.
                        </p>
                    </div>

                    <div class="bg-purple-950/40 rounded-xl p-5 border border-purple-500/20">
                        <h3 class="text-lg font-bold text-purple-200 mb-2">💰 Interés Compuesto</h3>
                        <p class="text-gray-300">
                            Las ganancias generan más ganancias. Si reinviertes tus beneficios, tu dinero crece exponencialmente con el tiempo.
                        </p>
                    </div>

                </div>
            </div>

            <!-- Pasos para empezar -->
            <div class="bg-gradient-to-br from-green-900/50 to-teal-900/50 rounded-3xl p-8 border border-green-500/30 shadow-2xl">
                <div class="flex items-center gap-4 mb-6">
                    <div class="text-4xl bg-green-500/20 w-16 h-16 flex items-center justify-center rounded-xl">🚀</div>
                    <h2 class="text-3xl font-bold text-white">Primeros Pasos</h2>
                </div>

                <div class="space-y-4">
                    <div class="flex gap-4 items-start">
                        <div class="bg-green-500 text-white font-bold w-10 h-10 rounded-full flex items-center justify-center flex-shrink-0 text-lg">
                            1
                        </div>
                        <div>
                            <h3 class="text-lg font-bold text-green-200 mb-1">Define tus objetivos</h3>
                            <p class="text-gray-300">¿Para qué inviertes? ¿Jubilación, comprar una casa, crear patrimonio?</p>
                        </div>
                    </div>

                    <div class="flex gap-4 items-start">
                        <div class="bg-green-500 text-white font-bold w-10 h-10 rounded-full flex items-center justify-center flex-shrink-0 text-lg">
                            2
                        </div>
                        <div>
                            <h3 class="text-lg font-bold text-green-200 mb-1">Conoce tu perfil de riesgo</h3>
                            <p class="text-gray-300">¿Eres conservador, moderado o agresivo? Esto define tu estrategia.</p>
                        </div>
                    </div>

                    <div class="flex gap-4 items-start">
                        <div class="bg-green-500 text-white font-bold w-10 h-10 rounded-full flex items-center justify-center flex-shrink-0 text-lg">
                            3
                        </div>
                        <div>
                            <h3 class="text-lg font-bold text-green-200 mb-1">Edúcate constantemente</h3>
                            <p class="text-gray-300">Lee, practica en simuladores y aprende de los mercados antes de invertir dinero real.</p>
                        </div>
                    </div>

                    <div class="flex gap-4 items-start">
                        <div class="bg-green-500 text-white font-bold w-10 h-10 rounded-full flex items-center justify-center flex-shrink-0 text-lg">
                            4
                        </div>
                        <div>
                            <h3 class="text-lg font-bold text-green-200 mb-1">Empieza pequeño</h3>
                            <p class="text-gray-300">No necesitas miles de dólares. Comienza con cantidades que puedas permitirte perder.</p>
                        </div>
                    </div>
                </div>
            </div>

            <!-- Advertencia final -->
            <div class="bg-yellow-900/30 rounded-2xl p-6 border border-yellow-500/30">
                <div class="flex gap-4 items-start">
                    <div class="text-3xl">⚠️</div>
                    <div>
                        <h3 class="text-xl font-bold text-yellow-300 mb-2">Recuerda</h3>
                        <p class="text-gray-300">
                            Toda inversión conlleva riesgos. Nunca inviertas dinero que necesites a corto plazo o que no puedas permitirte perder. 
                            Investiga siempre antes de tomar decisiones y considera consultar a un asesor financiero profesional.
                        </p>
                    </div>
                </div>
            </div>

        </div>
        """ # Resumido para no ocupar espacio
    },
    'bolsa': {
        'title': 'Bolsa de Valores',
        'level': 'Intermedio',
        'color': 'blue',
        'icon': '📈',
        'content': """
        <!-- Contenido Principal -->
        <div class="space-y-8">

            <!-- ¿Qué es la Bolsa? -->
            <div class="bg-gradient-to-br from-indigo-900/50 to-purple-900/50 rounded-3xl p-8 border border-indigo-500/30 shadow-2xl">
                <div class="flex items-center gap-4 mb-6">
                    <div class="text-4xl bg-indigo-500/20 w-16 h-16 flex items-center justify-center rounded-xl">🏢</div>
                    <h2 class="text-3xl font-bold text-white">¿Qué es la Bolsa de Valores?</h2>
                </div>
                <p class="text-gray-300 text-lg leading-relaxed mb-4">
                    Es un mercado organizado donde se negocian valores (principalmente acciones y bonos). Las empresas emiten acciones para obtener financiamiento, y los inversores las compran esperando que aumenten de valor o generen dividendos.
                </p>
                <div class="bg-indigo-950/50 rounded-xl p-5 border border-indigo-500/20">
                    <p class="text-indigo-200 font-semibold">🌍 Principales bolsas del mundo:</p>
                    <div class="grid grid-cols-2 gap-3 mt-3 text-gray-300">
                        <div>• <span class="text-indigo-300">NYSE</span> (Nueva York)</div>
                        <div>• <span class="text-indigo-300">NASDAQ</span> (EE.UU.)</div>
                        <div>• <span class="text-indigo-300">Tokyo Stock Exchange</span></div>
                        <div>• <span class="text-indigo-300">London Stock Exchange</span></div>
                    </div>
                </div>
            </div>

            <!-- Cómo funciona -->
            <div class="bg-gray-800 rounded-3xl p-8 border border-gray-700 shadow-2xl">
                <div class="flex items-center gap-4 mb-6">
                    <div class="text-4xl bg-cyan-500/20 w-16 h-16 flex items-center justify-center rounded-xl">⚙️</div>
                    <h2 class="text-3xl font-bold text-white">¿Cómo Funciona?</h2>
                </div>
                
                <div class="space-y-6">
                    
                    <div class="bg-gradient-to-r from-cyan-900/30 to-blue-900/30 rounded-2xl p-6 border border-cyan-500/30">
                        <div class="flex items-start gap-4">
                            <div class="bg-cyan-500 text-white font-bold w-10 h-10 rounded-full flex items-center justify-center flex-shrink-0">
                                1
                            </div>
                            <div>
                                <h3 class="text-xl font-bold text-cyan-200 mb-2">Oferta Pública Inicial (IPO)</h3>
                                <p class="text-gray-300">
                                    Una empresa decide "salir a bolsa" vendiendo acciones al público por primera vez para recaudar capital.
                                </p>
                            </div>
                        </div>
                    </div>

                    <div class="bg-gradient-to-r from-blue-900/30 to-purple-900/30 rounded-2xl p-6 border border-blue-500/30">
                        <div class="flex items-start gap-4">
                            <div class="bg-blue-500 text-white font-bold w-10 h-10 rounded-full flex items-center justify-center flex-shrink-0">
                                2
                            </div>
                            <div>
                                <h3 class="text-xl font-bold text-blue-200 mb-2">Mercado Secundario</h3>
                                <p class="text-gray-300">
                                    Después del IPO, las acciones se negocian entre inversores en la bolsa. El precio fluctúa según oferta y demanda.
                                </p>
                            </div>
                        </div>
                    </div>

                    <div class="bg-gradient-to-r from-purple-900/30 to-pink-900/30 rounded-2xl p-6 border border-purple-500/30">
                        <div class="flex items-start gap-4">
                            <div class="bg-purple-500 text-white font-bold w-10 h-10 rounded-full flex items-center justify-center flex-shrink-0">
                                3
                            </div>
                            <div>
                                <h3 class="text-xl font-bold text-purple-200 mb-2">Intermediarios (Brokers)</h3>
                                <p class="text-gray-300">
                                    Los inversores no compran directamente en la bolsa, sino a través de brokers o plataformas de trading autorizadas.
                                </p>
                            </div>
                        </div>
                    </div>

                </div>
            </div>

            <!-- Índices Bursátiles -->
            <div class="bg-gradient-to-br from-orange-900/50 to-red-900/50 rounded-3xl p-8 border border-orange-500/30 shadow-2xl">
                <div class="flex items-center gap-4 mb-6">
                    <div class="text-4xl bg-orange-500/20 w-16 h-16 flex items-center justify-center rounded-xl">📊</div>
                    <h2 class="text-3xl font-bold text-white">Índices Bursátiles</h2>
                </div>

                <p class="text-gray-300 text-lg mb-6">
                    Son indicadores que miden el desempeño de un grupo de acciones representativas del mercado. Funcionan como termómetros de la economía.
                </p>

                <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
                    
                    <div class="bg-orange-950/40 rounded-xl p-5 border border-orange-500/20">
                        <h3 class="text-lg font-bold text-orange-200 mb-2">📈 S&P 500</h3>
                        <p class="text-gray-300 text-sm">
                            Agrupa las 500 empresas más grandes de EE.UU. Es el indicador más seguido del mercado americano.
                        </p>
                    </div>

                    <div class="bg-orange-950/40 rounded-xl p-5 border border-orange-500/20">
                        <h3 class="text-lg font-bold text-orange-200 mb-2">💻 NASDAQ 100</h3>
                        <p class="text-gray-300 text-sm">
                            Compuesto principalmente por empresas tecnológicas como Apple, Microsoft, Amazon y Google.
                        </p>
                    </div>

                    <div class="bg-orange-950/40 rounded-xl p-5 border border-orange-500/20">
                        <h3 class="text-lg font-bold text-orange-200 mb-2">🏭 Dow Jones</h3>
                        <p class="text-gray-300 text-sm">
                            Incluye 30 empresas estadounidenses de gran capitalización en diversos sectores industriales.
                        </p>
                    </div>

                    <div class="bg-orange-950/40 rounded-xl p-5 border border-orange-500/20">
                        <h3 class="text-lg font-bold text-orange-200 mb-2">🌍 FTSE 100</h3>
                        <p class="text-gray-300 text-sm">
                            Las 100 empresas más grandes del Reino Unido listadas en la Bolsa de Londres.
                        </p>
                    </div>

                </div>
            </div>

            <!-- Tipos de órdenes -->
            <div class="bg-gradient-to-br from-green-900/50 to-emerald-900/50 rounded-3xl p-8 border border-green-500/30 shadow-2xl">
                <div class="flex items-center gap-4 mb-6">
                    <div class="text-4xl bg-green-500/20 w-16 h-16 flex items-center justify-center rounded-xl">💼</div>
                    <h2 class="text-3xl font-bold text-white">Tipos de Órdenes</h2>
                </div>

                <div class="space-y-4">
                    
                    <div class="bg-green-950/40 rounded-xl p-5 border border-green-500/20">
                        <div class="flex items-start gap-3">
                            <span class="text-2xl">🎯</span>
                            <div>
                                <h3 class="text-lg font-bold text-green-200 mb-1">Orden de Mercado</h3>
                                <p class="text-gray-300">
                                    Se ejecuta inmediatamente al mejor precio disponible. Usada cuando quieres comprar/vender rápido.
                                </p>
                            </div>
                        </div>
                    </div>

                    <div class="bg-green-950/40 rounded-xl p-5 border border-green-500/20">
                        <div class="flex items-start gap-3">
                            <span class="text-2xl">🎚️</span>
                            <div>
                                <h3 class="text-lg font-bold text-green-200 mb-1">Orden Limitada</h3>
                                <p class="text-gray-300">
                                    Defines el precio máximo al que compras o mínimo al que vendes. Se ejecuta solo si se alcanza ese precio.
                                </p>
                            </div>
                        </div>
                    </div>

                    <div class="bg-green-950/40 rounded-xl p-5 border border-green-500/20">
                        <div class="flex items-start gap-3">
                            <span class="text-2xl">🛡️</span>
                            <div>
                                <h3 class="text-lg font-bold text-green-200 mb-1">Stop Loss</h3>
                                <p class="text-gray-300">
                                    Orden automática de venta que se activa si el precio cae a cierto nivel, para limitar pérdidas.
                                </p>
                            </div>
                        </div>
                    </div>

                </div>
            </div>

            <!-- Factores que mueven el mercado -->
            <div class="bg-gradient-to-br from-purple-900/50 to-blue-900/50 rounded-3xl p-8 border border-purple-500/30 shadow-2xl">
                <div class="flex items-center gap-4 mb-6">
                    <div class="text-4xl bg-purple-500/20 w-16 h-16 flex items-center justify-center rounded-xl">🌊</div>
                    <h2 class="text-3xl font-bold text-white">¿Qué Mueve los Precios?</h2>
                </div>

                <div class="grid grid-cols-1 md:grid-cols-2 gap-5">
                    
                    <div class="bg-purple-950/40 rounded-xl p-5 border border-purple-500/20">
                        <h3 class="text-lg font-bold text-purple-200 mb-2">📰 Noticias Económicas</h3>
                        <p class="text-gray-300">
                            Informes de ganancias, fusiones, escándalos o innovaciones tecnológicas impactan el precio de las acciones.
                        </p>
                    </div>

                    <div class="bg-purple-950/40 rounded-xl p-5 border border-purple-500/20">
                        <h3 class="text-lg font-bold text-purple-200 mb-2">🏦 Política Monetaria</h3>
                        <p class="text-gray-300">
                            Decisiones de los bancos centrales sobre tasas de interés afectan directamente al mercado.
                        </p>
                    </div>

                    <div class="bg-purple-950/40 rounded-xl p-5 border border-purple-500/20">
                        <h3 class="text-lg font-bold text-purple-200 mb-2">😰 Sentimiento del Mercado</h3>
                        <p class="text-gray-300">
                            El miedo o la codicia colectiva pueden causar movimientos bruscos, a veces irracionales.
                        </p>
                    </div>

                    <div class="bg-purple-950/40 rounded-xl p-5 border border-purple-500/20">
                        <h3 class="text-lg font-bold text-purple-200 mb-2">🌍 Eventos Globales</h3>
                        <p class="text-gray-300">
                            Guerras, pandemias, elecciones y desastres naturales generan volatilidad en los mercados.
                        </p>
                    </div>

                </div>
            </div>

            <!-- Horarios y trading -->
            <div class="bg-gray-800 rounded-3xl p-8 border border-gray-700 shadow-2xl">
                <div class="flex items-center gap-4 mb-6">
                    <div class="text-4xl bg-blue-500/20 w-16 h-16 flex items-center justify-center rounded-xl">⏰</div>
                    <h2 class="text-3xl font-bold text-white">Horarios de Trading</h2>
                </div>

                <p class="text-gray-300 text-lg mb-5">
                    Las bolsas operan en horarios específicos. Fuera de estos horarios existe el "after-hours trading" con menor liquidez.
                </p>

                <div class="bg-blue-950/30 rounded-xl p-6 border border-blue-500/20">
                    <div class="grid grid-cols-1 md:grid-cols-2 gap-4 text-gray-300">
                        <div>
                            <span class="text-blue-300 font-bold">NYSE/NASDAQ:</span>
                            <p class="mt-1">9:30 AM - 4:00 PM EST</p>
                        </div>
                        <div>
                            <span class="text-blue-300 font-bold">London Stock Exchange:</span>
                            <p class="mt-1">8:00 AM - 4:30 PM GMT</p>
                        </div>
                        <div>
                            <span class="text-blue-300 font-bold">Tokyo Stock Exchange:</span>
                            <p class="mt-1">9:00 AM - 3:00 PM JST</p>
                        </div>
                        <div>
                            <span class="text-blue-300 font-bold">Frankfurt Stock Exchange:</span>
                            <p class="mt-1">9:00 AM - 5:30 PM CET</p>
                        </div>
                    </div>
                </div>
            </div>

            <!-- Tips para invertir -->
            <div class="bg-gradient-to-br from-teal-900/50 to-cyan-900/50 rounded-3xl p-8 border border-teal-500/30 shadow-2xl">
                <div class="flex items-center gap-4 mb-6">
                    <div class="text-4xl bg-teal-500/20 w-16 h-16 flex items-center justify-center rounded-xl">💡</div>
                    <h2 class="text-3xl font-bold text-white">Consejos para Operar</h2>
                </div>

                <div class="space-y-3">
                    <div class="flex gap-3 items-start bg-teal-950/30 rounded-xl p-4 border border-teal-500/20">
                        <span class="text-xl">✅</span>
                        <p class="text-gray-300">Investiga las empresas antes de comprar sus acciones (fundamentales, balances, líderes)</p>
                    </div>
                    <div class="flex gap-3 items-start bg-teal-950/30 rounded-xl p-4 border border-teal-500/20">
                        <span class="text-xl">✅</span>
                        <p class="text-gray-300">Diversifica tu portafolio en diferentes sectores y geografías</p>
                    </div>
                    <div class="flex gap-3 items-start bg-teal-950/30 rounded-xl p-4 border border-teal-500/20">
                        <span class="text-xl">✅</span>
                        <p class="text-gray-300">No inviertas dinero que necesitas a corto plazo o que no puedas perder</p>
                    </div>
                    <div class="flex gap-3 items-start bg-teal-950/30 rounded-xl p-4 border border-teal-500/20">
                        <span class="text-xl">✅</span>
                        <p class="text-gray-300">Mantén la calma en momentos de volatilidad y evita decisiones emocionales</p>
                    </div>
                </div>
            </div>

            <!-- Advertencia -->
            <div class="bg-red-900/30 rounded-2xl p-6 border border-red-500/30">
                <div class="flex gap-4 items-start">
                    <div class="text-3xl">⚠️</div>
                    <div>
                        <h3 class="text-xl font-bold text-red-300 mb-2">Importante</h3>
                        <p class="text-gray-300">
                            El mercado de valores es volátil y puede generar pérdidas significativas. Este contenido es educativo y no constituye asesoría financiera. Consulta siempre con un profesional antes de invertir.
                        </p>
                    </div>
                </div>
            </div>

        </div>
        """
    },
    'cripto': {
        'title': 'Criptomonedas',
        'level': 'Avanzado',
        'color': 'purple',
        'icon': '₿',
        'content': """
        <!-- Contenido Principal -->
        <div class="space-y-8">

            <!-- Fundamentos de Blockchain -->
            <div class="bg-gradient-to-br from-purple-900/50 to-indigo-900/50 rounded-3xl p-8 border border-purple-500/30 shadow-2xl">
                <div class="flex items-center gap-4 mb-6">
                    <div class="text-4xl bg-purple-500/20 w-16 h-16 flex items-center justify-center rounded-xl">⛓️</div>
                    <h2 class="text-3xl font-bold text-white">Tecnología Blockchain</h2>
                </div>
                <p class="text-gray-300 text-lg leading-relaxed mb-4">
                    Blockchain es un libro contable distribuido e inmutable que registra transacciones en bloques enlazados criptográficamente. Cada bloque contiene un hash del bloque anterior, creando una cadena verificable y resistente a manipulaciones.
                </p>
                <div class="grid grid-cols-1 md:grid-cols-3 gap-4 mt-6">
                    <div class="bg-purple-950/50 rounded-xl p-5 border border-purple-500/20">
                        <h3 class="text-lg font-bold text-purple-200 mb-2">🔐 Descentralización</h3>
                        <p class="text-gray-300 text-sm">No hay autoridad central. Los nodos validan transacciones mediante consenso.</p>
                    </div>
                    <div class="bg-purple-950/50 rounded-xl p-5 border border-purple-500/20">
                        <h3 class="text-lg font-bold text-purple-200 mb-2">🔒 Inmutabilidad</h3>
                        <p class="text-gray-300 text-sm">Una vez registrado, un bloque no puede ser alterado sin modificar toda la cadena.</p>
                    </div>
                    <div class="bg-purple-950/50 rounded-xl p-5 border border-purple-500/20">
                        <h3 class="text-lg font-bold text-purple-200 mb-2">👁️ Transparencia</h3>
                        <p class="text-gray-300 text-sm">Todas las transacciones son públicas y auditables en tiempo real.</p>
                    </div>
                </div>
            </div>

            <!-- Mecanismos de Consenso -->
            <div class="bg-gray-800 rounded-3xl p-8 border border-gray-700 shadow-2xl">
                <div class="flex items-center gap-4 mb-6">
                    <div class="text-4xl bg-cyan-500/20 w-16 h-16 flex items-center justify-center rounded-xl">⚡</div>
                    <h2 class="text-3xl font-bold text-white">Mecanismos de Consenso</h2>
                </div>
                
                <div class="space-y-5">
                    
                    <div class="bg-gradient-to-r from-yellow-900/30 to-orange-900/30 rounded-2xl p-6 border border-yellow-500/30">
                        <div class="flex items-start gap-4">
                            <span class="text-3xl">⛏️</span>
                            <div>
                                <h3 class="text-xl font-bold text-yellow-200 mb-2">Proof of Work (PoW)</h3>
                                <p class="text-gray-300 mb-3">
                                    Los mineros compiten resolviendo complejos problemas criptográficos. Consume mucha energía pero ofrece alta seguridad.
                                </p>
                                <span class="text-sm text-yellow-300">Usado por: Bitcoin, Ethereum Classic, Litecoin</span>
                            </div>
                        </div>
                    </div>

                    <div class="bg-gradient-to-r from-blue-900/30 to-cyan-900/30 rounded-2xl p-6 border border-blue-500/30">
                        <div class="flex items-start gap-4">
                            <span class="text-3xl">🏦</span>
                            <div>
                                <h3 class="text-xl font-bold text-blue-200 mb-2">Proof of Stake (PoS)</h3>
                                <p class="text-gray-300 mb-3">
                                    Los validadores "apuestan" sus tokens para validar bloques. Más eficiente energéticamente y escalable.
                                </p>
                                <span class="text-sm text-blue-300">Usado por: Ethereum 2.0, Cardano, Polkadot, Solana</span>
                            </div>
                        </div>
                    </div>

                    <div class="bg-gradient-to-r from-purple-900/30 to-pink-900/30 rounded-2xl p-6 border border-purple-500/30">
                        <div class="flex items-start gap-4">
                            <span class="text-3xl">🔱</span>
                            <div>
                                <h3 class="text-xl font-bold text-purple-200 mb-2">Delegated Proof of Stake (DPoS)</h3>
                                <p class="text-gray-300 mb-3">
                                    Los holders votan por delegados que validan transacciones. Mayor velocidad pero menor descentralización.
                                </p>
                                <span class="text-sm text-purple-300">Usado por: EOS, Tron, Tezos</span>
                            </div>
                        </div>
                    </div>

                </div>
            </div>

            <!-- DeFi -->
            <div class="bg-gradient-to-br from-green-900/50 to-teal-900/50 rounded-3xl p-8 border border-green-500/30 shadow-2xl">
                <div class="flex items-center gap-4 mb-6">
                    <div class="text-4xl bg-green-500/20 w-16 h-16 flex items-center justify-center rounded-xl">🏛️</div>
                    <h2 class="text-3xl font-bold text-white">DeFi: Finanzas Descentralizadas</h2>
                </div>

                <p class="text-gray-300 text-lg mb-6">
                    Ecosistema financiero basado en smart contracts que opera sin intermediarios tradicionales. Permite préstamos, intercambios y rendimientos programables.
                </p>

                <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
                    
                    <div class="bg-green-950/40 rounded-xl p-5 border border-green-500/20">
                        <h3 class="text-lg font-bold text-green-200 mb-2">🔄 DEX (Exchanges Descentralizados)</h3>
                        <p class="text-gray-300 text-sm mb-2">
                            Plataformas como Uniswap y PancakeSwap usan Automated Market Makers (AMM) para intercambiar tokens sin libro de órdenes.
                        </p>
                        <span class="text-xs text-green-300">Modelo: Liquidity Pools + Algoritmos de pricing</span>
                    </div>

                    <div class="bg-green-950/40 rounded-xl p-5 border border-green-500/20">
                        <h3 class="text-lg font-bold text-green-200 mb-2">💎 Yield Farming & Staking</h3>
                        <p class="text-gray-300 text-sm mb-2">
                            Deposita criptomonedas en protocolos DeFi para ganar rendimientos, a menudo superiores al 10% APY.
                        </p>
                        <span class="text-xs text-green-300">Riesgo: Smart contract vulnerabilities, impermanent loss</span>
                    </div>

                    <div class="bg-green-950/40 rounded-xl p-5 border border-green-500/20">
                        <h3 class="text-lg font-bold text-green-200 mb-2">🏦 Lending Protocols</h3>
                        <p class="text-gray-300 text-sm mb-2">
                            Aave, Compound y MakerDAO permiten prestar/tomar prestado activos sin KYC mediante colateralización.
                        </p>
                        <span class="text-xs text-green-300">Ratio típico: 150-200% de colateral</span>
                    </div>

                    <div class="bg-green-950/40 rounded-xl p-5 border border-green-500/20">
                        <h3 class="text-lg font-bold text-green-200 mb-2">🪙 Stablecoins</h3>
                        <p class="text-gray-300 text-sm mb-2">
                            Criptomonedas ancladas al dólar: USDT (centralized), USDC (audited), DAI (algorithmic).
                        </p>
                        <span class="text-xs text-green-300">Función: Reducir volatilidad en operaciones DeFi</span>
                    </div>

                </div>
            </div>

            <!-- NFTs y Smart Contracts -->
            <div class="bg-gradient-to-br from-pink-900/50 to-rose-900/50 rounded-3xl p-8 border border-pink-500/30 shadow-2xl">
                <div class="flex items-center gap-4 mb-6">
                    <div class="text-4xl bg-pink-500/20 w-16 h-16 flex items-center justify-center rounded-xl">🎨</div>
                    <h2 class="text-3xl font-bold text-white">NFTs y Smart Contracts</h2>
                </div>

                <div class="space-y-5">
                    
                    <div class="bg-pink-950/40 rounded-xl p-5 border border-pink-500/20">
                        <h3 class="text-lg font-bold text-pink-200 mb-2">📜 Smart Contracts</h3>
                        <p class="text-gray-300">
                            Programas auto-ejecutables en blockchain (principalmente Ethereum, Solidity). Condiciones "if-then" inmutables que eliminan intermediarios en transacciones complejas.
                        </p>
                    </div>

                    <div class="bg-pink-950/40 rounded-xl p-5 border border-pink-500/20">
                        <h3 class="text-lg font-bold text-pink-200 mb-2">🖼️ NFTs (Non-Fungible Tokens)</h3>
                        <p class="text-gray-300">
                            Tokens únicos e indivisibles que representan propiedad digital. Estándar ERC-721 y ERC-1155. Usos: arte digital, gaming, metaverso, certificados de autenticidad.
                        </p>
                    </div>

                    <div class="bg-pink-950/40 rounded-xl p-5 border border-pink-500/20">
                        <h3 class="text-lg font-bold text-pink-200 mb-2">⛽ Gas Fees</h3>
                        <p class="text-gray-300">
                            Costo computacional para ejecutar operaciones en blockchain. Varía según congestión de red. Layer 2 solutions (Polygon, Arbitrum) reducen costos.
                        </p>
                    </div>

                </div>
            </div>

            <!-- Análisis Técnico Cripto -->
            <div class="bg-gradient-to-br from-indigo-900/50 to-blue-900/50 rounded-3xl p-8 border border-indigo-500/30 shadow-2xl">
                <div class="flex items-center gap-4 mb-6">
                    <div class="text-4xl bg-indigo-500/20 w-16 h-16 flex items-center justify-center rounded-xl">📊</div>
                    <h2 class="text-3xl font-bold text-white">Métricas y Análisis</h2>
                </div>

                <div class="grid grid-cols-1 md:grid-cols-2 gap-5">
                    
                    <div class="bg-indigo-950/40 rounded-xl p-5 border border-indigo-500/20">
                        <h3 class="text-lg font-bold text-indigo-200 mb-2">💰 Market Cap vs FDV</h3>
                        <p class="text-gray-300 text-sm">
                            <span class="text-indigo-300 font-semibold">Market Cap:</span> Precio × Supply circulante<br>
                            <span class="text-indigo-300 font-semibold">FDV:</span> Precio × Total supply (incluye tokens bloqueados)
                        </p>
                    </div>

                    <div class="bg-indigo-950/40 rounded-xl p-5 border border-indigo-500/20">
                        <h3 class="text-lg font-bold text-indigo-200 mb-2">📈 TVL (Total Value Locked)</h3>
                        <p class="text-gray-300 text-sm">
                            Mide capital depositado en protocolos DeFi. Mayor TVL indica confianza del mercado y utilidad real del protocolo.
                        </p>
                    </div>

                    <div class="bg-indigo-950/40 rounded-xl p-5 border border-indigo-500/20">
                        <h3 class="text-lg font-bold text-indigo-200 mb-2">🔥 Tokenomics</h3>
                        <p class="text-gray-300 text-sm">
                            Analiza distribución de supply, vesting schedules, mecanismos de burn, y utilidad del token en el ecosistema.
                        </p>
                    </div>

                    <div class="bg-indigo-950/40 rounded-xl p-5 border border-indigo-500/20">
                        <h3 class="text-lg font-bold text-indigo-200 mb-2">👥 Dominancia de Bitcoin</h3>
                        <p class="text-gray-300 text-sm">
                            Porcentaje del market cap total cripto que representa BTC. Inversamente correlacionado con "altcoin season".
                        </p>
                    </div>

                </div>
            </div>

            <!-- Riesgos específicos -->
            <div class="bg-gradient-to-br from-orange-900/50 to-red-900/50 rounded-3xl p-8 border border-orange-500/30 shadow-2xl">
                <div class="flex items-center gap-4 mb-6">
                    <div class="text-4xl bg-orange-500/20 w-16 h-16 flex items-center justify-center rounded-xl">⚠️</div>
                    <h2 class="text-3xl font-bold text-white">Riesgos del Ecosistema Cripto</h2>
                </div>

                <div class="space-y-3">
                    <div class="flex gap-3 items-start bg-orange-950/30 rounded-xl p-4 border border-orange-500/20">
                        <span class="text-xl">🎢</span>
                        <div>
                            <h3 class="text-orange-200 font-bold mb-1">Volatilidad Extrema</h3>
                            <p class="text-gray-300 text-sm">Movimientos del 20-50% en días. Requiere alta tolerancia al riesgo y gestión de capital estricta.</p>
                        </div>
                    </div>
                    <div class="flex gap-3 items-start bg-orange-950/30 rounded-xl p-4 border border-orange-500/20">
                        <span class="text-xl">🐛</span>
                        <div>
                            <h3 class="text-orange-200 font-bold mb-1">Smart Contract Bugs</h3>
                            <p class="text-gray-300 text-sm">Auditorías no garantizan seguridad 100%. Protocolos han perdido millones por exploits.</p>
                        </div>
                    </div>
                    <div class="flex gap-3 items-start bg-orange-950/30 rounded-xl p-4 border border-orange-500/20">
                        <span class="text-xl">🎭</span>
                        <div>
                            <h3 class="text-orange-200 font-bold mb-1">Rug Pulls y Scams</h3>
                            <p class="text-gray-300 text-sm">Proyectos fraudulentos abundan. Verifica contratos, equipo doxxed, liquidez bloqueada antes de invertir.</p>
                        </div>
                    </div>
                    <div class="flex gap-3 items-start bg-orange-950/30 rounded-xl p-4 border border-orange-500/20">
                        <span class="text-xl">⚖️</span>
                        <div>
                            <h3 class="text-orange-200 font-bold mb-1">Regulación Incierta</h3>
                            <p class="text-gray-300 text-sm">Gobiernos pueden prohibir o regular fuertemente el espacio cripto sin previo aviso.</p>
                        </div>
                    </div>
                </div>
            </div>

            <!-- Estrategias avanzadas -->
            <div class="bg-gradient-to-br from-violet-900/50 to-purple-900/50 rounded-3xl p-8 border border-violet-500/30 shadow-2xl">
                <div class="flex items-center gap-4 mb-6">
                    <div class="text-4xl bg-violet-500/20 w-16 h-16 flex items-center justify-center rounded-xl">🎯</div>
                    <h2 class="text-3xl font-bold text-white">Estrategias Avanzadas</h2>
                </div>

                <div class="space-y-4">
                    <div class="bg-violet-950/40 rounded-xl p-5 border border-violet-500/20">
                        <h3 class="text-lg font-bold text-violet-200 mb-2">💱 Arbitraje entre Exchanges</h3>
                        <p class="text-gray-300">
                            Explotar diferencias de precio entre exchanges. Requiere capital, bots automatizados y gestión de fees/slippage.
                        </p>
                    </div>
                    <div class="bg-violet-950/40 rounded-xl p-5 border border-violet-500/20">
                        <h3 class="text-lg font-bold text-violet-200 mb-2">🌉 Cross-Chain Bridges</h3>
                        <p class="text-gray-300">
                            Transferir activos entre blockchains (Ethereum ↔ BSC ↔ Polygon). Importante: verifica seguridad del bridge.
                        </p>
                    </div>
                    <div class="bg-violet-950/40 rounded-xl p-5 border border-violet-500/20">
                        <h3 class="text-lg font-bold text-violet-200 mb-2">🔮 On-Chain Analysis</h3>
                        <p class="text-gray-300">
                            Usa Glassnode, Nansen o Dune Analytics para rastrear movimientos de whales, exchange flows y métricas de holders.
                        </p>
                    </div>
                </div>
            </div>

            <!-- Advertencia final -->
            <div class="bg-red-900/30 rounded-2xl p-6 border border-red-500/30">
                <div class="flex gap-4 items-start">
                    <div class="text-3xl">🚨</div>
                    <div>
                        <h3 class="text-xl font-bold text-red-300 mb-2">Advertencia Crítica</h3>
                        <p class="text-gray-300">
                            El mercado cripto es altamente especulativo y no regulado. Nunca inviertas más de lo que puedes perder. 
                            Este contenido es educativo y no constituye asesoría financiera. DYOR (Do Your Own Research) siempre. 
                            Custodia segura: usa hardware wallets y habilita 2FA en todos los exchanges.
                        </p>
                    </div>
                </div>
            </div>

        </div>
        """
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