from flask import request, jsonify, session
from models import db, Admin, User, EarthquakeInfo, Province
import datetime

def register_routes(app):

    # 跨域
    @app.after_request
    def after_request(resp):
        resp.headers["Access-Control-Allow-Origin"] = "*"
        resp.headers["Access-Control-Allow-Methods"] = "GET,POST,OPTIONS"
        resp.headers["Access-Control-Allow-Headers"] = "Content-Type"
        return resp

    # ====================== 管理员注册、登录 ======================
    @app.route('/api/admin/register', methods=['POST'])
    def admin_register():
        data = request.get_json()
        account = data.get('admin_account')
        pwd = data.get('password')
        admin_key = data.get('admin_key')
        if not account or not pwd or not admin_key:
            return jsonify({"code":400,"msg":"参数不能为空"}),400
        if admin_key != "ADMIN_2025_EARTHQUAKE":
            return jsonify({"code":403,"msg":"密钥错误"}),403
        if Admin.query.filter_by(admin_account=account).first():
            return jsonify({"code":400,"msg":"账号已存在"}),400
        new_admin = Admin(admin_account=account,password=pwd,admin_key=admin_key)
        db.session.add(new_admin)
        db.session.commit()
        return jsonify({"code":200,"msg":"注册成功"})

    @app.route('/api/admin/login', methods=['POST'])
    def admin_login():
        data = request.get_json()
        account = data.get('admin_account')
        pwd = data.get('password')
        admin = Admin.query.filter_by(admin_account=account,password=pwd).first()
        if not admin:
            return jsonify({"code":401,"msg":"账号或密码错误"}),401
        session['is_admin'] = True
        return jsonify({"code":200,"msg":"登录成功"})

    # ====================== 用户 ======================
    @app.route('/api/user/register', methods=['POST'])
    def user_register():
        data = request.get_json()
        account = data.get('user_account')
        pwd = data.get('password')
        if not account or not pwd:
            return jsonify({"code":400,"msg":"不能为空"}),400
        if User.query.filter_by(user_account=account).first():
            return jsonify({"code":400,"msg":"已存在"}),400
        u = User(user_account=account,password=pwd)
        db.session.add(u)
        db.session.commit()
        return jsonify({"code":200,"msg":"注册成功"})

    @app.route('/api/user/login', methods=['POST'])
    def user_login():
        data = request.get_json()
        account = data.get('user_account')
        pwd = data.get('password')
        u = User.query.filter_by(user_account=account,password=pwd).first()
        if not u:
            return jsonify({"code":401,"msg":"失败"}),401
        return jsonify({"code":200,"msg":"登录成功"})

    # ====================== 地震 增删改查 ======================
    @app.route('/api/admin/earthquake/add', methods=['POST'])
    def add_eq():
        data = request.get_json()
        token = data.get('admin_token')
        if not session.get('is_admin') and token != "ADMIN_2025_EARTHQUAKE":
            return jsonify({"code":403,"msg":"无权限"}),403
        req = ["province_id","earthquake_time","latitude","longitude","depth","magnitude"]
        for f in req:
            if not data.get(f):
                return jsonify({"code":400,"msg":"不能为空"}),400
        if not Province.query.get(data['province_id']):
            return jsonify({"code":400,"msg":"省份不存在"}),400
        try:
            t = datetime.datetime.fromisoformat(data['earthquake_time'])
        except:
            return jsonify({"code":400,"msg":"时间格式错误"}),400
        eq = EarthquakeInfo(
            province_id=data['province_id'],
            earthquake_time=t,
            latitude=data['latitude'],
            longitude=data['longitude'],
            depth=data['depth'],
            magnitude=data['magnitude'],
            earthquake_message=data.get('earthquake_message','')
        )
        db.session.add(eq)
        db.session.commit()
        return jsonify({"code":200,"msg":"添加成功"})

    @app.route('/api/admin/earthquake/update', methods=['POST'])
    def update_eq():
        data = request.get_json()
        token = data.get('admin_token')
        if not session.get('is_admin') and token != "ADMIN_2025_EARTHQUAKE":
            return jsonify({"code":403,"msg":"无权限"}),403
        eq = EarthquakeInfo.query.get(data.get('earthquake_id'))
        if not eq: return jsonify({"code":400,"msg":"不存在"}),400
        if data.get('province_id'): eq.province_id = data['province_id']
        if data.get('latitude'): eq.latitude = data['latitude']
        if data.get('longitude'): eq.longitude = data['longitude']
        if data.get('depth'): eq.depth = data['depth']
        if data.get('magnitude'): eq.magnitude = data['magnitude']
        if data.get('earthquake_message'): eq.earthquake_message = data['earthquake_message']
        if data.get('earthquake_time'):
            eq.earthquake_time = datetime.datetime.fromisoformat(data['earthquake_time'])
        db.session.commit()
        return jsonify({"code":200,"msg":"修改成功"})

    @app.route('/api/admin/earthquake/delete', methods=['POST'])
    def delete_eq():
        data = request.get_json()
        token = data.get('admin_token')
        if not session.get('is_admin') and token != "ADMIN_2025_EARTHQUAKE":
            return jsonify({"code":403,"msg":"无权限"}),403
        eq = EarthquakeInfo.query.get(data.get('earthquake_id'))
        if not eq: return jsonify({"code":400,"msg":"不存在"}),400
        db.session.delete(eq)
        db.session.commit()
        return jsonify({"code":200,"msg":"删除成功"})

    @app.route('/api/earthquake/list', methods=['GET'])
    def list_eq():
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
        return jsonify({"code":200,"data":res})