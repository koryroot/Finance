# /blueprints/budget.py

from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from datetime import datetime
from firebase_config import db
from .auth import login_required

budget_bp = Blueprint('budget', __name__, template_folder='../templates')

@budget_bp.route('/planner', methods=['GET', 'POST'])
@login_required
def planner():
    user_id = session['user']
    now = datetime.now()
    month_key = now.strftime('%Y-%m')
    user_ref = db.collection('users').document(user_id)
    
    # --- LÓGICA POST: GUARDAR EL PRESUPUESTO DETALLADO ---
    if request.method == 'POST':
        try:
            budget_data = {}
            total_budgeted_global = 0
            
            cats_docs = user_ref.collection('categories').stream()
            cat_ids = [doc.id for doc in cats_docs]

            for cat_id in cat_ids:
                descriptions = request.form.getlist(f'desc_{cat_id}[]')
                amounts = request.form.getlist(f'amount_{cat_id}[]')
                
                items = []
                cat_total = 0
                
                for desc, amt in zip(descriptions, amounts):
                    if desc.strip() and amt.strip(): 
                        try:
                            val = float(amt)
                            items.append({'name': desc, 'amount': val})
                            cat_total += val
                        except ValueError: continue
                
                budget_data[cat_id] = {'items': items, 'total': cat_total}
                total_budgeted_global += cat_total
            
            user_ref.collection('monthly_budgets').document(month_key).set({
                'detailed_budget': budget_data,
                'total_global': total_budgeted_global,
                'updated_at': datetime.now()
            })
            
            flash('¡Planificación guardada!', 'success')
            return redirect(url_for('budget.planner'))
            
        except Exception as e:
            flash(f'Error al guardar: {e}', 'danger')

    # --- LÓGICA GET: MOSTRAR ---
    
    # 1. Ingresos
    income_docs = user_ref.collection('income').stream()
    total_income = 0
    for doc in income_docs:
        d = doc.to_dict()
        freq = d.get('frequency', 'ocasional')
        amt = float(d.get('amount', 0))
        if freq == 'mensual': total_income += amt
        elif freq == 'quincenal': total_income += (amt * 26) / 12
        elif freq == 'anual': total_income += amt / 12

    # 2. Gastos Reales
    expenses_ref = user_ref.collection('expenses')
    expenses_docs = expenses_ref.stream()
    actual_spent_by_cat = {}
    
    for doc in expenses_docs:
        d = doc.to_dict()
        date_str = d.get('date')
        if date_str:
            try:
                e_date = datetime.strptime(date_str, '%Y-%m-%d')
                if e_date.year == now.year and e_date.month == now.month:
                    c_id = d.get('categoryId')
                    amt = float(d.get('amount', 0))
                    
                    freq = d.get('frequency', 'ocasional')
                    val_to_sum = amt
                    if freq == 'quincenal': val_to_sum = (amt * 26) / 12
                    elif freq == 'anual': val_to_sum = amt / 12
                    
                    actual_spent_by_cat[c_id] = actual_spent_by_cat.get(c_id, 0) + val_to_sum
            except: pass

    # 3. Datos Guardados y Categorías
    cats_docs = user_ref.collection('categories').stream()
    budget_doc = user_ref.collection('monthly_budgets').document(month_key).get()
    saved_budget_data = budget_doc.to_dict().get('detailed_budget', {}) if budget_doc.exists else {}

    categories_data = []
    for doc in cats_docs:
        c = doc.to_dict()
        c_id = doc.id
        
        cat_plan = saved_budget_data.get(c_id, {})
        saved_items = cat_plan.get('items', [])
        planned_total = cat_plan.get('total', 0)
        spent_real = actual_spent_by_cat.get(c_id, 0)
        
        # AQUÍ ESTÁ LA CLAVE: Usamos el porcentaje que el usuario definió
        user_percent = c.get('budget_percent', 0)
        rule_limit = total_income * (user_percent / 100)

        categories_data.append({
            'id': c_id,
            'name': c.get('name'),
            'color': c.get('color'),
            'percent': user_percent, # Pasamos el % real del usuario
            'rule_limit': rule_limit,
            'planned_total': planned_total,
            'spent_real': spent_real,
            'saved_items': saved_items
        })

    return render_template('budget_planner.html', 
                           categories=categories_data, 
                           total_income=total_income,
                           month_name=now.strftime('%B').capitalize())

# --- NUEVA RUTA: ACTUALIZAR REGLAS (PORCENTAJES) ---
@budget_bp.route('/update_rules', methods=['POST'])
@login_required
def update_rules():
    user_id = session['user']
    try:
        total_percent = 0
        batch = db.batch() # Usamos batch para guardar todo junto
        user_ref = db.collection('users').document(user_id)
        
        # Recorremos el formulario
        for key, value in request.form.items():
            if key.startswith('rule_percent_'):
                cat_id = key.split('rule_percent_')[1]
                new_percent = int(value)
                total_percent += new_percent
                
                cat_ref = user_ref.collection('categories').document(cat_id)
                batch.update(cat_ref, {'budget_percent': new_percent})
        
        # Validación opcional: Advertir si no suma 100%, pero permitir guardar
        if total_percent != 100:
            flash(f'Nota: Tus reglas suman {total_percent}%. Lo ideal es 100%.', 'warning')
        else:
            flash('Reglas de presupuesto actualizadas correctamente.', 'success')
            
        batch.commit()
        
    except Exception as e:
        flash(f'Error al actualizar reglas: {e}', 'danger')
        
    return redirect(url_for('budget.planner'))