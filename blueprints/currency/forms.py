
from flask_wtf import FlaskForm
from wtforms import StringField, IntegerField, DecimalField, SelectField
from wtforms.validators import DataRequired, NumberRange

class CurrencyForm(FlaskForm):
    name = StringField('Name', render_kw={'maxlength': 255})
    symbol = StringField('Symbol', render_kw={'maxlength': 16})
    precision_digit = IntegerField('Precision_digit', validators=[NumberRange(min=0)])

    def __init__(self, *args, **kwargs):
        super(CurrencyForm, self).__init__(*args, **kwargs)
        # Tidak ada relasi atau data terkait untuk field ini
