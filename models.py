import datetime
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin

db = SQLAlchemy()

# 省份
class Province(db.Model):
    __tablename__ = 'province'
    province_id = db.Column(db.Integer, primary_key=True)
    province_name = db.Column(db.String(50), unique=True, nullable=False)
    # db.relationship()函数能够自动找到关系中的外键
    # backref 反向引用，自动在另一侧建立关系属性。lazy用于指定加载相关记录的方式，默认时lazy=true代表必要时要一次性加载全部记录
    # joined和父查询一样加载记录，等同于lazy=false
    # dynamic不直接加载记录，而是返回一个包含相关记录的query对象
    # province.earthquakes取这个省的所有地震   能实现通过省份查该省份所有地震；backref能实现通过地震查所属省份
    earthquakes = db.relationship('EarthquakeInfo', backref='province', lazy=True)

# 管理员
class Admin(UserMixin, db.Model):
    __tablename__ = 'admin'
    admin_id = db.Column(db.Integer, primary_key=True)
    admin_account = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    admin_key = db.Column(db.String(50), nullable=False)
    create_time = db.Column(db.DateTime, default=datetime.datetime.now)

    def get_id(self):
        return str(self.admin_id)

# 用户
class User(UserMixin, db.Model):
    __tablename__ = 'user'
    user_id = db.Column(db.Integer, primary_key=True)
    user_account = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    create_time = db.Column(db.DateTime, default=datetime.datetime.now)
    # subscribes用来获取这个用户订阅的所有省份。通过关联表：用户订阅省份表。反向引用，能够通过订阅记录直接取它属于哪个用户
    subscribes = db.relationship('UserSubscribeProvince', backref='user', lazy=True)
    alerts = db.relationship('UserEarthquakeAlert', backref='user', lazy=True)
    # 用户.feedback可以拿到这个用户的所有反馈。feedback.user可以拿到这条反馈是谁发的
    feedbacks = db.relationship('UserFeedback', backref='user', lazy=True)
    chats = db.relationship('ChatMessage', backref='user', lazy=True)
    # flask-login登录验证，返回唯一识别的id  没有这个标识无法保持登录状态
    def get_id(self):
        return str(self.user_id)

# 地震信息
class EarthquakeInfo(db.Model):
    __tablename__ = 'earthquake_info'
    earthquake_id = db.Column(db.Integer, primary_key=True)
    province_id = db.Column(db.Integer, db.ForeignKey('province.province_id'), nullable=False)
    earthquake_time = db.Column(db.DateTime, nullable=False)
    latitude = db.Column(db.Float, nullable=False)
    longitude = db.Column(db.Float, nullable=False)
    depth = db.Column(db.Float, nullable=False)
    magnitude = db.Column(db.Float, nullable=False)
    earthquake_message = db.Column(db.Text, default="")
    create_time = db.Column(db.DateTime, default=datetime.datetime.now)

# 用户订阅省份
class UserSubscribeProvince(db.Model):
    __tablename__ = 'user_subscribe_province'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.user_id'), nullable=False)
    province_id = db.Column(db.Integer, db.ForeignKey('province.province_id'), nullable=False)
    subscribe_time = db.Column(db.DateTime, default=datetime.datetime.now)

# 用户地震预警
class UserEarthquakeAlert(db.Model):
    __tablename__ = 'user_earthquake_alert'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.user_id'), nullable=False)
    earthquake_id = db.Column(db.Integer, db.ForeignKey('earthquake_info.earthquake_id'), nullable=False)
    is_read = db.Column(db.Boolean, default=False)
    create_time = db.Column(db.DateTime, default=datetime.datetime.now)

# 聊天消息
class ChatMessage(db.Model):
    __tablename__ = 'chat_message'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.user_id'), nullable=False)
    content = db.Column(db.Text, nullable=False)
    create_time = db.Column(db.DateTime, default=db.func.now())

# 用户反馈
class UserFeedback(db.Model):
    __tablename__ = "user_feedback"
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.ForeignKey('user.user_id'), nullable=False)
    feedback_type = db.Column(db.String(30))
    content = db.Column(db.Text)
    priority = db.Column(db.String(10), default="中")
    status = db.Column(db.String(20), default="未处理")
    submit_time = db.Column(db.DateTime, default=datetime.datetime.now)
    handle_time = db.Column(db.DateTime)

# 管理员操作日志
class AdminOperationLog(db.Model):
    __tablename__ = "admin_operation_log"
    id = db.Column(db.Integer, primary_key=True)
    admin_id = db.Column(db.Integer, db.ForeignKey('admin.admin_id'), nullable=False)
    operation = db.Column(db.String(50), nullable=False)
    target_earthquake_id = db.Column(db.Integer)
    create_time = db.Column(db.DateTime, default=datetime.datetime.now)