from flask import Flask, render_template, request, session, redirect, url_for, flash
import mysql.connector
from mysql.connector import Error
import os
import secrets

app = Flask(__name__)
app.secret_key = os.environ.get('FLASK_SECRET_KEY') or secrets.token_urlsafe(32)
# Databaskonfiguration
DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',  # Ändra detta till ditt MySQL-användarnamn
    'password': '',  # Ändra detta till ditt MySQL-lösenord
    'database': 'inlamning_1'  
}

def get_db_connection():
    """Skapa och returnera en databasanslutning"""
    try:
        connection = mysql.connector.connect(**DB_CONFIG)
        return connection
    except Error as e:
        print(f"Fel vid anslutning till MySQL: {e}")
        return None

@app.route('/')
def index():
    if 'username' in session:
        return render_template('home.html', username=session['username'])
    return render_template('login.html')

@app.route('/logout')
def logout():
    # Rensa sessionen för att logga ut användaren
    session.clear()
    return redirect(url_for('index'))

@app.route('/login', methods=['POST'])
def login():
    # hantera POST request från inloggningsformuläret
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        # Anslut till databasen
        connection = get_db_connection()
        if connection is None:
            return "Databasanslutning misslyckades", 500
        
        try:
            cursor = connection.cursor(dictionary=True)
            
            # Fråga för att kontrollera om användare finns med matchande användarnamn
            query = "SELECT * FROM users WHERE username = %s"
            cursor.execute(query, (username,))
            user = cursor.fetchone()
            
       
            if user and user['password'] == password: 
                session["username"] = user['username']
                flash('Inloggning lyckades! Välkommen!', 'success')
                return redirect(url_for('index'))
            else:
                # Inloggning misslyckades, skicka http status 401 (Unauthorized)
                flash('Ogiltigt användarnamn eller lösenord', 'error')
                return redirect(url_for('index'))

        except Error as e:
            print(f"Databasfel: {e}")
            return "Databasfel inträffade", 500
        
        finally:
            if connection.is_connected():
                cursor.close()
                connection.close()

if __name__ == '__main__':
    app.run(debug=True)