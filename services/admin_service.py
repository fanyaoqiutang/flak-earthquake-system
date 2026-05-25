from flask import request, jsonify, session
from werkzeug.security import generate_password_hash, check_password_hash
import secrets, datetime
from models import db, Admin, EarthquakeInfo, Province,ChatMessage,UserFeedback,User, AdminOperationLog, UserSubscribeProvince, UserEarthquakeAlert
from sqlalchemy import func,desc

ADMIN_SECRET_KEY = "ADMIN_2025_EARTHQUAKE"

def verify_admin():
    if session.get('is_admin'):
        return True
    data = request.get_json(silent=True) or {}
    token = data.get('admin_token')
    if token and token == session.get('admin_token'):
        return True
    return False

def add_admin_log(admin_id, operation, target_earthquake_id=None, remark=""):
    log = AdminOperationLog(
        admin_id=admin_id,
        operation=operation,
        target_earthquake_id=target_earthquake_id,
    )
    db.session.add(log)
    db.session.commit()

def generate_alerts(earthquake_id):
    eq = EarthquakeInfo.query.get(earthquake_id)
    if not eq or eq.magnitude < 4.0:
        return False
    subscribers = UserSubscribeProvince.query.filter_by(province_id=eq.province_id).all()
    cnt = 0
    for sub in subscribers:
        exist = UserEarthquakeAlert.query.filter_by(user_id=sub.user_id, earthquake_id=earthquake_id).first()
        if not exist:
            a = UserEarthquakeAlert(user_id=sub.user_id, earthquake_id=earthquake_id)
            db.session.add(a)
            cnt +=1
    if cnt>0:
        db.session.commit()
    return cnt>0

def svc_admin_register():
    data = request.get_json(force=True)
    account = data.get('admin_account')
    pwd = data.get('password')
    admin_key = data.get('admin_key')
    if not account or not pwd or not admin_key:
        return jsonify({"code": 400, "msg": "参数不能为空"}), 400
    if len(account) < 3 or len(account) > 20:
        return jsonify({"code": 400, "msg": "账号长度3-20位"}), 400
    if len(pwd) < 6:
        return jsonify({"code": 400, "msg": "密码长度至少6位"}), 400
    if admin_key != ADMIN_SECRET_KEY:
        return jsonify({"code": 403, "msg": "密钥错误"}), 403
    if Admin.query.filter_by(admin_account=account).first():
        return jsonify({"code": 400, "msg": "账号已存在"}), 400
    hashed_pwd = generate_password_hash(pwd)
    new_admin = Admin(admin_account=account, password=hashed_pwd, admin_key=admin_key)
    db.session.add(new_admin)
    db.session.commit()
    return jsonify({"code": 200, "msg": "注册成功"})

def svc_admin_login():
    data = request.get_json(force=True)
    account = data.get('admin_account')
    pwd = data.get('password')
    if not account or not pwd:
        return jsonify({"code": 400, "msg": "参数不能为空"}), 400
    admin = Admin.query.filter_by(admin_account=account).first()
    if not admin or not check_password_hash(admin.password, pwd):
        return jsonify({"code": 401, "msg": "账号或密码错误"}), 401
    session['is_admin'] = True
    session['admin_id'] = admin.admin_id
    session['admin_account'] = admin.admin_account
    token = secrets.token_hex(32)
    session['admin_token'] = token
    return jsonify({"code": 200, "msg": "登录成功", "data": {"admin_token": token, "admin_account": admin.admin_account}})

def svc_admin_logout():
    session.clear()
    return jsonify({"code": 200, "msg": "退出成功"})

def svc_admin_info():
    if not session.get('is_admin'):
        return jsonify({"code": 401, "msg": "未登录"}), 401
    return jsonify({"code": 200, "data": {"admin_id": session.get("admin_id"), "admin_account": session.get("admin_account")}})

def svc_add_earthquake():
    if not verify_admin():
        return jsonify({"code": 403, "msg": "无权限，请先以管理员身份登录"}), 403
    data = request.get_json(force=True)
    req = ["province_id", "earthquake_time", "latitude", "longitude", "depth", "magnitude"]
    for f in req:
        if not data.get(f):
            return jsonify({"code": 400, "msg": f"参数 {f} 不能为空"}), 400
    try:
        province_id = int(data['province_id'])
        latitude = float(data['latitude'])
        longitude = float(data['longitude'])
        depth = float(data['depth'])
        magnitude = float(data['magnitude'])
    except:
        return jsonify({"code": 400, "msg": "数值格式错误"}), 400
    if not Province.query.get(province_id):
        return jsonify({"code": 400, "msg": "省份不存在"}), 400
    try:
        t = datetime.datetime.fromisoformat(data['earthquake_time'])
    except:
        return jsonify({"code": 400, "msg": "时间格式错误，请使用 YYYY-MM-DD HH:MM:SS"}), 400
    eq = EarthquakeInfo(province_id=province_id, earthquake_time=t, latitude=latitude, longitude=longitude, depth=depth, magnitude=magnitude, earthquake_message=data.get('earthquake_message', ''))
    db.session.add(eq)
    db.session.commit()
    add_admin_log(session.get('admin_id'), "添加地震", eq.earthquake_id)
    generate_alerts(eq.earthquake_id)
    return jsonify({"code": 200, "msg": "添加成功"})

def svc_update_earthquake():
    if not verify_admin():
        return jsonify({"code": 403, "msg": "无权限，请先以管理员身份登录"}), 403

    data = request.get_json()
    earthquake_id = data.get('earthquake_id')

    if not earthquake_id:
        return jsonify({"code": 400, "msg": "地震ID不能为空"}), 400

    eq = EarthquakeInfo.query.get(earthquake_id)
    if not eq:
        return jsonify({"code": 404, "msg": "地震记录不存在"}), 404

    if data.get('province_id'):
        try:
            pid = int(data.get('province_id'))
            if Province.query.get(pid):
                eq.province_id = pid
        except:
            pass

    if data.get('earthquake_time'):
        try:
            eq.earthquake_time = datetime.datetime.fromisoformat(data.get('earthquake_time'))
        except:
            pass

    if data.get('latitude'):
        try:
            eq.latitude = float(data.get('latitude'))
        except:
            pass

    if data.get('longitude'):
        try:
            eq.longitude = float(data.get('longitude'))
        except:
            pass

    if data.get('depth'):
        try:
            eq.depth = float(data.get('depth'))
        except:
            pass

    if data.get('magnitude'):
        try:
            eq.magnitude = float(data.get('magnitude'))
        except:
            pass

    if data.get('earthquake_message') is not None:
        eq.earthquake_message = data.get('earthquake_message')

    db.session.commit()

    add_admin_log(session.get('admin_id'), "修改地震", eq.earthquake_id)
    return jsonify({"code": 200, "msg": "修改成功"})

def svc_delete_earthquake():
    if not verify_admin():
        return jsonify({"code": 403, "msg": "无权限，请先以管理员身份登录"}), 403
    data = request.get_json(force=True)
    if not data.get('earthquake_id'):
        return jsonify({"code": 400, "msg": "地震ID不能为空"}), 400
    eq = EarthquakeInfo.query.get(data.get('earthquake_id'))
    if not eq:
        return jsonify({"code": 400, "msg": "地震记录不存在"}), 400
    db.session.delete(eq)
    db.session.commit()
    add_admin_log(session.get('admin_id'), "删除地震", eq.earthquake_id)
    return jsonify({"code": 200, "msg": "删除成功"})

# ==========================
# 【升级】用户管理（支持搜索、状态、最后活跃）
# ==========================
def svc_admin_get_all_users():
    if not verify_admin():
        return jsonify({"code": 403, "msg": "无管理员权限"}), 403

    keyword = request.args.get("keyword")
    status = request.args.get("status")

    query = User.query

    if status:
        query = query.filter_by(status=status)
    if keyword:
        query = query.filter(
            (User.user_account.like(f"%{keyword}%")) |
            (User.phone.like(f"%{keyword}%"))
        )

    users = query.all()
    data = []
    now = datetime.datetime.now()

    for u in users:
        subs = UserSubscribeProvince.query.filter_by(user_id=u.user_id).all()
        provinces = []
        for s in subs:
            p = Province.query.get(s.province_id)
            if p:
                provinces.append(p.province_name)

        # 最后活跃时间格式化
        if u.last_active_time:
            delta = now - u.last_active_time
            if delta.days >= 1:
                last = f"{delta.days}天前"
            elif delta.seconds >= 3600:
                last = f"{delta.seconds//3600}小时前"
            elif delta.seconds >= 60:
                last = f"{delta.seconds//60}分钟前"
            else:
                last = "刚刚"
        else:
            last = "未知"

        data.append({
            "user_id": u.user_id,
            "user_account": u.user_account,
            "phone": u.phone or "未绑定",
            "status": u.status,
            "create_time": u.create_time.strftime("%Y-%m-%d %H:%M:%S"),
            "last_active": last,
            "subscribed_provinces": provinces
        })
    return jsonify({"code": 200, "data": data})

# ==========================
# 【新增】用户统计（总用户/活跃/禁用）
# ==========================
def svc_admin_get_user_stats():
    if not verify_admin():
        return jsonify({"code":403,"msg":"无权限"}),403

    now = datetime.datetime.now()
    thirty_days_ago = now - datetime.timedelta(days=30)

    total = User.query.count()
    active = User.query.filter(User.last_active_time >= thirty_days_ago).count()
    disabled = User.query.filter_by(status="禁用").count()

    return jsonify({
        "code":200,
        "data":{
            "total_users":total,
            "active_users":active,
            "disabled_users":disabled
        }
    })

# ==========================
# 【新增】切换用户状态（正常/禁用）
# ==========================
def svc_admin_toggle_user_status(user_id):
    if not verify_admin():
        return jsonify({"code":403,"msg":"无权限"}),403
    u = User.query.get(user_id)
    if not u:
        return jsonify({"code":404,"msg":"用户不存在"}),404
    u.status = "禁用" if u.status == "正常" else "正常"
    db.session.commit()
    return jsonify({"code":200,"msg":"状态已更新"})

def svc_admin_delete_user(user_id):
    if not verify_admin():
        return jsonify({"code": 403, "msg": "无权限"}), 403

    user = User.query.get(user_id)
    if not user:
        return jsonify({"code": 404, "msg": "用户不存在"}), 404

    UserSubscribeProvince.query.filter_by(user_id=user_id).delete()
    UserFeedback.query.filter_by(user_id=user_id).delete()
    ChatMessage.query.filter_by(user_id=user_id).delete()

    db.session.delete(user)
    db.session.commit()
    return jsonify({"code": 200, "msg": "用户已删除"})

# ==========================
# 反馈管理
# ==========================
def svc_admin_get_all_feedbacks():
    if not verify_admin():
        return jsonify({"code": 403, "msg": "无权限"}), 403

    fs = UserFeedback.query.order_by(desc(UserFeedback.submit_time)).all()
    res = []
    for f in fs:
        u = User.query.get(f.user_id)
        res.append({
            "feedback_id": f.id,
            "user_id": f.user_id,
            "user_account": u.user_account if u else "已注销",
            "feedback_type": f.feedback_type,
            "content": f.content,
            "priority": f.priority,
            "status": f.status,
            "submit_time": f.submit_time.strftime("%Y-%m-%d %H:%M:%S"),
            "handle_time": f.handle_time.strftime("%Y-%m-%d %H:%M:%S") if f.handle_time else None
        })
    return jsonify({"code": 200, "data": res})

def svc_admin_handle_feedback(feedback_id):
    if not verify_admin():
        return jsonify({"code": 403, "msg": "无权限"}), 403

    fb = UserFeedback.query.get(feedback_id)
    if not fb:
        return jsonify({"code": 404, "msg": "反馈不存在"}), 404

    fb.status = "已处理"
    fb.handle_time = datetime.datetime.now()
    db.session.commit()
    return jsonify({"code": 200, "msg": "已处理"})

# ==========================
# 聊天消息管理
# ==========================
def svc_admin_get_all_chat_messages():
    if not verify_admin():
        return jsonify({"code": 403, "msg": "无权限"}), 403

    ms = ChatMessage.query.order_by(desc(ChatMessage.create_time)).all()
    res = []
    for m in ms:
        u = User.query.get(m.user_id)
        res.append({
            "msg_id": m.id,
            "user_id": m.user_id,
            "user_account": u.user_account if u else "已注销",
            "content": m.content,
            "create_time": m.create_time.strftime("%Y-%m-%d %H:%M:%S")
        })
    return jsonify({"code": 200, "data": res})

def svc_admin_delete_chat_msg(msg_id):
    if not verify_admin():
        return jsonify({"code": 403, "msg": "无权限"}), 403

    msg = ChatMessage.query.get(msg_id)
    if not msg:
        return jsonify({"code": 404, "msg": "消息不存在"}), 404

    db.session.delete(msg)
    db.session.commit()
    return jsonify({"code": 200, "msg": "删除成功"})