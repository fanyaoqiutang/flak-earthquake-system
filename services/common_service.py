from flask import request, jsonify
from models import EarthquakeInfo, Province, City, db, UserSubscribeProvince
from sqlalchemy import func, and_
from datetime import datetime, timedelta



# 地震列表信息按条件筛查
def svc_list_earthquake():
    province_id = request.args.get('province_id')
    city_id = request.args.get('city_id')
    province_name = request.args.get('province_name', '').strip()
    city_name = request.args.get('city_name', '').strip()
    time_scope = request.args.get("time", "1y")
    mag_min = request.args.get("mag_min", type=float, default=0)

    query = EarthquakeInfo.query.join(City, EarthquakeInfo.city_id == City.city_id) \
        .join(Province, City.province_id == Province.province_id)
    query = query.order_by(EarthquakeInfo.earthquake_time.desc())

    # 时间筛选
    now = datetime.now()
    if time_scope == "24h":
        start = now - timedelta(days=1)
    elif time_scope == "7d":
        start = now - timedelta(days=7)
    elif time_scope == "30d":
        start = now - timedelta(days=30)
    else:
        start = now - timedelta(days=365)
    query = query.filter(EarthquakeInfo.earthquake_time >= start)

    # 最低震级筛选
    if mag_min > 0:
        query = query.filter(EarthquakeInfo.magnitude >= mag_min)

    # 省份ID筛选
    if province_id:
        try:
            query = query.filter(City.province_id == int(province_id))
        except (ValueError, TypeError):
            return jsonify({"code": 400, "msg": "省份ID格式错误"}), 400

    # 城市ID筛选
    if city_id:
        try:
            query = query.filter(EarthquakeInfo.city_id == int(city_id))
        except (ValueError, TypeError):
            return jsonify({"code": 400, "msg": "城市ID格式错误"}), 400

    # 省份名称模糊查询
    if province_name:
        like_key = f"%{province_name}%"
        query = query.filter(Province.province_name.like(like_key))

    # 城市名称模糊查询
    if city_name:
        like_key = f"%{city_name}%"
        query = query.filter(City.city_name.like(like_key))

    lst = query.all()
    res = []
    for eq in lst:
        city = eq.city
        province = city.province if city else None
        res.append({
            "earthquake_id": eq.earthquake_id,
            "province_name": province.province_name if province else "未知",
            "city_name": city.city_name if city else "未知",
            "earthquake_time": eq.earthquake_time.strftime("%Y-%m-%d %H:%M:%S"),
            "latitude": eq.latitude,
            "longitude": eq.longitude,
            "depth": eq.depth,
            "magnitude": eq.magnitude
        })
    return jsonify({"code": 200, "data": res, "total": len(res)})


# 查询所有省份
def svc_get_all_provinces():
    provinces = Province.query.all()
    res = [{"province_id": p.province_id, "province_name": p.province_name} for p in provinces]
    return jsonify({"code": 200, "data": res})


# 查询所有城市（新增）
def svc_get_all_cities():
    province_id = request.args.get('province_id')

    query = City.query
    if province_id:
        query = query.filter_by(province_id=int(province_id))

    cities = query.all()
    res = [{
        "city_id": c.city_id,
        "city_name": c.city_name,
        "province_id": c.province_id,
        "province_name": c.province.province_name
    } for c in cities]
    return jsonify({"code": 200, "data": res})


# 按七大地理大区对省份分组，用于批量订阅，按大区分类
def svc_get_provinces_group_by_region():
    # 定义7大地区（包含华北地区）
    regions = [
        "华北地区", "东北地区", "华东地区", "华中地区",
        "华南地区", "西南地区", "西北地区", "港澳台地区"
    ]

    result = []

    for region_name in regions:
        # 查询该地区的省份
        provinces = Province.query.filter_by(region=region_name).all()

        result.append({
            "region_name": region_name,
            "province_list": [
                {"province_id": p.province_id, "province_name": p.province_name}
                for p in provinces
            ]
        })

    # 如果所有地区都没有数据，返回所有省份到第一个地区
    if all(len(r["province_list"]) == 0 for r in result):
        all_provinces = Province.query.all()
        result[0]["province_list"] = [
            {"province_id": p.province_id, "province_name": p.province_name}
            for p in all_provinces
        ]

    return jsonify({"code": 200, "data": result})



# 统计每个省份的地震次数（按省份聚合城市数据）
def svc_earthquake_stats_province():
    thirty_days_ago = datetime.now() - timedelta(days=30)
    data = (
        db.session.query(
            Province.province_name,
            func.count(EarthquakeInfo.earthquake_id).label("count")
        )
        .join(City, Province.province_id == City.province_id)
        .join(EarthquakeInfo, City.city_id == EarthquakeInfo.city_id)
        .filter(EarthquakeInfo.earthquake_time >= thirty_days_ago)
        .group_by(Province.province_id)
        .all()
    )
    return jsonify({
        "code": 200,
        "data": [{"name": n, "value": c} for n, c in data]
    })


# 统计每个城市的地震次数（新增城市级别统计）
def svc_earthquake_stats_city():
    thirty_days_ago = datetime.now() - timedelta(days=30)
    data = (
        db.session.query(
            City.city_name,
            func.count(EarthquakeInfo.earthquake_id).label("count")
        )
        .join(EarthquakeInfo)
        .filter(EarthquakeInfo.earthquake_time >= thirty_days_ago)
        .group_by(City.city_id)
        .all()
    )
    return jsonify({
        "code": 200,
        "data": [{"name": n, "value": c} for n, c in data]
    })


# 统计每日地震数量，生成时间趋势折线图
def svc_earthquake_stats_trend():
    # 计算30天前的时间
    thirty_days_ago = datetime.now() - timedelta(days=30)

    rows = (
        db.session.query(
            func.date(EarthquakeInfo.earthquake_time).label("dt"),
            func.count(EarthquakeInfo.earthquake_id)
        )
        .filter(EarthquakeInfo.earthquake_time >= thirty_days_ago)
        .group_by(func.date(EarthquakeInfo.earthquake_time))
        .order_by("dt")
        .all()
    )

    return jsonify({
        "code": 200,
        "data": [{"date": str(d), "count": c} for d, c in rows]
    })


# 地震高发省份 TOP5 排名（按省份聚合）
def svc_earthquake_rank():
    data = db.session.query(
        Province.province_name,
        func.count(EarthquakeInfo.earthquake_id).label("count")
    ).join(City, Province.province_id == City.province_id) \
        .join(EarthquakeInfo, City.city_id == EarthquakeInfo.city_id) \
        .group_by(Province.province_id) \
        .order_by(func.count(EarthquakeInfo.earthquake_id).desc()) \
        .limit(5) \
        .all()

    res = []
    for idx, (name, count) in enumerate(data, 1):
        res.append({
            "rank": idx,
            "name": name,
            "count": count
        })
    return jsonify({"code": 200, "data": res})


# 地震高发城市 TOP5 排名（新增）
def svc_earthquake_city_rank():
    data = db.session.query(
        City.city_name,
        func.count(EarthquakeInfo.earthquake_id).label("count")
    ).join(EarthquakeInfo) \
        .group_by(City.city_id) \
        .order_by(func.count(EarthquakeInfo.earthquake_id).desc()) \
        .limit(5) \
        .all()

    res = []
    for idx, (name, count) in enumerate(data, 1):
        res.append({
            "rank": idx,
            "name": name,
            "count": count
        })
    return jsonify({"code": 200, "data": res})


# 统计多条件统计 支持省份，城市，时间范围，最低震级筛选，一次返回趋势，震级，省份排行
def svc_earthquake_statistics():
    # 获取前端筛选参数
    province_id = request.args.get('province_id')
    city_id = request.args.get('city_id')
    start_time = request.args.get('start_time')
    end_time = request.args.get('end_time')
    mag_min = request.args.get('mag_min', 0, type=float)

    query = EarthquakeInfo.query.join(City, EarthquakeInfo.city_id == City.city_id)

    # 省份筛选
    if province_id:
        try:
            query = query.filter(City.province_id == int(province_id))
        except:
            return jsonify({"code": 400, "msg": "省份ID格式错误"}), 400

    # 城市筛选
    if city_id:
        try:
            query = query.filter(EarthquakeInfo.city_id == int(city_id))
        except:
            return jsonify({"code": 400, "msg": "城市ID格式错误"}), 400

    # 时间范围筛选
    if start_time and end_time:
        try:
            start_dt = datetime.strptime(start_time, "%Y-%m-%d %H:%M:%S")
            end_dt = datetime.strptime(end_time, "%Y-%m-%d %H:%M:%S")
            query = query.filter(
                and_(
                    EarthquakeInfo.earthquake_time >= start_dt,
                    EarthquakeInfo.earthquake_time <= end_dt
                )
            )
        except:
            return jsonify({"code": 400, "msg": "时间格式错误"}), 400

    # 最低震级筛选
    if mag_min > 0:
        query = query.filter(EarthquakeInfo.magnitude >= mag_min)

    earthquake_list = query.all()

    trend_data = get_trend_data(earthquake_list)
    magnitude_data = get_magnitude_data(earthquake_list)
    province_data = get_province_data(earthquake_list)
    city_data = get_city_data(earthquake_list)

    return jsonify({
        "code": 200,
        "data": {
            "trend": trend_data,
            "magnitude": magnitude_data,
            "province": province_data,
            "city": city_data
        }
    })


# 生成时间趋势
def get_trend_data(earthquake_list):
    trend_dict = {}

    for eq in earthquake_list:
        date_str = eq.earthquake_time.strftime("%Y-%m-%d")
        trend_dict[date_str] = trend_dict.get(date_str, 0) + 1
    # 按日期排序，列表返回
    trend_list = [{"date": k, "count": v} for k, v in sorted(trend_dict.items())]
    return trend_list


# 按震级区间统计 自定义6个震级分段
def get_magnitude_data(earthquake_list):
    ranges = [
        ("0-2.9", 0, 2.9),
        ("3.0-3.9", 3.0, 3.9),
        ("4.0-4.9", 4.0, 4.9),
        ("5.0-5.9", 5.0, 5.9),
        ("6.0-6.9", 6.0, 6.9),
        ("7.0+", 7.0, 99.9)
    ]

    magnitude_list = []
    for range_name, min_mag, max_mag in ranges:
        # 统计地震数量
        count = sum(1 for eq in earthquake_list if min_mag <= eq.magnitude <= max_mag)
        # 当前区间所有震级，最大值，平均值
        mags = [eq.magnitude for eq in earthquake_list if min_mag <= eq.magnitude <= max_mag]
        max_mag_val = max(mags) if mags else 0
        avg_mag_val = sum(mags) / len(mags) if mags else 0

        magnitude_list.append({
            "range": range_name,
            "count": count,
            "max_mag": max_mag_val,
            "avg_mag": avg_mag_val
        })

    return magnitude_list


# 按省份统计并倒序
def get_province_data(earthquake_list):
    province_dict = {}
    # 按省份分组统计
    for eq in earthquake_list:
        city = eq.city
        if city and city.province:
            p = city.province
            province_dict[p.province_id] = {
                "province_name": p.province_name,
                "count": province_dict.get(p.province_id, {}).get("count", 0) + 1
            }

    province_list = [{"province_name": v["province_name"], "count": v["count"]}
                     for v in province_dict.values()]
    province_list.sort(key=lambda x: x["count"], reverse=True)

    return province_list


# 按城市统计并倒序（新增）
def get_city_data(earthquake_list):
    city_dict = {}
    # 按城市分组统计
    for eq in earthquake_list:
        city = eq.city
        if city:
            city_dict[city.city_id] = {
                "city_name": city.city_name,
                "province_name": city.province.province_name if city.province else "未知",
                "count": city_dict.get(city.city_id, {}).get("count", 0) + 1
            }

    city_list = [{"city_name": v["city_name"], "province_name": v["province_name"], "count": v["count"]}
                 for v in city_dict.values()]
    city_list.sort(key=lambda x: x["count"], reverse=True)

    return city_list


# 震级分布统计（柱状图）
def svc_earthquake_stats_magnitude():
    """统计不同震级区间的地震数量"""
    thirty_days_ago = datetime.now() - timedelta(days=30)

    # 定义震级区间
    ranges = [
        ("0-2.9", 0, 2.9),
        ("3.0-3.9", 3.0, 3.9),
        ("4.0-4.9", 4.0, 4.9),
        ("5.0-5.9", 5.0, 5.9),
        ("6.0-6.9", 6.0, 6.9),
        ("7.0+", 7.0, 99.9)
    ]

    result = []
    for range_name, min_mag, max_mag in ranges:
        count = db.session.query(func.count(EarthquakeInfo.earthquake_id)).filter(
            and_(
                EarthquakeInfo.earthquake_time >= thirty_days_ago,
                EarthquakeInfo.magnitude >= min_mag,
                EarthquakeInfo.magnitude <= max_mag
            )
        ).scalar()

        result.append({
            "name": range_name,
            "value": count
        })

    return jsonify({
        "code": 200,
        "data": result
    })