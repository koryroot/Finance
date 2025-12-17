# /blueprints/main.py

from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from functools import wraps
from datetime import datetime
from firebase_config import db # Importamos solo la base de datos
from .auth import login_required # Importamos el decorador desde nuestro blueprint de auth

# Creamos el Blueprint para las rutas principales de la aplicación.
main_bp = Blueprint('main', __name__, template_folder='../templates')


# --- DECORADOR DE RUTAS ---
def onboarding_required(f):
    """
    Decorador que verifica si el usuario ha completado el proceso de onboarding.
    Si no, lo redirige al paso correspondiente.
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        user_id = session.get('user')
        if not user_id: return redirect(url_for('auth.login'))
        
        user_ref = db.collection('users').document(user_id)
        user_doc = user_ref.get()
        
        if user_doc.exists and user_doc.to_dict().get('onboarding_complete', False):
            return f(*args, **kwargs)
        else:
            # Lógica para redirigir al paso correcto del onboarding
            income_check = user_ref.collection('income').limit(1).get()
            if not income_check:
                return redirect(url_for('main.onboarding_income'))
            return redirect(url_for('main.onboarding_budget'))
    return decorated_function


# --- RUTAS DE ONBOARDING ---
@main_bp.route('/welcome')
@login_required
def onboarding_welcome():
    return render_template('onboarding_welcome.html')


@main_bp.route('/onboarding/income', methods=['GET', 'POST'])
@login_required
def onboarding_income():
    user_id = session['user']
    if request.method == 'POST':
        try:
            # --- INICIO DE LA NUEVA LÓGICA DE PROCESAMIENTO ---
            incomes_data = {}
            for key, value in request.form.items():
                # Agrupamos los datos por su índice (ej. 'source-0', 'amount-0' -> índice 0)
                if '-' in key:
                    field, index = key.rsplit('-', 1)
                    if index.isdigit():
                        index = int(index)
                        if index not in incomes_data:
                            incomes_data[index] = {}
                        incomes_data[index][field] = value

            incomes_to_save = []
            # Validamos cada grupo de ingresos recolectado
            for index in sorted(incomes_data.keys()):
                data = incomes_data[index]
                source = data.get('source')
                amount_str = data.get('amount')
                frequency = data.get('frequency')

                if not (source and amount_str and frequency):
                    continue # Ignorar entradas incompletas

                try:
                    amount = float(amount_str)
                except (ValueError, TypeError):
                    flash(f"El monto '{amount_str}' no es un número válido.", "danger")
                    return redirect(url_for('main.onboarding_income'))

                if amount < 0:
                    flash("Los montos de ingreso no pueden ser negativos.", "danger")
                    return redirect(url_for('main.onboarding_income'))

                incomes_to_save.append({
                    'source': source,
                    'amount': amount,
                    'frequency': frequency,
                    'date': datetime.now().strftime('%Y-%m-%d')
                })

            if not incomes_to_save:
                flash("Debes añadir al menos una fuente de ingreso válida.", "danger")
                return redirect(url_for('main.onboarding_income'))
            
            # --- FIN DE LA NUEVA LÓGICA ---

            # Procedemos a guardar en la base de datos
            income_ref = db.collection('users').document(user_id).collection('income')
            
            for doc in income_ref.stream():
                doc.reference.delete()
            
            for income_data in incomes_to_save:
                income_ref.add(income_data)
            
            return redirect(url_for('main.onboarding_budget'))

        except Exception as e:
            flash(f"Ocurrió un error al guardar tus ingresos: {e}", "danger")
            return redirect(url_for('main.onboarding_income'))

    # Lógica para cargar la página (petición GET)
    try:
        user_doc = db.collection('users').document(user_id).get()
        user_data = user_doc.to_dict() if user_doc.exists else {}
        incomes_stream = db.collection('users').document(user_id).collection('income').stream()
        existing_incomes = [doc.to_dict() for doc in incomes_stream]
        return render_template('onboarding_income.html', user=user_data, incomes=existing_incomes)
    except Exception as e:
        flash(f"Error al cargar la página: {e}", "danger")
        return redirect(url_for('main.onboarding_currency'))


@main_bp.route('/onboarding/budget', methods=['GET', 'POST'])
@login_required
def onboarding_budget():
    user_id = session['user']
    if request.method == 'POST':
        return redirect(url_for('main.onboarding_savings'))
    
    categories_docs = db.collection('users').document(user_id).collection('categories').stream()
    categories = [doc.to_dict() for doc in categories_docs]
    return render_template('onboarding_budget.html', categories=categories)

@main_bp.route('/onboarding/savings', methods=['GET', 'POST'])
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
        return redirect(url_for('main.dashboard'))
    
    income_docs = db.collection('users').document(user_id).collection('income').stream()
    total_income = sum(doc.to_dict().get('amount', 0) for doc in income_docs)
    suggested_goal = total_income * 3
    return render_template('onboarding_savings.html', suggested_goal=suggested_goal)

@main_bp.route('/skip-savings')
@login_required
def skip_savings_goal():
    user_id = session['user']
    db.collection('users').document(user_id).update({'onboarding_complete': True})
    flash('Puedes configurar tu meta de ahorro más tarde. ¡Bienvenido/a!', 'success')
    return redirect(url_for('main.dashboard'))

@main_bp.route('/onboarding/currency', methods=['GET', 'POST'])
@login_required
def onboarding_currency():
    user_id = session['user']
    if request.method == 'POST':
        currency = request.form.get('currency')
        if currency:
            db.collection('users').document(user_id).update({'currency': currency})
            # Una vez guardada la moneda, lo enviamos al siguiente paso que era el de ingresos.
            return redirect(url_for('main.onboarding_income'))
        else:
            flash("Por favor, selecciona una moneda.", "danger")

    return render_template('onboarding_currency.html')

# --- RUTAS PRINCIPALES (PROTEGIDAS) ---
#dashboard

@main_bp.route('/dashboard')
@login_required
@onboarding_required
def dashboard():
    user_id = session['user']
    try:
        # 1. DATOS DE USUARIO Y FECHA
        user_doc = db.collection('users').document(user_id).get()
        user_data = user_doc.to_dict() if user_doc.exists else {}
        
        now = datetime.now()
        current_month = now.month
        current_year = now.year

        # 2. OBTENER COLECCIONES
        income_docs = db.collection('users').document(user_id).collection('income').stream()
        expenses_docs = db.collection('users').document(user_id).collection('expenses').stream()
        categories_docs = db.collection('users').document(user_id).collection('categories').stream()

        all_income = [doc.to_dict() for doc in income_docs]
        all_expenses = [doc.to_dict() for doc in expenses_docs]
        all_categories = [{'id': doc.id, **doc.to_dict()} for doc in categories_docs]

        # 3. CALCULAR INGRESOS (Híbrido: Fijos + Variables del mes)
        total_monthly_income = 0
        for inc in all_income:
            freq = inc.get('frequency', 'ocasional')
            amount = float(inc.get('amount', 0))
            
            if freq == 'mensual':
                total_monthly_income += amount
            elif freq == 'quincenal':
                total_monthly_income += (amount * 26) / 12
            elif freq == 'anual':
                total_monthly_income += amount / 12
            else: # Ocasional
                inc_date_str = inc.get('date')
                if inc_date_str:
                    try:
                        inc_date = datetime.strptime(inc_date_str, '%Y-%m-%d')
                        if inc_date.month == current_month and inc_date.year == current_year:
                            total_monthly_income += amount
                    except ValueError: pass

        # 4. CALCULAR GASTOS (Híbrido) Y PREPARAR LISTA PARA CATEGORÍAS
        total_monthly_expenses = 0
        monthly_expenses_active = [] # Lista con el monto mensualizado para cálculos de categoría

        for exp in all_expenses:
            freq = exp.get('frequency', 'ocasional')
            amount = float(exp.get('amount', 0))
            is_active_this_month = False
            effective_amount = 0 # Cuánto impacta este gasto al mes (ej. quincenal se ajusta)

            # Lógica de Proyección
            if freq == 'mensual':
                effective_amount = amount
                is_active_this_month = True
            elif freq == 'quincenal':
                effective_amount = (amount * 26) / 12
                is_active_this_month = True
            elif freq == 'anual':
                effective_amount = amount / 12
                is_active_this_month = True
            else: # Ocasional
                exp_date_str = exp.get('date')
                if exp_date_str:
                    try:
                        exp_date = datetime.strptime(exp_date_str, '%Y-%m-%d')
                        if exp_date.month == current_month and exp_date.year == current_year:
                            effective_amount = amount
                            is_active_this_month = True
                    except ValueError: pass
            
            # Si el gasto cuenta este mes, sumamos al total global y lo guardamos para categorías
            if is_active_this_month:
                total_monthly_expenses += effective_amount
                # Guardamos una copia con el monto "efectivo" para que la suma por categoría cuadre
                active_expense = exp.copy()
                active_expense['effective_amount'] = effective_amount
                monthly_expenses_active.append(active_expense)

        # 5. PROCESAR CATEGORÍAS
        # Usamos 'total_monthly_income' para definir el tope de gasto (Presupuesto)
        total_budgeted = total_monthly_income 
        
        expenses_by_category = []
        for cat in all_categories:
            if not cat: continue
            
            # Presupuesto de esta categoría = % del Ingreso Total Real
            budget_amount = total_monthly_income * (cat.get('budget_percent', 0) / 100)
            
            # Lo gastado en esta categoría (Usando los montos mensualizados calculados arriba)
            spent = sum(x['effective_amount'] for x in monthly_expenses_active if x.get('categoryId') == cat.get('id'))
            
            percentage = (spent / budget_amount * 100) if budget_amount > 0 else 0
            
            expenses_by_category.append({
                **cat, 
                'budget_amount': budget_amount, 
                'spent': spent, 
                'remaining': budget_amount - spent, 
                'percentage_capped': min(percentage, 100)
            })

        return render_template(
            'dashboard.html', 
            user=user_data,
            month_name=now.strftime('%B').capitalize(),
            total_income=total_monthly_income, 
            total_expenses=total_monthly_expenses,
            total_budgeted=total_budgeted,
            expenses_by_category=expenses_by_category, 
            categories=all_categories,
            today_date=now.strftime('%Y-%m-%d')
        )
    except Exception as e:
        print(f"Error en dashboard: {e}") # Ayuda a depurar en consola
        flash(f"Ocurrió un error al cargar tus datos: {e}", "danger")
        return render_template('dashboard.html', month_name=datetime.now().strftime('%B').capitalize())

#dashboard final

@main_bp.route('/add_transaction', methods=['POST'])
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
    
    return redirect(url_for('main.dashboard'))

@main_bp.route('/budget', methods=['GET', 'POST'])
@login_required
@onboarding_required
def budget():
    user_id = session['user']
    user_ref = db.collection('users').document(user_id)
    
    if request.method == 'POST':
        for doc in user_ref.collection('categories').stream():
            cat_id = doc.id
            percent_val = request.form.get(f'percent_{cat_id}')
            if percent_val:
                doc.reference.update({'budget_percent': int(percent_val)})
        flash('Presupuesto actualizado.', 'success')
        return redirect(url_for('main.budget'))

    income_docs = user_ref.collection('income').stream()
    all_income = [{'id': doc.id, **doc.to_dict()} for doc in income_docs]
    
    categories_docs = user_ref.collection('categories').stream()
    all_categories = [{'id': doc.id, **doc.to_dict()} for doc in categories_docs]

    return render_template('budget.html', incomes=all_income, categories=all_categories, today_date=datetime.now().strftime('%Y-%m-%d'))

@main_bp.route('/delete_income/<income_id>', methods=['POST'])
@login_required
def delete_income_route(income_id):
    user_id = session['user']
    db.collection('users').document(user_id).collection('income').document(income_id).delete()
    flash('Ingreso eliminado.', 'success')
    return redirect(url_for('main.budget'))

@main_bp.route('/savings')
@login_required
@onboarding_required
def savings():
    user_id = session['user']
    emergency_fund_doc = db.collection('users').document(user_id).collection('savings').document('emergency_fund').get()
    emergency_fund = emergency_fund_doc.to_dict() if emergency_fund_doc.exists else {'goal': 0, 'current': 0}
    savings_goals_docs = db.collection('users').document(user_id).collection('savings_goals').stream()
    savings_goals = [{'id': doc.id, **doc.to_dict()} for doc in savings_goals_docs]
    return render_template('savings.html', emergency_fund=emergency_fund, savings_goals=savings_goals)
    
@main_bp.route('/charts')
@login_required
@onboarding_required
def charts():
    return render_template('charts.html')

@main_bp.route('/category/<category_id>')
@login_required
@onboarding_required
def category_detail(category_id):
    user_id = session['user']
    category_doc = db.collection('users').document(user_id).collection('categories').document(category_id).get()
    if not category_doc.exists:
        return "Categoría no encontrada", 404
    
    category = {'id': category_doc.id, **category_doc.to_dict()}
    
    expenses_docs = db.collection('users').document(user_id).collection('expenses').where('categoryId', '==', category_id).stream()
    expenses = sorted([doc.to_dict() for doc in expenses_docs], key=lambda x: x['date'], reverse=True)
    
    return render_template('category_detail.html', category=category, expenses=expenses)
