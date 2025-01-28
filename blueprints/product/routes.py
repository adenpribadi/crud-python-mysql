from flask import render_template, request, redirect, url_for, flash, session
from . import product_bp

from sqlalchemy.orm import joinedload
from models import get_session
from models.product_model import Product
# Tambahkan model-model yang diperlukan

from .forms import ProductForm

@product_bp.route('/products')
def lists():
    db_session = get_session()
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))
    try:
        products = db_session.query(Product).options(
            # Tambahkan eager loading jika diperlukan
        ).all()

    finally:
        db_session.close()

    return render_template('products/index.html', products=products)

@product_bp.route('/product/new', methods=['GET', 'POST'])
def new():
    form = ProductForm()
    db_session = get_session()
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))

    # Ambil data tambahan jika diperlukan

    if form.validate_on_submit():
        # Menambahkan product baru
        product = Product(
            # Ambil data dari form
            name = form.name.data,
            internal_reference = form.internal_reference.data,
            status = form.status.data,
            created_by=session['user_id'],
            updated_by=None
        )
        db_session.add(product)
        db_session.commit()
        db_session.close()
        flash('Product created successfully!', 'success')
        return redirect(url_for('product.lists'))
    db_session.close()
    return render_template('products/new.html', form=form)

@product_bp.route('/product/<int:id>/edit', methods=['GET', 'POST'])
def edit(id):
    db_session = get_session()
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))
    try:
        product = db_session.query(Product).get(id)
        if not product:
            flash('Product not found!', 'danger')
            return redirect(url_for('product.lists'))

        form = ProductForm(obj=product)

        if form.validate_on_submit():
            # Update data
            product.name = form.name.data
            product.internal_reference = form.internal_reference.data
            product.status = form.status.data
            Product.updated_by = session['user_id']

            db_session.commit()
            flash('Product updated successfully!', 'success')
            return redirect(url_for('product.lists'))

        # Debug jika validasi form gagal
        if not form.validate_on_submit():
            flash(form.errors, 'danger')

        return render_template('products/edit.html', form=form, product=product)

    except Exception as e:
        db_session.rollback()
        flash('An error occurred while editing Product.', 'danger')
        print("Error:", e)
        return redirect(url_for('product.lists'))
    finally:
        db_session.close()

@product_bp.route('/product/<int:id>')
def show(id):
    db_session = get_session()
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))
    product = db_session.query(Product).get(id)

    db_session.close()
    if not product:
        flash('Product not found!', 'danger')
        return redirect(url_for('product.lists'))
    return render_template('products/show.html', product=product)
