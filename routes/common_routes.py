from flask import Blueprint, request
from services.common_service import svc_list_earthquake, svc_earthquake_stats_province, svc_earthquake_stats_city, svc_earthquake_stats_trend, svc_earthquake_stats_magnitude, svc_earthquake_rank, svc_earthquake_city_rank, svc_get_provinces_group_by_region, svc_get_all_provinces, svc_earthquake_statistics, svc_get_all_cities, svc_ai_chat, svc_simulate_earthquake_alert
from websocket_service import check_and_push_earthquake_alert

common_bp = Blueprint("common", __name__, url_prefix="/api")

# ======================
# 公共接口（所有人可看）
# ======================

# 地震列表
@common_bp.route("/earthquake/list", methods=["GET"])
def eq_list():
    return svc_list_earthquake()

# 省份列表
@common_bp.route("/provinces", methods=["GET"])
def provinces():
    return svc_get_all_provinces()

# 城市列表
@common_bp.route("/cities", methods=["GET"])
def cities():
    return svc_get_all_cities()

# 省份地震统计（饼图）
@common_bp.route("/earthquake/stats/province", methods=["GET"])
def earthquake_stats_province():
    return svc_earthquake_stats_province()

# 城市地震统计
@common_bp.route("/earthquake/stats/city", methods=["GET"])
def earthquake_stats_city():
    return svc_earthquake_stats_city()

# 时间趋势统计（折线图）
@common_bp.route("/earthquake/stats/trend", methods=["GET"])
def earthquake_stats_trend():
    return svc_earthquake_stats_trend()

# 震级分布统计（柱状图）
@common_bp.route("/earthquake/stats/magnitude", methods=["GET"])
def earthquake_stats_magnitude():
    return svc_earthquake_stats_magnitude()

# 地震频次 TOP5 排名（省份）
@common_bp.route("/earthquake/rank", methods=["GET"])
def earthquake_rank():
    return svc_earthquake_rank()

# 城市地震频次 TOP5 排名
@common_bp.route("/earthquake/city_rank", methods=["GET"])
def earthquake_city_rank():
    return svc_earthquake_city_rank()


@common_bp.route("/province/group", methods=["GET"])
def get_provinces_group_by_region():
    return svc_get_provinces_group_by_region()

# ======================
# 数据统计接口
# ======================
@common_bp.route("/statistics", methods=["GET"])
def earthquake_statistics():
    return svc_earthquake_statistics()

# ======================
# AI智能问答接口
# ======================
@common_bp.route("/ai/chat", methods=["POST"])
def ai_chat():
    """AI智能问答接口"""
    return svc_ai_chat()


# ======================
# 模拟地震预警（持久化到数据库）
# ======================
@common_bp.route("/earthquake/simulate-alert", methods=["POST"])
def simulate_earthquake_alert():
    """模拟地震预警 - 创建真实地震数据和预警记录"""
    return svc_simulate_earthquake_alert()



