# /blueprints/income.py

from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from datetime import datetime
from firebase_config import db
from .auth import login_required # Reutilizamos tu decorador de seguridad

income_bp = Blueprint('income', __name__, template_folder='../templates')

@income_bp.route('/history')
@login_required
def history():
    user_id = session['user']
    
    # Obtenemos todos los ingresos registrados
    income_ref = db.collection('users').document(user_id).collection('income')
    docs = income_ref.stream()
    
    incomes = []
    total_monthly_projection = 0

    for doc in docs:
        data = doc.to_dict()
        data['id'] = doc.id
        
        # Calculamos cuánto aporta esto al mes (solo visualmente para esta tabla)
        amount = data.get('amount', 0)
        freq = data.get('frequency', 'mensual')
        
        if freq == 'quincenal':
            monthly_val = (amount * 26) / 12
        elif freq == 'anual':
            monthly_val = amount / 12
        else: # mensual u ocasional
            monthly_val = amount

        # Marcamos si es un ingreso fijo (recurrente) vs ocasional
        # Asumimos que si tiene frecuencia definida es "fijo"
        data['monthly_val'] = monthly_val
        incomes.append(data)
        total_monthly_projection += monthly_val

    return render_template('income_history.html', incomes=incomes, total_projection=total_monthly_projection)

@income_bp.route('/add', methods=['POST'])
@login_required
def add():
    user_id = session['user']
    
    source = request.form.get('source')
    amount = float(request.form.get('amount'))
    frequency = request.form.get('frequency') # mensual, quincenal, ocasional
    date = request.form.get('date', datetime.now().strftime('%Y-%m-%d'))

    try:
        data = {
            'source': source,
            'amount': amount,
            'frequency': frequency,
            'date': date,
            'created_at': datetime.now()
        }
        
        db.collection('users').document(user_id).collection('income').add(data)
        flash('Ingreso agregado correctamente.', 'success')
        
    except Exception as e:
        flash(f'Error al guardar: {e}', 'danger')

    # Nos mantenemos en la página de historial
    return redirect(url_for('income.history'))

@income_bp.route('/delete/<income_id>', methods=['POST'])
@login_required
def delete(income_id):
    user_id = session['user']
    try:
        db.collection('users').document(user_id).collection('income').document(income_id).delete()
        flash('Ingreso eliminado.', 'success')
    except Exception as e:
        flash(f'Error al eliminar: {e}', 'danger')
        
    return redirect(url_for('income.history'))