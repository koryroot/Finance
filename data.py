# data.py
import datetime

DB = {
    "income": [
        {'id': 1, 'source': 'Salario Quincenal', 'amount': 25000, 'date': '2025-08-15'},
        {'id': 2, 'source': 'Salario Quincenal', 'amount': 25000, 'date': '2025-08-30'},
    ],
    "categories": [
        {'id': 1, 'name': 'Diezmo', 'budget_percent': 10, 'color': '#f97316'},
        {'id': 2, 'name': 'Gastos Fijos', 'budget_percent': 40, 'color': '#3b82f6'},
        {'id': 3, 'name': 'Gastos Personales', 'budget_percent': 30, 'color': '#8b5cf6'},
        {'id': 4, 'name': 'Ahorro e Inversión', 'budget_percent': 20, 'color': '#10b981'},
    ],
    "planned_expenses": [
        {'id': 1, 'categoryId': 2, 'description': 'Alquiler', 'amount': 15000, 'is_paid': False},
        {'id': 2, 'categoryId': 2, 'description': 'Luz', 'amount': 1500, 'is_paid': True},
        {'id': 3, 'categoryId': 2, 'description': 'Internet y Cable', 'amount': 2500, 'is_paid': False},
        {'id': 4, 'categoryId': 3, 'description': 'Supermercado', 'amount': 8000, 'is_paid': False},
    ],
    "expenses": [
        {'id': 1, 'categoryId': 2, 'description': 'Luz', 'amount': 1500, 'date': '2025-08-05'},
        {'id': 2, 'categoryId': 3, 'description': 'Salida con amigos', 'amount': 1200, 'date': '2025-08-10'},
        {'id': 3, 'categoryId': 1, 'description': 'Ofrenda', 'amount': 2500, 'date': '2025-08-17'},
    ],
    "emergency_fund": { "goal": 150000, "current": 75000 },
    "savings_goals": [
        {'id': 1, 'name': 'Vacaciones a la playa', 'goal': 30000, 'current': 5000},
        {'id': 2, 'name': 'Nueva Laptop', 'goal': 60000, 'current': 35000},
    ]
}

# --- FUNCIONES DE DATOS ---
def get_all_data(): return DB

def get_category_by_id(category_id):
    return next((cat for cat in DB['categories'] if cat['id'] == category_id), None)

# --- FUNCIONES DE PRESUPUESTO ---
def update_budget_percentages(percentages):
    for cat in DB['categories']:
        key = f"percent_{cat['id']}"
        if key in percentages and percentages[key]:
            cat['budget_percent'] = int(percentages[key])

def add_planned_expense(description, amount, category_id):
    if not all([description, amount, category_id]): return
    new_id = max([p['id'] for p in DB['planned_expenses']] + [0]) + 1
    DB['planned_expenses'].append({
        'id': new_id, 'categoryId': int(category_id), 'description': description,
        'amount': float(amount), 'is_paid': False
    })

def pay_planned_expense(planned_expense_id):
    planned_exp = next((p for p in DB['planned_expenses'] if p['id'] == planned_expense_id), None)
    if planned_exp and not planned_exp['is_paid']:
        planned_exp['is_paid'] = True
        # --- INICIO DE LA CORRECCIÓN ---
        add_expense(
            planned_exp['description'], planned_exp['amount'],
            planned_exp['categoryId'], datetime.datetime.now().strftime('%Y-%m-%d')
        )
        # --- FIN DE LA CORRECCIÓN ---

def unpay_planned_expense(planned_expense_id):
    planned_exp = next((p for p in DB['planned_expenses'] if p['id'] == planned_expense_id), None)
    if planned_exp and planned_exp['is_paid']:
        planned_exp['is_paid'] = False
        expense_to_delete = next((
            exp for exp in DB['expenses']
            if exp['description'] == planned_exp['description'] and
               exp['amount'] == planned_exp['amount'] and
               exp['categoryId'] == planned_exp['categoryId']
        ), None)
        if expense_to_delete:
            DB['expenses'].remove(expense_to_delete)

def delete_planned_expense(planned_expense_id):
    DB['planned_expenses'] = [p for p in DB['planned_expenses'] if p['id'] != planned_expense_id]

# --- FUNCIONES DE GASTOS ---
def add_expense(description, amount, category_id, date_str):
    if not all([description, amount, category_id, date_str]): return
    new_id = max([exp['id'] for exp in DB['expenses']] + [0]) + 1
    DB['expenses'].append({
        'id': new_id, 'categoryId': int(category_id), 'description': description,
        'amount': float(amount), 'date': date_str
    })

def get_expense_by_id(expense_id):
    return next((exp for exp in DB['expenses'] if exp['id'] == expense_id), None)

def delete_expense(expense_id):
    DB['expenses'] = [exp for exp in DB['expenses'] if exp['id'] != expense_id]

# --- FUNCIONES DE INGRESOS ---
def add_income(source, amount, date_str):
    if not all([source, amount, date_str]): return
    new_id = max([inc['id'] for inc in DB['income']] + [0]) + 1
    DB['income'].append({'id': new_id, 'source': source, 'amount': float(amount), 'date': date_str})

def delete_income(income_id):
    DB['income'] = [inc for inc in DB['income'] if inc['id'] != income_id]

# --- FUNCIONES DE AHORROS ---
def update_emergency_fund(goal, current):
    DB['emergency_fund'].update({'goal': float(goal), 'current': float(current)})

def add_savings_goal(name, goal, current):
    if not all([name, goal, current]): return
    new_id = max([g['id'] for g in DB['savings_goals']] + [0]) + 1
    DB['savings_goals'].append({'id': new_id, 'name': name, 'goal': float(goal), 'current': float(current)})

def delete_savings_goal(goal_id):
    DB['savings_goals'] = [g for g in DB['savings_goals'] if g['id'] != goal_id]
