# /blueprints/auth.py

from flask import Blueprint, render_template, request, redirect, url_for, flash, session, jsonify
from functools import wraps
from firebase_config import db, firebase_auth # Importamos desde nuestro config central
from firebase_admin import firestore

# Creamos el Blueprint para las rutas de autenticación.
auth_bp = Blueprint('auth', __name__, template_folder='../templates')


# --- DECORADOR DE RUTAS ---
def login_required(f):
    """
    Decorador que verifica si un usuario ha iniciado sesión.
    Si no, lo redirige a la página de login.
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user' not in session:
            flash("Debes iniciar sesión para ver esta página.", "warning")
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated_function


# --- FUNCIÓN AUXILIAR ---
def check_and_create_user_data(user_id, email):
    """
    Verifica si un usuario ya existe en Firestore. Si no, crea su documento
    inicial con categorías y metas de ahorro por defecto.
    """
    user_ref = db.collection('users').document(user_id)
    if not user_ref.get().exists:
        user_ref.set({
            'email': email, 
            'created_at': firestore.SERVER_TIMESTAMP, 
            'onboarding_complete': False
        })
        # Añadir datos iniciales para un nuevo usuario
        categories_ref = user_ref.collection('categories')
        categories_ref.add({'name': 'Necesidades', 'budget_percent': 50, 'color': '#3b82f6'})
        categories_ref.add({'name': 'Deseos', 'budget_percent': 30, 'color': '#8b5cf6'})
        categories_ref.add({'name': 'Ahorro e Inversión', 'budget_percent': 20, 'color': '#10b981'})
        user_ref.collection('savings').document('emergency_fund').set({'goal': 0, 'current': 0})
        return True # Es un nuevo usuario
    return False # Es un usuario existente


# --- RUTAS DE AUTENTICACIÓN ---

@auth_bp.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        try:
            # Usamos el Admin SDK para crear el usuario. Es más seguro.
            user = firebase_auth.create_user(email=email, password=password)
            # Creamos su documento en Firestore
            check_and_create_user_data(user.uid, email)
            flash('¡Cuenta creada exitosamente! Por favor, inicia sesión.', 'success')
            return redirect(url_for('auth.login'))
        except Exception as e:
            flash(f'Error al crear la cuenta: {e}', 'danger')
    return render_template('signup.html')


@auth_bp.route('/login', methods=['GET'])
def login():
    if 'user' in session:
        return redirect(url_for('main.dashboard'))
    # El formulario de login ahora será manejado por JavaScript para mayor seguridad.
    return render_template('login.html')


@auth_bp.route('/session-login', methods=['POST'])
def session_login():
    """
    Esta ruta recibe un ID Token del cliente (JavaScript), lo verifica
    y crea la sesión del servidor. Este es el flujo de trabajo seguro.
    """
    try:
        id_token = request.json['idToken']
        # Verificamos el token con el Admin SDK. Esto es muy seguro.
        decoded_token = firebase_auth.verify_id_token(id_token)
        user_id = decoded_token['uid']
        
        # Guardamos el ID del usuario en la sesión de Flask.
        session['user'] = user_id
        session.permanent = True # Para que la sesión dure más tiempo

        # Verificamos si es un usuario nuevo (por si inició con Google y no tenía doc)
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
