"""
中国地震目录爬虫
从中国地震台网中心 (ceic.ac.cn) 抓取地震数据并导入数据库
"""
import requests
from bs4 import BeautifulSoup
import re
from datetime import datetime,timedelta
from app import app
from models import EarthquakeInfo, Province, City, PendingLocation, db
import time

# 地震台网 API 地址（返回 JSON 格式）
CEIC_API_URL = "https://www.ceic.ac.cn/ajax/speedsearch"



def get_city_mapping():
    """获取城市映射表（增强版）"""
    mapping = {}
    with app.app_context():
        cities = City.query.all()
        for city in cities:
            # 1. 完整城市名：如 "库车市"
            mapping[city.city_name] = city.city_id

            # 2. 不带"市"的版本：如 "库车"
            city_short = city.city_name.replace("市", "")
            mapping[city_short] = city.city_id

            # 3. 处理特殊行政区划：如 "阿拉善盟" -> "阿拉善"
            for suffix in ["盟", "自治州", "地区", "自治县"]:
                if city.city_name.endswith(suffix):
                    base_name = city.city_name.replace(suffix, "")
                    mapping[base_name] = city.city_id
                    mapping[city.city_name.replace(suffix, "市")] = city.city_id

    return mapping


def parse_location_to_city(location_str, city_mapping):
    """
    解析位置字符串，找到对应的城市ID

    示例：
    "新疆阿克苏地区库车市" -> 返回库车市的city_id
    "内蒙古阿拉善盟阿拉善左旗" -> 返回阿拉善盟的city_id
    """
    if not location_str:
        return None

    # 策略1：从长到短匹配（优先匹配更精确的城市）
    # 例如：库车市(3字符) > 库车(2字符) > 阿克苏市(4字符) > 阿克苏(3字符)
    sorted_cities = sorted(city_mapping.keys(), key=len, reverse=True)

    for city_name in sorted_cities:
        if city_name in location_str:
            return city_mapping[city_name]

    # 策略2：如果策略1失败，尝试按分隔符分割
    # 位置字符串通常是: "省份+地区+城市+区县"
    # 例如："新疆阿克苏地区库车市"
    # 我们尝试提取最后一个有意义的部分

    # 移除省份前缀
    provinces = [
        "新疆维吾尔自治区", "新疆",
        "内蒙古自治区", "内蒙古",
        "西藏自治区", "西藏",
        "广西壮族自治区", "广西",
        "宁夏回族自治区", "宁夏",
        "黑龙江省", "黑龙江",
        "吉林省", "吉林",
        "辽宁省", "辽宁",
        "河北省", "河北",
        "河南省", "河南",
        "山东省", "山东",
        "山西省", "山西",
        "陕西省", "陕西",
        "甘肃省", "甘肃",
        "青海省", "青海",
        "四川省", "四川",
        "云南省", "云南",
        "贵州省", "贵州",
        "湖北省", "湖北",
        "湖南省", "湖南",
        "广东省", "广东",
        "海南省", "海南",
        "福建省", "福建",
        "浙江省", "浙江",
        "江苏省", "江苏",
        "安徽省", "安徽",
        "江西省", "江西",
        "台湾省", "台湾",
        "重庆市", "重庆",
        "上海市", "上海",
        "北京市", "北京",
        "天津市", "天津",
        "香港特别行政区", "香港",
        "澳门特别行政区", "澳门",
    ]

    clean_location = location_str
    for province in provinces:
        if location_str.startswith(province):
            clean_location = location_str[len(province):]
            break

    # 尝试从清理后的字符串中匹配
    # 例如："新疆阿克苏地区库车市" -> 清理后 "阿克苏地区库车市"
    # 先尝试匹配 "库车市"，再匹配 "库车"，再匹配 "阿克苏市" 等
    for city_name in sorted_cities:
        if city_name in clean_location:
            return city_mapping[city_name]

    # 策略3：按"区"、"县"、"市"分割，提取关键地名
    # 例如："新疆阿克苏地区库车市" -> ["新疆", "阿克苏地区", "库车市"]
    # 取最后一部分 "库车市" 进行匹配
    keywords = ["自治区", "盟", "地区", "自治州", "市", "县", "区", "旗"]

    # 从后往前查找分隔符
    last_part = location_str
    for keyword in keywords:
        if keyword in location_str:
            # 找到最后一个关键词
            idx = location_str.rfind(keyword)
            if idx != -1:
                # 提取关键词前面的部分
                before_keyword = location_str[:idx]
                # 找倒数第二个分隔符
                for kw2 in keywords:
                    idx2 = before_keyword.rfind(kw2)
                    if idx2 != -1:
                        last_part = before_keyword[idx2 + len(kw2):]
                        break
                break

    # 尝试匹配最后一部分
    last_part = last_part.strip()
    for city_name in sorted_cities:
        if city_name in last_part or last_part in city_name:
            return city_mapping[city_name]

    # 策略4：如果是海域或国外，返回 None
    if any(keyword in location_str for keyword in ["海域", "群岛", "洋"]):
        return None

    foreign_keywords = [
        "缅甸", "日本", "哈萨克斯坦", "塔吉克斯坦", "印尼",
        "菲律宾", "印度", "克什米尔", "泰国", "越南", "老挝",
        "蒙古", "俄罗斯", "尼泊尔", "不丹", "孟加拉", "斯里兰卡"
    ]
    if any(keyword in location_str for keyword in foreign_keywords):
        return None

    # 如果所有策略都失败，返回 None
    return None


def is_in_china(latitude, longitude):
    """
    判断经纬度是否在中国境内

    中国范围：
    - 纬度：3°N ~ 54°N
    - 经度：73°E ~ 135°E
    """
    return (3 <= latitude <= 54) and (73 <= longitude <= 135)


def fetch_earthquake_data(days=30):
    """
    抓取最近 N 天的中国地震数据

    Args:
        days: 抓取最近几天的数据（默认30天）
    """
    print(f"开始抓取最近 {days} 天的地震数据...")
    print(f"API地址: https://www.ceic.ac.cn/data/data.json\n")

    china_earthquakes = []

    try:
        # 添加浏览器请求头
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'application/json, text/plain, */*',
            'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
            'Referer': 'https://www.ceic.ac.cn/',
        }

        # 发送请求
        url = "https://www.ceic.ac.cn/data/data.json"
        response = requests.get(url, headers=headers, timeout=15)
        response.encoding = 'utf-8'

        print(f"HTTP状态码: {response.status_code}")

        if response.status_code != 200:
            print(f"❌ 请求失败，状态码: {response.status_code}")
            return []

        # 解析JSON
        import json
        data = response.json()

        # 检查数据结构
        if isinstance(data, list):
            earthquake_list = data
        elif isinstance(data, dict) and 'earthquakes' in data:
            earthquake_list = data['earthquakes']
        elif isinstance(data, dict):
            # 可能是单层对象，直接就是列表
            earthquake_list = list(data.values())[0] if data else []
        else:
            print(f"⚠️  未知的数据结构: {type(data)}")
            return []

        print(f"✅ API返回 {len(earthquake_list)} 条地震数据\n")

        # 解析并过滤中国地震
        for item in earthquake_list:
            try:
                latitude = float(item.get('latitude', 0))
                longitude = float(item.get('longitude', 0))

                earthquake = {
                    'id': item.get('id', ''),
                    'location': item.get('location', ''),
                    'time': item.get('time', ''),
                    'latitude': latitude,
                    'longitude': longitude,
                    'depth': float(item.get('depth', 0)),
                    'magnitude': float(item.get('magnitude', 0)),
                }

                # 过滤中国地震
                if is_in_china(latitude, longitude):
                    china_earthquakes.append(earthquake)

            except Exception as e:
                print(f"⚠️  解析单条数据失败: {str(e)}")
                continue

        print(f"🇨🇳 筛选后 {len(china_earthquakes)} 条中国地震数据\n")

    except requests.exceptions.RequestException as e:
        print(f"❌ 网络请求失败: {str(e)}")
        return []
    except json.JSONDecodeError as e:
        print(f"❌ JSON解析失败: {str(e)}")
        print(f"响应内容前500字符:\n{response.text[:500]}")
        return []
    except Exception as e:
        print(f" 未知错误: {str(e)}")
        import traceback
        traceback.print_exc()
        return []

    return china_earthquakes


# ... existing code ...

def import_earthquakes_to_db(earthquakes):
    """
    将地震数据导入数据库（智能匹配版 + 待审核记录）

    Args:
        earthquakes: 地震数据列表
    """
    with app.app_context():
        print("开始导入数据到数据库...")

        # 获取城市映射
        city_mapping = get_city_mapping()
        print(f"已加载 {len(city_mapping)} 个城市映射\n")

        success_count = 0
        skip_count = 0
        fail_count = 0
        unmatched_locations = {}  # 用字典统计重复位置

        for eq in earthquakes:
            try:
                # 1. 查找城市（只匹配已有城市）
                city_id = parse_location_to_city(eq['location'], city_mapping)

                # 2. 未匹配，记录到待审核（不自动添加）
                if not city_id:
                    loc = eq['location']
                    if loc not in unmatched_locations:
                        unmatched_locations[loc] = {
                            'count': 0,
                            'latest_magnitude': None,
                            'latest_time': None,
                            'sample_data': []
                        }

                    unmatched_locations[loc]['count'] += 1
                    unmatched_locations[loc]['latest_magnitude'] = eq['magnitude']
                    unmatched_locations[loc]['latest_time'] = datetime.strptime(eq['time'], '%Y-%m-%d %H:%M:%S')

                    # 保存前3条示例数据
                    if len(unmatched_locations[loc]['sample_data']) < 3:
                        unmatched_locations[loc]['sample_data'].append(eq)

                    skip_count += 1
                    continue

                # 3. 检查是否已存在（避免重复导入）
                existing = EarthquakeInfo.query.filter_by(
                    earthquake_time=datetime.strptime(eq['time'], '%Y-%m-%d %H:%M:%S'),
                    latitude=eq['latitude'],
                    longitude=eq['longitude']
                ).first()

                if existing:
                    skip_count += 1
                    continue

                # 4. 创建新记录
                earthquake = EarthquakeInfo(
                    city_id=city_id,
                    earthquake_time=datetime.strptime(eq['time'], '%Y-%m-%d %H:%M:%S'),
                    latitude=eq['latitude'],
                    longitude=eq['longitude'],
                    depth=eq['depth'],
                    magnitude=eq['magnitude'],
                    earthquake_message=eq['location']
                )

                db.session.add(earthquake)
                db.session.flush()
                success_count += 1

                if success_count % 50 == 0:
                    print(f"已导入 {success_count} 条...")

            except Exception as e:
                print(f"❌ 导入失败: {eq}, 错误: {str(e)}")
                fail_count += 1
                db.session.rollback()

        db.session.commit()

        # 保存未匹配位置到待审核表
        pending_count = save_pending_locations(unmatched_locations)

        # 打印统计信息
        print(f"\n{'=' * 60}")
        print(f"导入完成！")
        print(f" ✅ 成功: {success_count} 条")
        print(f" ⚠️  跳过: {skip_count} 条")
        print(f" ❌ 失败: {fail_count} 条")
        print(f" 📋 待审核位置: {pending_count} 个")
        print(f" 总计: {len(earthquakes)} 条")
        print(f"{'=' * 60}\n")


def save_pending_locations(unmatched_dict):
    """
    保存未匹配位置到待审核表

    Args:
        unmatched_dict: 未匹配位置统计字典

    Returns:
        保存的数量
    """
    import json

    count = 0
    for location_name, data in unmatched_dict.items():
        # 检查是否已存在
        existing = PendingLocation.query.filter_by(
            location_name=location_name,
            status='pending'
        ).first()

        if existing:
            # 更新现有记录
            existing.occurrence_count = data['count']
            existing.latest_magnitude = data['latest_magnitude']
            existing.latest_time = data['latest_time']
            count += 1
        else:
            # 推测省份
            province_candidate = infer_province_name(location_name)

            # 提取候选城市名
            city_candidate = extract_city_candidate(location_name)

            # 创建新记录
            pending = PendingLocation(
                location_name=location_name,
                province_candidate=province_candidate,
                city_candidate=city_candidate,
                occurrence_count=data['count'],
                latest_magnitude=data['latest_magnitude'],
                latest_time=data['latest_time'],
                sample_earthquakes=json.dumps(data['sample_data'], ensure_ascii=False, default=str)
            )
            db.session.add(pending)
            count += 1

    db.session.commit()

    print(f"\n✅ 已保存 {count} 个位置到待审核列表")
    print(f"   管理员可在后台查看并审核")

    return count


def infer_province_name(location_str):
    """推断省份名称"""
    province_keywords = {
        "新疆": "新疆维吾尔自治区",
        "内蒙古": "内蒙古自治区",
        "西藏": "西藏自治区",
        "宁夏": "宁夏回族自治区",
        "广西": "广西壮族自治区",
        "北京": "北京市",
        "天津": "天津市",
        "上海": "上海市",
        "重庆": "重庆市",
        "河北": "河北省",
        "山西": "山西省",
        "辽宁": "辽宁省",
        "吉林": "吉林省",
        "黑龙江": "黑龙江省",
        "江苏": "江苏省",
        "浙江": "浙江省",
        "安徽": "安徽省",
        "福建": "福建省",
        "江西": "江西省",
        "山东": "山东省",
        "河南": "河南省",
        "湖北": "湖北省",
        "湖南": "湖南省",
        "广东": "广东省",
        "海南": "海南省",
        "四川": "四川省",
        "贵州": "贵州省",
        "云南": "云南省",
        "陕西": "陕西省",
        "甘肃": "甘肃省",
        "青海": "青海省",
        "台湾": "台湾省",
    }

    for keyword, province_name in province_keywords.items():
        if keyword in location_str:
            return province_name

    return None


def extract_city_candidate(location_str):
    """从位置字符串中提取候选城市名"""
    import re

    # 策略1：提取"市"
    match = re.search(r'([^省市区县旗盟]+?市)$', location_str)
    if match:
        return match.group(1)

    # 策略2：提取"地区"、"盟"、"州"
    match = re.search(r'([^省]+?(?:地区|盟|州))$', location_str)
    if match:
        return match.group(1)

    # 策略3：提取"县"
    match = re.search(r'([^省市区县旗盟]+?县)$', location_str)
    if match:
        return match.group(1)

    return None


def infer_province_from_location(location_str):
    """
    从位置字符串中推断所属省份

    Args:
        location_str: 位置字符串

    Returns:
        province_id 或 None
    """
    province_keywords = {
        "新疆": "新疆维吾尔自治区",
        "内蒙古": "内蒙古自治区",
        "西藏": "西藏自治区",
        "宁夏": "宁夏回族自治区",
        "广西": "广西壮族自治区",
        "北京": "北京市",
        "天津": "天津市",
        "上海": "上海市",
        "重庆": "重庆市",
        "河北": "河北省",
        "山西": "山西省",
        "辽宁": "辽宁省",
        "吉林": "吉林省",
        "黑龙江": "黑龙江省",
        "江苏": "江苏省",
        "浙江": "浙江省",
        "安徽": "安徽省",
        "福建": "福建省",
        "江西": "江西省",
        "山东": "山东省",
        "河南": "河南省",
        "湖北": "湖北省",
        "湖南": "湖南省",
        "广东": "广东省",
        "海南": "海南省",
        "四川": "四川省",
        "贵州": "贵州省",
        "云南": "云南省",
        "陕西": "陕西省",
        "甘肃": "甘肃省",
        "青海": "青海省",
        "台湾": "台湾省",
    }

    with app.app_context():
        for keyword, province_name in province_keywords.items():
            if keyword in location_str:
                province = Province.query.filter_by(province_name=province_name).first()
                if province:
                    return province.province_id

        return None



def main():
    """主函数"""
    from datetime import timedelta

    print("\n" + "=" * 60)
    print(" 中国地震目录爬虫")
    print("=" * 60 + "\n")

    # 抓取数据
    earthquakes = fetch_earthquake_data(days=30)  # 抓取最近30天

    if not earthquakes:
        print("没有抓取到数据，程序退出")
        return

    # 导入数据库
    import_earthquakes_to_db(earthquakes)

    print("\n✅ 爬虫运行完成！")


if __name__ == '__main__':
    main()
