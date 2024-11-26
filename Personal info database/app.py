from flask import Flask, render_template, request, redirect, url_for, flash, session
import sqlite3

app = Flask(__name__)
app.secret_key = "your_secret_key"  # For session management and flashing messages


# Database Initialization
def init_db():
    conn = sqlite3.connect('personal_info.db')
    cursor = conn.cursor()

    # Create users table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL,
            password TEXT NOT NULL
        )
    ''')

    # Create persons table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS persons (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            age INTEGER NOT NULL,
            contact TEXT NOT NULL
        )
    ''')

    # Insert a default admin user if not exists
    cursor.execute("SELECT * FROM users WHERE username = 'admin'")
    if not cursor.fetchone():
        cursor.execute("INSERT INTO users (username, password) VALUES ('admin', 'password123')")
        print("Default admin user created: username='admin', password='password123'")

    conn.commit()
    conn.close()


# Login page
@app.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        conn = sqlite3.connect('personal_info.db')
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE username = ? AND password = ?", (username, password))
        user = cursor.fetchone()
        conn.close()

        if user:
            session['username'] = username
            flash('Login successful!', 'success')
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid username or password!', 'error')

    return render_template('login.html')


# Logout route
@app.route('/logout')
def logout():
    session.pop('username', None)
    flash('You have been logged out.', 'success')
    return redirect(url_for('login'))


# Dashboard route
@app.route('/dashboard')
def dashboard():
    if 'username' not in session:
        flash('Please log in first.', 'error')
        return redirect(url_for('login'))
    return render_template('dashboard.html')


# Add person route
@app.route('/add', methods=['GET', 'POST'])
def add_person():
    if 'username' not in session:
        flash('Please log in first.', 'error')
        return redirect(url_for('login'))

    if request.method == 'POST':
        name = request.form['name']
        age = request.form['age']
        contact = request.form['contact']

        conn = sqlite3.connect('personal_info.db')
        cursor = conn.cursor()
        cursor.execute("INSERT INTO persons (name, age, contact) VALUES (?, ?, ?)", (name, int(age), contact))
        conn.commit()
        conn.close()

        flash('Personal information added successfully!', 'success')
        return redirect(url_for('view_persons'))

    return render_template('add_person.html')


# View all persons route
@app.route('/view')
def view_persons():
    if 'username' not in session:
        flash('Please log in first.', 'error')
        return redirect(url_for('login'))

    conn = sqlite3.connect('personal_info.db')
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM persons")
    persons = cursor.fetchall()
    conn.close()

    return render_template('view_persons.html', persons=persons)


# Delete person route
@app.route('/delete/<int:person_id>', methods=['POST'])
def delete_person(person_id):
    if 'username' not in session:
        flash('Please log in first.', 'error')
        return redirect(url_for('login'))

    conn = sqlite3.connect('personal_info.db')
    cursor = conn.cursor()
    cursor.execute("DELETE FROM persons WHERE id = ?", (person_id,))
    conn.commit()
    conn.close()

    flash('Personal information deleted successfully!', 'success')
    return redirect(url_for('view_persons'))


if __name__ == '__main__':
    init_db()  # Initialize the database
    app.run(debug=True)
