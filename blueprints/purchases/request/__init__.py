from flask import Blueprint

purchases_request_bp = Blueprint('purchases_request', __name__, template_folder='templates')

from . import routes
