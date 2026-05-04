from flask import Flask,request,jsonify
from flask_sqlalchemy import SQLAlchemy
import datetime
app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI']='sqlite:///test.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS']=False
app.config['SECRET_KEY']='your_secret_key'

db=SQLAlchemy(app)

# 1、管理员表 admin
class Admin(db.Model):
    __tablename__='admin'
    admin_id=db.Column(db.Integer,primary_key=True)
    admin_account=db.Column(db.String(50),nullable=False)
    password=db.Column(db.String(100),nullable=False)
    operation_permission=db.Column(db.String(100),nullable=False)

#2、用户表user
class User(db.Model):
    __tablename__='user'
    user_id=db.Column(db.Integer,primary_key=True)
    user_account=db.Column(db.String(50),nullable=False)
    password=db.Column(db.String(100),nullable=False)

# 3、省份表
class Province(db.Model):
    __tablename__='province'
    province_id=db.Column(db.Integer,primary_key=True)
    province_name=db.Column(db.String(50),nullable=False)

#4、 地震信息表
class EarthquakeInfo(db.Model):
    __tablename__='earthquake_info'
    earthquake_id=db.Column(db.Integer,primary_key=True)
    province_id=db.Column(db.Integer,db.ForeignKey('province.province_id'),nullable=False)
    earthquake_time=db.Column(db.DateTime,nullable=False)
    latitude=db.Column(db.Numeric(10,6),nullable=False)
    longitude=db.Column(db.Numeric(10,6),nullable=False)
    depth=db.Column(db.Numeric(5,2),nullable=False)
    magnitude=db.Column(db.Numeric(3,1),nullable=False)
    earthquake_message=db.Column(db.Text,nullable=True)
# 5、聊天信息表
class ChatMessage(db.Model):
    __tablename__='chat_message'
    message_id=db.Column(db.Integer,primary_key=True)
    user_id=db.Column(db.Integer,db.ForeignKey('user.user_id'),nullable=False)
    content=db.Column(db.Text,nullable=False)
    message_status=db.Column(db.SmallInteger,nullable=False)
    send_time=db.Column(db.DateTime,default=datetime.datetime.now)
# 6、用户订阅省份表
class UserSubscribeProvince(db.Model):
    __tablename__='user_subscribe_province'
    user_id=db.Column(db.Integer,db.ForeignKey('user.user_id'),primary_key=True)
    province_id=db.Column(db.Integer,db.ForeignKey('province.province_id'),primary_key=True)
    subscribe_time=db.Column(db.DateTime,default=datetime.datetime.now)

# 7、地震预警推送表
class UserEarthquakeAlert(db.Model):
    __tablename__='user_earthquake_alert'
    user_id=db.Column(db.Integer,db.ForeignKey('user.user_id'),primary_key=True)
    earthquake_id=db.Column(db.Integer,db.ForeignKey('earthquake_info.earthquake_id'),primary_key=True)
    alert_time=db.Column(db.DateTime,default=datetime.datetime.now)
    alert_status=db.Column(db.SmallInteger,nullable=False)

# 管理员登录接口
@app.route('/api/admin/login',methods=['POST','GET'])
def admin_login():
    if request.method == 'GET':
        return jsonify({
            "code":200,
            "msg":"请使用POST请求登录",
            "test_account":"admin",
            "test_pwd":"123456"
        })

    if not request.is_json:
        return jsonify({"code":400,"msg":"请传入JSON格式"}),400

    data=request.get_json()
    account=data.get('admin_account')
    pwd=data.get('password')

    admin=Admin.query.filter_by(admin_account=account,password=pwd).first()

    if admin:
        return jsonify({
            "code":200,
            "msg":"登录成功",
            "admin_id":admin.admin_id
        })
    else:
        return jsonify({
            "code":401,
            "msg":"账号或密码错误"
        }),401

@app.route('/')
def index():
    return "Hello, Earthquake System!"
# 创建表
with app.app_context():
    db.create_all()
    print("SQLite 数据库与7张表创建成功")

    admin=Admin.query.filter_by(admin_account="admin").first()
    if not admin:
        test_admin=Admin(
            admin_account="admin",
            password="123456",
            operation_permission="all"
        )
        db.session.add(test_admin)
        db.session.commit()
        print("测试管理员账号创建成果")

if __name__ == '__main__':
    app.run(debug=True)