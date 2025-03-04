from flask_wtf import FlaskForm
from wtforms import StringField, IntegerField, DateField, SelectField, FieldList, FormField, DecimalField
from wtforms.validators import DataRequired, InputRequired, Optional
from models import get_session
from models.department_model import Department
from models.employee_section_model import EmployeeSection

class PurchaseRequestItemForm(FlaskForm):
    # 2024-12-30 tidak bisa menggunakan 'id' harus diubah jadi 'record_id'
    record_id = IntegerField('ID', default=None)

    material_id = IntegerField('Material', validators=[Optional()])  # Mengizinkan nilai kosong
    general_id = IntegerField('General', validators=[Optional()])  # Mengizinkan nilai kosong
    
    quantity = DecimalField('Quantity', places=2, validators=[InputRequired()])
    remarks = StringField('Remarks')
    status = StringField('Status')

class PurchaseRequestForm(FlaskForm):
    remarks = StringField('remarks')
    request_kind = StringField('request_kind')
    reference_date = DateField('Request Date', validators=[DataRequired()])
    department = SelectField('Department', coerce=int, validators=[DataRequired()])
    employee_section = SelectField('Employee Section', coerce=int, validators=[DataRequired()])
    
    # Daftar item terkait dengan PurchaseRequest
    items = FieldList(FormField(PurchaseRequestItemForm), min_entries=1)

    # Metode untuk mengisi daftar departemen dan supplier
    def __init__(self, *args, **kwargs):
        super(PurchaseRequestForm, self).__init__(*args, **kwargs)
        # Isi dropdown Departemen dengan data dari model Department
        session = get_session()
        self.department.choices = [(d.id, d.name) for d in session.query(Department).all()]
        self.employee_section.choices = [(e.id, e.name) for e in session.query(EmployeeSection).all()]
