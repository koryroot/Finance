# app.py
from flask import Flask, render_template, request, redirect, url_for, flash
from data import *
import os
from datetime import datetime
from collections import defaultdict
import locale

basedir = os.path.abspath(os.path.dirname(__file__))
app = Flask(__name__, template_folder=os.path.join(basedir, 'templates'))
app.secret_key = 'tu_clave_secreta_aqui'

try:
    locale.setlocale(locale.LC_TIME, 'es_ES.UTF-8')
except locale.Error:
    locale.setlocale(locale.LC_TIME, 'Spanish')

# --- RUTAS PRINCIPALES ---
@app.route('/')
def dashboard():
    DATA = get_all_data()
    current_month = datetime.now().month
    current_year = datetime.now().year
    
    monthly_income_list = [inc for inc in DATA['income'] if datetime.fromisoformat(inc['date']).month == current_month and datetime.fromisoformat(inc['date']).year == current_year]
    monthly_expenses = [exp for exp in DATA['expenses'] if datetime.fromisoformat(exp['date']).month == current_month and datetime.fromisoformat(exp['date']).year == current_year]
    
    total_monthly_income = sum(inc['amount'] for inc in monthly_income_list)
    total_monthly_expenses = sum(exp['amount'] for exp in monthly_expenses)
    
    total_budgeted = total_monthly_income

    expenses_by_category = []
    for cat in DATA['categories']:
        budget_amount = total_monthly_income * (cat['budget_percent'] / 100)
        spent = sum(exp['amount'] for exp in monthly_expenses if exp['categoryId'] == cat['id'])
        percentage = (spent / budget_amount * 100) if budget_amount > 0 else 0
        
        expenses_by_category.append({
            **cat, 'budget_amount': budget_amount, 'spent': spent, 
            'remaining': budget_amount - spent, 'percentage_capped': min(percentage, 100)
        })

    return render_template(
        'dashboard.html', month_name=datetime.now().strftime('%B').capitalize(),
        total_income=total_monthly_income, total_expenses=total_monthly_expenses,
        total_budgeted=total_budgeted,
        expenses_by_category=expenses_by_category, categories=DATA['categories'],
        today_date=datetime.now().strftime('%Y-%m-%d')
    )

@app.route('/budget', methods=['GET', 'POST'])
def budget():
    if request.method == 'POST':
        update_budget_percentages(request.form)
        flash('Porcentajes del presupuesto actualizados.', 'success')
        return redirect(url_for('budget'))
        
    DATA = get_all_data()
    total_income = sum(inc['amount'] for inc in DATA['income'])
    
    budget_details = []
    for cat in DATA['categories']:
        budget_amount = total_income * (cat['budget_percent'] / 100)
        planned_exp = [p for p in DATA['planned_expenses'] if p['categoryId'] == cat['id']]
        budget_details.append({**cat, 'budget_amount': budget_amount, 'planned_expenses': planned_exp})

    return render_template('budget.html', data=DATA, budget_details=budget_details, total_income=total_income)

@app.route('/savings', methods=['GET', 'POST'])
def savings():
    if request.method == 'POST':
        update_emergency_fund(request.form.get('goal'), request.form.get('current'))
        flash('Fondo de emergencia actualizado.', 'success')
        return redirect(url_for('savings'))
    return render_template('savings.html', data=get_all_data())

@app.route('/charts')
def charts():
    DATA = get_all_data()
    current_month = datetime.now().month
    current_year = datetime.now().year
    monthly_expenses = [exp for exp in DATA['expenses'] if datetime.fromisoformat(exp['date']).month == current_month and datetime.fromisoformat(exp['date']).year == current_year]
    total_monthly_income = sum(inc['amount'] for inc in DATA['income'] if datetime.fromisoformat(inc['date']).month == current_month and datetime.fromisoformat(inc['date']).year == current_year)

    pie_data = defaultdict(float)
    for exp in monthly_expenses:
        cat_name = next((c['name'] for c in DATA['categories'] if c['id'] == exp['categoryId']), "Otro")
        pie_data[cat_name] += exp['amount']

    budget_vs_actual = []
    for cat in DATA['categories']:
        budget_amount = total_monthly_income * (cat['budget_percent'] / 100)
        spent = sum(exp['amount'] for exp in monthly_expenses if exp['categoryId'] == cat['id'])
        budget_vs_actual.append({'name': cat['name'], 'budget': budget_amount, 'spent': spent})
        
    return render_template('charts.html', pie_data=dict(pie_data), budget_vs_actual=budget_vs_actual)

# --- RUTAS DE ACCIONES ---
@app.route('/add_transaction', methods=['POST'])
def add_transaction_route():
    trans_type = request.form.get('type')
    description = request.form.get('description')
    amount = request.form.get('amount')
    date = request.form.get('date')

    if trans_type == 'expense':
        category_id = request.form.get('category_id')
        add_expense(description, amount, category_id, date)
        flash('Gasto añadido con éxito.', 'success')
    elif trans_type == 'income':
        add_income(description, amount, date)
        flash('Ingreso añadido con éxito.', 'success')
    
    return redirect(url_for('dashboard'))

@app.route('/add_planned_expense', methods=['POST'])
def add_planned_expense_route():
    add_planned_expense(request.form.get('description'), request.form.get('amount'), request.form.get('category_id'))
    return redirect(url_for('budget'))

@app.route('/pay_planned_expense/<int:planned_expense_id>', methods=['POST'])
def pay_planned_expense_route(planned_expense_id):
    pay_planned_expense(planned_expense_id)
    return redirect(request.referrer or url_for('budget'))

@app.route('/unpay_planned_expense/<int:planned_expense_id>', methods=['POST'])
def unpay_planned_expense_route(planned_expense_id):
    unpay_planned_expense(planned_expense_id)
    return redirect(request.referrer or url_for('budget'))

@app.route('/delete_planned_expense/<int:planned_expense_id>', methods=['POST'])
def delete_planned_expense_route(planned_expense_id):
    delete_planned_expense(planned_expense_id)
    return redirect(url_for('budget'))
    
@app.route('/category/<int:category_id>')
def category_detail(category_id):
    category = get_category_by_id(category_id)
    if not category: return "Categoría no encontrada", 404
    
    category_expenses = sorted([exp for exp in get_all_data()['expenses'] if exp['categoryId'] == category_id], key=lambda x: x['date'], reverse=True)
    planned_expenses = [p for p in get_all_data()['planned_expenses'] if p['categoryId'] == category_id]
    
    return render_template('category_detail.html', category=category, expenses=category_expenses, planned_expenses=planned_expenses)

@app.route('/delete_expense/<int:expense_id>', methods=['POST'])
def delete_expense_route(expense_id):
    expense = get_expense_by_id(expense_id)
    if expense:
        category_id = expense['categoryId']
        delete_expense(expense_id)
        flash('Gasto eliminado.', 'success')
        return redirect(url_for('category_detail', category_id=category_id))
    return redirect(url_for('dashboard'))

@app.route('/add_savings_goal', methods=['POST'])
def add_savings_goal_route():
    add_savings_goal(request.form.get('name'), request.form.get('goal'), request.form.get('current', 0))
    flash('Nueva meta de ahorro añadida.', 'success')
    return redirect(url_for('savings'))

@app.route('/delete_savings_goal/<int:goal_id>', methods=['POST'])
def delete_savings_goal_route(goal_id):
    delete_savings_goal(goal_id)
    flash('Meta de ahorro eliminada.', 'success')
    return redirect(url_for('savings'))

if __name__ == '__main__':
    app.run(debug=True, port=5001)
