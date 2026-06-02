from flask import Blueprint, request, jsonify, session
from flask_login import login_required, current_user
from services.user_service import *
from services.common_service import svc_get_all_provinces

user_bp = Blueprint("user", __name__, url_prefix="/api/user")

@user_bp.route("/register", methods=["POST"])
def user_register():
    return svc_user_register()

@user_bp.route("/login", methods=["POST"])
def user_login():
    return svc_user_login()

@user_bp.route("/logout", methods=["POST"])
@login_required
def user_logout():
    return svc_user_logout()

@user_bp.route("/info", methods=["GET"])
@login_required
def user_info():
    return svc_user_info()

@user_bp.route("/subscribe", methods=["POST"])
@login_required
def subscribe():
    return svc_subscribe_province()

@user_bp.route("/subscribe/<int:subscribe_id>", methods=["DELETE"])
@login_required
def unsubscribe(subscribe_id):
    return svc_unsubscribe_province(subscribe_id)

@user_bp.route("/subscriptions", methods=["GET"])
@login_required
def subscriptions():
    return svc_get_subscriptions()

@user_bp.route("/alerts", methods=["GET"])
@login_required
def alerts():
    return svc_get_user_alerts()

@user_bp.route("/alerts/unread", methods=["GET"])
@login_required
def unread():
    return svc_get_unread_alerts_count()

@user_bp.route("/alerts/<int:alert_id>/read", methods=["POST"])
@login_required
def read(alert_id):
    return svc_mark_alert_read(alert_id)

@user_bp.route("/alerts/read-all", methods=["POST"])
@login_required
def read_all():
    return svc_mark_all_alerts_read()

# ====================== 批量订阅省份（多选大区） ======================
@user_bp.route("/subscribe/batch", methods=["POST"])
@login_required
def subscribe_batch():
    return svc_user_batch_subscribe()

# ====================== 获取我的订阅ID列表（用于前端回显勾选） ======================
@user_bp.route("/subscribe/my", methods=["GET"])
@login_required
def my_subscribe_ids():
    return svc_user_my_subscribe_ids()

# ====================== 预警设置（频率 + 通知方式） ======================
@user_bp.route("/alert/settings", methods=["GET"])
@login_required
def get_alert_settings():
    return svc_user_get_alert_settings()

@user_bp.route("/alert/settings", methods=["POST"])
@login_required
def update_alert_settings():
    return svc_user_update_alert_settings()

# ====================== 用户反馈（必须登录） ======================
@user_bp.route("/feedback", methods=["POST"])
@login_required
def user_feedback():
    data = request.get_json()
    return svc_submit_feedback(current_user.user_id, data)

# ====================== 公共聊天室：发送消息（必须登录） ======================
@user_bp.route("/chat", methods=["POST"])
@login_required
def send_chat():
    data = request.get_json()
    return svc_send_chat_message(current_user.user_id, data)

# ====================== 公共聊天室：获取所有历史消息 ======================
@user_bp.route("/chat/list", methods=["GET"])
@login_required
def chat_list():
    return svc_get_chat_list()

# 获取全部省份列表
@user_bp.route("/provinces", methods=["GET"])
def get_all_province():
    return svc_get_all_provinces()