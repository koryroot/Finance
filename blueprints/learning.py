# /blueprints/learning.py

from flask import Blueprint, render_template
from .auth import login_required


learning_bp = Blueprint('learning', __name__, template_folder='../templates')

@learning_bp.route('/')
@login_required
def index():
    # Aquí podrías cargar artículos desde Firebase en el futuro.
    # Por ahora, usamos datos estáticos para maquetar.
    modules = [
        {
            'title': 'Fundamentos de Inversión',
            'desc': '¿Qué es el interés compuesto y cómo funciona a tu favor?',
            'level': 'Básico',
            'icon': '🌱',
            'color': 'green'
        },
        {
            'title': 'Bolsa de Valores',
            'desc': 'Entendiendo acciones, ETFs y el mercado bursátil.',
            'level': 'Intermedio',
            'icon': '📈',
            'color': 'blue'
        },
        {
            'title': 'Criptomonedas',
            'desc': 'Blockchain, Bitcoin y la nueva economía digital.',
            'level': 'Avanzado',
            'icon': '₿',
            'color': 'purple'
        },
        {
            'title': 'Bienes Raíces',
            'desc': 'Inversión inmobiliaria: Pros, contras y Fideicomisos.',
            'level': 'Intermedio',
            'icon': '🏢',
            'color': 'yellow'
        }
    ]

    return render_template('learning/index.html', modules=modules)