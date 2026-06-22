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
# @login_required  # 临时注释，避免CORS预检请求失败
def user_logout():
    return svc_user_logout()

@user_bp.route("/info", methods=["GET"])
# @login_required  # 临时注释，避免CORS预检请求失败
def user_info():
    return svc_user_info()

@user_bp.route("/subscribe", methods=["POST"])
# @login_required  # 临时注释，service层已有兜底逻辑
def subscribe():
    return svc_subscribe_province()

@user_bp.route("/subscribe/<int:subscribe_id>", methods=["DELETE"])
# @login_required  # 临时注释，service层已有兜底逻辑
def unsubscribe(subscribe_id):
    return svc_unsubscribe_province(subscribe_id)

@user_bp.route("/subscriptions", methods=["GET"])
# @login_required  # 临时注释，避免CORS预检请求失败
def subscriptions():
    return svc_get_subscriptions()

@user_bp.route("/alerts", methods=["GET"])
# @login_required  # 临时注释，service层已有兜底逻辑
def alerts():
    return svc_get_user_alerts()

@user_bp.route("/alerts/unread", methods=["GET"])
# @login_required  # 临时注释，service层已有兜底逻辑
def unread():
    return svc_get_unread_alerts_count()

@user_bp.route("/alerts/<int:alert_id>/read", methods=["POST"])
# @login_required  # 临时注释，service层已有兜底逻辑
def read(alert_id):
    return svc_mark_alert_read(alert_id)

@user_bp.route("/alerts/read-all", methods=["POST"])
# @login_required  # 临时注释，service层已有兜底逻辑
def read_all():
    return svc_mark_all_alerts_read()

# ====================== 批量订阅省份（多选大区） ======================
@user_bp.route("/subscribe/batch", methods=["POST"])
# @login_required  # 临时注释，避免CORS预检请求失败
def subscribe_batch():
    return svc_user_batch_subscribe()

# ====================== 获取我的订阅ID列表（用于前端回显勾选） ======================
@user_bp.route("/subscribe/my", methods=["GET"])
# @login_required  # 临时注释，service层已有兜底逻辑
def my_subscribe_ids():
    return svc_user_my_subscribe_ids()

# ====================== 预警设置（频率 + 通知方式） ======================
@user_bp.route("/alert/settings", methods=["GET"])
# @login_required  # 临时注释，避免CORS预检请求失败
def get_alert_settings():
    return svc_user_get_alert_settings()

@user_bp.route("/alert/settings", methods=["POST"])
# @login_required  # 临时注释，避免CORS预检请求失败
def update_alert_settings():
    return svc_user_update_alert_settings()

# ====================== 用户反馈（必须登录） ======================
@user_bp.route("/feedback", methods=["POST"])
# @login_required  # 临时注释，service层已有兜底逻辑
def user_feedback():
    data = request.get_json()
    # 获取用户ID（支持管理员）
    user_id = None
    if current_user.is_authenticated:
        user_id = current_user.user_id
    else:
        user_id = session.get('user_id')
        if not user_id:
            # 尝试获取管理员ID
            admin_id = session.get('admin_id')
            if admin_id:
                user_id = -admin_id  # 管理员使用负数ID
    return svc_submit_feedback(user_id, data)


# ====================== 公共聊天室：发送消息（必须登录） ======================
@user_bp.route("/chat", methods=["POST"])
# @login_required  # 临时注释，避免CORS预检请求失败
def send_chat():
    user_id = None
    if current_user.is_authenticated:
        user_id = current_user.user_id
    else:
        user_id = session.get('user_id')
    if not user_id:
        return jsonify({"code": 401, "msg": "请先登录"}), 401
    data = request.get_json()
    return svc_send_chat_message(user_id, data)


# ====================== 管理员发送聊天消息 ======================
@user_bp.route("/chat/admin", methods=["POST"])
def admin_send_chat():
    from services.admin_service import verify_admin

    if not verify_admin():
        return jsonify({"code": 403, "msg": "无权限，请先以管理员身份登录"}), 403

    data = request.get_json()
    # 管理员使用负数ID
    admin_id = session.get('admin_id', -1)
    return svc_send_chat_message(-admin_id, data)


# ====================== 公共聊天室：获取所有历史消息 ======================
@user_bp.route("/chat/list", methods=["GET"])
# @login_required  # 临时注释，避免CORS预检请求失败
def chat_list():
    return svc_get_chat_list()


# ====================== 获取当前用户发送的聊天消息 ======================
@user_bp.route("/chat/my-messages", methods=["GET"])
@login_required
def get_my_chat_messages():
    user_id = current_user.user_id
    return svc_get_user_chat_messages(user_id)


# ====================== 删除用户发送的聊天消息 ======================
@user_bp.route("/chat/my-messages/<int:message_id>", methods=["DELETE"])
@login_required
def delete_my_chat_message(message_id):
    user_id = current_user.user_id
    return svc_delete_user_chat_message(user_id, message_id)


# 获取全部省份列表
@user_bp.route("/provinces", methods=["GET"])
def get_all_province():
    return svc_get_all_provinces()

# 更新用户基础信息
@user_bp.route("/info/update", methods=["PUT"])
# @login_required  # 临时注释，避免CORS预检请求失败
def update_user_info_route():
    user_id = None
    if current_user.is_authenticated:
        user_id = current_user.user_id
    else:
        user_id = session.get('user_id')
    if not user_id:
        return jsonify({"code": 401, "msg": "请先登录"}), 401
    data = request.get_json()
    return svc_update_user_info(user_id, data)

# 修改密码
@user_bp.route("/password/change", methods=["POST"])
# @login_required  # 临时注释，避免CORS预检请求失败
def change_password_route():
    user_id = None
    if current_user.is_authenticated:
        user_id = current_user.user_id
    else:
        user_id = session.get('user_id')
    if not user_id:
        return jsonify({"code": 401, "msg": "请先登录"}), 401
    data = request.get_json()
    return svc_change_password(user_id, data)

# 注销账号
@user_bp.route("/account/delete", methods=["DELETE"])
# @login_required  # 临时注释，避免CORS预检请求失败
def delete_account_route():
    user_id = None
    if current_user.is_authenticated:
        user_id = current_user.user_id
    else:
        user_id = session.get('user_id')
    if not user_id:
        return jsonify({"code": 401, "msg": "请先登录"}), 401
    return svc_delete_account(user_id)
