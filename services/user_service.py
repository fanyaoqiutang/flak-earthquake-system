from flask import request, jsonify, session
from flask_login import login_user, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
import secrets
from models import db, User, UserSubscribeProvince, UserEarthquakeAlert, Province, EarthquakeInfo,UserFeedback,ChatMessage

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
    login_user(u)
    session['user_id'] = u.user_id
    session['user_account'] = u.user_account
    token = secrets.token_hex(32)
    session['user_token'] = token
    return jsonify({"code": 200, "msg": "登录成功", "data": {"user_id": u.user_id, "user_account": u.user_account, "user_token": token}})

def svc_user_logout():
    logout_user()
    session.clear()
    return jsonify({"code": 200, "msg": "退出成功"})

def svc_user_info():
    return jsonify({"code": 200, "data": {"user_id": current_user.user_id, "user_account": current_user.user_account}})

def svc_subscribe_province():
    data = request.get_json(force=True)
    province_id = data.get('province_id')

    # 这里加一个判断：如果是空字符串，也视为有值
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

    user_id = current_user.user_id
    existing = UserSubscribeProvince.query.filter_by(user_id=user_id, province_id=province_id).first()
    if existing:
        return jsonify({"code": 400, "msg": "已订阅该省份"}), 400

    sub = UserSubscribeProvince(user_id=user_id, province_id=province_id)
    db.session.add(sub)
    db.session.commit()
    return jsonify({"code": 200, "msg": "订阅成功"})

def svc_unsubscribe_province(subscribe_id):
    sub = UserSubscribeProvince.query.get(subscribe_id)
    if not sub or sub.user_id != current_user.user_id:
        return jsonify({"code": 403, "msg": "无权限"}), 403
    db.session.delete(sub)
    db.session.commit()
    return jsonify({"code": 200, "msg": "取消订阅成功"})

def svc_get_subscriptions():
    subs = UserSubscribeProvince.query.filter_by(user_id=current_user.user_id).all()
    res = []
    for s in subs:
        p = Province.query.get(s.province_id)
        res.append({"id": s.id, "province_id": s.province_id, "province_name": p.province_name if p else "未知"})
    return jsonify({"code": 200, "data": res})

def svc_get_user_alerts():
    alerts = UserEarthquakeAlert.query.filter_by(user_id=current_user.user_id).order_by(UserEarthquakeAlert.id.desc()).all()
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
    cnt = UserEarthquakeAlert.query.filter_by(user_id=current_user.user_id, is_read=False).count()
    return jsonify({"code": 200, "data": {"unread_count": cnt}})

def svc_mark_alert_read(alert_id):
    a = UserEarthquakeAlert.query.get(alert_id)
    if not a or a.user_id != current_user.user_id:
        return jsonify({"code": 403, "msg": "无权限"}), 403
    a.is_read = True
    db.session.commit()
    return jsonify({"code": 200, "msg": "已标记已读"})

def svc_mark_all_alerts_read():
    alerts = UserEarthquakeAlert.query.filter_by(user_id=current_user.user_id, is_read=False).all()
    for a in alerts:
        a.is_read = True
    db.session.commit()
    return jsonify({"code": 200, "msg": "全部已读"})

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
        user = User.query.get(m.user_id)
        username = user.user_account if user else "未知用户"

        res.append({
            "user_id": m.user_id,
            "username": username,
            "content": m.content,
            "create_time": m.create_time.strftime("%Y-%m-%d %H:%M:%S")
        })

    return jsonify({"code": 200, "data": res})