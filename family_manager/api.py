from flask import Flask, jsonify, request, send_from_directory
import sqlite3
import argparse
import logging

logging.basicConfig(filename='api.log', level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

app = Flask(__name__, static_folder='static')

def get_db():
    conn = sqlite3.connect('family_manager.db')  # Same directory
    conn.row_factory = sqlite3.Row
    return conn

@app.route('/api/inventory', methods=['GET'])
def get_inventory():
    conn = get_db()
    items = conn.execute('SELECT * FROM inventory').fetchall()
    conn.close()
    return jsonify([dict(row) for row in items])

@app.route('/api/inventory', methods=['POST'])
def add_inventory():
    data = request.json
    conn = get_db()
    conn.execute('INSERT INTO inventory (name, category, qty, unit, exp_date, location) VALUES (?, ?, ?, ?, ?, ?)',
                 (data['name'], data['category'], data['qty'], data['unit'], data.get('exp_date'), data.get('location', '')))
    conn.commit()
    conn.close()
    return jsonify({'status': 'ok'})

@app.route('/api/meals', methods=['GET'])
def get_meals():
    conn = get_db()
    meals = conn.execute('SELECT * FROM meals').fetchall()
    conn.close()
    return jsonify([dict(row) for row in meals])

@app.route('/api/meals', methods=['POST'])
def add_meal():
    data = request.json
    conn = get_db()
    conn.execute('INSERT INTO meals (date, meal_type, name, ingredients, recipe, time) VALUES (?, ?, ?, ?, ?, ?)',
                 (data['date'], data['meal_type'], data['name'], data['ingredients'], data['recipe'], data.get('time', '')))
    conn.commit()
    conn.close()
    return jsonify({'status': 'ok'})

@app.route('/api/shopping', methods=['GET'])
def get_shopping():
    conn = get_db()
    items = conn.execute('SELECT * FROM shopping_list ORDER BY aisle, item').fetchall()
    conn.close()
    return jsonify([dict(row) for row in items])

@app.route('/api/shopping', methods=['POST'])
def add_shopping():
    data = request.json
    conn = get_db()
    conn.execute('INSERT INTO shopping_list (item, qty, price, aisle) VALUES (?, ?, ?, ?)',
                 (data['item'], data['qty'], data['price'], data.get('aisle', '')))
    conn.commit()
    conn.close()
    return jsonify({'status': 'ok'})

@app.route('/api/shopping/<int:id>', methods=['PUT'])
def update_shopping(id):
    conn = get_db()
    conn.execute('UPDATE shopping_list SET checked = 1 WHERE id = ?', (id,))
    conn.commit()
    conn.close()
    return jsonify({'status': 'ok'})

@app.route('/api/bills', methods=['GET'])
def get_bills():
    conn = get_db()
    bills = conn.execute('SELECT * FROM bills').fetchall()
    conn.close()
    return jsonify([dict(row) for row in bills])

@app.route('/api/bills', methods=['POST'])
def add_bill():
    data = request.json
    conn = get_db()
    conn.execute('INSERT INTO bills (name, amount, due_date, category, recurring, frequency) VALUES (?, ?, ?, ?, ?, ?)',
                 (data['name'], data['amount'], data['due_date'], data['category'], data['recurring'], data['frequency']))
    conn.commit()
    conn.close()
    return jsonify({'status': 'ok'})

@app.route('/api/bills/<int:id>', methods=['PUT'])
def update_bill(id):
    # Mark as paid, and if recurring, create next
    conn = get_db()
    bill = conn.execute('SELECT * FROM bills WHERE id = ?', (id,)).fetchone()
    if bill:
        conn.execute('UPDATE bills SET paid = 1 WHERE id = ?', (id,))
        if bill['recurring']:
            from datetime import datetime, timedelta
            due_date = datetime.strptime(bill['due_date'], "%Y-%m-%d").date()
            if bill['frequency'] == "Weekly":
                next_due = due_date + timedelta(weeks=1)
            elif bill['frequency'] == "Bi-Weekly":
                next_due = due_date + timedelta(weeks=2)
            elif bill['frequency'] == "Monthly":
                next_due = due_date + timedelta(days=30)
            elif bill['frequency'] == "Yearly":
                next_due = due_date + timedelta(days=365)
            else:
                next_due = due_date
            conn.execute('INSERT INTO bills (name, amount, due_date, category, recurring, frequency) VALUES (?, ?, ?, ?, ?, ?)',
                         (bill['name'], bill['amount'], next_due.isoformat(), bill['category'], bill['recurring'], bill['frequency']))
    conn.commit()
    conn.close()
    return jsonify({'status': 'ok'})

@app.route('/api/expenses', methods=['GET'])
def get_expenses():
    conn = get_db()
    expenses = conn.execute('SELECT * FROM expenses').fetchall()
    conn.close()
    return jsonify([dict(row) for row in expenses])

@app.route('/api/expenses', methods=['POST'])
def add_expense():
    data = request.json
    conn = get_db()
    conn.execute('INSERT INTO expenses (date, description, amount, category) VALUES (?, ?, ?, ?)',
                 (data['date'], data['description'], data['amount'], data['category']))
    conn.commit()
    conn.close()
    return jsonify({'status': 'ok'})

@app.route('/api/suggestions', methods=['GET'])
def get_suggestions():
    # Simple meal-based for mobile
    conn = get_db()
    cursor = conn.cursor()
    from datetime import datetime, timedelta
    week_ago = (datetime.now() - timedelta(days=7)).date().isoformat()
    cursor.execute("SELECT ingredients FROM meals WHERE date >= ?", (week_ago,))
    recent_ings = []
    for (ing_str,) in cursor.fetchall():
        if ing_str:
            recent_ings.extend([i.strip() for i in ing_str.split(',') if i.strip()])
    ing_counts = {}
    for ing in recent_ings:
        ing_counts[ing] = ing_counts.get(ing, 0) + 1
    suggestions = [{'item': ing, 'reason': f'Used {count} times recently', 'qty': 1} for ing, count in ing_counts.items() if count > 1]
    # Low stock
    cursor.execute("SELECT name FROM inventory WHERE qty < 1")
    low_stock = [{'item': row[0], 'reason': 'Low stock', 'qty': 1} for row in cursor.fetchall()]
    all_sug = suggestions + low_stock
    conn.close()
    return jsonify(all_sug[:10])

@app.route('/manifest.json')
def manifest():
    return send_from_directory('static', 'manifest.json')

@app.route('/static/<path:path>')
def static_files(path):
    return send_from_directory('static', path)

from flask import render_template

@app.route('/')
def index():
    return '''
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <title>Family Manager Mobile</title>
        <meta name="viewport" content="width=device-width, initial-scale=1">
        <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
        <link href="https://cdn.jsdelivr.net/npm/bootstrap-icons@1.10.0/font/bootstrap-icons.css" rel="stylesheet">
        <link rel="manifest" href="/manifest.json">
        <style>
            body { padding-bottom: 70px; }
            .card { margin-bottom: 10px; }
            .tab-content { margin-top: 20px; }
        </style>
    </head>
    <body class="bg-light">
        <nav class="navbar navbar-expand-lg navbar-dark bg-primary fixed-top">
            <div class="container-fluid">
                <a class="navbar-brand" href="#">Family Manager</a>
            </div>
        </nav>
        <div class="container mt-5 pt-4">
            <h1 class="text-center mb-4">Family Household Manager</h1>
            <ul class="nav nav-tabs" id="myTab" role="tablist">
                <li class="nav-item" role="presentation">
                    <button class="nav-link active" id="inventory-tab" data-bs-toggle="tab" data-bs-target="#inventory" type="button" role="tab">Inventory</button>
                </li>
                <li class="nav-item" role="presentation">
                    <button class="nav-link" id="meals-tab" data-bs-toggle="tab" data-bs-target="#meals" type="button" role="tab">Meals</button>
                </li>
                <li class="nav-item" role="presentation">
                    <button class="nav-link" id="shopping-tab" data-bs-toggle="tab" data-bs-target="#shopping" type="button" role="tab">Shopping</button>
                </li>
                <li class="nav-item" role="presentation">
                    <button class="nav-link" id="bills-tab" data-bs-toggle="tab" data-bs-target="#bills" type="button" role="tab">Bills</button>
                </li>
                <li class="nav-item" role="presentation">
                    <button class="nav-link" id="expenses-tab" data-bs-toggle="tab" data-bs-target="#expenses" type="button" role="tab">Expenses</button>
                </li>
            </ul>
            <div class="tab-content" id="myTabContent">
                <div class="tab-pane fade show active" id="inventory" role="tabpanel">
                    <h2>Add Inventory Item</h2>
                    <form id="inventory-form" class="mb-3">
                        <div class="row g-2">
                            <div class="col-md-6"><input class="form-control" id="inv-name" placeholder="Name" required></div>
                            <div class="col-md-6"><input class="form-control" id="inv-category" placeholder="Category" required></div>
                            <div class="col-md-4"><input class="form-control" id="inv-qty" type="number" placeholder="Quantity" required></div>
                            <div class="col-md-4"><select class="form-select" id="inv-unit" required><option value="">Unit</option><option>pcs</option><option>lbs</option><option>kg</option><option>oz</option><option>gal</option><option>cups</option><option>dozen</option><option>liters</option><option>boxes</option><option>cans</option><option>bottles</option><option value="other">Other</option></select></div>
                            <div class="col-md-4" id="inv-unit-other" style="display:none;"><input class="form-control" id="inv-unit-custom" placeholder="Custom Unit"></div>
                            <div class="col-12"><button type="submit" class="btn btn-primary"><i class="bi bi-plus-circle"></i> Add Item <span class="spinner-border spinner-border-sm d-none" role="status"></span></button></div>
                        </div>
                    </form>
                    <h3>Inventory List</h3>
                    <div id="inventory-list" class="row"></div>
                </div>
                <div class="tab-pane fade" id="meals" role="tabpanel">
                    <h2>Add Meal</h2>
                    <form id="meal-form" class="mb-3">
                        <div class="row g-2">
                            <div class="col-md-6"><input class="form-control" id="meal-date" type="date" required></div>
                            <div class="col-md-6"><select class="form-select" id="meal-type" required><option>Breakfast</option><option>Lunch</option><option>Dinner</option><option>Snack</option></select></div>
                            <div class="col-12"><input class="form-control" id="meal-name" placeholder="Name" required></div>
                            <div class="col-12"><textarea class="form-control" id="meal-ingredients" placeholder="Ingredients"></textarea></div>
                            <div class="col-12"><textarea class="form-control" id="meal-recipe" placeholder="Recipe"></textarea></div>
                            <div class="col-12"><button type="submit" class="btn btn-primary"><i class="bi bi-egg-fried"></i> Add Meal</button></div>
                        </div>
                    </form>
                    <h3>Meals</h3>
                    <div id="meals-list"></div>
                </div>
                <div class="tab-pane fade" id="shopping" role="tabpanel">
                    <h2>Add Shopping Item</h2>
                    <form id="shopping-form" class="mb-3">
                        <div class="row g-2">
                            <div class="col-md-8"><input class="form-control" id="shop-item" placeholder="Item" required></div>
                            <div class="col-md-4"><input class="form-control" id="shop-qty" type="number" placeholder="Qty" required></div>
                            <div class="col-md-6"><input class="form-control" id="shop-price" type="number" step="0.01" placeholder="Price"></div>
                            <div class="col-md-6"><input class="form-control" id="shop-aisle" placeholder="Aisle"></div>
                            <div class="col-12"><button type="submit" class="btn btn-primary"><i class="bi bi-cart-plus"></i> Add Item</button></div>
                        </div>
                    </form>
                    <button id="suggestions-btn" class="btn btn-info mb-3"><i class="bi bi-lightbulb"></i> Get Smart Suggestions</button>
                    <div id="suggestions-list" class="mb-3" style="display:none;"></div>
                    <h3>Shopping List</h3>
                    <div id="shopping-list"></div>
                </div>
                <div class="tab-pane fade" id="bills" role="tabpanel">
                    <h2>Add Bill</h2>
                    <form id="bill-form" class="mb-3">
                        <div class="row g-2">
                            <div class="col-md-6"><input class="form-control" id="bill-name" placeholder="Name" required></div>
                            <div class="col-md-6"><input class="form-control" id="bill-amount" type="number" step="0.01" placeholder="Amount" required></div>
                            <div class="col-md-6"><input class="form-control" id="bill-due" type="date" required></div>
                            <div class="col-md-6"><input class="form-control" id="bill-category" placeholder="Category"></div>
                            <div class="col-12"><div class="form-check"><input class="form-check-input" type="checkbox" id="bill-recurring"><label class="form-check-label">Recurring</label></div></div>
                            <div class="col-12" id="freq-div" style="display:none;"><select class="form-select" id="bill-freq"><option>Weekly</option><option>Bi-Weekly</option><option>Monthly</option><option>Yearly</option></select></div>
                            <div class="col-12"><button type="submit" class="btn btn-primary"><i class="bi bi-receipt"></i> Add Bill</button></div>
                        </div>
                    </form>
                    <h3>Bills</h3>
                    <div id="bills-list"></div>
                </div>
                <div class="tab-pane fade" id="expenses" role="tabpanel">
                    <h2>Add Expense</h2>
                    <form id="expense-form" class="mb-3">
                        <div class="row g-2">
                            <div class="col-md-6"><input class="form-control" id="exp-date" type="date" required></div>
                            <div class="col-md-6"><input class="form-control" id="exp-desc" placeholder="Description" required></div>
                            <div class="col-md-6"><input class="form-control" id="exp-amount" type="number" step="0.01" placeholder="Amount" required></div>
                            <div class="col-md-6"><input class="form-control" id="exp-category" placeholder="Category"></div>
                            <div class="col-12"><button type="submit" class="btn btn-primary"><i class="bi bi-cash-stack"></i> Add Expense</button></div>
                        </div>
                    </form>
                    <h3>Expenses</h3>
                    <div id="expenses-list"></div>
                </div>
            </div>
        </div>
        <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js"></script>
        <script>
            if ('serviceWorker' in navigator) {
                navigator.serviceWorker.register('/static/sw.js')
                  .then((registration) => console.log('SW registered'))
                  .catch((error) => console.log('SW registration failed'));
            }
        </script>
        <script>
            document.getElementById('bill-recurring').addEventListener('change', function() {
                document.getElementById('freq-div').style.display = this.checked ? 'block' : 'none';
            });

            // Inventory
            document.getElementById('inv-unit').addEventListener('change', function() {
                const otherDiv = document.getElementById('inv-unit-other');
                if (this.value === 'other') {
                    otherDiv.style.display = 'block';
                } else {
                    otherDiv.style.display = 'none';
                }
            });

            document.getElementById('inventory-form').addEventListener('submit', async (e) => {
                e.preventDefault();
                const spinner = e.target.querySelector('.spinner-border');
                spinner.classList.remove('d-none');
                let unit = document.getElementById('inv-unit').value;
                if (unit === 'other') {
                    unit = document.getElementById('inv-unit-custom').value || 'other';
                }
                const data = {
                    name: document.getElementById('inv-name').value,
                    category: document.getElementById('inv-category').value,
                    qty: parseFloat(document.getElementById('inv-qty').value),
                    unit: unit,
                    exp_date: document.getElementById('inv-exp').value || null,
                    location: ''
                };
                await fetch('/api/inventory', { method: 'POST', headers: {'Content-Type': 'application/json'}, body: JSON.stringify(data) });
                loadInventory();
                document.getElementById('inventory-form').reset();
                document.getElementById('inv-unit-other').style.display = 'none';
                spinner.classList.add('d-none');
            });

            async function loadInventory() {
                const res = await fetch('/api/inventory');
                const items = await res.json();
                document.getElementById('inventory-list').innerHTML = items.map(i => `
                    <div class="col-md-6 col-lg-4">
                        <div class="card">
                            <div class="card-body">
                                <h5 class="card-title">${i.name}</h5>
                                <p class="card-text">Qty: ${i.qty} ${i.unit}<br>Category: ${i.category}<br>Exp: ${i.exp_date || 'N/A'}</p>
                            </div>
                        </div>
                    </div>
                `).join('');
            }

            // Meals
            document.getElementById('meal-form').addEventListener('submit', async (e) => {
                e.preventDefault();
                const data = {
                    date: document.getElementById('meal-date').value,
                    meal_type: document.getElementById('meal-type').value,
                    name: document.getElementById('meal-name').value,
                    ingredients: document.getElementById('meal-ingredients').value,
                    recipe: document.getElementById('meal-recipe').value,
                    time: '12:00'
                };
                await fetch('/api/meals', { method: 'POST', headers: {'Content-Type': 'application/json'}, body: JSON.stringify(data) });
                loadMeals();
                document.getElementById('meal-form').reset();
            });

            async function loadMeals() {
                const res = await fetch('/api/meals');
                const meals = await res.json();
                document.getElementById('meals-list').innerHTML = meals.map(m => `
                    <div class="card mb-2">
                        <div class="card-body">
                            <h5 class="card-title">${m.name} (${m.meal_type})</h5>
                            <p class="card-text">Date: ${m.date}<br>Ingredients: ${m.ingredients}<br>Recipe: ${m.recipe}</p>
                        </div>
                    </div>
                `).join('');
            }

            // Shopping
            document.getElementById('shopping-form').addEventListener('submit', async (e) => {
                e.preventDefault();
                const data = {
                    item: document.getElementById('shop-item').value,
                    qty: parseInt(document.getElementById('shop-qty').value),
                    price: parseFloat(document.getElementById('shop-price').value) || 0,
                    aisle: document.getElementById('shop-aisle').value
                };
                await fetch('/api/shopping', { method: 'POST', headers: {'Content-Type': 'application/json'}, body: JSON.stringify(data) });
                loadShopping();
                document.getElementById('shopping-form').reset();
            });

            async function loadShopping() {
                const res = await fetch('/api/shopping');
                const items = await res.json();
                document.getElementById('shopping-list').innerHTML = items.map(s => `
                    <div class="card mb-2">
                        <div class="card-body d-flex justify-content-between align-items-center">
                            <div><strong>${s.item}</strong> - Qty: ${s.qty} - $${s.price} - Aisle: ${s.aisle}</div>
                            <button class="btn btn-sm btn-success" onclick="markChecked(${s.id})">Check</button>
                        </div>
                    </div>
                `).join('');
            }

            async function markChecked(id) {
                await fetch('/api/shopping/' + id, { method: 'PUT' });
                loadShopping();
            }

            // Suggestions
            document.getElementById('suggestions-btn').addEventListener('click', async () => {
                const res = await fetch('/api/suggestions');
                const suggestions = await res.json();
                const sugDiv = document.getElementById('suggestions-list');
                if (suggestions.length === 0) {
                    sugDiv.innerHTML = '<p>No suggestions available.</p>';
                } else {
                    sugDiv.innerHTML = suggestions.map(s => `
                        <div class="card mb-2">
                            <div class="card-body d-flex justify-content-between align-items-center">
                                <div><strong>${s.item}</strong> (${s.reason}) - Qty: ${s.qty}</div>
                                <button class="btn btn-sm btn-success" onclick="addSuggestion('${s.item}', ${s.qty})">Add</button>
                            </div>
                        </div>
                    `).join('');
                }
                sugDiv.style.display = 'block';
            });

            async function addSuggestion(item, qty) {
                const data = { item: item, qty: qty, price: 0, aisle: '' };
                await fetch('/api/shopping', { method: 'POST', headers: {'Content-Type': 'application/json'}, body: JSON.stringify(data) });
                loadShopping();
                document.getElementById('suggestions-list').style.display = 'none';
            }

            // Bills
            document.getElementById('bill-form').addEventListener('submit', async (e) => {
                e.preventDefault();
                const data = {
                    name: document.getElementById('bill-name').value,
                    amount: parseFloat(document.getElementById('bill-amount').value),
                    due_date: document.getElementById('bill-due').value,
                    category: document.getElementById('bill-category').value,
                    recurring: document.getElementById('bill-recurring').checked ? 1 : 0,
                    frequency: document.getElementById('bill-freq').value
                };
                await fetch('/api/bills', { method: 'POST', headers: {'Content-Type': 'application/json'}, body: JSON.stringify(data) });
                loadBills();
                document.getElementById('bill-form').reset();
            });

            async function loadBills() {
                const res = await fetch('/api/bills');
                const bills = await res.json();
                document.getElementById('bills-list').innerHTML = bills.map(b => `
                    <div class="card mb-2">
                        <div class="card-body d-flex justify-content-between align-items-center">
                            <div><strong>${b.name}</strong> - $${b.amount} - Due: ${b.due_date} - ${b.category} - Recurring: ${b.recurring ? 'Yes' : 'No'}</div>
                            ${!b.paid ? `<button class="btn btn-sm btn-warning" onclick="markPaid(${b.id})">Pay</button>` : '<span class="text-success">Paid</span>'}
                        </div>
                    </div>
                `).join('');
            }

            async function markPaid(id) {
                await fetch('/api/bills/' + id, { method: 'PUT' });
                loadBills();
            }

            // Expenses
            document.getElementById('expense-form').addEventListener('submit', async (e) => {
                e.preventDefault();
                const data = {
                    date: document.getElementById('exp-date').value,
                    description: document.getElementById('exp-desc').value,
                    amount: parseFloat(document.getElementById('exp-amount').value),
                    category: document.getElementById('exp-category').value
                };
                await fetch('/api/expenses', { method: 'POST', headers: {'Content-Type': 'application/json'}, body: JSON.stringify(data) });
                loadExpenses();
                document.getElementById('expense-form').reset();
            });

            async function loadExpenses() {
                const res = await fetch('/api/expenses');
                const expenses = await res.json();
                document.getElementById('expenses-list').innerHTML = expenses.map(e => `
                    <div class="card mb-2">
                        <div class="card-body">
                            <h5 class="card-title">${e.description}</h5>
                            <p class="card-text">Date: ${e.date} - $${e.amount} - ${e.category}</p>
                        </div>
                    </div>
                `).join('');
            }

            // Load all on start
            loadInventory();
            loadMeals();
            loadShopping();
            loadBills();
            loadExpenses();
        </script>
    </body>
    </html>
    '''

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Family Manager Web Server')
    parser.add_argument('--port', type=int, default=8000, help='Port to run the server on')
    args = parser.parse_args()
    app.run(host='127.0.0.1', port=args.port, debug=False)