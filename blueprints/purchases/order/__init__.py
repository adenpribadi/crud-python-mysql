from flask import Blueprint

purchases_order_bp = Blueprint('purchases_order', __name__, template_folder='templates')

from . import routes
