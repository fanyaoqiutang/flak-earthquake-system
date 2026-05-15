# test_alert.py  预警功能测试（通过）
import requests

print("=" * 50)
print("测试预警系统功能")
print("=" * 50)

# 创建 Session 对象，用于保持登录状态（Cookie）
admin_session = requests.Session()
user_session = requests.Session()

# 1. 管理员登录
print("\n📌 步骤 1: 管理员登录")
try:
    admin_login = admin_session.post(
        "http://127.0.0.1:5000/api/admin/login",
        json={"admin_account": "admin", "password": "123456"}
    )
    admin_result = admin_login.json()
    print(f"管理员登录响应: {admin_result}")

    if admin_result['code'] != 200:
        print("❌ 管理员登录失败")
        exit()
except Exception as e:
    print(f"❌ 管理员登录异常: {e}")
    exit()

# 2. 用户登录
print("\n📌 步骤 2: 用户登录 (testuser)")
try:
    user_login = user_session.post(
        "http://127.0.0.1:5000/api/user/login",
        json={"user_account": "testuser", "password": "123456"}
    )
    user_result = user_login.json()
    print(f"用户登录响应: {user_result}")

    if user_result['code'] != 200:
        print("❌ 用户登录失败")
        exit()
except Exception as e:
    print(f" 用户登录异常: {e}")
    exit()

# 3. 添加地震数据（模拟触发预警）
print("\n 步骤 3: 添加地震数据（震级 5.0，应触发预警）")
earthquake_data = {
    "province_id": 21,  # 四川省
    "earthquake_time": "2026-05-15 14:30:00",
    "latitude": 30.5,
    "longitude": 104.0,
    "depth": 15.0,
    "magnitude": 5.0,
    "earthquake_message": "测试预警功能 - 四川省 5.0 级地震"
}

try:
    # 注意：管理员添加操作可能需要 session 验证，或者不需要额外参数
    add_res = admin_session.post(
        "http://127.0.0.1:5000/api/admin/earthquake/add",
        json=earthquake_data
    )
    print(f"添加地震 HTTP 状态码: {add_res.status_code}")
    print(f"添加地震响应: {add_res.text}")

    if add_res.status_code == 200:
        add_json = add_res.json()
        if add_json['code'] == 200:
            print("✅ 地震数据添加成功")
        else:
            print(f"❌ 添加失败: {add_json['msg']}")
except Exception as e:
    print(f"❌ 添加异常: {e}")

# 4. 用户查看预警列表
print("\n📌 步骤 4: 用户查看预警列表")
try:
    alerts_res = user_session.get("http://127.0.0.1:5000/api/user/alerts")
    print(f"预警列表响应: {alerts_res.json()}")
except Exception as e:
    print(f"❌ 获取预警列表失败: {e}")

# 5. 查看未读预警数量
print("\n📌 步骤 5: 查看未读预警数量")
try:
    unread_res = user_session.get("http://127.0.0.1:5000/api/user/alerts/unread")
    print(f"未读数量响应: {unread_res.json()}")
except Exception as e:
    print(f"❌ 获取未读数量失败: {e}")

print("\n" + "=" * 50)
print("预警系统测试完成！")
print("=" * 50)
