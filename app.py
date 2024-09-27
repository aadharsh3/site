from flask import Flask, render_template, request, redirect, url_for, session, flash
import sqlite3
from flask_session import Session
from datetime import datetime

app = Flask(__name__)

app.secret_key = 'your_secret_key'
app.config['SESSION_TYPE'] = 'filesystem'
Session(app)

ADMIN_CREDENTIALS = {
    'Admin': 'admin123',
    'aadhi': '12345'
}

def init_db():
    conn = sqlite3.connect("database.db")
    c = conn.cursor()
    c.execute("""CREATE TABLE IF NOT EXISTS emp (
                  id INTEGER PRIMARY KEY AUTOINCREMENT, 
                  name TEXT NOT NULL, 
                  mail TEXT NOT NULL,
                  date TEXT NOT NULL)""")
    print("Table created")
    conn.commit()
    conn.close()

@app.route('/')
def index():
    if not session.get('loggedin'):
        return redirect(url_for('login'))
    return render_template('index.html')

@app.route('/submit', methods=['POST'])
def submit():
    name = request.form['name']
    mail = request.form['mail']
    date_str = request.form['date']

    appointment_date = datetime.strptime(date_str, '%Y-%m-%d')
    current_date = datetime.now()

    if appointment_date < current_date:
        flash("Error: The appointment date cannot be in the past.")
        return redirect(url_for('index'))

    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    cursor.execute('INSERT INTO emp (name, mail, date) VALUES (?, ?, ?)', (name, mail, date_str))
    conn.commit()
    conn.close()
    
    flash("Appointment successfully created.")
    return redirect(url_for('index'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        if username in ADMIN_CREDENTIALS and ADMIN_CREDENTIALS[username] == password:
            session['loggedin'] = True
            flash('Successfully logged in!')
            return redirect(url_for('index'))  
        else:
            flash('Invalid credentials, please try again.')
            return redirect(url_for('login'))

    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('loggedin', None)
    flash('You have been logged out.')
    return redirect(url_for('login'))

@app.route('/result')
def result():
    if not session.get('loggedin'):  
        return redirect(url_for('login'))

    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM emp')  
    data = cursor.fetchall()
    conn.close()  

    return render_template('result.html', data=data)

if __name__ == '__main__':
    init_db() 
    app.run(debug=True)