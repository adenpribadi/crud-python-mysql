from flask import Blueprint

currency_bp = Blueprint('currency', __name__, template_folder='templates')

from . import routes  # Memanggil routes.py untuk mendefinisikan rute
