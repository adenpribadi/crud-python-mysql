from flask import render_template, request, redirect, url_for, flash, session
from . import tax_bp

from sqlalchemy.orm import joinedload
from models import get_session
from models.tax_model import Tax
# Tambahkan model-model yang diperlukan

from .forms import TaxForm

@tax_bp.route('/taxes')
def lists():
    db_session = get_session()
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))
    try:
        taxes = db_session.query(Tax).options(
            # Tambahkan eager loading jika diperlukan
        ).all()

    finally:
        db_session.close()

    return render_template('taxes/index.html', taxes=taxes)

@tax_bp.route('/tax/new', methods=['GET', 'POST'])
def new():
    form = TaxForm()
    db_session = get_session()
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))

    # Ambil data tambahan jika diperlukan

    if form.validate_on_submit():
        # Menambahkan tax baru
        tax = Tax(
            # Ambil data dari form
            name = form.name.data,
            value = form.value.data,
            status = form.status.data,
            created_by=session['user_id'],
            updated_by=None
        )
        db_session.add(tax)
        db_session.commit()
        db_session.close()
        flash('Tax created successfully!', 'success')
        return redirect(url_for('tax.lists'))
    db_session.close()
    return render_template('taxes/new.html', form=form)

@tax_bp.route('/tax/<int:id>/edit', methods=['GET', 'POST'])
def edit(id):
    db_session = get_session()
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))
    try:
        tax = db_session.query(Tax).get(id)
        if not tax:
            flash('Tax not found!', 'danger')
            return redirect(url_for('tax.lists'))

        form = TaxForm(obj=tax)

        if form.validate_on_submit():
            # Update data
            tax.name = form.name.data
            tax.value = form.value.data
            tax.status = form.status.data
            Tax.updated_by = session['user_id']

            db_session.commit()
            flash('Tax updated successfully!', 'success')
            return redirect(url_for('tax.lists'))

        # Debug jika validasi form gagal
        if not form.validate_on_submit():
            flash(form.errors, 'danger')

        return render_template('taxes/edit.html', form=form, tax=tax)

    except Exception as e:
        db_session.rollback()
        flash('An error occurred while editing Tax.', 'danger')
        print("Error:", e)
        return redirect(url_for('tax.lists'))
    finally:
        db_session.close()

@tax_bp.route('/tax/<int:id>')
def show(id):
    db_session = get_session()
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))
    tax = db_session.query(Tax).get(id)

    db_session.close()
    if not tax:
        flash('Tax not found!', 'danger')
        return redirect(url_for('tax.lists'))
    return render_template('taxes/show.html', tax=tax)
