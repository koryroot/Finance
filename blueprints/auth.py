# /blueprints/auth.py

from flask import Blueprint, render_template, request, redirect, url_for, flash, session, jsonify
from functools import wraps
from firebase_config import db, firebase_auth
from firebase_admin import firestore

auth_bp = Blueprint('auth', __name__, template_folder='../templates')

# --- DECORADOR DE RUTAS (sin cambios) ---
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user' not in session:
            flash("Debes iniciar sesión para ver esta página.", "warning")
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated_function

# --- FUNCIÓN AUXILIAR (con cambios) ---
def check_and_create_user_data(user_id, email):
    user_ref = db.collection('users').document(user_id)
    if not user_ref.get().exists:
        # CAMBIO 1: Añadimos el campo 'currency' al crear el usuario.
        user_ref.set({
            'email': email, 
            'created_at': firestore.SERVER_TIMESTAMP, 
            'onboarding_complete': False,
            'currency': 'USD' # Usamos USD como un valor por defecto seguro.
        })
        categories_ref = user_ref.collection('categories')
        categories_ref.add({'name': 'Necesidades', 'budget_percent': 50, 'color': '#3b82f6'})
        categories_ref.add({'name': 'Deseos', 'budget_percent': 30, 'color': '#8b5cf6'})
        categories_ref.add({'name': 'Ahorro e Inversión', 'budget_percent': 20, 'color': '#10b981'})
        user_ref.collection('savings').document('emergency_fund').set({'goal': 0, 'current': 0})
        return True
    return False

# --- RUTAS DE AUTENTICACIÓN (con cambios) ---

@auth_bp.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        try:
            user = firebase_auth.create_user(email=email, password=password)
            check_and_create_user_data(user.uid, email)
            
            session['user'] = user.uid
            session.permanent = True
            
            # CORRECCIÓN: Redirigimos a la página de bienvenida para que se vea el efecto.
            return redirect(url_for('main.onboarding_welcome'))

        except Exception as e:
            error_message = f'Error al crear la cuenta: {e}'
            if 'EMAIL_EXISTS' in str(e):
                error_message = 'El correo electrónico ya está en uso. Por favor, intenta con otro.'
            flash(error_message, 'danger')
            
    return render_template('signup.html')

# El resto de las rutas (login, session_login, logout) no necesitan cambios.
@auth_bp.route('/login', methods=['GET'])
def login():
    if 'user' in session:
        return redirect(url_for('main.dashboard'))
    return render_template('login.html')

@auth_bp.route('/session-login', methods=['POST'])
def session_login():
    try:
        id_token = request.json['idToken']
        decoded_token = firebase_auth.verify_id_token(id_token)
        user_id = decoded_token['uid']
        
        session['user'] = user_id
        session.permanent = True

        is_new_user = check_and_create_user_data(user_id, decoded_token.get('email'))
        
        return jsonify({'status': 'success', 'new_user': is_new_user})
    except Exception as e:
        return jsonify({'status': 'error', 'message': f'Error de autenticación: {e}'}), 401

@auth_bp.route('/logout')
@login_required
def logout():
    session.pop('user', None)
    flash('Has cerrado sesión.', 'success')
    return redirect(url_for('index'))
