# app.py
from flask import Flask, render_template, request, redirect, url_for, flash, session
import firebase_admin
from firebase_admin import credentials, firestore
import pyrebase
from firebase_config import config
import os
from datetime import datetime
from collections import defaultdict
import locale

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

# --- FUNCIÓN AUXILIAR ---
def check_and_create_user_data(user_id, email):
    """Verifica si un usuario tiene datos iniciales y los crea si no existen."""
    user_ref = db.collection('users').document(user_id)
    
    if not user_ref.get().exists:
        # El usuario es nuevo, crear documento y datos iniciales
        user_ref.set({'email': email, 'created_at': firestore.SERVER_TIMESTAMP})
        
        categories_ref = user_ref.collection('categories')
        categories_ref.add({'name': 'Diezmo', 'budget_percent': 10, 'color': '#f97316'})
        categories_ref.add({'name': 'Gastos Fijos', 'budget_percent': 40, 'color': '#3b82f6'})
        categories_ref.add({'name': 'Gastos Personales', 'budget_percent': 30, 'color': '#8b5cf6'})
        categories_ref.add({'name': 'Ahorro e Inversión', 'budget_percent': 20, 'color': '#10b981'})
        
        user_ref.collection('savings').document('emergency_fund').set({'goal': 50000, 'current': 0})
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
            flash('¡Cuenta creada con éxito! Por favor, inicia sesión.', 'success')
            return redirect(url_for('login'))
        except Exception as e:
            flash('Error al crear la cuenta. El correo ya podría estar en uso.', 'danger')
    return render_template('signup.html')

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
            # Verificar si es la primera vez que inicia sesión (por si acaso)
            user_info = auth.get_account_info(user['idToken'])
            user_email = user_info['users'][0]['email']
            check_and_create_user_data(user['localId'], user_email)
            return redirect(url_for('dashboard'))
        except Exception as e:
            flash('Correo o contraseña incorrectos.', 'danger')
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('user', None)
    flash('Has cerrado sesión.', 'success')
    return redirect(url_for('landing'))

# --- RUTAS PRINCIPALES (PROTEGIDAS) ---
@app.route('/dashboard')
def dashboard():
    if 'user' not in session:
        return redirect(url_for('login'))
    
    user_id = session['user']
    
    try:
        # Obtener datos del usuario desde Firestore
        income_docs = db.collection('users').document(user_id).collection('income').stream()
        expenses_docs = db.collection('users').document(user_id).collection('expenses').stream()
        categories_docs = db.collection('users').document(user_id).collection('categories').stream()

        all_income = [doc.to_dict() for doc in income_docs]
        all_expenses = [doc.to_dict() for doc in expenses_docs]
        all_categories = [doc.to_dict() for doc in categories_docs]

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

# --- El resto de tus rutas irán aquí ---

if __name__ == '__main__':
    app.run(debug=True, port=5001)
