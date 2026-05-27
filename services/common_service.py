from flask import request, jsonify
from models import EarthquakeInfo, Province, db
from sqlalchemy import func, and_
from datetime import datetime


# ==========================
# 公共服务：地震列表（支持按省份筛选）
# ==========================
def svc_list_earthquake():
    province_id = request.args.get('province_id')

    query = EarthquakeInfo.query.order_by(EarthquakeInfo.earthquake_time.desc())

    if province_id:
        try:
            query = query.filter_by(province_id=int(province_id))
        except:
            return jsonify({"code": 400, "msg": "省份ID格式错误"}), 400

    lst = query.all()
    res = []
    for eq in lst:
        p = eq.province
        res.append({
            "earthquake_id": eq.earthquake_id,
            "province_id": eq.province_id,
            "province_name": p.province_name if p else "未知",
            "earthquake_time": eq.earthquake_time.strftime("%Y-%m-%d %H:%M:%S"),
            "latitude": eq.latitude,
            "longitude": eq.longitude,
            "depth": eq.depth,
            "magnitude": eq.magnitude,
            "earthquake_message": eq.earthquake_message
        })
    return jsonify({"code": 200, "data": res, "total": len(res)})


# ==========================
# 公共服务：获取所有省份
# ==========================
def svc_get_all_provinces():
    provinces = Province.query.all()
    res = [{"province_id": p.province_id, "province_name": p.province_name} for p in provinces]
    return jsonify({"code": 200, "data": res})


# ==========================
# 【新增】按地理大区分组获取省份（用于前端折叠面板）
# ==========================
def svc_get_provinces_group_by_region():
    regions = [
        "东北地区", "华东地区", "华中地区",
        "华南地区", "西南地区", "西北地区", "港澳台地区"
    ]
    result = []
    for region_name in regions:
        provinces = Province.query.filter_by(region=region_name).all()
        result.append({
            "region_name": region_name,
            "province_list": [
                {"province_id": p.province_id, "province_name": p.province_name}
                for p in provinces
            ]
        })
    return jsonify({"code": 200, "data": result})


# ==========================
# 图表1：省份地震数量统计（饼图）
# ==========================
def svc_earthquake_stats_province():
    data = db.session.query(
        Province.province_name,
        func.count(EarthquakeInfo.earthquake_id).label("count")
    ).join(EarthquakeInfo) \
        .group_by(Province.province_id) \
        .all()

    return jsonify({
        "code": 200,
        "data": [{"name": n, "value": c} for n, c in data]
    })


# ==========================
# 图表2：按日期统计地震趋势（折线图）
# ==========================
def svc_earthquake_stats_trend():
    rows = db.session.query(
        func.date(EarthquakeInfo.earthquake_time).label("dt"),
        func.count(EarthquakeInfo.earthquake_id)
    ).group_by(func.date(EarthquakeInfo.earthquake_time)) \
        .order_by("dt") \
        .all()

    return jsonify({
        "code": 200,
        "data": [{"date": str(d), "count": c} for d, c in rows]
    })


# ==========================
# 图表3：震级分布统计（柱状图）
# ==========================
def svc_earthquake_stats_magnitude():
    data = db.session.query(
        func.round(EarthquakeInfo.magnitude, 1).label("mag"),
        func.count(EarthquakeInfo.earthquake_id)
    ).group_by("mag") \
        .order_by("mag") \
        .all()

    return jsonify({
        "code": 200,
        "data": [{"mag": m, "count": c} for m, c in data]
    })


# ==========================
# 图表4：地震高发省份 TOP5 排名
# ==========================
def svc_earthquake_rank():
    data = db.session.query(
        Province.province_name,
        func.count(EarthquakeInfo.earthquake_id).label("count")
    ).join(EarthquakeInfo) \
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


# ==========================
# 【新增】综合数据统计接口（支持筛选条件）
# ==========================
def svc_earthquake_statistics():
    province_id = request.args.get('province_id')
    start_time = request.args.get('start_time')
    end_time = request.args.get('end_time')
    mag_min = request.args.get('mag_min', 0, type=float)

    query = EarthquakeInfo.query

    if province_id:
        try:
            query = query.filter_by(province_id=int(province_id))
        except:
            return jsonify({"code": 400, "msg": "省份ID格式错误"}), 400

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

    if mag_min > 0:
        query = query.filter(EarthquakeInfo.magnitude >= mag_min)

    earthquake_list = query.all()

    trend_data = get_trend_data(earthquake_list)
    magnitude_data = get_magnitude_data(earthquake_list)
    province_data = get_province_data(earthquake_list)

    return jsonify({
        "code": 200,
        "data": {
            "trend": trend_data,
            "magnitude": magnitude_data,
            "province": province_data
        }
    })


def get_trend_data(earthquake_list):
    trend_dict = {}
    for eq in earthquake_list:
        date_str = eq.earthquake_time.strftime("%Y-%m-%d")
        trend_dict[date_str] = trend_dict.get(date_str, 0) + 1

    trend_list = [{"date": k, "count": v} for k, v in sorted(trend_dict.items())]
    return trend_list


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
        count = sum(1 for eq in earthquake_list if min_mag <= eq.magnitude <= max_mag)
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


def get_province_data(earthquake_list):
    province_dict = {}
    for eq in earthquake_list:
        p = eq.province
        if p:
            province_dict[p.province_id] = {
                "province_name": p.province_name,
                "count": province_dict.get(p.province_id, {}).get("count", 0) + 1
            }

    province_list = [{"province_name": v["province_name"], "count": v["count"]}
                     for v in province_dict.values()]
    province_list.sort(key=lambda x: x["count"], reverse=True)

    return province_list
