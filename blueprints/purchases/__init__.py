from flask import Blueprint

# Create the main blueprint for 'purchases'
purchases_bp = Blueprint('purchases', __name__, template_folder='templates')

# Import and register sub-blueprints
from .request import purchases_request_bp
from .order import purchases_order_bp

# Register the 'order' blueprint as a sub-blueprint
purchases_bp.register_blueprint(purchases_request_bp, url_prefix='/requests')
purchases_bp.register_blueprint(purchases_order_bp, url_prefix='/orders')
