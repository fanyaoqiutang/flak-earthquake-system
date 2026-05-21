from flask import request, jsonify
from models import EarthquakeInfo, Province

def svc_list_earthquake():
    province_id = request.args.get('province_id')
    if province_id:
        try:
            province_id = int(province_id)
            lst = EarthquakeInfo.query.filter_by(province_id=province_id).all()
        except:
            return jsonify({"code":400,"msg":"省份ID格式错误"}),400
    else:
        lst = EarthquakeInfo.query.all()
    res = []
    for eq in lst:
        p = Province.query.get(eq.province_id)
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
    return jsonify({"code":200,"data":res,"total":len(res)})

def svc_get_all_provinces():
    provinces = Province.query.all()
    res = [{"province_id":p.province_id,"province_name":p.province_name} for p in provinces]
    return jsonify({"code":200,"data":res})