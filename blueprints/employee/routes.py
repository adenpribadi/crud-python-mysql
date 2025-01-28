import os
import subprocess
from flask import render_template, request, redirect, url_for, flash, session, send_from_directory, jsonify
from werkzeug.utils import secure_filename
from dotenv import load_dotenv
from . import employee_bp

from sqlalchemy.orm import joinedload
from models import get_session
from models.employee_model import Employee
from models.department_model import Department
from models.position_model import Position
from models.work_status_model import WorkStatus

from .forms import EmployeeForm
# Memuat variabel dari file .env
load_dotenv()

# Ambil nilai CDN_HOST dari file .env
CDN_HOST = os.getenv('CDN_HOST')
CDN_USER = os.getenv('CDN_USER')
CDN_PASSWORD = os.getenv('CDN_PASSWORD')

@employee_bp.route('/employees')
def lists():
    # Gunakan db_session untuk query dengan eager loading
    db_session = get_session()
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))
    try:
        employees = db_session.query(Employee).options(
            joinedload(Employee.department),  # eager load department
            joinedload(Employee.position),  # eager load department
            joinedload(Employee.work_status)      # eager load work_status
        ).all()

    finally:
        db_session.close()

    # Kirim data ke template
    return render_template('employees/index.html', employees=employees)

@employee_bp.route('/employee/new', methods=['GET', 'POST'])
def new():
    form = EmployeeForm()
    db_session = get_session()
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))
    
    # Ambil daftar posisi, departemen, dan status kerja
    positions = db_session.query(Position).all()
    departments = db_session.query(Department).all()
    work_statuses = db_session.query(WorkStatus).all()

    if form.validate_on_submit():
        # Menambahkan employee baru
        employee = Employee(
            nik=form.nik.data,
            name=form.name.data,
            gender=form.gender.data,
            born_date=form.born_date.data,
            born_place=form.born_place.data,
            department_id=form.department.data,
            position_id=form.position.data,
            work_status_id=form.work_status.data,
            email_address=form.email_address.data,
            phone_number=form.phone_number.data,
            created_by=session['user_id'],
            updated_by=None
        )
        db_session.add(employee)
        db_session.commit()

        file = request.files.get('image')  # Ambil file dari form
        filename = ''
        
        if file and allowed_file(file.filename):
            # Ambil ekstensi file
            file_extension = os.path.splitext(file.filename)[1]
            
            # Gunakan ID employee untuk nama file unik
            filename = f"employee_{employee.id}{file_extension}"

            # Tentukan path penyimpanan file
            # upload_directory = os.path.join(f'\\\\{CDN_HOST}\\uploads$\\employee\\image')

            # Tentukan path penyimpanan file
            network_path = f"\\\\{CDN_HOST}\\uploads$\\employee\\image"

            # Melakukan login ke share network
            os.system(f'net use {network_path} /user:{CDN_USER} {CDN_PASSWORD}')
            os.makedirs(network_path, exist_ok=True)  # Buat folder jika belum ada

            filepath = os.path.join(network_path, filename)
            file.save(filepath)  # Simpan file ke path yang ditentukan
            # os.system(f'net use {network_path} /delete')

            # Perbarui employee dengan nama file gambar
            employee.image = filename
            db_session.commit()  # Commit perubahan untuk update image

        db_session.close()
        flash('Employee created successfully!', 'success')
        return redirect(url_for('employee.lists'))
    db_session.close()

    # Debug jika validasi form gagal
    if not form.validate_on_submit():
        flash(form.errors, 'danger')

    return render_template('employees/new.html', form=form, positions=positions, departments=departments, work_statuses=work_statuses)

@employee_bp.route('/employee/<int:id>/edit', methods=['GET', 'POST'])
def edit(id):
    # Mengambil db_session
    db_session = get_session()
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))
    try:
        # Ambil data employee berdasarkan ID
        employee = db_session.query(Employee).get(id)
        if not employee:
            flash('Employee not found!', 'danger')
            return redirect(url_for('employee.lists'))
        
        # Ambil daftar posisi, departemen, dan status kerja
        positions = db_session.query(Position).all()
        departments = db_session.query(Department).all()
        work_statuses = db_session.query(WorkStatus).all()

        # Bind data ke form
        form = EmployeeForm(obj=employee)

        # Proses ketika form dikirim
        if form.validate_on_submit():
            # Proses penghapusan gambar jika checkbox dicentang
            if 'remove_image' in request.form:
                if employee.image:
                    # Hapus file fisik jika ada
                    # image_path = os.path.join(os.getcwd(), 'uploads', 'employee', 'image', employee.image)
                    # image_path = os.path.join(f'\\\\{CDN_HOST}\\uploads$\\employee\\image', employee.image)

                    # Menentukan kredensial
                    network_path = f"\\\\{CDN_HOST}\\uploads$\\employee\\image"

                    # Melakukan login ke share network
                    os.system(f'net use {network_path} /user:{CDN_USER} {CDN_PASSWORD}')
                    
                    # Cek apakah bisa mengakses file setelah login
                    image_path = os.path.join(network_path, 'employee_5.jpeg')

                    if os.path.exists(image_path):
                        os.remove(image_path)
                    employee.image = None  # Hapus referensi gambar dari database
                    # os.system(f'net use {network_path} /delete')

            file = request.files.get('image')  # Ambil file dari form
            
            if file and allowed_file(file.filename):
                # Ambil ekstensi file
                file_extension = os.path.splitext(file.filename)[1]  # Mendapatkan .jpg, .png, dll.
                
                # Tentukan nama file unik dengan ID employee
                filename = f"employee_{id}{file_extension}"
                
                # Tentukan path penyimpanan file
                network_path = f"\\\\{CDN_HOST}\\uploads$\\employee\\image"

                # Melakukan login ke share network
                os.system(f'net use {network_path} /user:{CDN_USER} {CDN_PASSWORD}')
                # upload_directory = os.path.join(f'\\\\{CDN_HOST}\\uploads$\\employee\\image')
                os.makedirs(network_path, exist_ok=True)  # Buat folder jika belum ada

                filepath = os.path.join(network_path, filename)
                file.save(filepath)  # Simpan file ke path yang ditentukan
                # os.system(f'net use {network_path} /delete')

                employee.image = filename

            # Update data employee
            employee.nik = form.nik.data
            employee.name = form.name.data
            employee.gender = form.gender.data
            employee.born_date = form.born_date.data
            employee.born_place = form.born_place.data
            employee.join_date = form.join_date.data
            employee.department_id = form.department.data
            employee.position_id = form.position.data
            employee.work_status_id = form.work_status.data
            employee.phone_number = form.phone_number.data
            employee.email_address = form.email_address.data
            employee.updated_by = session['user_id']
            
            # Commit perubahan
            db_session.commit()
            flash('Employee updated successfully!', 'success')
            return redirect(url_for('employee.lists'))
        
        # Debug jika validasi form gagal
        if not form.validate_on_submit():
            flash(form.errors, 'danger')
        
        # Render template edit
        return render_template(
            'employees/edit.html',
            form=form,
            employee=employee,
            positions=positions,
            departments=departments,
            work_statuses=work_statuses
        )
    except Exception as e:
        db_session.rollback()  # Rollback jika ada error
        flash('An error occurred while editing employee.', 'danger')
        print("Error:", e)
        return redirect(url_for('employee.lists'))
    finally:
        db_session.close()  # Selalu tutup db_session


@employee_bp.route('/employee/<int:id>')
def show(id):
    db_session = get_session()
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))
    employee = db_session.query(Employee).get(id)

    # Ambil daftar posisi, departemen, dan status kerja
    positions = db_session.query(Position).all()
    departments = db_session.query(Department).all()
    work_statuses = db_session.query(WorkStatus).all()

    db_session.close()
    if not employee:
        flash('Employee not found!', 'danger')
        return redirect(url_for('employee.employees'))
    return render_template('employees/show.html', employee=employee, disabled='true', positions=positions, departments=departments, work_statuses=work_statuses)

@employee_bp.route('/employee/uploads/<filename>')
def uploaded_file(filename):
    load_dotenv()

    CDN_HOST = os.getenv('CDN_HOST')
    CDN_USER = os.getenv('CDN_USER')
    CDN_PASSWORD = os.getenv('CDN_PASSWORD')

    # Tentukan path menggunakan CDN_HOST untuk file yang di-upload
    UPLOAD_FOLDER = os.path.join(f'\\\\{CDN_HOST}\\uploads$\\employee\\image')

    # Melakukan login ke share network dan mengecek status koneksi
    network_path = f'\\\\{CDN_HOST}\\uploads$'
    command = f'net use {network_path} /user:{CDN_USER} {CDN_PASSWORD}'
    process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
    stdout, stderr = process.communicate()

    if process.returncode == 0:  # Berhasil terhubung
        # Mengecek apakah file tersedia
        if os.path.exists(os.path.join(UPLOAD_FOLDER, filename)):
            # Menghapus koneksi setelah selesai
            os.system(f'net use {network_path} /delete')
            # Menggunakan send_from_directory untuk mengirimkan file dari shared folder
            return send_from_directory(UPLOAD_FOLDER, filename)
        else:
            # File tidak ditemukan
            os.system(f'net use {network_path} /delete')
            return jsonify(success=False, message=f"File '{filename}' not found."), 404
    else:  # Jika koneksi gagal
        return jsonify(success=False, message="Invalid credentials or unable to access the network path."), 403

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'pdf', 'docx'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS
