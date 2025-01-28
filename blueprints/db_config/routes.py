from flask import Blueprint, render_template, request, flash, redirect, url_for, jsonify
from sqlalchemy import create_engine
from sqlalchemy.exc import OperationalError
import os
import urllib.parse
from dotenv import load_dotenv, set_key
import subprocess

# Load .env file
load_dotenv()

db_bp = Blueprint("db_config", __name__, url_prefix="/db-config")

@db_bp.route("/", methods=["GET", "POST"])
def update_db_config():
    db_file = ".env"  # Path ke file .env
    current_config = {
        "cdn_host": os.getenv("CDN_HOST"),
        "cdn_user": os.getenv("CDN_USER"),
        "cdn_password": os.getenv("CDN_PASSWORD"),
        "host": os.getenv("DB_HOST"),
        "port": os.getenv("DB_PORT"),
        "user": os.getenv("DB_USER"),
        "password": os.getenv("DB_PASSWORD"),
        "database": os.getenv("DB_NAME")
    }

    if request.method == "POST":
        # Ambil data dari formulir
        new_config = {
            "cdn_host": request.form["cdn_host"],
            "cdn_user": request.form["cdn_user"],
            "cdn_password": request.form["cdn_password"],
            "host": request.form["host"],
            "port": request.form["port"],
            "user": request.form["user"],
            "password": request.form["password"],
            "database": request.form["database"],
        }

        # Update file .env dengan konfigurasi baru menggunakan python-dotenv
        set_key(db_file, "CDN_HOST", new_config["cdn_host"])
        set_key(db_file, "CDN_USER", new_config["cdn_user"])
        set_key(db_file, "CDN_PASSWORD", new_config["cdn_password"])
        set_key(db_file, "DB_HOST", new_config["host"])
        set_key(db_file, "DB_PORT", new_config["port"])
        set_key(db_file, "DB_USER", new_config["user"])
        set_key(db_file, "DB_PASSWORD", new_config["password"])
        set_key(db_file, "DB_NAME", new_config["database"])

        # Muat ulang file .env setelah diperbarui
        load_dotenv()
        
        # Tampilkan pesan sukses
        return render_template("db_config/form.html", config=new_config, success=True)

    # Tampilkan formulir dengan nilai konfigurasi saat ini
    return render_template("db_config/form.html", config=current_config)

@db_bp.route('/test-connection', methods=['POST'])
def test_connection():
    cdn_host = request.form.get('cdn_host')
    cdn_user = request.form.get('cdn_user')
    cdn_password = request.form.get('cdn_password')
    host = request.form.get('host')
    port = request.form.get('port')
    user = request.form.get('user')
    password = urllib.parse.quote_plus(request.form.get('password'))
    database = request.form.get('database')

    # Membuat URL koneksi dengan SQLAlchemy
    connection_string = f"mysql+mysqlconnector://{user}:{password}@{host}:{port}/{database}"

    # Path yang akan diperiksa
    network_path = rf'\\{cdn_host}\uploads$'

    response = {}

    try:
        # Membuat engine SQLAlchemy
        engine = create_engine(connection_string)

        # Menghubungkan dan menguji koneksi database
        with engine.connect() as connection:
            response['database_connection'] = {
                'success': True,
                'message': "Connection to database successful!"
            }
    except OperationalError as e:
        response['database_connection'] = {
            'success': False,
            'error': str(e)
        }

    # Melakukan login ke share network dan mengecek status koneksi
    command = f'net use {network_path} /user:{cdn_user} {cdn_password}'
    process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
    stdout, stderr = process.communicate()

    if process.returncode == 0:  # Berhasil terhubung
        # Mengecek akses ke path
        if os.path.exists(network_path):
            response['path_access'] = {
                'success': True,
                'message': f"Path '{network_path}' is accessible."
            }
        else:
            response['path_access'] = {
                'success': False,
                'message': f"Path '{network_path}' is not accessible or does not exist."
            }

        # Menghapus koneksi setelah selesai
        os.system(f'net use {network_path} /delete')
    else:  # Jika koneksi gagal
        response['path_access'] = {
            'success': False,
            'message': f"Invalid credentials or unable to access the path '{network_path}'."
        }

    # Mengembalikan respon JSON gabungan
    return jsonify(response)


