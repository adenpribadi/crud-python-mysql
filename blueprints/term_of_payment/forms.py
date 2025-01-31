
from flask_wtf import FlaskForm
from wtforms import StringField, IntegerField, DecimalField, SelectField
from wtforms.validators import DataRequired, NumberRange

class TermOfPaymentForm(FlaskForm):
    name = StringField('Name', render_kw={'maxlength': 24})
    code = StringField('Code', render_kw={'maxlength': 8})

    def __init__(self, *args, **kwargs):
        super(TermOfPaymentForm, self).__init__(*args, **kwargs)
        # Tidak ada relasi atau data terkait untuk field ini
