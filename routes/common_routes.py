from flask import Blueprint
from services.common_service import *

common_bp = Blueprint("common", __name__, url_prefix="/api")

@common_bp.route("/earthquake/list", methods=["GET"])
def eq_list():
    return svc_list_earthquake()

@common_bp.route("/provinces", methods=["GET"])
def provinces():
    return svc_get_all_provinces()