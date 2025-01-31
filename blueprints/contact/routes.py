from flask import render_template, request, redirect, url_for, flash, session
from . import contact_bp

from sqlalchemy.orm import joinedload
from models import get_session
from models.contact_model import Contact
# Tambahkan model-model yang diperlukan

from .forms import ContactForm

@contact_bp.route('/contacts')
def lists():
    db_session = get_session()
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))
    try:
        contacts = db_session.query(Contact).options(
            # Tambahkan eager loading jika diperlukan
        ).all()

    finally:
        db_session.close()

    return render_template('contacts/index.html', contacts=contacts)

@contact_bp.route('/contact/new', methods=['GET', 'POST'])
def new():
    form = ContactForm()
    db_session = get_session()
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))

    # Ambil data tambahan jika diperlukan

    if form.validate_on_submit():
        # Menambahkan contact baru
        contact = Contact(
            # Ambil data dari form
            name = form.name.data,
            status = form.status.data,
            created_by=session['user_id'],
            updated_by=None
        )
        db_session.add(contact)
        db_session.commit()
        db_session.close()
        flash('Contact created successfully!', 'success')
        return redirect(url_for('contact.lists'))
    db_session.close()
    return render_template('contacts/new.html', form=form)

@contact_bp.route('/contact/<int:id>/edit', methods=['GET', 'POST'])
def edit(id):
    db_session = get_session()
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))
    try:
        contact = db_session.query(Contact).get(id)
        if not contact:
            flash('Contact not found!', 'danger')
            return redirect(url_for('contact.lists'))

        form = ContactForm(obj=contact)

        if form.validate_on_submit():
            # Update data
            contact.name = form.name.data
            contact.status = form.status.data
            Contact.updated_by = session['user_id']

            db_session.commit()
            flash('Contact updated successfully!', 'success')
            return redirect(url_for('contact.lists'))

        # Debug jika validasi form gagal
        if not form.validate_on_submit():
            flash(form.errors, 'danger')

        return render_template('contacts/edit.html', form=form, contact=contact)

    except Exception as e:
        db_session.rollback()
        flash('An error occurred while editing Contact.', 'danger')
        print("Error:", e)
        return redirect(url_for('contact.lists'))
    finally:
        db_session.close()

@contact_bp.route('/contact/<int:id>')
def show(id):
    db_session = get_session()
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))
    contact = db_session.query(Contact).get(id)

    db_session.close()
    if not contact:
        flash('Contact not found!', 'danger')
        return redirect(url_for('contact.lists'))
    return render_template('contacts/show.html', contact=contact)
