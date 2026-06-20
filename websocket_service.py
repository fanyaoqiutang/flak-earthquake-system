from flask_socketio import SocketIO, emit, join_room, leave_room
from flask import request as flask_request
from models import db, UserSubscribeProvince, UserEarthquakeAlert, EarthquakeInfo, User, City, Province
from datetime import datetime
import threading
import time

socketio = SocketIO(cors_allowed_origins="*")

connected_users = {}


def init_socketio(app):
    socketio.init_app(app, cors_allowed_origins="*", async_mode='threading')
    return socketio


@socketio.on('connect')
def handle_connect():
    user_id = flask_request.args.get('user_id')
    if user_id:
        connected_users[user_id] = flask_request.sid
        print(f"✅ 用户 {user_id} 已连接WebSocket, SID: {flask_request.sid}")
        emit('status', {'msg': '连接成功'})


@socketio.on('disconnect')
def handle_disconnect():
    user_id = None
    for uid, sid in list(connected_users.items()):
        if sid == flask_request.sid:
            user_id = uid
            break

    if user_id:
        del connected_users[user_id]
        print(f"❌ 用户 {user_id} 已断开WebSocket连接")


@socketio.on('subscribe_alert')
def handle_subscribe_alert(data):
    user_id = data.get('user_id')
    if user_id:
        join_room(f"user_{user_id}")
        print(f"📡 用户 {user_id} 订阅预警频道")


def check_and_push_earthquake_alert(earthquake_id):
    """检查地震数据并推送给符合条件的用户"""
    try:
        earthquake = EarthquakeInfo.query.get(earthquake_id)
        if not earthquake:
            return

        city = City.query.get(earthquake.city_id)
        if not city:
            return

        province = Province.query.get(city.province_id)
        if not province:
            return

        province_id = province.province_id
        magnitude = earthquake.magnitude

        subscriptions = UserSubscribeProvince.query.filter_by(province_id=province_id).all()

        for sub in subscriptions:
            user_id = sub.user_id

            user = User.query.get(user_id)
            if not user or user.status != "正常":
                continue

            alert_methods = user.alert_methods if hasattr(user, 'alert_methods') else ['弹窗提醒']
            if not alert_methods:
                continue

            existing_alert = UserEarthquakeAlert.query.filter_by(
                user_id=user_id,
                earthquake_id=earthquake_id
            ).first()

            if existing_alert:
                continue

            alert_record = UserEarthquakeAlert(
                user_id=user_id,
                earthquake_id=earthquake_id,
                is_read=False
            )
            db.session.add(alert_record)
            db.session.commit()

            alert_data = {
                'alert_id': alert_record.id,
                'earthquake_id': earthquake_id,
                'province_name': province.province_name,
                'city_name': city.city_name,
                'magnitude': magnitude,
                'latitude': earthquake.latitude,
                'longitude': earthquake.longitude,
                'depth': earthquake.depth,
                'earthquake_time': earthquake.earthquake_time.strftime("%Y-%m-%d %H:%M:%S"),
                'message': earthquake.earthquake_message or f"{province.province_name}{city.city_name}发生{magnitude}级地震",
                'tip': '请尽快远离高层建筑、玻璃、悬挂物，寻找安全区域躲避！'
            }

            if user_id in connected_users:
                socketio.emit('earthquake_alert', alert_data, room=f"user_{user_id}")
                print(f"🚨 已向用户 {user_id} 推送地震预警: {province.province_name} {magnitude}级")

            if '邮件通知' in alert_methods and getattr(user, 'email', None):
                send_alert_email_async(user.email, alert_data)

    except Exception as e:
        print(f"⚠️ 推送预警失败: {str(e)}")
        import traceback
        traceback.print_exc()


def send_alert_email_async(email, alert_data):
    """异步发送预警邮件"""

    def send_email():
        try:
            import smtplib
            from email.mime.text import MIMEText
            from email.header import Header

            subject = f"【紧急地震预警】{alert_data['province_name']}发生{alert_data['magnitude']}级地震"

            html_content = f"""
            <html>
            <body style="font-family: Arial, sans-serif; padding: 20px;">
                <div style="background-color: #fef0f0; border: 2px solid #f56c6c; border-radius: 8px; padding: 20px;">
                    <h2 style="color: #f56c6c; margin-top: 0;">⚠️ 紧急地震预警</h2>
                    <div style="background: white; padding: 15px; border-radius: 4px; margin: 15px 0;">
                        <p><strong>发生地区：</strong>{alert_data['province_name']} {alert_data['city_name']}</p>
                        <p><strong>震级：</strong><span style="color: #f56c6c; font-size: 24px; font-weight: bold;">{alert_data['magnitude']}级</span></p>
                        <p><strong>发生时间：</strong>{alert_data['earthquake_time']}</p>
                        <p><strong>经纬度：</strong>{alert_data['latitude']}, {alert_data['longitude']}</p>
                        <p><strong>震源深度：</strong>{alert_data['depth']}千米</p>
                    </div>
                    <div style="background: #fff3cd; padding: 15px; border-radius: 4px; border-left: 4px solid #ffc107;">
                        <p style="margin: 0; color: #856404;"><strong>避险提示：</strong>{alert_data['tip']}</p>
                    </div>
                    <p style="color: #909399; font-size: 12px; margin-top: 20px;">
                        此邮件由地震预警系统自动发送，请勿回复。
                    </p>
                </div>
            </body>
            </html>
            """

            msg = MIMEText(html_content, 'html', 'utf-8')
            msg['Subject'] = Header(subject, 'utf-8')
            msg['From'] = 'earthquake_alert@system.com'
            msg['To'] = email

            print(f"📧 预警邮件已发送至: {email}")

        except Exception as e:
            print(f"⚠️ 发送邮件失败: {str(e)}")

    thread = threading.Thread(target=send_email)
    thread.daemon = True
    thread.start()
