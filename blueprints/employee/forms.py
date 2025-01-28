from flask_wtf import FlaskForm
from wtforms import StringField, DateField, SelectField
from wtforms.validators import DataRequired
from models import get_session
from models.department_model import Department
from models.position_model import Position
from models.work_status_model import WorkStatus

class EmployeeForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired()])
    born_date = DateField('Born Date', validators=[DataRequired()])
    department = SelectField('Department', coerce=int)
    position = SelectField('Position', coerce=int)
    work_status = SelectField('Work Status', coerce=int)

    born_place = StringField('born_place')
    join_date = DateField('Join Date')
    image = StringField('image')
    gender = StringField('gender')
    nik = StringField('nik')
    phone_number = StringField('Phone Number', validators=[DataRequired()])
    email_address = StringField('email_address', validators=[DataRequired()])

    def __init__(self, *args, **kwargs):
        super(EmployeeForm, self).__init__(*args, **kwargs)
        session = get_session()
        self.department.choices = [(d.id, d.name) for d in session.query(Department).all()]
        self.position.choices = [(p.id, p.name) for p in session.query(Position).all()]
        self.work_status.choices = [(ws.id, ws.name) for ws in session.query(WorkStatus).all()]
        session.close()
