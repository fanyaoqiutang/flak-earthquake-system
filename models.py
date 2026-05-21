import datetime
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin

db = SQLAlchemy()

# 省份
class Province(db.Model):
    __tablename__ = 'province'
    province_id = db.Column(db.Integer, primary_key=True)
    province_name = db.Column(db.String(50), unique=True, nullable=False)
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

    subscribes = db.relationship('UserSubscribeProvince', backref='user', lazy=True)
    alerts = db.relationship('UserEarthquakeAlert', backref='user', lazy=True)
    feedbacks = db.relationship('UserFeedback', backref='user', lazy=True)
    chats = db.relationship('ChatMessage', backref='user', lazy=True)

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
    remark = db.Column(db.String(200))
    create_time = db.Column(db.DateTime, default=datetime.datetime.now)