
from flask_wtf import FlaskForm
from wtforms import StringField, IntegerField, DecimalField, SelectField
from wtforms.validators import DataRequired, NumberRange

class TaxForm(FlaskForm):
    name = StringField('Name', render_kw={'maxlength': 16})
    status = SelectField('Status', choices=[('active', 'active'), ('suspend', 'suspend')], coerce=str)

    def __init__(self, *args, **kwargs):
        super(TaxForm, self).__init__(*args, **kwargs)
        # Tidak ada relasi atau data terkait untuk field ini
