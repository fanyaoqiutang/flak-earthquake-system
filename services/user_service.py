from flask import request, jsonify, session
from flask_login import login_user, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
import secrets, datetime
from models import db, User, UserSubscribeProvince, UserEarthquakeAlert, Province, EarthquakeInfo, UserFeedback, \
    ChatMessage


# ====================== 登录注册 ======================
def svc_user_register():
    data = request.get_json(force=True)
    account = data.get('user_account')
    pwd = data.get('password')
    if not account or not pwd:
        return jsonify({"code": 400, "msg": "不能为空"}), 400
    if len(account) < 3 or len(account) > 20:
        return jsonify({"code": 400, "msg": "账号长度3-20位"}), 400
    if len(pwd) < 6:
        return jsonify({"code": 400, "msg": "密码长度至少6位"}), 400
    if User.query.filter_by(user_account=account).first():
        return jsonify({"code": 400, "msg": "账号已存在"}), 400
    hashed_pwd = generate_password_hash(pwd)
    u = User(user_account=account, password=hashed_pwd)
    db.session.add(u)
    db.session.commit()
    return jsonify({"code": 200, "msg": "注册成功"})


def svc_user_login():
    data = request.get_json(force=True)
    account = data.get('user_account')
    pwd = data.get('password')
    if not account or not pwd:
        return jsonify({"code": 400, "msg": "参数不能为空"}), 400
    u = User.query.filter_by(user_account=account).first()
    if not u or not check_password_hash(u.password, pwd):
        return jsonify({"code": 401, "msg": "账号或密码错误"}), 401

    # 登录时更新最后活跃时间
    u.last_active_time = datetime.datetime.now()
    db.session.commit()

    # 使用Flask-Login登录
    login_user(u, remember=True)
    
    # 设置session
    session['user_id'] = u.user_id
    session['user_account'] = u.user_account
    token = secrets.token_hex(32)
    session['user_token'] = token
    
    # 清除可能的管理员session
    if 'admin_id' in session:
        del session['admin_id']
    if 'admin_account' in session:
        del session['admin_account']
    if 'admin_token' in session:
        del session['admin_token']
    
    # 确保session被保存
    session.modified = True
    session.permanent = True
    
    print(f"✅ 普通用户 {account} (ID: {u.user_id}) 登录成功")
    
    return jsonify({"code": 200, "msg": "登录成功",
                    "data": {"user_id": u.user_id, "user_account": u.user_account, "user_token": token}})


def svc_user_logout():
    # 只清除用户相关的session
    keys_to_remove = ['user_id', 'user_account', 'user_token']
    for key in keys_to_remove:
        if key in session:
            del session[key]
    session.modified = True
    
    # 退出Flask-Login
    logout_user()
    
    print("✅ 普通用户退出登录")
    return jsonify({"code": 200, "msg": "退出成功"})


def svc_user_info():
    # 支持管理员和普通用户
    if current_user.is_authenticated:
        return jsonify({"code": 200, "data": {"user_id": current_user.user_id, "user_account": current_user.user_account}})
    else:
        # 尝试从session获取
        user_id = session.get('user_id')
        user_account = session.get('user_account')
        if user_id and user_account:
            return jsonify({"code": 200, "data": {"user_id": user_id, "user_account": user_account}})
        
        # 尝试获取管理员
        admin_id = session.get('admin_id')
        admin_account = session.get('admin_account')
        if admin_id and admin_account:
            return jsonify({"code": 200, "data": {"user_id": -admin_id, "user_account": admin_account, "role": "admin"}})
        
        return jsonify({"code": 401, "msg": "请先登录"}), 401


# ====================== 单省份订阅（保留兼容） ======================
def svc_subscribe_province():
    # 获取用户ID（支持管理员）
    user_id = _get_current_user_id()
    if not user_id:
        return jsonify({"code": 401, "msg": "请先登录"}), 401
    
    data = request.get_json(force=True)
    province_id = data.get('province_id')

    if province_id == "":
        province_id = None

    if not province_id:
        return jsonify({"code": 400, "msg": "省份ID不能为空"}), 400

    try:
        province_id = int(province_id)
    except:
        return jsonify({"code": 400, "msg": "省份ID格式错误"}), 400

    if not Province.query.get(province_id):
        return jsonify({"code": 400, "msg": "省份不存在"}), 400

    existing = UserSubscribeProvince.query.filter_by(user_id=user_id, province_id=province_id).first()
    if existing:
        return jsonify({"code": 400, "msg": "已订阅该省份"}), 400

    sub = UserSubscribeProvince(user_id=user_id, province_id=province_id)
    db.session.add(sub)
    db.session.commit()
    return jsonify({"code": 200, "msg": "订阅成功"})


def svc_unsubscribe_province(subscribe_id):
    # 获取用户ID（支持管理员）
    user_id = _get_current_user_id()
    if not user_id:
        return jsonify({"code": 401, "msg": "请先登录"}), 401
    
    sub = UserSubscribeProvince.query.get(subscribe_id)
    if not sub or sub.user_id != user_id:
        return jsonify({"code": 403, "msg": "无权限"}), 403
    db.session.delete(sub)
    db.session.commit()
    return jsonify({"code": 200, "msg": "取消订阅成功"})


def svc_get_subscriptions():
    # 获取用户ID（支持管理员）
    user_id = _get_current_user_id()
    
    if not user_id:
        return jsonify({"code": 401, "msg": "请先登录"}), 401
    
    print(f"📋 查询订阅 - 用户ID: {user_id}")
    subs = UserSubscribeProvince.query.filter_by(user_id=user_id).all()
    res = []
    for s in subs:
        p = Province.query.get(s.province_id)
        res.append({"id": s.id, "province_id": s.province_id, "province_name": p.province_name if p else "未知"})
    print(f" 订阅数量: {len(res)}")
    return jsonify({"code": 200, "data": res})


# ====================== 辅助函数：获取当前用户ID ======================
def _get_current_user_id():
    """获取当前用户ID，支持普通用户和管理员"""
    # 打印当前session内容（调试用）
    print(f"🔍 当前session内容: {dict(session)}")
    
    # 尝试从Flask-Login获取（优先）
    if current_user.is_authenticated:
        print(f"✅ 从Flask-Login获取用户ID: {current_user.user_id}")
        return current_user.user_id
    
    # 尝试从session获取普通用户ID
    user_id = session.get('user_id')
    user_account = session.get('user_account')
    if user_id:
        print(f"✅ 从session获取普通用户ID: {user_id}, 账号: {user_account}")
        return user_id
    
    # 尝试从session获取管理员ID
    admin_id = session.get('admin_id')
    admin_account = session.get('admin_account')
    if admin_id:
        print(f"✅ 从session获取管理员ID: {admin_id}, 账号: {admin_account}")
        return -admin_id  # 管理员使用负数ID
    
    # 没有登录，返回None
    print("⚠️ 用户未登录")
    return None


# ====================== 【新增】批量订阅（支持多选大区） ======================
def svc_user_batch_subscribe():
    # 获取用户ID（支持管理员）
    user_id = _get_current_user_id()
    
    if not user_id:
        return jsonify({"code": 401, "msg": "请先登录"}), 401
    
    province_ids = request.get_json().get("province_ids", [])
    print(f"✅ 批量订阅 - 用户ID: {user_id}, 省份IDs: {province_ids}")

    # 清空原有订阅
    deleted_count = UserSubscribeProvince.query.filter_by(user_id=user_id).delete()
    print(f"🗑️ 删除旧订阅: {deleted_count} 条")

    # 批量添加
    added_count = 0
    for pid in province_ids:
        if Province.query.get(pid):
            db.session.add(UserSubscribeProvince(user_id=user_id, province_id=pid))
            added_count += 1

    db.session.commit()
    print(f"✅ 批量订阅成功 - 新增: {added_count} 条")
    return jsonify({"code": 200, "msg": "订阅已更新"})


def svc_user_my_subscribe_ids():
    # 获取用户ID（支持管理员）
    user_id = _get_current_user_id()
    
    if not user_id:
        return jsonify({"code": 401, "msg": "请先登录"}), 401
    
    subs = UserSubscribeProvince.query.filter_by(user_id=user_id).all()
    pids = [s.province_id for s in subs]
    return jsonify({"code": 200, "data": pids})


# ====================== 预警 ======================
def svc_get_user_alerts():
    # 获取用户ID（支持管理员）
    user_id = _get_current_user_id()
    
    if not user_id:
        return jsonify({"code": 401, "msg": "请先登录"}), 401
    
    # 管理员没有预警
    if user_id < 0:
        return jsonify({"code": 200, "data": []})
    
    alerts = UserEarthquakeAlert.query.filter_by(user_id=user_id).order_by(
        UserEarthquakeAlert.id.desc()).all()
    res = []
    for a in alerts:
        eq = EarthquakeInfo.query.get(a.earthquake_id)
        p = Province.query.get(eq.province_id) if eq else None
        res.append({
            "alert_id": a.id,
            "earthquake_id": a.earthquake_id,
            "is_read": a.is_read,
            "province_name": p.province_name if p else "未知",
            "magnitude": eq.magnitude if eq else 0,
            "earthquake_time": eq.earthquake_time.strftime("%Y-%m-%d %H:%M:%S") if eq else "",
            "earthquake_message": eq.earthquake_message if eq else ""
        })
    return jsonify({"code": 200, "data": res})


def svc_get_unread_alerts_count():
    # 获取用户ID（支持管理员）
    user_id = _get_current_user_id()
    
    if not user_id:
        return jsonify({"code": 401, "msg": "请先登录"}), 401
    
    # 管理员没有预警
    if user_id < 0:
        return jsonify({"code": 200, "data": {"unread_count": 0}})
    
    cnt = UserEarthquakeAlert.query.filter_by(user_id=user_id, is_read=False).count()
    return jsonify({"code": 200, "data": {"unread_count": cnt}})


def svc_mark_alert_read(alert_id):
    # 获取用户ID（支持管理员）
    user_id = _get_current_user_id()
    
    if not user_id:
        return jsonify({"code": 401, "msg": "请先登录"}), 401
    
    a = UserEarthquakeAlert.query.get(alert_id)
    if not a or a.user_id != user_id:
        return jsonify({"code": 403, "msg": "无权限"}), 403
    a.is_read = True
    db.session.commit()
    return jsonify({"code": 200, "msg": "已标记已读"})


def svc_mark_all_alerts_read():
    # 获取用户ID（支持管理员）
    user_id = _get_current_user_id()
    
    if not user_id:
        return jsonify({"code": 401, "msg": "请先登录"}), 401
    
    alerts = UserEarthquakeAlert.query.filter_by(user_id=user_id, is_read=False).all()
    for a in alerts:
        a.is_read = True
    db.session.commit()
    return jsonify({"code": 200, "msg": "全部已读"})


# ====================== 【新增】预警设置（频率 + 通知方式） ======================
def svc_user_get_alert_settings():
    # 获取用户ID（支持管理员）
    user_id = _get_current_user_id()
    
    if not user_id:
        return jsonify({"code": 401, "msg": "请先登录"}), 401
    
    # 管理员没有这些设置，返回默认值
    if user_id < 0:
        return jsonify({
            "code": 200,
            "data": {
                "alert_frequency": "实时预警",
                "alert_methods": ["站内信"]
            }
        })
    
    user = User.query.get(user_id)
    if not user:
        return jsonify({"code": 404, "msg": "用户不存在"}), 404
    
    return jsonify({
        "code": 200,
        "data": {
            "alert_frequency": user.alert_frequency,
            "alert_methods": user.alert_methods
        }
    })


def svc_user_update_alert_settings():
    # 获取用户ID（支持管理员）
    user_id = _get_current_user_id()
    
    if not user_id:
        return jsonify({"code": 401, "msg": "请先登录"}), 401
    
    # 管理员不更新这些设置
    if user_id < 0:
        return jsonify({"code": 200, "msg": "管理员无需设置"})
    
    data = request.get_json()
    u = User.query.get(user_id)
    if not u:
        return jsonify({"code": 404, "msg": "用户不存在"}), 404

    freq = data.get("alert_frequency")
    methods = data.get("alert_methods", [])

    if freq in ["实时预警", "每日汇总"]:
        u.alert_frequency = freq

    valid = ["站内信", "短信通知", "邮件通知"]
    u.alert_methods = [m for m in methods if m in valid]

    db.session.commit()
    return jsonify({"code": 200, "msg": "保存成功"})


# ====================== 用户反馈 ======================
def svc_submit_feedback(user_id, data):
    feedback_type = data.get("feedback_type")
    content = data.get("content")
    priority = data.get("priority", "中")

    if not feedback_type or not content:
        return jsonify({"code": 400, "msg": "反馈类型和内容不能为空"}), 400

    fb = UserFeedback(
        user_id=user_id,
        feedback_type=feedback_type,
        content=content,
        priority=priority
    )
    db.session.add(fb)
    db.session.commit()

    return jsonify({"code": 200, "msg": "反馈提交成功"})


# ====================== 发送聊天消息 ======================
def svc_send_chat_message(user_id, data):
    content = data.get("content", "").strip()

    if not content:
        return jsonify({"code": 400, "msg": "消息不能为空"}), 400

    # 如果是管理员（负数ID），不关联到User表
    if user_id < 0:
        msg = ChatMessage(
            user_id=None,  # 管理员消息不关联用户
            content=f"[管理员] {content}"
        )
    else:
        # 检查用户状态，禁用的用户不允许发送消息
        user = User.query.get(user_id)
        if not user:
            return jsonify({"code": 404, "msg": "用户不存在"}), 404

        if user.status == "禁用":
            return jsonify({"code": 403, "msg": "您的账号已被禁用，无法发送消息"}), 403

        msg = ChatMessage(
            user_id=user_id,
            content=content
        )

    db.session.add(msg)
    db.session.commit()

    return jsonify({"code": 200, "msg": "发送成功"})


# ====================== 获取聊天记录 ======================
def svc_get_chat_list():
    messages = ChatMessage.query.order_by(ChatMessage.create_time).all()
    res = []

    for m in messages:
        if m.user_id is None:
            # 管理员消息
            username = "管理员"
        else:
            user = User.query.get(m.user_id)
            username = user.user_account if user else "未知用户"

        res.append({
            "id": m.id,
            "user_id": m.user_id,
            "username": username,
            "content": m.content,
            "create_time": m.create_time.strftime("%Y-%m-%d %H:%M:%S"),
            "status": m.status if hasattr(m, 'status') else 'normal'
        })

    return jsonify({"code": 200, "data": res})


# ... existing code ...

def svc_update_user_info(user_id, data):
    """更新用户基础信息"""
    user = User.query.get(user_id)
    if not user:
        return jsonify({"code": 404, "msg": "用户不存在"}), 404

    # 更新字段
    if "nickname" in data:
        user.user_nickname = data["nickname"]
    if "phone" in data:
        user.phone = data["phone"]
    if "email" in data:
        user.email = data["email"]

    db.session.commit()
    return jsonify({"code": 200, "msg": "更新成功"})


def svc_change_password(user_id, data):
    """修改密码"""
    user = User.query.get(user_id)
    if not user:
        return jsonify({"code": 404, "msg": "用户不存在"}), 404

    old_password = data.get("old_password", "")
    new_password = data.get("new_password", "")

    if not old_password or not new_password:
        return jsonify({"code": 400, "msg": "旧密码和新密码不能为空"}), 400

    # 验证旧密码
    if not user.check_password(old_password):
        return jsonify({"code": 401, "msg": "旧密码错误"}), 401

    # 更新密码
    user.set_password(new_password)
    db.session.commit()

    return jsonify({"code": 200, "msg": "密码修改成功"})


def svc_delete_account(user_id):
    """注销账号（软删除）"""
    user = User.query.get(user_id)
    if not user:
        return jsonify({"code": 404, "msg": "用户不存在"}), 404

    # 软删除：将状态设置为已注销
    user.status = "已注销"
    db.session.commit()

    return jsonify({"code": 200, "msg": "账号已注销"})
