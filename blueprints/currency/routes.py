from flask import render_template, request, redirect, url_for, flash, session
from . import currency_bp

from sqlalchemy.orm import joinedload
from models import get_session
from models.currency_model import Currency
# Tambahkan model-model yang diperlukan

from .forms import CurrencyForm

@currency_bp.route('/currencies')
def lists():
    db_session = get_session()
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))
    try:
        currencies = db_session.query(Currency).options(
            # Tambahkan eager loading jika diperlukan
        ).all()

    finally:
        db_session.close()

    return render_template('currencies/index.html', currencies=currencies)

@currency_bp.route('/currency/new', methods=['GET', 'POST'])
def new():
    form = CurrencyForm()
    db_session = get_session()
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))

    # Ambil data tambahan jika diperlukan

    if form.validate_on_submit():
        # Menambahkan currency baru
        currency = Currency(
            # Ambil data dari form
            name = form.name.data,
            symbol = form.symbol.data,
            precision_digit = form.precision_digit.data,
            created_by=session['user_id'],
            updated_by=None
        )
        db_session.add(currency)
        db_session.commit()
        db_session.close()
        flash('Currency created successfully!', 'success')
        return redirect(url_for('currency.lists'))
    db_session.close()
    return render_template('currencies/new.html', form=form)

@currency_bp.route('/currency/<int:id>/edit', methods=['GET', 'POST'])
def edit(id):
    db_session = get_session()
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))
    try:
        currency = db_session.query(Currency).get(id)
        if not currency:
            flash('Currency not found!', 'danger')
            return redirect(url_for('currency.lists'))

        form = CurrencyForm(obj=currency)

        if form.validate_on_submit():
            # Update data
            currency.name = form.name.data
            currency.symbol = form.symbol.data
            currency.precision_digit = form.precision_digit.data
            Currency.updated_by = session['user_id']

            db_session.commit()
            flash('Currency updated successfully!', 'success')
            return redirect(url_for('currency.lists'))

        # Debug jika validasi form gagal
        if not form.validate_on_submit():
            flash(form.errors, 'danger')

        return render_template('currencies/edit.html', form=form, currency=currency)

    except Exception as e:
        db_session.rollback()
        flash('An error occurred while editing Currency.', 'danger')
        print("Error:", e)
        return redirect(url_for('currency.lists'))
    finally:
        db_session.close()

@currency_bp.route('/currency/<int:id>')
def show(id):
    db_session = get_session()
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))
    currency = db_session.query(Currency).get(id)

    db_session.close()
    if not currency:
        flash('Currency not found!', 'danger')
        return redirect(url_for('currency.lists'))
    return render_template('currencies/show.html', currency=currency)
