from flask import request, jsonify
from models import EarthquakeInfo, Province, db
from sqlalchemy import func


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