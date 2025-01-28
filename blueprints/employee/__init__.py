from flask import Blueprint

employee_bp = Blueprint('employee', __name__, template_folder='templates')

from . import routes  # Memanggil routes.py untuk mendefinisikan rute
