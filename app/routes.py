from flask import Blueprint

trip_bp = Blueprint("trip_bp", __name__, url_prefix="/trips")