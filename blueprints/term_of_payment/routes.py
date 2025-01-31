from flask import render_template, request, redirect, url_for, flash, session
from . import term_of_payment_bp

from sqlalchemy.orm import joinedload
from models import get_session
from models.term_of_payment_model import TermOfPayment
# Tambahkan model-model yang diperlukan

from .forms import TermOfPaymentForm

@term_of_payment_bp.route('/term_of_payments')
def lists():
    db_session = get_session()
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))
    try:
        term_of_payments = db_session.query(TermOfPayment).options(
            # Tambahkan eager loading jika diperlukan
        ).all()

    finally:
        db_session.close()

    return render_template('term_of_payments/index.html', term_of_payments=term_of_payments)

@term_of_payment_bp.route('/term_of_payment/new', methods=['GET', 'POST'])
def new():
    form = TermOfPaymentForm()
    db_session = get_session()
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))

    # Ambil data tambahan jika diperlukan

    if form.validate_on_submit():
        # Menambahkan term_of_payment baru
        term_of_payment = TermOfPayment(
            # Ambil data dari form
            name = form.name.data,
            code = form.code.data,
            created_by=session['user_id'],
            updated_by=None
        )
        db_session.add(term_of_payment)
        db_session.commit()
        db_session.close()
        flash('TermOfPayment created successfully!', 'success')
        return redirect(url_for('term_of_payment.lists'))
    db_session.close()
    return render_template('term_of_payments/new.html', form=form)

@term_of_payment_bp.route('/term_of_payment/<int:id>/edit', methods=['GET', 'POST'])
def edit(id):
    db_session = get_session()
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))
    try:
        term_of_payment = db_session.query(TermOfPayment).get(id)
        if not term_of_payment:
            flash('TermOfPayment not found!', 'danger')
            return redirect(url_for('term_of_payment.lists'))

        form = TermOfPaymentForm(obj=term_of_payment)

        if form.validate_on_submit():
            # Update data
            term_of_payment.name = form.name.data
            term_of_payment.code = form.code.data
            TermOfPayment.updated_by = session['user_id']

            db_session.commit()
            flash('TermOfPayment updated successfully!', 'success')
            return redirect(url_for('term_of_payment.lists'))

        # Debug jika validasi form gagal
        if not form.validate_on_submit():
            flash(form.errors, 'danger')

        return render_template('term_of_payments/edit.html', form=form, term_of_payment=term_of_payment)

    except Exception as e:
        db_session.rollback()
        flash('An error occurred while editing TermOfPayment.', 'danger')
        print("Error:", e)
        return redirect(url_for('term_of_payment.lists'))
    finally:
        db_session.close()

@term_of_payment_bp.route('/term_of_payment/<int:id>')
def show(id):
    db_session = get_session()
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))
    term_of_payment = db_session.query(TermOfPayment).get(id)

    db_session.close()
    if not term_of_payment:
        flash('TermOfPayment not found!', 'danger')
        return redirect(url_for('term_of_payment.lists'))
    return render_template('term_of_payments/show.html', term_of_payment=term_of_payment)
