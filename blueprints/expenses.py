# /blueprints/expenses.py

from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from datetime import datetime
from firebase_config import db
from .auth import login_required

expenses_bp = Blueprint('expenses', __name__, template_folder='../templates')

@expenses_bp.route('/history')
@login_required
def history():
    user_id = session['user']
    
    # 1. Obtener gastos
    expenses_ref = db.collection('users').document(user_id).collection('expenses')
    expenses_docs = expenses_ref.stream()
    
    # 2. Obtener categorías (Para mostrar nombres y colores)
    categories_ref = db.collection('users').document(user_id).collection('categories').stream()
    categories = {doc.id: doc.to_dict() for doc in categories_ref}

    expenses = []
    total_monthly_projection = 0

    for doc in expenses_docs:
        data = doc.to_dict()
        data['id'] = doc.id
        
        # Enriquecer con datos de categoría
        cat_id = data.get('categoryId')
        if cat_id and cat_id in categories:
            data['category_name'] = categories[cat_id].get('name')
            data['category_color'] = categories[cat_id].get('color')
        else:
            data['category_name'] = 'Sin Categoría'
            data['category_color'] = '#6b7280' # Gris por defecto

        # Calcular proyección mensual
        amount = float(data.get('amount', 0))
        freq = data.get('frequency', 'ocasional') # Por defecto es ocasional
        
        if freq == 'mensual':
            total_monthly_projection += amount
        elif freq == 'quincenal':
            total_monthly_projection += (amount * 26) / 12
        elif freq == 'anual':
            total_monthly_projection += amount / 12
        else:
            # Si es ocasional, solo cuenta para la proyección si es de este mes
            date_str = data.get('date')
            if date_str:
                try:
                    exp_date = datetime.strptime(date_str, '%Y-%m-%d')
                    now = datetime.now()
                    if exp_date.month == now.month and exp_date.year == now.year:
                        total_monthly_projection += amount
                except:
                    pass
        
        expenses.append(data)

    # Ordenar por fecha (más reciente primero)
    expenses.sort(key=lambda x: x.get('date', ''), reverse=True)

    # Necesitamos pasar las categorías al template para el formulario de "Agregar"
    # Convertimos el dict de categorías a una lista
    categories_list = [{'id': k, **v} for k, v in categories.items()]

    return render_template('expenses_history.html', 
                           expenses=expenses, 
                           total_projection=total_monthly_projection,
                           categories=categories_list,
                           today_date=datetime.now().strftime('%Y-%m-%d'))

@expenses_bp.route('/add', methods=['POST'])
@login_required
def add():
    user_id = session['user']
    
    description = request.form.get('description')
    amount = float(request.form.get('amount'))
    category_id = request.form.get('category_id')
    frequency = request.form.get('frequency') # mensual, ocasional, etc.
    date = request.form.get('date')

    try:
        data = {
            'description': description,
            'amount': amount,
            'categoryId': category_id,
            'frequency': frequency,
            'date': date,
            'created_at': datetime.now()
        }
        
        db.collection('users').document(user_id).collection('expenses').add(data)
        flash('Gasto registrado correctamente.', 'success')
        
    except Exception as e:
        flash(f'Error al guardar: {e}', 'danger')

    return redirect(url_for('expenses.history'))

@expenses_bp.route('/delete/<expense_id>', methods=['POST'])
@login_required
def delete(expense_id):
    user_id = session['user']
    try:
        db.collection('users').document(user_id).collection('expenses').document(expense_id).delete()
        flash('Gasto eliminado.', 'success')
    except Exception as e:
        flash(f'Error al eliminar: {e}', 'danger')
        
    return redirect(url_for('expenses.history'))