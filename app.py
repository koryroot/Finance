# app.py
from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify
import firebase_admin
from firebase_admin import credentials, firestore
import pyrebase
from firebase_config import config
import os
from datetime import datetime
from collections import defaultdict
import locale
from functools import wraps

# --- INICIALIZACIÓN ---
cred = credentials.Certificate('firebase_credentials.json')
firebase_admin.initialize_app(cred)
db = firestore.client()

firebase = pyrebase.initialize_app(config)
auth = firebase.auth()

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'una_clave_por_defecto_solo_para_pruebas')

try:
    locale.setlocale(locale.LC_TIME, 'es_ES.UTF-8')
except locale.Error:
    locale.setlocale(locale.LC_TIME, 'Spanish')

@app.template_filter('number_format')
def number_format(value):
    try:
        return "{:,.2f}".format(float(value))
    except (ValueError, TypeError):
        return value

# --- DECORADORES DE RUTAS ---
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

def onboarding_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        user_id = session.get('user')
        if not user_id: return redirect(url_for('login'))
        user_ref = db.collection('users').document(user_id)
        user_doc = user_ref.get()
        if user_doc.exists and user_doc.to_dict().get('onboarding_complete', False):
            return f(*args, **kwargs)
        else:
            # Redirigir al paso de onboarding correspondiente
            income_check = user_ref.collection('income').limit(1).get()
            if not income_check:
                return redirect(url_for('onboarding_income'))
            # Si ya tiene ingresos, pero no ha completado, lo mandamos al siguiente paso
            return redirect(url_for('onboarding_budget'))
    return decorated_function

# --- FUNCIÓN AUXILIAR ---
def check_and_create_user_data(user_id, email):
    user_ref = db.collection('users').document(user_id)
    if not user_ref.get().exists:
        user_ref.set({'email': email, 'created_at': firestore.SERVER_TIMESTAMP, 'onboarding_complete': False})
        categories_ref = user_ref.collection('categories')
        categories_ref.add({'name': 'Necesidades', 'budget_percent': 50, 'color': '#3b82f6'})
        categories_ref.add({'name': 'Deseos', 'budget_percent': 30, 'color': '#8b5cf6'})
        categories_ref.add({'name': 'Ahorro e Inversión', 'budget_percent': 20, 'color': '#10b981'})
        user_ref.collection('savings').document('emergency_fund').set({'goal': 0, 'current': 0})
        return True # Es un usuario nuevo
    return False # Es un usuario existente

# --- RUTAS DE AUTENTICACIÓN Y PÚBLICAS ---
@app.route('/')
def landing():
    if 'user' in session:
        return redirect(url_for('dashboard'))
    return render_template('landing.html')

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        try:
            user = auth.create_user_with_email_and_password(email, password)
            check_and_create_user_data(user['localId'], email)
            session['user'] = user['localId']
            return redirect(url_for('onboarding_welcome'))
        except Exception as e:
            flash('Error al crear la cuenta.', 'danger')
    return render_template('signup.html', firebase_config=config)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if 'user' in session:
        return redirect(url_for('dashboard'))
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        try:
            user = auth.sign_in_with_email_and_password(email, password)
            session['user'] = user['localId']
            return redirect(url_for('dashboard'))
        except Exception as e:
            flash('Correo o contraseña incorrectos.', 'danger')
    return render_template('login.html', firebase_config=config)

@app.route('/google-signin', methods=['POST'])
def google_signin():
    try:
        token = request.json['idToken']
        user = auth.get_account_info(token)['users'][0]
        user_id = user['localId']
        user_email = user['email']
        is_new_user = not db.collection('users').document(user_id).get().exists
        check_and_create_user_data(user_id, user_email)
        session['user'] = user_id
        return jsonify({'status': 'success', 'new_user': is_new_user})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)})

@app.route('/logout')
def logout():
    session.pop('user', None)
    flash('Has cerrado sesión.', 'success')
    return redirect(url_for('landing'))

# --- RUTAS DE ONBOARDING ---
@app.route('/welcome')
@login_required
def onboarding_welcome():
    return render_template('onboarding_welcome.html')

@app.route('/onboarding/income', methods=['GET', 'POST'])
@login_required
def onboarding_income():
    user_id = session['user']
    if request.method == 'POST':
        source = request.form.get('source')
        amount = request.form.get('amount')
        date = datetime.now().strftime('%Y-%m-%d')
        db.collection('users').document(user_id).collection('income').add({
            'source': source, 'amount': float(amount), 'date': date
        })
        return redirect(url_for('onboarding_budget'))
    return render_template('onboarding_income.html')

@app.route('/onboarding/budget', methods=['GET', 'POST'])
@login_required
def onboarding_budget():
    user_id = session['user']
    if request.method == 'POST':
        return redirect(url_for('onboarding_savings'))
    
    categories_docs = db.collection('users').document(user_id).collection('categories').stream()
    categories = [doc.to_dict() for doc in categories_docs]
    return render_template('onboarding_budget.html', categories=categories)

@app.route('/onboarding/savings', methods=['GET', 'POST'])
@login_required
def onboarding_savings():
    user_id = session['user']
    if request.method == 'POST':
        goal = request.form.get('goal')
        db.collection('users').document(user_id).collection('savings').document('emergency_fund').update({
            'goal': float(goal)
        })
        db.collection('users').document(user_id).update({'onboarding_complete': True})
        flash('¡Configuración completada! Ya puedes empezar a usar tu billetera.', 'success')
        return redirect(url_for('dashboard'))
    
    income_docs = db.collection('users').document(user_id).collection('income').stream()
    total_income = sum(doc.to_dict().get('amount', 0) for doc in income_docs)
    suggested_goal = total_income * 3
    return render_template('onboarding_savings.html', suggested_goal=suggested_goal)

@app.route('/skip-savings')
@login_required
def skip_savings_goal():
    user_id = session['user']
    db.collection('users').document(user_id).update({'onboarding_complete': True})
    flash('Puedes configurar tu meta de ahorro más tarde. ¡Bienvenido/a!', 'success')
    return redirect(url_for('dashboard'))

# --- RUTAS PRINCIPALES (PROTEGIDAS) ---
@app.route('/dashboard')
@login_required
@onboarding_required
def dashboard():
    user_id = session['user']
    
    try:
        # Obtener datos del usuario desde Firestore
        income_docs = db.collection('users').document(user_id).collection('income').stream()
        expenses_docs = db.collection('users').document(user_id).collection('expenses').stream()
        categories_docs = db.collection('users').document(user_id).collection('categories').stream()

        all_income = [doc.to_dict() for doc in income_docs]
        all_expenses = [doc.to_dict() for doc in expenses_docs]
        all_categories = [{'id': doc.id, **doc.to_dict()} for doc in categories_docs]

        # Lógica de cálculo
        current_month = datetime.now().month
        current_year = datetime.now().year

        monthly_income = [inc for inc in all_income if inc and 'date' in inc and datetime.fromisoformat(inc['date']).month == current_month and datetime.fromisoformat(inc['date']).year == current_year]
        monthly_expenses = [exp for exp in all_expenses if exp and 'date' in exp and datetime.fromisoformat(exp['date']).month == current_month and datetime.fromisoformat(exp['date']).year == current_year]

        total_monthly_income = sum(inc.get('amount', 0) for inc in monthly_income)
        total_monthly_expenses = sum(exp.get('amount', 0) for exp in monthly_expenses)
        total_budgeted = total_monthly_income

        expenses_by_category = []
        for cat in all_categories:
            if not cat: continue
            budget_amount = total_monthly_income * (cat.get('budget_percent', 0) / 100)
            spent = sum(exp.get('amount', 0) for exp in monthly_expenses if exp.get('categoryId') == cat.get('id'))
            percentage = (spent / budget_amount * 100) if budget_amount > 0 else 0
            
            expenses_by_category.append({
                **cat, 'budget_amount': budget_amount, 'spent': spent, 
                'remaining': budget_amount - spent, 'percentage_capped': min(percentage, 100)
            })

        return render_template(
            'dashboard.html', month_name=datetime.now().strftime('%B').capitalize(),
            total_income=total_monthly_income, total_expenses=total_monthly_expenses,
            total_budgeted=total_budgeted,
            expenses_by_category=expenses_by_category, categories=all_categories,
            today_date=datetime.now().strftime('%Y-%m-%d')
        )
    except Exception as e:
        flash(f"Ocurrió un error al cargar tus datos: {e}", "danger")
        return render_template('dashboard.html', month_name=datetime.now().strftime('%B').capitalize())

@app.route('/add_transaction', methods=['POST'])
@login_required
def add_transaction_route():
    user_id = session['user']
    trans_type = request.form.get('type')
    description = request.form.get('description')
    amount = float(request.form.get('amount'))
    date = request.form.get('date')

    if trans_type == 'expense':
        category_id = request.form.get('category_id')
        db.collection('users').document(user_id).collection('expenses').add({
            'description': description, 'amount': amount, 'categoryId': category_id, 'date': date
        })
        flash('Gasto añadido con éxito.', 'success')
    elif trans_type == 'income':
        db.collection('users').document(user_id).collection('income').add({
            'source': description, 'amount': amount, 'date': date
        })
        flash('Ingreso añadido con éxito.', 'success')
    
    return redirect(url_for('dashboard'))

# --- Rutas Placeholder para el resto de la app ---
@app.route('/budget')
@login_required
@onboarding_required
def budget():
    # Lógica futura para la página de presupuesto
    return "Página de Presupuesto en construcción"

@app.route('/savings')
@login_required
@onboarding_required
def savings():
    # Lógica futura para la página de ahorros
    return "Página de Ahorros en construcción"
    
@app.route('/charts')
@login_required
@onboarding_required
def charts():
    # Lógica futura para la página de gráficos
    return "Página de Gráficos en construcción"

@app.route('/category/<category_id>')
@login_required
@onboarding_required
def category_detail(category_id):
    # Lógica futura para la página de detalle de categoría
    return f"Página de detalle para la categoría {category_id} en construcción"

if __name__ == '__main__':
    app.run(debug=True, port=5001)