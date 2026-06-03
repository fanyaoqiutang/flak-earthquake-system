from flask import Blueprint, request
from services.common_service import *
from services.common_service import svc_get_provinces_group_by_region
from services.common_service import svc_ai_chat
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

# 省份地震统计（饼图）
@common_bp.route("/earthquake/stats/province", methods=["GET"])
def earthquake_stats_province():
    return svc_earthquake_stats_province()

# 时间趋势统计（折线图）
@common_bp.route("/earthquake/stats/trend", methods=["GET"])
def earthquake_stats_trend():
    return svc_earthquake_stats_trend()

# 震级分布统计（柱状图）
@common_bp.route("/earthquake/stats/magnitude", methods=["GET"])
def earthquake_stats_magnitude():
    return svc_earthquake_stats_magnitude()

# 地震频次 TOP5 排名
@common_bp.route("/earthquake/rank", methods=["GET"])
def earthquake_rank():
    return svc_earthquake_rank()


@common_bp.route("/province/group", methods=["GET"])
def get_provinces_group_by_region():
    return svc_get_provinces_group_by_region()

# ======================
# AI 智能问答接口
# ======================
@common_bp.route("/ai/chat", methods=["POST"])
def ai_chat():
    return svc_ai_chat()

# ======================
# 数据统计接口
# ======================
@common_bp.route("/statistics", methods=["GET"])
def earthquake_statistics():
    return svc_earthquake_statistics()
