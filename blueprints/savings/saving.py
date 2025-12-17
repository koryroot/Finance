
from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from datetime import datetime
from firebase_config import db
from .auth import login_required

savings_bp = Blueprint('savings', __name__, template_folder='../templates')

@savings_bp.route('/history')
@login_required
def history():
    user_id = session['user']
    
    # Obtenemos todos los ahorros registrados
    savings_ref = db.collection('users').document(user_id).collection('savings')
    docs = savings_ref.stream()
    
    savings = []
    total_savings = 0

    for doc in docs:
        data = doc.to_dict()
        data['id'] = doc.id
        amount = data.get('saved_amount', 0)
        total_savings += amount
        savings.append(data)

    return render_template('savings_history.html', savings=savings, total_savings=total_savings)

@savings_bp.route('/add', methods=['GET','POST'])
@login_required
def add():
    if request.method == 'GET':
        return render_template('add_saving.html')
    user_id = session['user']    
    goal_name = request.form.get('goal_name')
    goal_amount = float(request.form.get('goal_amount'))
    have__Money_commitment = bool(request.form.get('have__Money_commitment'))
    target_date = request.form.get('target_date', datetime.now().strftime('%Y-%m-%d'))
    try:
        data = {
            'goal_name': goal_name,
            'goal_amount': goal_amount,
            "saved_amount": 0,
            "achieved" : False,
            'target_date': target_date,
            'monthly_commitment': calculate_monthly_commitment(goal_amount, target_date) if have__Money_commitment else 0,
            'created_at': datetime.now()
        }
        db.collection('users').document(user_id).collection('savings').add(data)
        flash('Ahorro agregado exitosamente.', 'success')
    except Exception as e:
        flash(f'Error al agregar el ahorro: {e}', 'danger')

    return redirect(url_for('savings.history'))

@savings_bp.route('/pay/<saving_id>', methods=['GET', 'POST'])
@login_required
def pay(saving_id):
    user_id = session['user']

    if request.method == 'GET':
        return render_template('pay_saving.html', saving_id=saving_id)

    payment_amount = float(request.form.get('payment_amount'))

    saving_ref = db.collection('users').document(user_id).collection('savings').document(saving_id)
    saving_doc = saving_ref.get()

    if not saving_doc.exists:
        flash('Ahorro no encontrado.', 'danger')
        return redirect(url_for('savings.history'))

    saving_data = saving_doc.to_dict()
    new_saved_amount = saving_data.get('saved_amount', 0) + payment_amount
    achieved = new_saved_amount >= saving_data.get('goal_amount', 0)

    try:
        saving_ref.update({
            'saved_amount': new_saved_amount,
            'achieved': achieved
        })
        flash('Pago registrado exitosamente.', 'success')
    except Exception as e:
        flash(f'Error al registrar el pago: {e}', 'danger')

    return redirect(url_for('savings.history'))


def calculate_monthly_commitment(goal_amount, target_date):
    now = datetime.now()
    target = datetime.strptime(target_date, '%Y-%m-%d')
    months_diff = (target.year - now.year) * 12 + (target.month - now.month)
    if months_diff <= 0:
        return goal_amount  # Si la fecha objetivo ya pasó o es este mes, se debe ahorrar todo de inmediato
    return goal_amount / months_diff