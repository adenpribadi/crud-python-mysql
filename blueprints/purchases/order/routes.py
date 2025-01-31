from flask import render_template, request, redirect, url_for, flash, session
from datetime import datetime, timedelta
from . import purchases_order_bp
from sqlalchemy.orm import joinedload
from sqlalchemy import case
from models import get_session
from models.purchases.order_model import PurchaseOrder
from models.purchases.order_item_model import PurchaseOrderItem
from models.purchases.request_model import PurchaseRequest
from models.purchases.request_item_model import PurchaseRequestItem

from models.department_model import Department
from models.employee_section_model import EmployeeSection
from models.material_model import Material
from models.general_model import General
from .forms import PurchaseOrderForm

@purchases_order_bp.route('/purchases/orders', methods=['GET'])
def lists():
    # Gunakan db_session untuk query dengan eager loading
    db_session = get_session()
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))

    try:
        # Default: hitung tanggal awal (awal bulan) dan tanggal akhir (akhir bulan)
        today = datetime.today()
        start_date = today.replace(day=1)
        next_month = today.replace(day=28) + timedelta(days=4)
        end_date = next_month - timedelta(days=next_month.day)

        # Ambil tanggal dari query string jika tersedia
        start_date_str = request.args.get('start_date', start_date.strftime('%Y-%m-%d'))
        end_date_str = request.args.get('end_date', end_date.strftime('%Y-%m-%d'))

        # Konversi string ke objek tanggal
        start_date = datetime.strptime(start_date_str, '%Y-%m-%d')
        end_date = datetime.strptime(end_date_str, '%Y-%m-%d')

        # Ambil kind dari query string
        kind = request.args.get('q')

        # Urutan status yang diinginkan
        status_order = ['new', 'canceled1', 'canceled2', 'canceled3', 'approved1', 'approved2', 'approved3', 'deleted', 'void']

        # Ambil nilai 'view' dari query string
        view_option = request.args.get('view', 'header')  # Default ke 'header' jika tidak ada parameter

        # Query purchase orders berdasarkan 'view' (header atau detail)
        if view_option == 'detail':
            # Ambil PurchaseOrderItem dan pastikan kita akses reference_date dari PurchaseOrder yang terkait
            purchase_orders = db_session.query(PurchaseOrderItem).options(
                joinedload(PurchaseOrderItem.purchase_order),
                joinedload(PurchaseOrderItem.material)
            ).join(PurchaseOrder).filter(
                PurchaseOrder.reference_date >= start_date,
                PurchaseOrder.reference_date <= end_date,
                PurchaseOrder.kind == kind
            ).all()
        else:
            # Buat ekspresi CASE untuk mengatur urutan status
            case_order = case(
                *[(PurchaseOrder.status == status, index) for index, status in enumerate(status_order)],
                else_=len(status_order)  # Untuk status yang tidak ada dalam daftar
            )

            # Query purchase orders dengan eager loading dan filter tanggal
            purchase_orders = db_session.query(PurchaseOrder).options(
                joinedload(PurchaseOrder.department),  # eager load department
                joinedload(PurchaseOrder.employee_section),  # eager load employee_section
            ).filter(
                PurchaseOrder.reference_date >= start_date,  # Filter berdasarkan tanggal awal
                PurchaseOrder.reference_date <= end_date,    # Filter berdasarkan tanggal akhir
                PurchaseOrder.kind == kind   # Filter berdasarkan kind
            ).order_by(
                case_order,  # Urutkan berdasarkan status
                PurchaseOrder.reference_date.desc(),
                PurchaseOrder.reference_number.desc()
            ).all()

    finally:
        db_session.close()

    # Kirim data ke template
    return render_template('purchases/orders/index.html', purchase_orders=purchase_orders, start_date=start_date_str, end_date=end_date_str, view_option=view_option)

@purchases_order_bp.route('/purchases/orders/new', methods=['GET', 'POST'])
def new():
    db_session = get_session()
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))

    # Ambil daftar department, status, dan user
    departments = db_session.query(Department).all()
    employee_sections = db_session.query(EmployeeSection).all()
    materials = db_session.query(Material).options(joinedload(Material.unit)).all()
    generals = db_session.query(General).options(joinedload(General.unit)).all()

    # Bind data ke form
    form = PurchaseOrderForm()
    # Proses ketika form dikirim
    if form.validate_on_submit():
        # Membuat PurchaseOrder baru
        purchase_order = PurchaseOrder(
            kind=form.kind.data,
            reference_date=form.reference_date.data,
            department_id=form.department.data,
            employee_section_id=form.employee_section.data, 
            outstanding=0,
            status='new',
            created_by=session['user_id'],
            updated_by=None
        )
        # Menyimpan PurchaseOrder ke database
        db_session.add(purchase_order)
        db_session.commit()  # Commit pertama agar purchase_order disimpan dan id-nya ter-set

        # Mengupdate atau menambah PurchaseOrderItem jika ada perubahan
        for item_data in form.items.entries:  # Misalnya items adalah field di form

            item_id = item_data.record_id.data
            item_purchase_request_item_id = item_data.purchase_request_item_id.data
            item_material_id = item_data.material_id.data
            item_general_id = item_data.general_id.data
            item_quantity = item_data.quantity.data
            item_unit_price = item_data.unit_price.data
            item_remarks = item_data.remarks.data
            item_status = 'active'
            print("item_id: ", item_id)

            if item_id:  # Update item yang sudah ada
                item = db_session.query(PurchaseOrderItem).get(item_id)
                if item:
                    item.purchase_request_item_id = item_material_id
                    item.material_id = item_purchase_request_item_id
                    item.general_id = item_general_id
                    item.quantity = item_quantity
                    item.unit_price = item_unit_price
                    item.remarks = item_remarks
                    item.status = item_status
                    item.created_by=session['user_id']
                    item.updated_by=None
            else:  # Tambah item baru
                new_item = PurchaseOrderItem(
                    purchase_request_item_id=item_purchase_request_item_id,
                    material_id=item_material_id,
                    general_id=item_general_id,
                    quantity=item_quantity, 
                    unit_price=item_unit_price, 
                    remarks=item_remarks,
                    status=item_status,
                    purchase_order_id=purchase_order.id,
                    created_by=session['user_id'],
                    updated_by=None
                )
                db_session.add(new_item)

        # Commit perubahan ke database
        db_session.commit()
        print("reference_number: ", purchase_order.reference_number)
        flash('Purchase order save successfully!', 'success')
        return redirect(url_for('purchases_order.lists', q=purchase_order.kind))
    
    # Debug jika validasi form gagal
    if not form.validate_on_submit():
        flash(form.errors, 'danger')
        print("form.errors: ", form.errors)

    return render_template(
        'purchases/orders/new.html',
        form=form,
        departments=departments,
        employee_sections=[{
            'id': section.id,
            'name': section.name,
            'department_id': section.department_id
        } for section in employee_sections],
        generals=[{
            'id': general.id,
            'name': general.name,
            'unit': general.unit.name if general.unit else ''
        } for general in generals],
        materials=[{
            'id': material.id,
            'name': material.name,
            'unit': material.unit.name if material.unit else ''
        } for material in materials]  # Convert material data to JSON format
    )


@purchases_order_bp.route('/purchases/orders/<int:id>/edit', methods=['GET', 'POST'])
def edit(id):
    # Mengambil db_session
    db_session = get_session()
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))
    try:
        # Ambil data PurchaseOrder berdasarkan ID
        purchase_order = db_session.query(PurchaseOrder).get(id)
        if not purchase_order:
            flash('Purchase order not found!', 'danger')
            return redirect(url_for('purchases_order_bp.lists'))
        
        # Ambil department_id dari purchase_order
        department_id = purchase_order.department_id
        employee_section_id = purchase_order.employee_section_id
        request_kind = purchase_order.kind

        # Ambil daftar departemen, supplier, dan item terkait
        departments = db_session.query(Department).all()
        employee_sections = db_session.query(EmployeeSection).filter_by(department_id=department_id).all()
        purchase_order_items = db_session.query(PurchaseOrderItem).filter_by(purchase_order_id=id, status='active').all()
        
        # Query untuk mengambil data PurchaseOrderItem dan relasinya dengan PurchaseRequestItem
        po_items = db_session.query(PurchaseOrderItem, PurchaseRequestItem.purchase_request_id).\
            join(PurchaseRequestItem, PurchaseRequestItem.id == PurchaseOrderItem.purchase_request_item_id).\
            filter(PurchaseOrderItem.purchase_order_id == id, PurchaseOrderItem.status == 'active').all()

        purchase_request_ids = [purchase_request_id for item, purchase_request_id in po_items]

        print("purchase_request_ids: ", purchase_request_ids)
        purchase_requests = db_session.query(PurchaseRequest).filter(
            PurchaseRequest.request_kind == request_kind,
            (PurchaseRequest.outstanding > 0) | (PurchaseRequest.id.in_(purchase_request_ids))
        ).all()

        materials = db_session.query(Material).options(joinedload(Material.unit)).all()
        generals = db_session.query(General).options(joinedload(General.unit)).all()

        # Bind data ke form
        form = PurchaseOrderForm(obj=purchase_order)
        # for item in purchase_order_items:
        #     item_form = PurchaseOrderItemForm(obj=item)
        #     form.items.append_entry(item_form)

        print("form: ", form.data)

        # Proses ketika form dikirim
        if form.validate_on_submit():

            # Update data PurchaseOrder
            purchase_order.remarks = form.remarks.data
            purchase_order.reference_date = form.reference_date.data
            
            db_session.add(purchase_order)

            # Mengupdate atau menambah PurchaseOrderItem jika ada perubahan
            for item_data in form.items.entries:  # Misalnya items adalah field di form

                item_id = item_data.record_id.data
                item_purchase_request_item_id = item_data.purchase_request_item_id.data
                item_material_id = item_data.material_id.data
                item_general_id = item_data.general_id.data
                item_quantity = item_data.quantity.data
                item_unit_price = item_data.unit_price.data
                item_remarks = item_data.remarks.data
                item_status = item_data.status.data
                print("item_id: ", item_id)

                if item_id:  # Update item yang sudah ada
                    item = db_session.query(PurchaseOrderItem).get(item_id)
                    if item:
                        item.purchase_request_item_id = item_purchase_request_item_id
                        item.material_id = item_material_id
                        item.general_id = item_general_id
                        item.quantity = item_quantity
                        item.unit_price = item_unit_price
                        item.remarks = item_remarks
                        item.status = item_status
                        item.updated_by=session['user_id']
                else:  # Tambah item baru
                    new_item = PurchaseOrderItem(
                        purchase_request_item_id=item_purchase_request_item_id,
                        material_id=item_material_id,
                        general_id=item_general_id,
                        quantity=item_quantity, 
                        unit_price=item_unit_price, 
                        remarks=item_remarks,
                        status=item_status,
                        purchase_order_id=purchase_order.id,
                        created_by=session['user_id'],
                        updated_by=None
                    )
                    db_session.add(new_item)

            # Commit perubahan
            db_session.commit()
            flash('Purchase order updated successfully!', 'success')
            return redirect(url_for('purchases_order.show', id=purchase_order.id, q=purchase_order.kind))
        
        # Debug jika validasi form gagal
        if not form.validate_on_submit():
            flash(form.errors, 'danger')
            print(" ---------------------- > Form.errors: ", form.errors)
        
        # Render template edit
        return render_template(
            'purchases/orders/edit.html',
            form=form,
            purchase_order=purchase_order,
            purchase_requests=purchase_requests,
            departments=departments,
            employee_sections=[{
                'id': section.id,
                'name': section.name,
                'department_id': section.department_id
            } for section in employee_sections],
            generals=[{
                'id': general.id,
                'name': general.name,
                'unit': general.unit.name if general.unit else ''
            } for general in generals],
            materials=[{
                'id': material.id,
                'name': material.name,
                'unit': material.unit.name if material.unit else ''
            } for material in materials],  # Convert material data to JSON format,
            purchase_order_items=purchase_order_items  # Kirimkan item terkait ke template
        )
    except Exception as e:
        print(" --------------------- > Error:", e)
        db_session.rollback()  # Rollback jika ada error
        flash('An error occurred while editing purchase order.', 'danger')
        return redirect(url_for('purchases_order.show', id=purchase_order.id, q=purchase_order.kind))
    finally:
        db_session.close()  # Selalu tutup db_session

@purchases_order_bp.route('/purchases/orders/<int:id>')
def show(id):
    db_session = get_session()
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))
    
    try:
        # Query untuk mengambil detail PurchaseOrder berdasarkan ID
        purchase_order = db_session.query(PurchaseOrder).get(id)

        # Jika PurchaseOrder tidak ditemukan
        if not purchase_order:
            flash('Purchase order not found!', 'danger')
            return redirect(url_for('purchases_order_bp.lists', q=purchase_order.kind))

        # Ambil department_id dari purchase_order
        department_id = purchase_order.department_id

        # Query untuk daftar departemen dan employee_sections
        departments = db_session.query(Department).all()
        employee_sections = db_session.query(EmployeeSection).filter_by(department_id=department_id).all()
        materials = db_session.query(Material).options(joinedload(Material.unit)).all()
        generals = db_session.query(General).options(joinedload(General.unit)).all()

        # Ambil semua item terkait dengan PurchaseOrder
        purchase_order_items = db_session.query(PurchaseOrderItem).options(
            joinedload(PurchaseOrderItem.material).joinedload(Material.unit),  # eager load material and unit
            joinedload(PurchaseOrderItem.general).joinedload(General.unit),  # eager load general and unit
            joinedload(PurchaseOrderItem.purchase_request_item).joinedload(PurchaseRequestItem.purchase_request),
        ).filter_by(purchase_order_id=id, status='active').all()

    finally:
        db_session.close()

    # Render template dengan data yang diambil
    return render_template(
        'purchases/orders/show.html',
        purchase_order=purchase_order,
        disabled='true',
        departments=departments,
        employee_sections=[{
            'id': section.id,
            'name': section.name,
            'department_id': section.department_id
        } for section in employee_sections],
        generals=[{
            'id': general.id,
            'name': general.name,
            'unit': general.unit.name if general.unit else ''
        } for general in generals],
        materials=[{
            'id': material.id,
            'name': material.name,
            'unit': material.unit.name if material.unit else ''
        } for material in materials],  # Convert material data to JSON format,
        purchase_order_items=purchase_order_items,  # Kirimkan item terkait ke template
    )