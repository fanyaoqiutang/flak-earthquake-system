from flask import request, jsonify, session
from werkzeug.security import generate_password_hash, check_password_hash
import secrets, datetime
from models import db, Admin, EarthquakeInfo, Province, AdminOperationLog, UserSubscribeProvince, UserEarthquakeAlert

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
        remark=remark
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
    data = request.get_json(force=True)
    if not data.get('earthquake_id'):
        return jsonify({"code": 400, "msg": "地震ID不能为空"}), 400
    eq = EarthquakeInfo.query.get(data.get('earthquake_id'))
    if not eq:
        return jsonify({"code": 400, "msg": "地震记录不存在"}), 400
    if data.get('province_id'):
        try:
            pid = int(data['province_id'])
            if not Province.query.get(pid):
                return jsonify({"code": 400, "msg": "省份不存在"}), 400
            eq.province_id = pid
        except:
            return jsonify({"code": 400, "msg": "省份ID格式错误"}), 400
    if data.get('latitude'):
        try: eq.latitude = float(data['latitude'])
        except: return jsonify({"code": 400, "msg": "纬度格式错误"}), 400
    if data.get('longitude'):
        try: eq.longitude = float(data['longitude'])
        except: return jsonify({"code": 400, "msg": "经度格式错误"}), 400
    if data.get('depth'):
        try: eq.depth = float(data['depth'])
        except: return jsonify({"code": 400, "msg": "深度格式错误"}), 400
    if data.get('magnitude'):
        try: eq.magnitude = float(data['magnitude'])
        except: return jsonify({"code": 400, "msg": "震级格式错误"}), 400
    if data.get('earthquake_message'):
        eq.earthquake_message = data['earthquake_message']
    if data.get('earthquake_time'):
        try:
            eq.earthquake_time = datetime.datetime.fromisoformat(data['earthquake_time'])
        except:
            return jsonify({"code": 400, "msg": "时间格式错误"}), 400
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