# # 接口文件
from flask import request, jsonify, session
from models import db, Admin, User, EarthquakeInfo, Province, UserSubscribeProvince, UserEarthquakeAlert
import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import login_user, logout_user, login_required, current_user
import secrets


def register_routes(app):
    @app.after_request
    def after_request(resp):
        resp.headers["Access-Control-Allow-Origin"] = "*"
        resp.headers["Access-Control-Allow-Methods"] = "GET,POST,OPTIONS"
        resp.headers["Access-Control-Allow-Headers"] = "Content-Type"
        return resp

    # ====================== 管理员注册 ======================
    @app.route('/api/admin/register', methods=['POST'])
    def admin_register():
        data = request.get_json()
        account = data.get('admin_account')
        pwd = data.get('password')
        admin_key = data.get('admin_key')

        if not account or not pwd or not admin_key:
            return jsonify({"code": 400, "msg": "参数不能为空"}), 400

        if len(account) < 3 or len(account) > 20:
            return jsonify({"code": 400, "msg": "账号长度3-20位"}), 400

        if len(pwd) < 6:
            return jsonify({"code": 400, "msg": "密码长度至少6位"}), 400

        if admin_key != "ADMIN_2025_EARTHQUAKE":
            return jsonify({"code": 403, "msg": "密钥错误"}), 403

        if Admin.query.filter_by(admin_account=account).first():
            return jsonify({"code": 400, "msg": "账号已存在"}), 400

        hashed_pwd = generate_password_hash(pwd)
        new_admin = Admin(
            admin_account=account,
            password=hashed_pwd,
            admin_key=admin_key
        )
        db.session.add(new_admin)
        db.session.commit()
        return jsonify({"code": 200, "msg": "注册成功"})
    # ======================= 管理员登录 ======================
    @app.route('/api/admin/login', methods=['POST'])
    def admin_login():
        data = request.get_json()
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

        return jsonify({
            "code": 200,
            "msg": "登录成功",
            "data": {
                "admin_token": token,
                "admin_account": admin.admin_account
            }
        })

    # ======================管理员登出======================
    @app.route('/api/admin/logout', methods=['POST'])
    def admin_logout():
        session.clear()
        return jsonify({"code": 200, "msg": "退出成功"})
    # ====================== 获取当前登录信息 ======================
    @app.route('/api/admin/info', methods=['GET'])
    def admin_info():
        if not session.get('is_admin'):
            return jsonify({"code": 401, "msg": "未登录"}), 401

        return jsonify({
            "code": 200,
            "data": {
                "admin_id": session.get('admin_id'),
                "admin_account": session.get('admin_account')
            }
        })

    # ====================== 用户注册 ======================
    @app.route('/api/user/register', methods=['POST'])
    def user_register():
        data = request.get_json()
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
    # ====================== 用户登录 ======================
    @app.route('/api/user/login', methods=['POST'])
    def user_login():
        data = request.get_json()
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

        return jsonify({
            "code": 200,
            "msg": "登录成功",
            "data": {
                "user_id": u.user_id,
                "user_account": u.user_account,
                "user_token": token
            }
        })
    # ====================== 用户登出 ======================
    @app.route('/api/user/logout', methods=['POST'])
    @login_required
    def user_logout():
        logout_user()
        session.clear()
        return jsonify({"code": 200, "msg": "退出成功"})

    # ====================== 获取当前用户登录状态 ======================
    @app.route('/api/user/info', methods=['GET'])
    @login_required
    def user_info():
        return jsonify({
            "code": 200,
            "data": {
                "user_id": current_user.user_id,
                "user_account": current_user.user_account
            }
        })

    # ====================== 身份验证 ======================
    def verify_admin():
        """验证管理员权限"""
        if session.get('is_admin'):
            return True

        data = request.get_json(silent=True) or {}
        token = data.get('admin_token')

        if token and token == session.get('admin_token'):
            return True

        return False
    # ====================== 添加地震信息 ======================
    @app.route('/api/admin/earthquake/add', methods=['POST'])
    def add_eq():
        if not verify_admin():
            return jsonify({"code": 403, "msg": "无权限，请先以管理员身份登录"}), 403

        data = request.get_json()

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
        except (ValueError, TypeError):
            return jsonify({"code": 400, "msg": "数值格式错误"}), 400

        if not Province.query.get(province_id):
            return jsonify({"code": 400, "msg": "省份不存在"}), 400

        try:
            t = datetime.datetime.fromisoformat(data['earthquake_time'])
        except:
            return jsonify({"code": 400, "msg": "时间格式错误，请使用 YYYY-MM-DD HH:MM:SS 格式"}), 400

        eq = EarthquakeInfo(
            province_id=province_id,
            earthquake_time=t,
            latitude=latitude,
            longitude=longitude,
            depth=depth,
            magnitude=magnitude,
            earthquake_message=data.get('earthquake_message', '')
        )
        db.session.add(eq)
        db.session.commit()
        # 触发预警检查
        try:
            generate_alerts(eq.earthquake_id)
        except Exception as e:
            print(f"[预警生成错误] {e}")

        return jsonify({"code": 200, "msg": "添加成功"})

     # ====================== 修改地震信息 ======================
    @app.route('/api/admin/earthquake/update', methods=['POST'])
    def update_eq():
        if not verify_admin():
            return jsonify({"code": 403, "msg": "无权限，请先以管理员身份登录"}), 403

        data = request.get_json()

        if not data.get('earthquake_id'):
            return jsonify({"code": 400, "msg": "地震ID不能为空"}), 400

        eq = EarthquakeInfo.query.get(data.get('earthquake_id'))
        if not eq:
            return jsonify({"code": 400, "msg": "地震记录不存在"}), 400

        if data.get('province_id'):
            try:
                province_id = int(data['province_id'])
                if not Province.query.get(province_id):
                    return jsonify({"code": 400, "msg": "省份不存在"}), 400
                eq.province_id = province_id
            except (ValueError, TypeError):
                return jsonify({"code": 400, "msg": "省份ID格式错误"}), 400

        if data.get('latitude'):
            try:
                eq.latitude = float(data['latitude'])
            except (ValueError, TypeError):
                return jsonify({"code": 400, "msg": "纬度格式错误"}), 400

        if data.get('longitude'):
            try:
                eq.longitude = float(data['longitude'])
            except (ValueError, TypeError):
                return jsonify({"code": 400, "msg": "经度格式错误"}), 400

        if data.get('depth'):
            try:
                eq.depth = float(data['depth'])
            except (ValueError, TypeError):
                return jsonify({"code": 400, "msg": "深度格式错误"}), 400

        if data.get('magnitude'):
            try:
                eq.magnitude = float(data['magnitude'])
            except (ValueError, TypeError):
                return jsonify({"code": 400, "msg": "震级格式错误"}), 400

        if data.get('earthquake_message'):
            eq.earthquake_message = data['earthquake_message']

        if data.get('earthquake_time'):
            try:
                eq.earthquake_time = datetime.datetime.fromisoformat(data['earthquake_time'])
            except:
                return jsonify({"code": 400, "msg": "时间格式错误"}), 400

        db.session.commit()
        return jsonify({"code": 200, "msg": "修改成功"})

    # ====================== 删除地震信息 ======================
    @app.route('/api/admin/earthquake/delete', methods=['POST'])
    def delete_eq():
        if not verify_admin():
            return jsonify({"code": 403, "msg": "无权限，请先以管理员身份登录"}), 403

        data = request.get_json()

        if not data.get('earthquake_id'):
            return jsonify({"code": 400, "msg": "地震ID不能为空"}), 400

        eq = EarthquakeInfo.query.get(data.get('earthquake_id'))
        if not eq:
            return jsonify({"code": 400, "msg": "地震记录不存在"}), 400

        db.session.delete(eq)
        db.session.commit()
        return jsonify({"code": 200, "msg": "删除成功"})

    # ====================== 列出地震信息 ======================
    @app.route('/api/earthquake/list', methods=['GET'])
    def list_eq():
        province_id = request.args.get('province_id')

        if province_id:
            try:
                province_id = int(province_id)
                lst = EarthquakeInfo.query.filter_by(province_id=province_id).all()
            except:
                return jsonify({"code":400,"msg":"省份ID格式错误"}),400
        else:
            lst = EarthquakeInfo.query.all()

        res = []
        for eq in lst:
            p = Province.query.get(eq.province_id)
            res.append({
                "earthquake_id": eq.earthquake_id,
                "province_id": eq.province_id,
                "province_name": p.province_name if p else "未知",
                "earthquake_time": eq.earthquake_time.strftime("%Y-%m-%d %H:%M:%S"),
                "latitude": eq.latitude,
                "longitude": eq.longitude,
                "depth": eq.depth,
                "magnitude": eq.magnitude,
                "earthquake_message": eq.earthquake_message
            })

        return jsonify({"code":200,"data":res,"total":len(res)})

    # ====================== 用户订阅省份 ======================
    @app.route('/api/user/subscribe', methods=['POST'])
    @login_required
    def subscribe_province():
        """用户订阅省份"""
        data = request.get_json()
        province_id = data.get('province_id')

        if not province_id:
            return jsonify({"code":400,"msg":"省份ID不能为空"}),400

        try:
            province_id = int(province_id)
        except:
            return jsonify({"code":400,"msg":"省份ID格式错误"}),400

        if not Province.query.get(province_id):
            return jsonify({"code":400,"msg":"省份不存在"}),400

        user_id = current_user.user_id

        existing = UserSubscribeProvince.query.filter_by(
            user_id=user_id,
            province_id=province_id
        ).first()

        if existing:
            return jsonify({"code":400,"msg":"已订阅该省份"}),400

        subscription = UserSubscribeProvince(
            user_id=user_id,
            province_id=province_id
        )
        db.session.add(subscription)
        db.session.commit()

        return jsonify({"code":200,"msg":"订阅成功"})

    @app.route('/api/user/subscribe/<int:subscribe_id>', methods=['DELETE'])
    @login_required
    def unsubscribe_province(subscribe_id):
        """取消订阅省份"""
        subscription = UserSubscribeProvince.query.get(subscribe_id)

        if not subscription:
            return jsonify({"code":400,"msg":"订阅记录不存在"}),400

        if subscription.user_id != current_user.user_id:
            return jsonify({"code":403,"msg":"无权限"}),403

        db.session.delete(subscription)
        db.session.commit()

        return jsonify({"code":200,"msg":"取消订阅成功"})

    @app.route('/api/user/subscriptions', methods=['GET'])
    @login_required
    def get_subscriptions():
        """获取用户的订阅列表"""
        user_id = current_user.user_id
        subscriptions = UserSubscribeProvince.query.filter_by(user_id=user_id).all()

        res = []
        for sub in subscriptions:
            province = Province.query.get(sub.province_id)
            res.append({
                "id": sub.id,
                "province_id": sub.province_id,
                "province_name": province.province_name if province else "未知"
            })

        return jsonify({"code":200,"data":res,"total":len(res)})

    @app.route('/api/provinces', methods=['GET'])
    def get_all_provinces():
        """获取所有省份列表（用于订阅选择）"""
        provinces = Province.query.all()
        res = []
        for p in provinces:
            res.append({
                "province_id": p.province_id,
                "province_name": p.province_name
            })
        return jsonify({"code":200,"data":res,"total":len(res)})

    # ====================== 预警系统 ======================
    def generate_alerts(earthquake_id):
        """预警自动生成逻辑"""
        earthquake = EarthquakeInfo.query.get(earthquake_id)

        if not earthquake:
            return False

        # 预警触发条件：震级 >= 4.0
        if earthquake.magnitude < 4.0:
            return False

        # 查找订阅了该省份的所有用户
        subscribers = UserSubscribeProvince.query.filter_by(
            province_id=earthquake.province_id
        ).all()

        if not subscribers:
            return False

        # 为每个订阅用户生成预警记录
        alert_count = 0
        for sub in subscribers:
            existing_alert = UserEarthquakeAlert.query.filter_by(
                user_id=sub.user_id,
                earthquake_id=earthquake_id
            ).first()

            if not existing_alert:
                alert = UserEarthquakeAlert(
                    user_id=sub.user_id,
                    earthquake_id=earthquake_id,
                    is_read=False
                )
                db.session.add(alert)
                alert_count += 1

        if alert_count > 0:
            db.session.commit()
            print(f"[预警] 地震ID {earthquake_id} 触发了 {alert_count} 条预警")

        return alert_count > 0

    @app.route('/api/user/alerts', methods=['GET'])
    @login_required
    def get_user_alerts():
        """获取用户的所有预警消息"""
        user_id = current_user.user_id

        alerts = UserEarthquakeAlert.query.filter_by(user_id=user_id).order_by(
            UserEarthquakeAlert.id.desc()
        ).all()

        res = []
        for alert in alerts:
            earthquake = EarthquakeInfo.query.get(alert.earthquake_id)
            province = Province.query.get(earthquake.province_id) if earthquake else None

            res.append({
                "alert_id": alert.id,
                "earthquake_id": alert.earthquake_id,
                "is_read": alert.is_read,
                "province_name": province.province_name if province else "未知",
                "magnitude": earthquake.magnitude if earthquake else 0,
                "earthquake_time": earthquake.earthquake_time.strftime("%Y-%m-%d %H:%M:%S") if earthquake else "",
                "earthquake_message": earthquake.earthquake_message if earthquake else ""
            })

        return jsonify({"code":200,"data":res,"total":len(res)})

    @app.route('/api/user/alerts/unread', methods=['GET'])
    @login_required
    def get_unread_alerts_count():
        """获取未读预警数量"""
        user_id = current_user.user_id
        count = UserEarthquakeAlert.query.filter_by(
            user_id=user_id,
            is_read=False
        ).count()

        return jsonify({"code":200,"data":{"unread_count":count}})

    @app.route('/api/user/alerts/<int:alert_id>/read', methods=['POST'])
    @login_required
    def mark_alert_read(alert_id):
        """标记预警为已读"""
        alert = UserEarthquakeAlert.query.get(alert_id)

        if not alert:
            return jsonify({"code":400,"msg":"预警记录不存在"}),400

        if alert.user_id != current_user.user_id:
            return jsonify({"code":403,"msg":"无权限"}),403

        alert.is_read = True
        db.session.commit()

        return jsonify({"code":200,"msg":"已标记为已读"})

    @app.route('/api/user/alerts/read-all', methods=['POST'])
    @login_required
    def mark_all_alerts_read():
        """标记所有预警为已读"""
        user_id = current_user.user_id

        alerts = UserEarthquakeAlert.query.filter_by(
            user_id=user_id,
            is_read=False
        ).all()

        for alert in alerts:
            alert.is_read = True

        db.session.commit()

        return jsonify({"code":200,"msg":f"已标记 {len(alerts)} 条预警为已读"})
