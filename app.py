from flask import Flask,render_template
from flask_login import LoginManager
from flask_cors import CORS
from models import db, User, Admin
# 导入蓝图
from routes.admin_routes import admin_bp
from routes.user_routes import user_bp
from routes.common_routes import common_bp

app = Flask(__name__)
CORS(app, supports_credentials=True)
app.secret_key = "earthquake_2025_secure_key_change_in_production"
app.config['SESSION_COOKIE_SAMESITE'] = None
app.config['SESSION_COOKIE_SECURE'] = False
# 通过URL链接数据库
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.session_protection = "strong"
login_manager.login_message = "请先登录"

@login_manager.user_loader
def load_user(user_id):
    user = User.query.get(int(user_id))
    if user:
        return user
    admin = Admin.query.get(int(user_id))
    return admin

@app.route('/')
def login():
    return render_template('LOGIN.html')

# 注册所有蓝图,用于模块划分
app.register_blueprint(admin_bp)
app.register_blueprint(user_bp)
app.register_blueprint(common_bp)

# 初始化数据
with app.app_context():
    db.create_all()
    from models import Province
    if not Province.query.first():
        # 👇 我只改了这里：给每个省份自动填上【所属大区 region】
        provinces = [
            # 华北
            Province(province_name="北京市", region="华北地区"),
            Province(province_name="天津市", region="华北地区"),
            Province(province_name="河北省", region="华北地区"),
            Province(province_name="山西省", region="华北地区"),
            Province(province_name="内蒙古自治区", region="华北地区"),

            # 东北
            Province(province_name="辽宁省", region="东北地区"),
            Province(province_name="吉林省", region="东北地区"),
            Province(province_name="黑龙江省", region="东北地区"),

            # 华东
            Province(province_name="上海市", region="华东地区"),
            Province(province_name="江苏省", region="华东地区"),
            Province(province_name="浙江省", region="华东地区"),
            Province(province_name="安徽省", region="华东地区"),
            Province(province_name="福建省", region="华东地区"),
            Province(province_name="江西省", region="华东地区"),
            Province(province_name="山东省", region="华东地区"),

            # 华中
            Province(province_name="河南省", region="华中地区"),
            Province(province_name="湖北省", region="华中地区"),
            Province(province_name="湖南省", region="华中地区"),

            # 华南
            Province(province_name="广东省", region="华南地区"),
            Province(province_name="广西壮族自治区", region="华南地区"),
            Province(province_name="海南省", region="华南地区"),

            # 西南
            Province(province_name="重庆市", region="西南地区"),
            Province(province_name="四川省", region="西南地区"),
            Province(province_name="贵州省", region="西南地区"),
            Province(province_name="云南省", region="西南地区"),
            Province(province_name="西藏自治区", region="西南地区"),

            # 西北
            Province(province_name="陕西省", region="西北地区"),
            Province(province_name="甘肃省", region="西北地区"),
            Province(province_name="青海省", region="西北地区"),
            Province(province_name="宁夏回族自治区", region="西北地区"),
            Province(province_name="新疆维吾尔自治区", region="西北地区"),

            # 港澳台
            Province(province_name="台湾省", region="港澳台地区"),
            Province(province_name="香港特别行政区", region="港澳台地区"),
            Province(province_name="澳门特别行政区", region="港澳台地区"),
        ]
        db.session.add_all(provinces)

    if not Admin.query.filter_by(admin_account="admin").first():
        from werkzeug.security import generate_password_hash
        hashed_pwd = generate_password_hash("123456")
        db.session.add(Admin(admin_account="admin", password=hashed_pwd, admin_key="ADMIN_2025_EARTHQUAKE"))

    if not User.query.filter_by(user_account="testuser").first():
        from werkzeug.security import generate_password_hash
        hashed_user_pwd = generate_password_hash("123456")
        db.session.add(User(user_account="testuser", password=hashed_user_pwd))

    db.session.commit()

if __name__ == '__main__':
    app.run(debug=True)