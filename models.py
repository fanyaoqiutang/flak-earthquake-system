import datetime
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

db = SQLAlchemy()

from sqlalchemy import Column, Integer, String, Text, DateTime

# 地震科普分类
class ScienceCategory(db.Model):
    __tablename__ = 'science_category'
    category_id = db.Column(db.Integer, primary_key=True)
    category_name = db.Column(db.String(50), unique=True, nullable=False, comment='分类名称')
    category_icon = db.Column(db.String(100), comment='分类图标')
    sort_order = db.Column(db.Integer, default=0, comment='排序')
    create_time = db.Column(db.DateTime, default=datetime.datetime.now)

    articles = db.relationship('EarthQuakePopular', backref='category', lazy=True)


# 地震科普文章（对应爬虫earthquake_popular表）
class EarthQuakePopular(db.Model):
    __tablename__ = "earthquake_popular"
    id = Column(Integer, primary_key=True, autoincrement=True)
    category_id = Column(Integer, db.ForeignKey('science_category.category_id'), nullable=True, comment='分类ID')
    title = Column(String(500), nullable=False, comment="科普标题")
    summary = Column(Text, comment="文章摘要")
    content = Column(Text, comment="科普正文")
    icon = Column(String(100), comment="文章图标")
    source = Column(String(200), default="国家地震科学数据中心", comment="来源")
    view_count = Column(Integer, default=0, comment="浏览量")
    is_active = Column(Integer, default=1, comment="是否启用 1:启用 0:禁用")
    create_time = Column(DateTime, default=datetime.datetime.now, comment="入库时间")
    update_time = Column(DateTime, nullable=True, comment="更新时间")


# 省份（省级行政区）
class Province(db.Model):
    __tablename__ = 'province'
    province_id = db.Column(db.Integer, primary_key=True)
    province_name = db.Column(db.String(50), unique=True, nullable=False)
    region = db.Column(db.String(20))  # 地理大区（华北/东北等）

    cities = db.relationship('City', backref='province', lazy=True)
    subscribes = db.relationship('UserSubscribeProvince', backref='province', lazy=True)


# 城市（地级市）
class City(db.Model):
    __tablename__ = 'city'
    city_id = db.Column(db.Integer, primary_key=True)
    city_name = db.Column(db.String(50), nullable=False)
    province_id = db.Column(db.Integer, db.ForeignKey('province.province_id'), nullable=False)
    city_code = db.Column(db.String(20))  # 城市编码（可选）

    earthquakes = db.relationship('EarthquakeInfo', backref='city', lazy=True)


class PendingLocation(db.Model):
    """待审核位置表（爬虫未匹配的位置）"""
    __tablename__ = 'pending_location'

    id = db.Column(db.Integer, primary_key=True)
    location_name = db.Column(db.String(100), nullable=False)  # 位置名称
    province_candidate = db.Column(db.String(50))  # 推测的省份
    city_candidate = db.Column(db.String(50))  # 推测的城市名
    occurrence_count = db.Column(db.Integer, default=1)  # 出现次数
    latest_magnitude = db.Column(db.Float)  # 最近震级
    latest_time = db.Column(db.DateTime)  # 最近发生时间
    status = db.Column(db.String(20), default='pending')  # pending/approved/rejected
    created_at = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)

    # 关联的地震消息（可选，记录详细信息）
    sample_earthquakes = db.Column(db.Text)  # JSON格式，存储几条示例地震


# 管理员
class Admin(UserMixin, db.Model):
    __tablename__ = 'admin'
    admin_id = db.Column(db.Integer, primary_key=True)
    admin_account = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    admin_key = db.Column(db.String(50), nullable=False)
    create_time = db.Column(db.DateTime, default=datetime.datetime.now)

    @property
    def is_admin(self):
        return True

    def get_id(self):
        return str(self.admin_id)

# 用户（新增：手机号、状态、最后活跃、预警配置）
class User(UserMixin, db.Model):
    __tablename__ = 'user'
    user_id = db.Column(db.Integer, primary_key=True)
    user_account = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    create_time = db.Column(db.DateTime, default=datetime.datetime.now)

    #  新增字段，实现用户管理面板
    phone = db.Column(db.String(11))  # 手机号
    status = db.Column(db.String(10), default="正常")  # 正常 / 禁用
    last_active_time = db.Column(db.DateTime, default=datetime.datetime.now)  # 最后活跃

    #  新增预警设置字段
    alert_frequency = db.Column(db.String(20), default="实时预警")  # 实时 / 每日汇总
    alert_methods = db.Column(db.JSON, default=["站内信"])  # 通知方式

    subscribes = db.relationship('UserSubscribeProvince', backref='user', lazy=True)
    alerts = db.relationship('UserEarthquakeAlert', backref='user', lazy=True)
    feedbacks = db.relationship('UserFeedback', backref='user', lazy=True)
    chats = db.relationship('ChatMessage', backref='user', lazy=True)

    @property
    def is_admin(self):
        return False

    def check_password(self, password):
        return check_password_hash(self.password, password)

    def set_password(self, password):
        self.password = generate_password_hash(password)

    def get_id(self):
        return str(self.user_id)

# 地震信息
class EarthquakeInfo(db.Model):
    __tablename__ = 'earthquake_info'
    earthquake_id = db.Column(db.Integer, primary_key=True)
    city_id = db.Column(db.Integer, db.ForeignKey('city.city_id'), nullable=False)
    earthquake_time = db.Column(db.DateTime, nullable=False)
    latitude = db.Column(db.Float, nullable=False)
    longitude = db.Column(db.Float, nullable=False)
    depth = db.Column(db.Float, nullable=False)
    magnitude = db.Column(db.Float, nullable=False)
    earthquake_message = db.Column(db.Text, default="")
    create_time = db.Column(db.DateTime, default=datetime.datetime.now)


# 用户订阅省份（保持省级订阅）
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
    user_id = db.Column(db.Integer, db.ForeignKey('user.user_id'), nullable=True)
    content = db.Column(db.Text, nullable=False)
    status = db.Column(db.String(20), default='normal')  # normal/deleted/banned
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
