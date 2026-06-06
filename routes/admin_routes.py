from flask import Blueprint, request, jsonify, session
from services.admin_service import *

admin_bp = Blueprint("admin", __name__, url_prefix="/api/admin")

@admin_bp.route("/dashboard/stats", methods=["GET"])
def get_dashboard_stats():
    return svc_get_dashboard_stats()

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

# ======================
# 地震管理（仅管理员）
# ======================
@admin_bp.route("/earthquakes", methods=["GET"])
def admin_earthquake_list():
    return svc_admin_get_earthquakes()

@admin_bp.route("/earthquake/add", methods=["POST"])
def add_eq():
    return svc_add_earthquake()

@admin_bp.route("/earthquake/update", methods=["POST"])
def update_eq():
    return svc_update_earthquake()

@admin_bp.route("/earthquake/delete", methods=["POST"])
def delete_eq():
    return svc_delete_earthquake()

# ======================
# 省份管理
# ======================
@admin_bp.route("/provinces", methods=["GET"])
def admin_provinces():
    return svc_admin_get_provinces()

# ======================
# 用户管理
# ======================
@admin_bp.route("/user/list", methods=["GET"])
def admin_user_list():
    return svc_admin_get_all_users()

# 新增：用户统计（总用户、活跃、禁用）
@admin_bp.route("/user/stats", methods=["GET"])
def admin_user_stats():
    return svc_admin_get_user_stats()

# 新增：切换用户状态（正常 / 禁用）
@admin_bp.route("/user/status/<int:user_id>", methods=["POST"])
def admin_user_status(user_id):
    return svc_admin_toggle_user_status(user_id)

@admin_bp.route("/user/delete/<int:user_id>", methods=["POST"])
def admin_user_delete(user_id):
    return svc_admin_delete_user(user_id)

# ======================
# 反馈管理
# ======================
@admin_bp.route("/feedback/list", methods=["GET"])
def admin_feedback_list():
    return svc_admin_get_all_feedbacks()

@admin_bp.route("/feedback/handle/<int:fb_id>", methods=["POST"])
def admin_feedback_handle(fb_id):
    return svc_admin_handle_feedback(fb_id)

# ======================
# 聊天管理
# ======================
@admin_bp.route("/chat-records", methods=["GET"])
def admin_chat_records():
    return svc_admin_get_chat_records()

@admin_bp.route("/chat/list", methods=["GET"])
def admin_chat_list():
    return svc_admin_get_all_chat_messages()

@admin_bp.route("/chat/delete/<int:msg_id>", methods=["POST"])
def admin_chat_delete(msg_id):
    return svc_admin_delete_chat_msg(msg_id)
