from flask import Flask
from models import db  # 只导入 db
from routes import register_routes
import datetime

app = Flask(__name__)
app.secret_key = "earthquake_2025"
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)
register_routes(app)

# 初始化数据
with app.app_context():
    db.create_all()

    # 在这里面导入！！！ 解决红色 + 报错
    from models import Province, Admin

    # 初始化全国省份
    if not Province.query.first():
        provinces = [
            Province(province_name="北京市"), Province(province_name="天津市"),
            Province(province_name="上海市"), Province(province_name="重庆市"),
            Province(province_name="河北省"), Province(province_name="山西省"),
            Province(province_name="辽宁省"), Province(province_name="吉林省"),
            Province(province_name="黑龙江省"), Province(province_name="江苏省"),
            Province(province_name="浙江省"), Province(province_name="安徽省"),
            Province(province_name="福建省"), Province(province_name="江西省"),
            Province(province_name="山东省"), Province(province_name="河南省"),
            Province(province_name="湖北省"), Province(province_name="湖南省"),
            Province(province_name="广东省"), Province(province_name="海南省"),
            Province(province_name="四川省"), Province(province_name="贵州省"),
            Province(province_name="云南省"), Province(province_name="陕西省"),
            Province(province_name="甘肃省"), Province(province_name="青海省"),
            Province(province_name="台湾省"), Province(province_name="内蒙古自治区"),
            Province(province_name="广西壮族自治区"), Province(province_name="西藏自治区"),
            Province(province_name="宁夏回族自治区"), Province(province_name="新疆维吾尔自治区"),
            Province(province_name="香港特别行政区"), Province(province_name="澳门特别行政区")
        ]
        db.session.add_all(provinces)

    # 初始化默认管理员
    if not Admin.query.filter_by(admin_account="admin").first():
        db.session.add(Admin(
            admin_account="admin",
            password="123456",
            admin_key="ADMIN_2025_EARTHQUAKE"
        ))

    db.session.commit()

    db.session.commit()

if __name__ == '__main__':
    app.run(debug=True)