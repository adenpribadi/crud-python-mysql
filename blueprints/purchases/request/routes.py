from flask import render_template, jsonify, request, redirect, url_for, flash, session
from datetime import datetime, timedelta
from . import purchases_request_bp
from sqlalchemy.orm import joinedload
from sqlalchemy import case
from models import get_session
from models.purchases.request_model import PurchaseRequest
from models.purchases.request_item_model import PurchaseRequestItem
from models.department_model import Department
from models.employee_section_model import EmployeeSection
from models.material_model import Material
from models.general_model import General
from .forms import PurchaseRequestForm

@purchases_request_bp.route('/purchases/requests', methods=['GET'])
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

        # Ambil request_kind dari query string
        request_kind = request.args.get('q')

        # Urutan status yang diinginkan
        status_order = ['new', 'canceled1', 'canceled2', 'canceled3', 'approved1', 'approved2', 'approved3', 'deleted', 'void']

        # Ambil nilai 'view' dari query string
        view_option = request.args.get('view', 'header')  # Default ke 'header' jika tidak ada parameter

        # Query purchase requests berdasarkan 'view' (header atau detail)
        if view_option == 'detail':
            # Ambil PurchaseRequestItem dan pastikan kita akses reference_date dari PurchaseRequest yang terkait
            purchase_requests = db_session.query(PurchaseRequestItem).options(
                joinedload(PurchaseRequestItem.purchase_request),
                joinedload(PurchaseRequestItem.material)
            ).join(PurchaseRequest).filter(
                PurchaseRequest.reference_date >= start_date,
                PurchaseRequest.reference_date <= end_date,
                PurchaseRequest.request_kind == request_kind
            ).all()
        else:
            # Buat ekspresi CASE untuk mengatur urutan status
            case_order = case(
                *[(PurchaseRequest.status == status, index) for index, status in enumerate(status_order)],
                else_=len(status_order)  # Untuk status yang tidak ada dalam daftar
            )

            # Query purchase requests dengan eager loading dan filter tanggal
            purchase_requests = db_session.query(PurchaseRequest).options(
                joinedload(PurchaseRequest.department),  # eager load department
                joinedload(PurchaseRequest.employee_section),  # eager load employee_section
            ).filter(
                PurchaseRequest.reference_date >= start_date,  # Filter berdasarkan tanggal awal
                PurchaseRequest.reference_date <= end_date,    # Filter berdasarkan tanggal akhir
                PurchaseRequest.request_kind == request_kind   # Filter berdasarkan request_kind
            ).order_by(
                case_order,  # Urutkan berdasarkan status
                PurchaseRequest.reference_date.desc(),
                PurchaseRequest.reference_number.desc()
            ).all()

    finally:
        db_session.close()

    # Kirim data ke template
    return render_template('purchases/requests/index.html', purchase_requests=purchase_requests, start_date=start_date_str, end_date=end_date_str, view_option=view_option)

@purchases_request_bp.route('/purchases/requests/new', methods=['GET', 'POST'])
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
    form = PurchaseRequestForm()
    # Proses ketika form dikirim
    if form.validate_on_submit():
        # Membuat PurchaseRequest baru
        purchase_request = PurchaseRequest(
            request_kind=form.request_kind.data,
            reference_date=form.reference_date.data,
            department_id=form.department.data,
            employee_section_id=form.employee_section.data, 
            outstanding=0,
            status='new',
            created_by=session['user_id'],
            updated_by=None
        )
        # Menyimpan PurchaseRequest ke database
        db_session.add(purchase_request)
        db_session.commit()  # Commit pertama agar purchase_request disimpan dan id-nya ter-set

        # Mengupdate atau menambah PurchaseRequestItem jika ada perubahan
        for item_data in form.items.entries:  # Misalnya items adalah field di form

            item_id = item_data.record_id.data
            item_material_id = item_data.material_id.data
            item_general_id = item_data.general_id.data
            item_quantity = item_data.quantity.data
            item_remarks = item_data.remarks.data
            item_status = 'active'
            print("item_id: ", item_id)

            if item_id:  # Update item yang sudah ada
                item = db_session.query(PurchaseRequestItem).get(item_id)
                if item:
                    item.material_id = item_material_id
                    item.general_id = item_general_id
                    item.quantity = item_quantity
                    item.remarks = item_remarks
                    item.status = item_status
                    item.created_by=session['user_id']
                    item.updated_by=None
            else:  # Tambah item baru
                new_item = PurchaseRequestItem(
                    material_id=item_material_id,
                    general_id=item_general_id,
                    quantity=item_quantity, 
                    remarks=item_remarks,
                    status=item_status,
                    purchase_request_id=purchase_request.id,
                    created_by=session['user_id'],
                    updated_by=None
                )
                db_session.add(new_item)

        # Commit perubahan ke database
        db_session.commit()
        print("reference_number: ", purchase_request.reference_number)
        flash('Purchase request save successfully!', 'success')
        return redirect(url_for('purchases_request.lists', q=purchase_request.request_kind))
    
    # Debug jika validasi form gagal
    if not form.validate_on_submit():
        flash(form.errors, 'danger')
        print("form.errors: ", form.errors)

    return render_template(
        'purchases/requests/new.html',
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


@purchases_request_bp.route('/purchases/requests/<int:id>/edit', methods=['GET', 'POST'])
def edit(id):
    # Mengambil db_session
    db_session = get_session()
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))
    try:
        # Ambil data PurchaseRequest berdasarkan ID
        purchase_request = db_session.query(PurchaseRequest).get(id)
        if not purchase_request:
            flash('Purchase request not found!', 'danger')
            return redirect(url_for('purchases_request_bp.lists'))
        
        # Ambil department_id dari purchase_request
        department_id = purchase_request.department_id

        # Ambil daftar departemen, supplier, dan item terkait
        departments = db_session.query(Department).all()
        employee_sections = db_session.query(EmployeeSection).filter_by(department_id=department_id).all()
        purchase_request_items = db_session.query(PurchaseRequestItem).filter_by(purchase_request_id=id).all()
        materials = db_session.query(Material).options(joinedload(Material.unit)).all()
        generals = db_session.query(General).options(joinedload(General.unit)).all()

        # Bind data ke form
        form = PurchaseRequestForm(obj=purchase_request)
        # for item in purchase_request_items:
        #     item_form = PurchaseRequestItemForm(obj=item)
        #     form.items.append_entry(item_form)

        print("form: ", form.data)

        # Proses ketika form dikirim
        if form.validate_on_submit():

            # Update data PurchaseRequest
            purchase_request.remarks = form.remarks.data
            purchase_request.reference_date = form.reference_date.data
            
            db_session.add(purchase_request)

            # Mengupdate atau menambah PurchaseRequestItem jika ada perubahan
            for item_data in form.items.entries:  # Misalnya items adalah field di form

                item_id = item_data.record_id.data
                item_material_id = item_data.material_id.data
                item_general_id = item_data.general_id.data
                item_quantity = item_data.quantity.data
                item_remarks = item_data.remarks.data
                item_status = item_data.status.data
                print("item_id: ", item_id)

                if item_id:  # Update item yang sudah ada
                    item = db_session.query(PurchaseRequestItem).get(item_id)
                    if item:
                        item.material_id = item_material_id
                        item.general_id = item_general_id
                        item.quantity = item_quantity
                        item.remarks = item_remarks
                        item.status = item_status
                        item.updated_by=session['user_id']
                else:  # Tambah item baru
                    new_item = PurchaseRequestItem(
                        material_id=item_material_id,
                        general_id=item_general_id,
                        quantity=item_quantity, 
                        remarks=item_remarks,
                        status=item_status,
                        purchase_request_id=purchase_request.id,
                        created_by=session['user_id'],
                        updated_by=None
                    )
                    db_session.add(new_item)

            # Commit perubahan
            db_session.commit()
            flash('Purchase request updated successfully!', 'success')
            return redirect(url_for('purchases_request.show', id=purchase_request.id, q=purchase_request.request_kind))
        
        # Debug jika validasi form gagal
        if not form.validate_on_submit():
            flash(form.errors, 'danger')
            print(" ---------------------- > Form.errors: ", form.errors)
        
        # Render template edit
        return render_template(
            'purchases/requests/edit.html',
            form=form,
            purchase_request=purchase_request,
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
            purchase_request_items=purchase_request_items  # Kirimkan item terkait ke template
        )
    except Exception as e:
        print(" --------------------- > Error:", e)
        db_session.rollback()  # Rollback jika ada error
        flash('An error occurred while editing purchase request.', 'danger')
        return redirect(url_for('purchases_request.show', id=purchase_request.id, q=purchase_request.request_kind))
    finally:
        db_session.close()  # Selalu tutup db_session

@purchases_request_bp.route('/purchases/requests/<int:id>')
def show(id):
    db_session = get_session()
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))
    
    try:
        # Query untuk mengambil detail PurchaseRequest berdasarkan ID
        purchase_request = db_session.query(PurchaseRequest).get(id)

        # Jika PurchaseRequest tidak ditemukan
        if not purchase_request:
            flash('Purchase request not found!', 'danger')
            return redirect(url_for('purchases_request_bp.lists', q=purchase_request.request_kind))

        # Ambil department_id dari purchase_request
        department_id = purchase_request.department_id

        # Query untuk daftar departemen dan employee_sections
        departments = db_session.query(Department).all()
        employee_sections = db_session.query(EmployeeSection).filter_by(department_id=department_id).all()
        materials = db_session.query(Material).options(joinedload(Material.unit)).all()
        generals = db_session.query(General).options(joinedload(General.unit)).all()

        # Ambil semua item terkait dengan PurchaseRequest
        purchase_request_items = db_session.query(PurchaseRequestItem).options(
            joinedload(PurchaseRequestItem.material).joinedload(Material.unit),  # eager load material and unit
            joinedload(PurchaseRequestItem.general).joinedload(General.unit),  # eager load general and unit
        ).filter_by(purchase_request_id=id, status='active').all()

    finally:
        db_session.close()

    # Render template dengan data yang diambil
    return render_template(
        'purchases/requests/show.html',
        purchase_request=purchase_request,
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
        purchase_request_items=purchase_request_items,  # Kirimkan item terkait ke template
    )

@purchases_request_bp.route('/purchases/requests/headers', defaults={'ids': None})
@purchases_request_bp.route('/purchases/requests/headers/<ids>')
def show_headers(ids):
    db_session = get_session()
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))
    
    try:
        # Jika ids ada, proses sebagai list ID yang dipisahkan koma
        if ids:
            try:
                id_list = [int(i) for i in ids.split(",")]
                purchase_requests = db_session.query(PurchaseRequest).filter(PurchaseRequest.id.in_(id_list)).all()

                # Jika tidak ada data ditemukan
                if not purchase_requests:
                    return jsonify({"error": "Purchase requests not found!"}), 404
            except ValueError:
                return jsonify({"error": "Invalid ID format"}), 400
        else:
            # Ambil parameter dari query string
            department_id = request.args.get('department_id')
            employee_section_id = request.args.get('employee_section_id')
            request_kind = request.args.get('q')

            # Mulai query dasar untuk PurchaseRequest
            query = db_session.query(PurchaseRequest)

            # Tambahkan filter hanya jika parameter ada
            if department_id:
                query = query.filter(PurchaseRequest.department_id == department_id)

            if employee_section_id:
                query = query.filter(PurchaseRequest.employee_section_id == employee_section_id)

            # Eksekusi query
            purchase_requests = query.filter(
                PurchaseRequest.status == "approved3",
                PurchaseRequest.request_kind == request_kind,
                ).order_by(
                    PurchaseRequest.reference_date.desc(),
                    PurchaseRequest.reference_number.desc()
                ).all()


        # Format hasil JSON hanya menampilkan header

        result = [
                {
                    "id": pr.id,
                    "reference_number": pr.reference_number,
                    "reference_date": pr.reference_date.strftime("%Y-%m-%d") if pr.reference_date else None,
                    "employee_section_id": pr.employee_section_id,
                    "status": pr.status,
                    "department_id": pr.department_id
                } for pr in purchase_requests
            ]

        return jsonify(result)

    finally:
        db_session.close()

@purchases_request_bp.route('/purchases/requests/<ids>/items')
def show_items(ids):
    db_session = get_session()
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))
    
    try:
        # Ubah '1,2,3' menjadi list [1,2,3]
        id_list = [int(i) for i in ids.split(",")]

        # Ambil semua purchase requests berdasarkan ID
        purchase_requests = db_session.query(PurchaseRequest).filter(PurchaseRequest.id.in_(id_list)).all()

        # Jika tidak ada data ditemukan
        if not purchase_requests:
            return jsonify({"error": "Purchase requests not found!"}), 404

        # Ambil semua items yang terkait dengan purchase_requests
        purchase_request_items = db_session.query(PurchaseRequestItem).filter(
            PurchaseRequestItem.purchase_request_id.in_(id_list),
            PurchaseRequestItem.status == 'active'
        ).all()

        # Format hasil JSON
        result = {
            "purchase_requests": [
                {
                    "id": pr.id,
                    "reference_number": pr.reference_number,
                    "reference_date": pr.reference_date,
                    "employee_section_id": pr.employee_section_id,
                    "status": pr.status,
                    "department_id": pr.department_id
                } for pr in purchase_requests
            ],
            "items": [
                {
                    "id": item.id,
                    "purchase_request_id": item.purchase_request_id,
                    "quantity": item.quantity,
                    "outstanding": item.outstanding,
                    "material": {
                        "id": item.material.id,
                        "name": item.material.name,
                        "unit": item.material.unit.name if item.material.unit else ''
                    } if item.material else None,
                    "general": {
                        "id": item.general.id,
                        "name": item.general.name,
                        "unit": item.general.unit.name if item.general.unit else ''
                    } if item.general else None
                } for item in purchase_request_items
            ]
        }

        return jsonify(result)

    finally:
        db_session.close()