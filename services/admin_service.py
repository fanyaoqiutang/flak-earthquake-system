from flask import request, jsonify, session
from werkzeug.security import generate_password_hash, check_password_hash
import secrets
import datetime as dt
from models import db, Admin, EarthquakeInfo, Province, City, ChatMessage, UserFeedback, User, AdminOperationLog, UserSubscribeProvince, UserEarthquakeAlert
from sqlalchemy import func, desc

ADMIN_SECRET_KEY = "ADMIN_2025_EARTHQUAKE"

def verify_admin():
    """
    管理员身份验证 - 简化版
    只检查 session，不依赖 token
    """
    is_admin = session.get('is_admin', False)
    admin_id = session.get('admin_id')
    
    if is_admin and admin_id:
        return True
    
    return False


def svc_admin_login():
    """管理员登录 - 简化版"""
    try:
        data = request.get_json(force=True)
        account = data.get('admin_account')
        pwd = data.get('password')
        admin_key = data.get('admin_key')

        if not account or not pwd:
            return jsonify({"code": 400, "msg": "账号和密码不能为空"}), 400
        
        if not admin_key:
            return jsonify({"code": 400, "msg": "请输入管理员密钥"}), 400

        if admin_key != ADMIN_SECRET_KEY:
            return jsonify({"code": 403, "msg": "管理员密钥错误"}), 403

        admin = Admin.query.filter_by(admin_account=account).first()
        if not admin:
            return jsonify({"code": 401, "msg": "管理员账号不存在"}), 401
        
        if not check_password_hash(admin.password, pwd):
            return jsonify({"code": 401, "msg": "密码错误"}), 401

        # 设置 session
        session.permanent = True
        session['is_admin'] = True
        session['admin_id'] = admin.admin_id
        session['admin_account'] = admin.admin_account
        
        # 生成 token（用于前端存储和后续请求）
        token = secrets.token_hex(32)
        session['admin_token'] = token

        return jsonify({
            "code": 200, 
            "msg": "登录成功", 
            "data": {
                "admin_token": token, 
                "admin_account": admin.admin_account,
                "admin_id": admin.admin_id
            }
        })
    except Exception as e:
        print(f"[ERROR] 管理员登录失败: {e}")
        return jsonify({"code": 500, "msg": f"服务器错误: {str(e)}"}), 500


def svc_admin_logout():
    """管理员登出"""
    session.clear()
    return jsonify({"code": 200, "msg": "退出成功"})


def svc_admin_info():
    """获取当前登录的管理员信息"""
    if not verify_admin():
        return jsonify({"code": 401, "msg": "未登录或登录已过期"}), 401
    
    return jsonify({
        "code": 200, 
        "data": {
            "admin_id": session.get("admin_id"), 
            "admin_account": session.get("admin_account")
        }
    })


def svc_get_dashboard_stats():
    """获取仪表盘统计数据"""
    if not verify_admin():
        return jsonify({"code": 403, "msg": "无权限，请先登录"}), 403

    try:
        total_users = User.query.count()
        today = dt.datetime.now().date()
        today_messages = ChatMessage.query.filter(
            func.date(ChatMessage.create_time) == today
        ).count()
        total_earthquakes = EarthquakeInfo.query.count()
        pending_feedbacks = UserFeedback.query.filter_by(status='未处理').count()

        return jsonify({
            'code': 200,
            'data': {
                'totalUsers': total_users,
                'todayMessages': today_messages,
                'totalEarthquakes': total_earthquakes,
                'pendingFeedbacks': pending_feedbacks
            }
        })
    except Exception as e:
        return jsonify({'code': 500, 'msg': f'获取统计数据失败: {str(e)}'}), 500


def svc_admin_get_all_users():
    """获取所有用户列表（支持分页）"""
    if not verify_admin():
        return jsonify({"code": 403, "msg": "无权限"}), 403

    try:
        page = int(request.args.get('page', 1))
        per_page = int(request.args.get('per_page', 10))
        
        keyword = request.args.get("keyword")
        status = request.args.get("status")

        query = User.query

        if status:
            query = query.filter_by(status=status)
        if keyword:
            query = query.filter(
                (User.user_account.like(f"%{keyword}%")) |
                (User.phone.like(f"%{keyword}%"))
            )

        query = query.order_by(desc(User.create_time))
        pagination = query.paginate(page=page, per_page=per_page, error_out=False)

        data = []
        now = dt.datetime.now()

        for u in pagination.items:
            subs = UserSubscribeProvince.query.filter_by(user_id=u.user_id).all()
            provinces = []
            for s in subs:
                p = Province.query.get(s.province_id)
                if p:
                    provinces.append({
                        "province_id": p.province_id,
                        "province_name": p.province_name
                    })

            if u.last_active_time:
                delta = now - u.last_active_time
                if delta.days >= 1:
                    last = f"{delta.days}天前"
                elif delta.seconds >= 3600:
                    last = f"{delta.seconds//3600}小时前"
                elif delta.seconds >= 60:
                    last = f"{delta.seconds//60}分钟前"
                else:
                    last = "刚刚"
            else:
                last = "未知"

            data.append({
                "user_id": u.user_id,
                "username": u.user_account,
                "phone": u.phone or "",
                "status": u.status,
                "created_at": u.create_time.strftime("%Y-%m-%d %H:%M:%S"),
                "last_active": last,
                "subscribed_provinces": provinces
            })
        
        return jsonify({
            "code": 200,
            "data": {
                "items": data,
                "total": pagination.total,
                "page": page,
                "per_page": per_page
            }
        })
    except Exception as e:
        print(f"[ERROR] 获取用户列表失败: {e}")
        return jsonify({"code": 500, "msg": f"获取用户列表失败: {str(e)}"}), 500


# 自动生成预警
def generate_alerts(earthquake_id):
    eq = EarthquakeInfo.query.get(earthquake_id)
    if not eq or eq.magnitude < 4.0:
        return False

    # 通过 city_id 获取 province_id
    city = City.query.get(eq.city_id)
    if not city:
        return False

    subscribers = UserSubscribeProvince.query.filter_by(province_id=city.province_id).all()
    cnt = 0
    for sub in subscribers:
        exist = UserEarthquakeAlert.query.filter_by(user_id=sub.user_id, earthquake_id=earthquake_id).first()
        if not exist:
            a = UserEarthquakeAlert(user_id=sub.user_id, earthquake_id=earthquake_id)
            db.session.add(a)
            cnt += 1
    if cnt > 0:
        db.session.commit()
    return cnt > 0

# 管理员注册
def svc_admin_register():
    data = request.get_json(force=True)
    account = data.get('admin_account')
    pwd = data.get('password')
    admin_key = data.get('admin_key')
    if not account or not pwd or not admin_key:
        return jsonify({"code": 400, "msg": "参数不能为空"}), 400
    if len(account) < 3 or len(account) > 20:
        return jsonify({"code": 400, "msg": "账号长度3-20位"}), 400
    if len(pwd) < 6:
        return jsonify({"code": 400, "msg": "密码长度至少6位"}), 400
    if admin_key != ADMIN_SECRET_KEY:
        return jsonify({"code": 403, "msg": "密钥错误"}), 403
    if Admin.query.filter_by(admin_account=account).first():
        return jsonify({"code": 400, "msg": "账号已存在"}), 400
    hashed_pwd = generate_password_hash(pwd)
    new_admin = Admin(admin_account=account, password=hashed_pwd, admin_key=admin_key)
    db.session.add(new_admin)
    db.session.commit()
    return jsonify({"code": 200, "msg": "注册成功"})

# 管理员操作日志（记录增删改操作）
def add_admin_log(admin_id, operation, target_earthquake_id=None, remark=""):
    log = AdminOperationLog(
        admin_id=admin_id,
        operation=operation,
        target_earthquake_id=target_earthquake_id,
    )
    db.session.add(log)
    db.session.commit()


# 新增地震信息
def svc_add_earthquake():
    try:
        if not verify_admin():
            return jsonify({"code": 403, "msg": "无权限，请先以管理员身份登录"}), 403

        data = request.get_json(force=True)
        print(f"[DEBUG] 接收到的数据: {data}")

        req = ["city_id", "earthquake_time", "latitude", "longitude", "depth", "magnitude"]
        for f in req:
            if not data.get(f):
                return jsonify({"code": 400, "msg": f"参数 {f} 不能为空"}), 400

        try:
            city_id = int(data['city_id'])
            latitude = float(data['latitude'])
            longitude = float(data['longitude'])
            depth = float(data['depth'])
            magnitude = float(data['magnitude'])
        except Exception as e:
            return jsonify({"code": 400, "msg": f"数值格式错误: {str(e)}"}), 400

        if not City.query.get(city_id):
            return jsonify({"code": 400, "msg": "城市不存在"}), 400

        try:
            try:
                t = dt.datetime.fromisoformat(data['earthquake_time'])
            except:
                t = dt.datetime.strptime(data['earthquake_time'], '%Y-%m-%d %H:%M:%S')
        except Exception as e:
            return jsonify({"code": 400, "msg": f"时间格式错误: {str(e)}"}), 400

        eq = EarthquakeInfo(
            city_id=city_id,
            earthquake_time=t,
            latitude=latitude,
            longitude=longitude,
            depth=depth,
            magnitude=magnitude,
            earthquake_message=data.get('earthquake_message', '')
        )
        db.session.add(eq)
        db.session.commit()

        print(f"[DEBUG] 地震数据保存成功, ID: {eq.earthquake_id}")

        # 记录日志（失败不影响主流程）
        admin_id = session.get('admin_id')
        if admin_id:
            try:
                add_admin_log(admin_id, "添加地震", eq.earthquake_id)
                print(f"[DEBUG] 日志记录成功")
            except Exception as e:
                print(f"[WARN] 日志记录失败（不影响主流程）: {e}")
        else:
            print(f"[WARN] 无法获取admin_id，跳过日志记录")

        # 生成预警（失败不影响主流程）
        try:
            generate_alerts(eq.earthquake_id)
            print(f"[DEBUG] 预警生成成功")
        except Exception as e:
            print(f"[WARN] 预警生成失败（不影响主流程）: {e}")

        return jsonify({"code": 200, "msg": "添加成功", "data": {"earthquake_id": eq.earthquake_id}})
    except Exception as e:
        db.session.rollback()
        print(f"[ERROR] 添加地震失败: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({"code": 500, "msg": f"服务器错误: {str(e)}"}), 500


        # 修改地震消息


# 修改地震消息
def svc_update_earthquake():
    try:
        if not verify_admin():
            return jsonify({"code": 403, "msg": "无权限，请先以管理员身份登录"}), 403

        data = request.get_json()
        earthquake_id = data.get('earthquake_id')

        if not earthquake_id:
            return jsonify({"code": 400, "msg": "地震ID不能为空"}), 400

        eq = EarthquakeInfo.query.get(earthquake_id)
        if not eq:
            return jsonify({"code": 404, "msg": "地震记录不存在"}), 404

        if data.get('city_id'):
            try:
                cid = int(data.get('city_id'))
                if City.query.get(cid):
                    eq.city_id = cid
            except:
                pass

        if data.get('earthquake_time'):
            try:
                eq.earthquake_time = dt.datetime.fromisoformat(data.get('earthquake_time'))
            except:
                pass

        if data.get('latitude'):
            try:
                eq.latitude = float(data.get('latitude'))
            except:
                pass

        if data.get('longitude'):
            try:
                eq.longitude = float(data.get('longitude'))
            except:
                pass

        if data.get('depth'):
            try:
                eq.depth = float(data.get('depth'))
            except:
                pass

        if data.get('magnitude'):
            try:
                eq.magnitude = float(data.get('magnitude'))
            except:
                pass

        if data.get('earthquake_message') is not None:
            eq.earthquake_message = data.get('earthquake_message')

        db.session.commit()

        # 记录日志（失败不影响主流程）
        admin_id = session.get('admin_id')
        if admin_id:
            try:
                add_admin_log(admin_id, "修改地震", eq.earthquake_id)
            except Exception as e:
                print(f"[WARN] 日志记录失败: {e}")

        return jsonify({"code": 200, "msg": "修改成功"})

    except Exception as e:
        db.session.rollback()
        print(f"[ERROR] 修改地震失败: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({"code": 500, "msg": f"服务器错误: {str(e)}"}), 500

# 删除地震消息
def svc_delete_earthquake():
    if not verify_admin():
        return jsonify({"code": 403, "msg": "无权限，请先以管理员身份登录"}), 403
    data = request.get_json(force=True)
    if not data.get('earthquake_id'):
        return jsonify({"code": 400, "msg": "地震ID不能为空"}), 400
    eq = EarthquakeInfo.query.get(data.get('earthquake_id'))
    if not eq:
        return jsonify({"code": 400, "msg": "地震记录不存在"}), 400
    db.session.delete(eq)
    db.session.commit()
    add_admin_log(session.get('admin_id'), "删除地震", eq.earthquake_id)
    return jsonify({"code": 200, "msg": "删除成功"})

# 用户管理（支持搜索、状态、最后活跃）
def svc_admin_get_all_users():
    if not verify_admin():
        return jsonify({"code": 403, "msg": "无管理员权限"}), 403

    try:
        # 获取分页参数
        page = int(request.args.get('page', 1))
        per_page = int(request.args.get('per_page', 10))
        
        keyword = request.args.get("keyword")
        status = request.args.get("status")

        query = User.query

        if status:
            query = query.filter_by(status=status)
        if keyword:
            query = query.filter(
                (User.user_account.like(f"%{keyword}%")) |
                (User.phone.like(f"%{keyword}%"))
            )

        # 按创建时间倒序排列
        query = query.order_by(desc(User.create_time))
        
        # 分页
        pagination = query.paginate(page=page, per_page=per_page, error_out=False)

        data = []
        now = dt.datetime.now()

        for u in pagination.items:
            subs = UserSubscribeProvince.query.filter_by(user_id=u.user_id).all()
            provinces = []
            for s in subs:
                p = Province.query.get(s.province_id)
                if p:
                    provinces.append({
                        "province_id": p.province_id,
                        "province_name": p.province_name
                    })

            # 最后活跃时间格式化
            if u.last_active_time:
                delta = now - u.last_active_time
                if delta.days >= 1:
                    last = f"{delta.days}天前"
                elif delta.seconds >= 3600:
                    last = f"{delta.seconds//3600}小时前"
                elif delta.seconds >= 60:
                    last = f"{delta.seconds//60}分钟前"
                else:
                    last = "刚刚"
            else:
                last = "未知"

            data.append({
                "user_id": u.user_id,
                "username": u.user_account,
                "phone": u.phone or "",
                "status": u.status,
                "created_at": u.create_time.strftime("%Y-%m-%d %H:%M:%S"),
                "last_active": last,
                "subscribed_provinces": provinces
            })
        
        return jsonify({
            "code": 200,
            "data": {
                "items": data,
                "total": pagination.total,
                "page": page,
                "per_page": per_page
            }
        })
    except Exception as e:
        print(f"[ERROR] 获取用户列表失败: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({"code": 500, "msg": f"获取用户列表失败: {str(e)}"}), 500

# 用户统计（总用户/活跃/禁用）
def svc_admin_get_user_stats():
    if not verify_admin():
        return jsonify({"code":403,"msg":"无权限"}),403

    now = dt.datetime.now()
    thirty_days_ago = now - dt.timedelta(days=30)

    total = User.query.count()
    active = User.query.filter(User.last_active_time >= thirty_days_ago).count()
    disabled = User.query.filter_by(status="禁用").count()

    return jsonify({
        "code":200,
        "data":{
            "total_users":total,
            "active_users":active,
            "disabled_users":disabled
        }
    })

# 切换用户状态（正常/禁用）
def svc_admin_toggle_user_status(user_id):
    if not verify_admin():
        return jsonify({"code":403,"msg":"无权限"}),403
    u = User.query.get(user_id)
    if not u:
        return jsonify({"code":404,"msg":"用户不存在"}),404
    u.status = "禁用" if u.status == "正常" else "正常"
    db.session.commit()
    return jsonify({"code":200,"msg":"状态已更新"})

# 删除用户
def svc_admin_delete_user(user_id):
    if not verify_admin():
        return jsonify({"code": 403, "msg": "无权限"}), 403

    user = User.query.get(user_id)
    if not user:
        return jsonify({"code": 404, "msg": "用户不存在"}), 404

    UserSubscribeProvince.query.filter_by(user_id=user_id).delete()
    UserFeedback.query.filter_by(user_id=user_id).delete()
    ChatMessage.query.filter_by(user_id=user_id).delete()

    db.session.delete(user)
    db.session.commit()
    return jsonify({"code": 200, "msg": "用户已删除"})

# 获取反馈信息
def svc_admin_get_all_feedbacks():
    if not verify_admin():
        return jsonify({"code": 403, "msg": "无权限"}), 403

    fs = UserFeedback.query.order_by(desc(UserFeedback.submit_time)).all()
    res = []
    for f in fs:
        u = User.query.get(f.user_id)
        res.append({
            "id": f.id,
            "feedback_id": f.id,
            "user_id": f.user_id,
            "user_account": u.user_account if u else "已注销",
            "feedback_type": f.feedback_type,
            "content": f.content,
            "priority": f.priority,
            "status": f.status,
            "submit_time": f.submit_time.strftime("%Y-%m-%d %H:%M:%S"),
            "handle_time": f.handle_time.strftime("%Y-%m-%d %H:%M:%S") if f.handle_time else None
        })
    return jsonify({"code": 200, "data": res})


# 处理反馈

def svc_admin_handle_feedback(feedback_id):
    if not verify_admin():
        return jsonify({"code": 403, "msg": "无权限"}), 403

    fb = UserFeedback.query.get(feedback_id)
    if not fb:
        return jsonify({"code": 404, "msg": "反馈不存在"}), 404

    fb.status = "已处理"
    fb.handle_time = dt.datetime.now()
    db.session.commit()
    return jsonify({"code": 200, "msg": "已处理"})

# 聊天消息管理
def svc_admin_get_all_chat_messages():
    if not verify_admin():
        return jsonify({"code": 403, "msg": "无权限"}), 403

    ms = ChatMessage.query.order_by(desc(ChatMessage.create_time)).all()
    res = []
    for m in ms:
        u = User.query.get(m.user_id)
        res.append({
            "id": m.id,
            "user_id": m.user_id,
            "username": u.user_account if u else "已注销",
            "user_account": u.user_account if u else "已注销",
            "content": m.content,
            "create_time": m.create_time.strftime("%Y-%m-%d %H:%M:%S"),
            "status": m.status if hasattr(m, 'status') else 'normal'
        })
    return jsonify({"code": 200, "data": res})


# 删除聊天信息
def svc_admin_delete_chat_msg(msg_id):
    if not verify_admin():
        return jsonify({"code": 403, "msg": "无权限"}), 403

    msg = ChatMessage.query.get(msg_id)
    if not msg:
        return jsonify({"code": 404, "msg": "消息不存在"}), 404

    db.session.delete(msg)
    db.session.commit()
    return jsonify({"code": 200, "msg": "删除成功"})



# 获取地震列表（分页）
def svc_admin_get_earthquakes():
    """获取地震列表（支持分页和筛选）"""
    if not verify_admin():
        return jsonify({"code": 403, "msg": "无权限"}), 403

    try:
        page = int(request.args.get('page', 1))
        per_page = int(request.args.get('per_page', 10))

        query = EarthquakeInfo.query.order_by(desc(EarthquakeInfo.earthquake_time))

        # 分页
        pagination = query.paginate(page=page, per_page=per_page, error_out=False)

        data = []
        for eq in pagination.items:
            city = City.query.get(eq.city_id)
            province = Province.query.get(city.province_id) if city else None

            data.append({
                "earthquake_id": eq.earthquake_id,
                "city_name": city.city_name if city else "未知",
                "province_name": province.province_name if province else "未知",
                "earthquake_time": eq.earthquake_time.strftime("%Y-%m-%d %H:%M:%S"),
                "latitude": eq.latitude,
                "longitude": eq.longitude,
                "depth": eq.depth,
                "magnitude": eq.magnitude,
                "earthquake_message": eq.earthquake_message
            })

        return jsonify({
            "code": 200,
            "data": {
                "items": data,
                "total": pagination.total,
                "page": page,
                "per_page": per_page
            }
        })
    except Exception as e:
        return jsonify({"code": 500, "msg": f"获取地震列表失败: {str(e)}"}), 500


# 获取省份列表
def svc_admin_get_provinces():
    """获取所有省份"""
    if not verify_admin():
        return jsonify({"code": 403, "msg": "无权限"}), 403

    try:
        provinces = Province.query.order_by(Province.province_id).all()
        data = []

        for p in provinces:
            # 统计该省份下的城市数量
            city_count = City.query.filter_by(province_id=p.province_id).count()

            data.append({
                "province_id": p.province_id,
                "province_name": p.province_name,
                "city_count": city_count
            })

        return jsonify({"code": 200, "data": data})
    except Exception as e:
        return jsonify({"code": 500, "msg": f"获取省份列表失败: {str(e)}"}), 500


# 获取聊天记录（分页）
def svc_admin_get_chat_records():
    """获取聊天记录（支持分页）"""
    if not verify_admin():
        return jsonify({"code": 403, "msg": "无权限"}), 403

    try:
        page = int(request.args.get('page', 1))
        per_page = int(request.args.get('per_page', 10))

        query = ChatMessage.query.order_by(desc(ChatMessage.create_time))

        # 分页
        pagination = query.paginate(page=page, per_page=per_page, error_out=False)

        data = []
        for m in pagination.items:
            u = User.query.get(m.user_id)
            data.append({
                "id": m.id,
                "user_id": m.user_id,
                "username": u.user_account if u else "已注销",
                "content": m.content,
                "create_time": m.create_time.strftime("%Y-%m-%d %H:%M:%S"),
                "status": m.status if hasattr(m, 'status') else 'normal'
            })

        return jsonify({
            "code": 200,
            "data": {
                "items": data,
                "total": pagination.total,
                "page": page,
                "per_page": per_page
            }
        })
    except Exception as e:
        return jsonify({"code": 500, "msg": f"获取聊天记录失败: {str(e)}"}), 500
