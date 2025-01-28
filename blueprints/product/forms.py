
from flask_wtf import FlaskForm
from wtforms import StringField, IntegerField, DecimalField, SelectField
from wtforms.validators import DataRequired, NumberRange

class ProductForm(FlaskForm):
    name = StringField('Name', render_kw={'maxlength': 126})
    internal_reference = StringField('Internal_reference', render_kw={'maxlength': 126})
    status = SelectField('Status', choices=[('active', 'active'), ('suspend', 'suspend')], coerce=str)

    def __init__(self, *args, **kwargs):
        super(ProductForm, self).__init__(*args, **kwargs)
        # Tidak ada relasi atau data terkait untuk field ini
