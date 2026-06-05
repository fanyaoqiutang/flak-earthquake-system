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


# ====================== 管理员发送聊天消息 ======================
@user_bp.route("/chat/admin", methods=["POST"])
def admin_send_chat():
    from services.admin_service import verify_admin
    
    print("=" * 50)
    print("[DEBUG] 管理员发送聊天消息请求")
    print(f"[DEBUG] Request headers: {dict(request.headers)}")
    print(f"[DEBUG] Request content-type: {request.content_type}")
    
    # 验证管理员身份
    if not verify_admin():
        print("[ERROR] 管理员验证失败")
        return jsonify({"code": 403, "msg": "无权限，请先以管理员身份登录"}), 403
    
    print("[DEBUG] 管理员验证成功")
    
    # 获取请求数据
    data = request.get_json(force=True, silent=True)
    print(f"[DEBUG] 接收到的数据: {data}")
    
    if not data:
        print("[ERROR] 请求数据为空或格式错误")
        return jsonify({"code": 400, "msg": "请求数据格式错误"}), 400
    
    # 管理员使用负数ID
    admin_id = session.get('admin_id', -1)
    print(f"[DEBUG] 管理员ID: {admin_id}")
    
    try:
        result = svc_send_chat_message(-admin_id, data)
        print(f"[DEBUG] 发送结果: {result}")
        print("=" * 50)
        return result
    except Exception as e:
        print(f"[ERROR] 发送消息异常: {e}")
        import traceback
        traceback.print_exc()
        print("=" * 50)
        return jsonify({"code": 500, "msg": f"服务器错误: {str(e)}"}), 500


# ====================== 公共聊天室：获取所有历史消息 ======================
@user_bp.route("/chat/list", methods=["GET"])
def chat_list():
    # 允许管理员和普通用户都查看聊天记录
    from services.admin_service import verify_admin
    
    # 如果是管理员，直接返回
    if verify_admin():
        return svc_get_chat_list()
    
    # 否则需要用户登录
    if not current_user.is_authenticated:
        return jsonify({"code": 401, "msg": "请先登录"}), 401
    
    return svc_get_chat_list()

# 获取全部省份列表
@user_bp.route("/provinces", methods=["GET"])
def get_all_province():
    return svc_get_all_provinces()

# 更新用户基础信息
@user_bp.route("/info/update", methods=["PUT"])
@login_required
def update_user_info_route():
    data = request.get_json()
    return svc_update_user_info(current_user.user_id, data)

# 修改密码
@user_bp.route("/password/change", methods=["POST"])
@login_required
def change_password_route():
    data = request.get_json()
    return svc_change_password(current_user.user_id, data)

# 注销账号
@user_bp.route("/account/delete", methods=["DELETE"])
@login_required
def delete_account_route():
    return svc_delete_account(current_user.user_id)
