import os
import pandas as pd
from flask import Flask, render_template_string, request, redirect, url_for, session, flash

app = Flask(__name__)
app.secret_key = 'presidential_secret_key_kemisetso'

# Login Credentials
USER_EMAIL = "molelekwakemisetso04@gmail.com"
USER_PASS = "Kemisetso@2009"

FILE_NAME = 'raw_dirty_data.csv'

def init_csv():
    if os.path.exists(FILE_NAME):
        df = pd.read_csv(FILE_NAME)
        if 'phone' not in df.columns or 'payment_status' not in df.columns:
            os.remove(FILE_NAME)

    if not os.path.exists(FILE_NAME):
        df = pd.DataFrame([
            {"task_id": 101, "client_name": "John Doe", "phone": "0821234567", "amount": 120.50, "status": "completed", "payment_status": "Paid"},
            {"task_id": 102, "client_name": "Jane Smith", "phone": "0719876543", "amount": 250.00, "status": "pending", "payment_status": "Unpaid"},
            {"task_id": 103, "client_name": "Alex Brown", "phone": "0835551234", "amount": 75.20, "status": "pending", "payment_status": "Unpaid"}
        ])
        df.to_csv(FILE_NAME, index=False)

init_csv()

LOGIN_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>Executive Access Portal | President HQ</title>
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <style>
        body { font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; margin: 0; padding: 0; background: #0f172a; color: #f8fafc; display: flex; justify-content: center; align-items: center; min-height: 100vh; }
        .login-card { background: #1e293b; padding: 40px; border-radius: 12px; box-shadow: 0 10px 25px rgba(0,0,0,0.5); width: 90%; max-width: 400px; border: 1px solid #334155; }
        h1 { color: #f59e0b; margin-top: 0; font-size: 24px; text-align: center; text-transform: uppercase; letter-spacing: 1.5px; }
        p.subtitle { text-align: center; color: #94a3b8; margin-bottom: 25px; font-size: 14px; }
        label { display: block; margin-bottom: 6px; font-weight: 600; color: #cbd5e1; font-size: 13px; }
        input[type=email], input[type=password] { width: 100%; padding: 12px; margin-bottom: 18px; box-sizing: border-box; border: 1px solid #475569; border-radius: 6px; background: #0f172a; color: #fff; font-size: 14px; }
        input[type=email]:focus, input[type=password]:focus { border-color: #f59e0b; outline: none; }
        .btn-login { background: #f59e0b; color: #0f172a; width: 100%; padding: 12px; border: none; border-radius: 6px; font-size: 16px; font-weight: bold; cursor: pointer; transition: 0.2s; }
        .btn-login:hover { background: #d97706; }
        .error-msg { background: #ef4444; color: white; padding: 10px; border-radius: 6px; margin-bottom: 15px; text-align: center; font-size: 13px; }
    </style>
</head>
<body>
    <div class="login-card">
        <h1>Kemisetso.Fx</h1>
        <p class="subtitle">Executive Command Center</p>
        {% with messages = get_flashed_messages() %}
          {% if messages %}
            <div class="error-msg">{{ messages[0] }}</div>
          {% endif %}
        {% endwith %}
        <form action="/login" method="POST">
            <label>Username (Email):</label>
            <input type="email" name="username" required placeholder="Enter executive email">
            
            <label>Security Password:</label>
            <input type="password" name="password" required placeholder="Enter password">
            
            <button type="submit" class="btn-login">Authenticate Access</button>
        </form>
    </div>
</body>
</html>
"""

DASHBOARD_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>Presidential Executive Dashboard</title>
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <style>
        body { font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; margin: 0; background: #0f172a; color: #f8fafc; }
        header { background: #1e293b; padding: 15px 20px; border-bottom: 2px solid #f59e0b; display: flex; justify-content: space-between; align-items: center; }
        header h1 { margin: 0; font-size: 20px; color: #f59e0b; letter-spacing: 1px; }
        .logout-btn { background: #dc2626; color: white; padding: 6px 12px; text-decoration: none; border-radius: 4px; font-size: 12px; font-weight: bold; }
        .container { max-width: 1000px; margin: 20px auto; padding: 0 15px; }
        .stats-grid { display: flex; gap: 15px; margin-bottom: 20px; }
        .stat-box { flex: 1; background: #1e293b; border: 1px solid #334155; padding: 20px; border-radius: 8px; text-align: center; }
        .stat-box h3 { margin: 0; font-size: 12px; color: #94a3b8; text-transform: uppercase; letter-spacing: 1px; }
        .stat-box p { margin: 8px 0 0; font-size: 26px; font-weight: bold; color: #f59e0b; }
        .card { background: #1e293b; border: 1px solid #334155; padding: 20px; border-radius: 8px; margin-bottom: 20px; }
        h2 { margin-top: 0; color: #f8fafc; font-size: 18px; border-bottom: 1px solid #334155; padding-bottom: 10px; }
        input[type=text], input[type=number] { width: 100%; padding: 10px; margin: 6px 0 16px; box-sizing: border-box; border: 1px solid #475569; border-radius: 6px; background: #0f172a; color: #fff; }
        .btn { background: #2563eb; color: white; padding: 10px 16px; border: none; border-radius: 6px; cursor: pointer; text-decoration: none; display: inline-block; font-weight: bold; font-size: 13px; }
        .btn-success { background: #16a34a; }
        .btn-call { background: #0284c7; color: white; }
        .btn-pay { background: #9333ea; color: white; }
        table { border-collapse: collapse; width: 100%; margin-top: 10px; font-size: 14px; }
        th, td { border: 1px solid #334155; padding: 12px; text-align: left; vertical-align: middle; }
        th { background: #0f172a; color: #f59e0b; text-transform: uppercase; font-size: 12px; letter-spacing: 0.5px; }
        tr:nth-child(even) { background: #182234; }
        .badge { padding: 4px 8px; border-radius: 4px; font-weight: bold; font-size: 11px; text-transform: uppercase; }
        .badge-pending { background: #d97706; color: #fff; }
        .badge-completed { background: #16a34a; color: #fff; }
        .badge-paid { background: #16a34a; color: #fff; }
    </style>
</head>
<body>
    <header>
        <h1>KEMISETSO.FX | EXECUTIVE SUITE</h1>
        <a href="/logout" class="logout-btn">Lock Portal</a>
    </header>

    <div class="container">
        <div class="stats-grid">
            <div class="stat-box">
                <h3>Active Directives</h3>
                <p>{{ total_tasks }}</p>
            </div>
            <div class="stat-box">
                <h3>Total Valuation</h3>
                <p>R{{ "%.2f"|format(total_revenue) }}</p>
            </div>
        </div>

        <div class="card">
            <h2>Submit Executive Task</h2>
            <form action="/add" method="POST">
                <label>Client Name:</label>
                <input type="text" name="client_name" placeholder="e.g. Mark Taylor" required>
                
                <label>Phone Number:</label>
                <input type="text" name="phone" placeholder="e.g. 0820001122" required>

                <label>Amount (ZAR):</label>
                <input type="number" step="0.01" name="amount" placeholder="e.g. 450.00" required>
                
                <button type="submit" class="btn">Log Entry</button>
            </form>
        </div>

        <div class="card">
            <h2>Operations Database</h2>
            <a href="/process" class="btn btn-success" style="margin-bottom: 15px;">Execute Automated Cleaning</a>
            {{ table_html | safe }}
        </div>
    </div>
</body>
</html>
"""

@app.route('/')
def index():
    if not session.get('logged_in'):
        return redirect(url_for('login_page'))

    df = pd.read_csv(FILE_NAME)
    
    total_tasks = len(df)
    total_revenue = pd.to_numeric(df['amount'], errors='coerce').sum() if 'amount' in df.columns else 0.0

    df_display = df.copy()
    
    if 'phone' in df_display.columns:
        df_display['Contact'] = df_display['phone'].apply(
            lambda num: f'<a href="tel:{num}" class="btn btn-call">Call {num}</a>'
        )
        df_display = df_display.drop(columns=['phone'])

    if 'status' in df_display.columns:
        df_display['status'] = df_display['status'].apply(
            lambda x: f'<span class="badge badge-completed">{x}</span>' if str(x).lower() == 'completed'
            else f'<span class="badge badge-pending">{x}</span>'
        )

    if 'payment_status' in df_display.columns:
        df_display['Payment'] = df_display.apply(
            lambda row: f'<span class="badge badge-paid">Paid</span>' if str(row['payment_status']).lower() == 'paid'
            else f'<a href="/pay/{row["task_id"]}" class="btn btn-pay">Mark Paid</a>', axis=1
        )
        df_display = df_display.drop(columns=['payment_status'])

    if 'amount' in df_display.columns:
        df_display['amount'] = df_display['amount'].apply(lambda x: f"R{float(x):.2f}" if pd.notnull(x) else "R0.00")

    table_html = df_display.to_html(classes='table', escape=False, index=False)
    
    return render_template_string(
        DASHBOARD_TEMPLATE, 
        table_html=table_html, 
        total_tasks=total_tasks, 
        total_revenue=total_revenue
    )

@app.route('/login', methods=['GET', 'POST'])
def login_page():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        if username == USER_EMAIL and password == USER_PASS:
            session['logged_in'] = True
            return redirect(url_for('index'))
        else:
            flash('Invalid executive credentials. Access denied.')
            return redirect(url_for('login_page'))
            
    return render_template_string(LOGIN_TEMPLATE)

@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    return redirect(url_for('login_page'))

@app.route('/add', methods=['POST'])
def add_record():
    if not session.get('logged_in'):
        return redirect(url_for('login_page'))

    client_name = request.form.get('client_name')
    phone = request.form.get('phone')
    amount = request.form.get('amount')
    
    df = pd.read_csv(FILE_NAME)
    new_id = int(df['task_id'].max() + 1) if 'task_id' in df.columns and not df.empty else 101
    
    new_row = pd.DataFrame([{
        "task_id": new_id,
        "client_name": client_name,
        "phone": phone,
        "amount": float(amount) if amount else 0.0,
        "status": "pending",
        "payment_status": "Unpaid"
    }])
    
    df = pd.concat([df, new_row], ignore_index=True)
    df.to_csv(FILE_NAME, index=False)
    return redirect(url_for('index'))

@app.route('/pay/<int:task_id>')
def mark_paid(task_id):
    if not session.get('logged_in'):
        return redirect(url_for('login_page'))

    df = pd.read_csv(FILE_NAME)
    df.loc[df['task_id'] == task_id, 'payment_status'] = 'Paid'
    df.to_csv(FILE_NAME, index=False)
    return redirect(url_for('index'))

@app.route('/process')
def process_data():
    if not session.get('logged_in'):
        return redirect(url_for('login_page'))

    if os.path.exists(FILE_NAME):
        df = pd.read_csv(FILE_NAME)
        if 'client_name' in df.columns:
            df['client_name'] = df['client_name'].astype(str).str.strip().str.title()
        if 'status' in df.columns:
            df['status'] = 'completed'
        df.to_csv(FILE_NAME, index=False)
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
