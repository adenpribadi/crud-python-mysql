from flask import render_template, request, redirect, url_for, flash, session
from . import auth_bp
from models.user_model import User
from models import get_session
from .forms import LoginForm, RegisterForm

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    print("login")
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        try:
            session_db = get_session()
            user = session_db.query(User).filter_by(username=username).first()
            session_db.close()

            if user:
                print(f"User found: {user.username}")
                print(f"Password Hash: {user.encrypted_password}")
                print(f"Password: {password}")
                print(f"Check: {user.check_password(password)}")

                # Verifikasi password menggunakan bcrypt
                if user.check_password(password):
                    session['user_id'] = user.id
                    flash('Login successful!', 'success')
                    return redirect(url_for('index'))
                else:
                    flash('Invalid username or password!', 'danger')
            else:
                flash('Invalid username or password!', 'danger')
        
        except Exception as e:
            print(f"Database connection error: {str(e)}")
            flash('There was an issue with the database connection. Please try again later.', 'danger')

    return render_template('auth/login.html')


@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data

        try:
            session_db = get_session()
            user_exists = session_db.query(User).filter_by(username=username).first()

            if user_exists:
                flash('Username already exists!', 'danger')
            else:
                new_user = User(username=username)
                new_user.set_password(password)
                session_db.add(new_user)
                session_db.commit()
                flash('Registration successful!', 'success')
                return redirect(url_for('auth.login'))

            session_db.close()

        except Exception as e:
            print(f"Database connection error: {str(e)}")
            flash('There was an issue with the database connection. Please try again later.', 'danger')

    return render_template('auth/register.html', form=form)

@auth_bp.route('/logout')
def logout():
    session.clear()
    flash('Logged out successfully!', 'success')
    return redirect(url_for('auth.login'))
