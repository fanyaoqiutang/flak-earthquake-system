# test_subscribe.py 订阅功能测试（通过）
import requests

print("=" * 50)
print("测试用户订阅省份功能")
print("=" * 50)

# 创建一个 Session 对象，它会自动保持 Cookie（登录状态）
session = requests.Session()

# 1. 登录
login_data = {
    "user_account": "testuser",
    "password": "123456"
}

print("\n正在连接服务器并登录...")
try:
    login_res = session.post("http://127.0.0.1:5000/api/user/login", json=login_data, timeout=5)

    if login_res.status_code == 200:
        result = login_res.json()
        if result['code'] == 200:
            print("✅ 登录成功！")
        else:
            print(f"❌ 登录业务失败: {result['msg']}")
            exit()
    else:
        print(f"❌ 登录请求失败，状态码: {login_res.status_code}")
        exit()
except Exception as e:
    print(f"❌ 连接错误: {e}")
    exit()

# 2. 获取所有省份
print("\n正在获取省份列表...")
try:
    provinces_res = session.get("http://127.0.0.1:5000/api/provinces")
    data = provinces_res.json()
    print(f"✅ 获取到 {data['total']} 个省份")
    # 显示前 5 个
    for p in data['data'][:5]:
        print(f"   ID={p['province_id']}, 名称={p['province_name']}")
except Exception as e:
    print(f"❌ 获取省份失败: {e}")

# 3. 订阅四川省（ID=21）
print("\n正在订阅四川省 (ID=21)...")
subscribe_data = {"province_id": 21}
try:
    subscribe_res = session.post(
        "http://127.0.0.1:5000/api/user/subscribe",
        json=subscribe_data
    )
    print(f"HTTP 状态码: {subscribe_res.status_code}")

    if subscribe_res.status_code == 200:
        res_json = subscribe_res.json()
        print(f"响应内容: {res_json}")
        if res_json['code'] == 200:
            print("✅ 订阅成功！")
        else:
            print(f"❌ 订阅失败: {res_json['msg']}")
    else:
        print(f"❌ 请求失败: {subscribe_res.text[:100]}")
except Exception as e:
    print(f"❌ 异常: {e}")

# 4. 查看订阅列表
print("\n正在获取我的订阅列表...")
try:
    subs_res = session.get("http://127.0.0.1:5000/api/user/subscriptions")
    print(f"✅ 订阅列表响应: {subs_res.json()}")
except Exception as e:
    print(f"❌ 获取列表失败: {e}")

print("\n" + "=" * 50)
print("测试结束")
print("=" * 50)
