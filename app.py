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
            income_check = user_ref.collection('income').limit(1).get()
            if not income_check:
                return redirect(url_for('onboarding_income'))
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

# --- INICIO DE LA CORRECCIÓN ---
@app.route('/skip-savings')
@login_required
def skip_savings_goal():
    user_id = session['user']
    db.collection('users').document(user_id).update({'onboarding_complete': True})
    flash('Puedes configurar tu meta de ahorro más tarde. ¡Bienvenido/a!', 'success')
    return redirect(url_for('dashboard'))
# --- FIN DE LA CORRECCIÓN ---

# --- RUTAS PRINCIPALES (PROTEGIDAS) ---
@app.route('/dashboard')
@login_required
@onboarding_required
def dashboard():
    user_id = session['user']
    
    try:
        # ... (lógica del dashboard sin cambios) ...
        return render_template('dashboard.html')
    except Exception as e:
        flash(f"Ocurrió un error al cargar tus datos: {e}", "danger")
        return render_template('dashboard.html')

# --- El resto de tus rutas (savings, charts, etc.) irán aquí ---

if __name__ == '__main__':
    app.run(debug=True, port=5001)
