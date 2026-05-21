from flask import Blueprint
from services.admin_service import *

admin_bp = Blueprint("admin", __name__, url_prefix="/api/admin")

@admin_bp.route("/register", methods=["POST"])
def admin_register():
    return svc_admin_register()

@admin_bp.route("/login", methods=["POST"])
def admin_login():
    return svc_admin_login()

@admin_bp.route("/logout", methods=["POST"])
def admin_logout():
    return svc_admin_logout()

@admin_bp.route("/info", methods=["GET"])
def admin_info():
    return svc_admin_info()

@admin_bp.route("/earthquake/add", methods=["POST"])
def add_eq():
    return svc_add_earthquake()

@admin_bp.route("/earthquake/update", methods=["POST"])
def update_eq():
    return svc_update_earthquake()

@admin_bp.route("/earthquake/delete", methods=["POST"])
def delete_eq():
    return svc_delete_earthquake()