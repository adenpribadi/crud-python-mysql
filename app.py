# app.py
import os
from dotenv import load_dotenv

# Fungsi untuk memeriksa dan membuat file .env jika tidak ada
def check_and_create_env():
    env_file = '.env'
    if not os.path.exists(env_file):
        # Jika .env tidak ada, buat dengan default value
        with open(env_file, 'w') as f:
            f.write("DB_USER='userMysql'\n")
            f.write("DB_PASSWORD='pwdMysql'\n")
            f.write("DB_HOST='127.0.0.1'\n")
            f.write("DB_PORT='3306'\n")
            f.write("DB_NAME='db_app'\n")
            f.write("CDN_HOST='127.0.0.1'\n")
            f.write("CDN_USER='user_win'\n")
            f.write("CDN_PASSWORD='passwd_win'\n")
        print(f"{env_file} tidak ditemukan. File .env baru telah dibuat.")
    else:
        print(f"{env_file} sudah ada.")

# Panggil fungsi pengecekan .env
check_and_create_env()

# Memuat variabel dari .env
load_dotenv()

from flask import Flask, render_template, request, redirect, url_for, session

from blueprints.auth.routes import auth_bp
from blueprints.employee.routes import employee_bp
from blueprints.db_config.routes import db_bp
from blueprints.purchases.request import purchases_request_bp
from blueprints.purchases.order import purchases_order_bp

import os
import threading
import webview

app = Flask(__name__)
# Set the secret key for the application
app.secret_key = os.urandom(24)  # Generate a random secret key

@app.route('/')
def index():
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))
    location = session.get('location', None)
    return render_template('index.html', location=location)

app.register_blueprint(auth_bp)
app.register_blueprint(employee_bp)
app.register_blueprint(db_bp)  # Register db_config blueprint

app.register_blueprint(purchases_request_bp) # Register purchases_request blueprint
app.register_blueprint(purchases_order_bp) # Register purchases_order blueprint

# Register blueprints by scaffold
from blueprints.product.routes import product_bp

app.register_blueprint(product_bp)

@app.route('/set_location', methods=['POST'])
def set_location():
    data = request.json
    if data:
        latitude = data.get('latitude')
        longitude = data.get('longitude')
        session['location'] = {'latitude': latitude, 'longitude': longitude}
        return {'message': 'Location received'}, 200
    print("set_location: ", session['location'])
    return {'message': 'Invalid data'}, 400

@app.route('/<path:path>')
def serve_page(path):
    try:
        return render_template(path)
    except:
        return render_template('404.html'), 404

def start_server():
    app.run(host='127.0.0.1', port=5000, debug=True, use_reloader=False)

if __name__ == '__main__':
    # Start the Flask server in a separate thread
    server = threading.Thread(target=start_server)
    server.daemon = True
    server.start()

    # Create a PyWebView window and load the Flask app
    window = webview.create_window('CoreUI Python App', 'http://127.0.0.1:5000', width=1024, height=768)

    # Start the PyWebView application with debug mode enabled
    webview.start(debug=False)
