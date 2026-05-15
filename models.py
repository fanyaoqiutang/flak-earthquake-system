from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

# 省份
class Province(db.Model):
    __tablename__ = 'province'
    province_id = db.Column(db.Integer, primary_key=True)
    province_name = db.Column(db.String(50), unique=True, nullable=False)

# 管理员
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
    create_time = db.Column(db.DateTime, default=db.func.now())