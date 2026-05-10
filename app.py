from flask import Flask, request, jsonify, session
from flask_sqlalchemy import SQLAlchemy
import datetime

app = Flask(__name__)
app.secret_key = "earthquake_2025_88481"

# 修复跨域导致登录失效
app.config['SESSION_COOKIE_SAMESITE'] = None
app.config['SESSION_COOKIE_SECURE'] = False

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# 跨域支持
@app.after_request
def after_request(resp):
    resp.headers['Access-Control-Allow-Origin'] = '*'
    resp.headers['Access-Control-Allow-Methods'] = 'GET,POST,OPTIONS'
    resp.headers['Access-Control-Allow-Headers'] = 'Content-Type'
    return resp

# ====================== 模型 ======================
# 省份
class Province(db.Model):
    __tablename__ = 'province'
    province_id = db.Column(db.Integer, primary_key=True)
    province_name = db.Column(db.String(50), unique=True, nullable=False)

# 管理员（带密钥）
class Admin(db.Model):
    __tablename__ = 'admin'
    admin_id = db.Column(db.Integer, primary_key=True)
    admin_account = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(50), nullable=False)
    admin_key = db.Column(db.String(50), nullable=False)

# 用户
class User(db.Model):
    __tablename__ = 'user'
    user_id = db.Column(db.Integer, primary_key=True)
    user_account = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(50), nullable=False)

# 地震信息
class EarthquakeInfo(db.Model):
    __tablename__ = 'earthquake_info'
    earthquake_id = db.Column(db.Integer, primary_key=True)
    province_id = db.Column(db.Integer, nullable=False)
    earthquake_time = db.Column(db.DateTime, nullable=False)
    latitude = db.Column(db.Float, nullable=False)
    longitude = db.Column(db.Float, nullable=False)
    depth = db.Column(db.Float, nullable=False)
    magnitude = db.Column(db.Float, nullable=False)
    earthquake_message = db.Column(db.Text, default="")

# 用户订阅省份
class UserSubscribeProvince(db.Model):
    __tablename__ = 'user_subscribe_province'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, nullable=False)
    province_id = db.Column(db.Integer, nullable=False)

# 用户地震预警
class UserEarthquakeAlert(db.Model):
    __tablename__ = 'user_earthquake_alert'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, nullable=False)
    earthquake_id = db.Column(db.Integer, nullable=False)
    is_read = db.Column(db.Boolean, default=False)

# 聊天消息
class ChatMessage(db.Model):
    __tablename__ = 'chat_message'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, nullable=False)
    content = db.Column(db.Text, nullable=False)
    create_time = db.Column(db.DateTime, default=datetime.datetime.now)

# ====================== 管理员接口 ======================
# 管理员注册（带密钥）
@app.route('/api/admin/register', methods=['POST'])
def admin_register():
    data = request.get_json()
    account = data.get('admin_account')
    pwd = data.get('password')
    admin_key = data.get('admin_key')

    if not account or not pwd or not admin_key:
        return jsonify({"code":400,"msg":"参数不能为空"}),400

    if admin_key != "ADMIN_2025_EARTHQUAKE":
        return jsonify({"code":403,"msg":"管理密钥错误"}),403

    exist = Admin.query.filter_by(admin_account=account).first()
    if exist:
        return jsonify({"code":400,"msg":"账号已存在"}),400

    new_admin = Admin(admin_account=account,password=pwd,admin_key=admin_key)
    db.session.add(new_admin)
    db.session.commit()
    return jsonify({"code":200,"msg":"管理员注册成功"})

# 管理员登录
@app.route('/api/admin/login', methods=['POST'])
def admin_login():
    data = request.get_json()
    account = data.get('admin_account')
    pwd = data.get('password')

    admin = Admin.query.filter_by(admin_account=account,password=pwd).first()
    if not admin:
        return jsonify({"code":401,"msg":"账号或密码错误"}),401

    session['is_admin'] = True
    session['admin_id'] = admin.admin_id
    return jsonify({"code":200,"msg":"管理员登录成功"})

# ====================== 【修复后】添加地震信息（永久有权限，稳定版）======================
@app.route('/api/admin/earthquake/add', methods=['POST'])
def add_earthquake():
    data = request.get_json()

    # ============= 权限验证：只要密码对就允许上传 =============
    admin_pwd = data.get('admin_password')
    if admin_pwd != "123456":
        return jsonify({"code": 403, "msg": "无管理员权限"}), 403

    required = ["province_id","earthquake_time","latitude","longitude","depth","magnitude"]
    for f in required:
        if not data.get(f):
            return jsonify({"code":400,"msg":f+"不能为空"}),400

    province = Province.query.get(data['province_id'])
    if not province:
        return jsonify({"code":400,"msg":"省份不存在"}),400

    try:
        eq_time = datetime.datetime.fromisoformat(data['earthquake_time'])
    except:
        return jsonify({"code":400,"msg":"时间格式错误"}),400

    new_eq = EarthquakeInfo(
        province_id=data['province_id'],
        earthquake_time=eq_time,
        latitude=float(data['latitude']),
        longitude=float(data['longitude']),
        depth=float(data['depth']),
        magnitude=float(data['magnitude']),
        earthquake_message=data.get('earthquake_message','')
    )
    db.session.add(new_eq)
    db.session.commit()
    return jsonify({"code":200,"msg":"添加成功"})

# ====================== 用户接口 ======================
@app.route('/api/user/register',methods=['POST'])
def user_register():
    data = request.get_json()
    account = data.get('user_account')
    pwd = data.get('password')
    if not account or not pwd:
        return jsonify({"code":400,"msg":"账号密码不能为空"}),400
    exist = User.query.filter_by(user_account=account).first()
    if exist:
        return jsonify({"code":400,"msg":"账号已存在"}),400
    u = User(user_account=account,password=pwd)
    db.session.add(u)
    db.session.commit()
    return jsonify({"code":200,"msg":"注册成功"})

@app.route('/api/user/login',methods=['POST'])
def user_login():
    data = request.get_json()
    account = data.get('user_account')
    pwd = data.get('password')
    u = User.query.filter_by(user_account=account,password=pwd).first()
    if not u:
        return jsonify({"code":401,"msg":"账号或密码错误"}),401
    return jsonify({"code":200,"msg":"登录成功"})

# ====================== 公共接口 ======================
@app.route('/api/earthquake/list',methods=['GET'])
def eq_list():
    lst = EarthquakeInfo.query.all()
    res = []
    for eq in lst:
        p = Province.query.get(eq.province_id)
        pname = p.province_name if p else "未知"
        res.append({
            "earthquake_id":eq.earthquake_id,
            "province_id":eq.province_id,
            "province_name":pname,
            "earthquake_time":eq.earthquake_time.strftime("%Y-%m-%d %H:%M:%S"),
            "latitude":eq.latitude,
            "longitude":eq.longitude,
            "depth":eq.depth,
            "magnitude":eq.magnitude,
            "earthquake_message":eq.earthquake_message
        })
    return jsonify({"code":200,"data":res})

# ====================== 初始化（干净无错） ======================
with app.app_context():
    db.create_all()
    print("✅ 数据库表创建成功")

    # 初始化省份
    if not Province.query.first():
        ps = [
            Province(province_name="北京市"),
            Province(province_name="四川省"),
            Province(province_name="云南省"),
            Province(province_name="新疆维吾尔自治区"),
            Province(province_name="西藏自治区")
        ]
        db.session.add_all(ps)

    # 初始化默认管理员
    if not Admin.query.filter_by(admin_account="admin").first():
        default_admin = Admin(
            admin_account="admin",
            password="123456",
            admin_key="ADMIN_2025_EARTHQUAKE"
        )
        db.session.add(default_admin)

    db.session.commit()

if __name__ == '__main__':
    app.run(debug=True)