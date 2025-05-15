from flask import Flask, render_template, request, redirect, session, jsonify
import sqlite3

app = Flask(__name__)
app.secret_key = 'secretkey123'

def init_db():
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT UNIQUE,
                    password TEXT
                )''')
    c.execute('''CREATE TABLE IF NOT EXISTS bookings (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER,
                    vehicle_type TEXT,
                    service_type TEXT,
                    service_date TEXT,
                    status TEXT DEFAULT 'Pending'
                )''')
    conn.commit()
    conn.close()

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/register', methods=['POST'])
def register():
    username = request.form['username']
    password = request.form['password']
    try:
        with sqlite3.connect('database.db') as conn:
            conn.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, password))
        return "Registered successfully"
    except sqlite3.IntegrityError:
        return "Username already exists", 400

@app.route('/login', methods=['POST'])
def login():
    username = request.form['username']
    password = request.form['password']
    with sqlite3.connect('database.db') as conn:
        cur = conn.cursor()
        cur.execute("SELECT id FROM users WHERE username=? AND password=?", (username, password))
        result = cur.fetchone()
        if result:
            session['user_id'] = result[0]
            return "Login successful"
        else:
            return "Invalid credentials", 401

@app.route('/book', methods=['POST'])
def book():
    if 'user_id' not in session:
        return "Unauthorized", 401
    vehicle = request.form['vehicle']
    service = request.form['service']
    date = request.form['date']
    with sqlite3.connect('database.db') as conn:
        conn.execute("INSERT INTO bookings (user_id, vehicle_type, service_type, service_date) VALUES (?, ?, ?, ?)",
                     (session['user_id'], vehicle, service, date))
    return "Booking successful"

@app.route('/history', methods=['GET'])
def history():
    if 'user_id' not in session:
        return "Unauthorized", 401
    with sqlite3.connect('database.db') as conn:
        cur = conn.cursor()
        cur.execute("SELECT vehicle_type, service_type, service_date, status FROM bookings WHERE user_id=?", (session['user_id'],))
        data = cur.fetchall()
    return jsonify(data)

if __name__ == '__main__':
    init_db()
    app.run(debug=True)

