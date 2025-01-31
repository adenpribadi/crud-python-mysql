from flask import Blueprint

term_of_payment_bp = Blueprint('term_of_payment', __name__, template_folder='templates')

from . import routes  # Memanggil routes.py untuk mendefinisikan rute
