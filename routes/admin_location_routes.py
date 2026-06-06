"""
管理员 - 待审核位置管理路由
"""
from flask import Blueprint, request, jsonify
from services.admin_location_service import (
    svc_get_pending_locations,
    svc_approve_location,
    svc_reject_location,
    svc_batch_approve
)
from services.admin_service import verify_admin

admin_location_bp = Blueprint('admin_location', __name__, url_prefix='/api/admin/locations')


@admin_location_bp.route('/pending', methods=['GET'])
def get_pending_locations():
    """获取待审核位置列表"""
    if not verify_admin():
        return jsonify({'code': 403, 'message': '无权限，请先以管理员身份登录'}), 403

    return svc_get_pending_locations()


@admin_location_bp.route('/approve/<int:location_id>', methods=['POST'])
def approve_location(location_id):
    """审核通过并添加城市"""
    if not verify_admin():
        return jsonify({'code': 403, 'message': '无权限，请先以管理员身份登录'}), 403

    data = request.get_json()
    city_name = data.get('city_name')
    province_id = data.get('province_id')

    if not city_name or not province_id:
        return jsonify({'code': 400, 'message': '缺少参数'}), 400

    return svc_approve_location(location_id, city_name, province_id)


@admin_location_bp.route('/reject/<int:location_id>', methods=['POST'])
def reject_location(location_id):
    """拒绝该位置（国外地震等）"""
    if not verify_admin():
        return jsonify({'code': 403, 'message': '无权限，请先以管理员身份登录'}), 403

    return svc_reject_location(location_id)


@admin_location_bp.route('/batch_approve', methods=['POST'])
def batch_approve_locations():
    """批量审核通过"""
    if not verify_admin():
        return jsonify({'code': 403, 'message': '无权限，请先以管理员身份登录'}), 403

    data = request.get_json()
    location_ids = data.get('location_ids', [])
    province_id = data.get('province_id')

    if not location_ids or not province_id:
        return jsonify({'code': 400, 'message': '缺少参数'}), 400

    return svc_batch_approve(location_ids, province_id)
