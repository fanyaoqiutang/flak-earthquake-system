"""
管理员 - 待审核位置服务层
"""
from flask import request, jsonify
from models import db, PendingLocation, City, Province
from datetime import datetime
import json


def svc_get_pending_locations():
    """获取待审核位置列表"""
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)
        status = request.args.get('status', 'pending')

        query = PendingLocation.query

        if status:
            query = query.filter_by(status=status)

        query = query.order_by(PendingLocation.occurrence_count.desc())

        pagination = query.paginate(page=page, per_page=per_page, error_out=False)

        locations = []
        for loc in pagination.items:
            locations.append({
                'id': loc.id,
                'location_name': loc.location_name,
                'province_candidate': loc.province_candidate,
                'city_candidate': loc.city_candidate,
                'occurrence_count': loc.occurrence_count,
                'latest_magnitude': loc.latest_magnitude,
                'latest_time': loc.latest_time.strftime('%Y-%m-%d %H:%M:%S') if loc.latest_time else None,
                'sample_earthquakes': json.loads(loc.sample_earthquakes) if loc.sample_earthquakes else [],
                'created_at': loc.created_at.strftime('%Y-%m-%d %H:%M:%S'),
                'status': loc.status
            })

        # 统计各状态数量
        stats = {
            'pending': PendingLocation.query.filter_by(status='pending').count(),
            'approved': PendingLocation.query.filter_by(status='approved').count(),
            'rejected': PendingLocation.query.filter_by(status='rejected').count()
        }

        return jsonify({
            'code': 200,
            'data': {
                'items': locations,
                'total': pagination.total,
                'pages': pagination.pages,
                'current_page': page,
                'stats': stats
            }
        })

    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({'code': 500, 'message': f'查询失败: {str(e)}'}), 500


def svc_approve_location(location_id, city_name, province_id):
    """审核通过并添加城市"""
    try:
        pending = PendingLocation.query.get(location_id)
        if not pending:
            return jsonify({'code': 404, 'message': '记录不存在'}), 404

        province = Province.query.get(province_id)
        if not province:
            return jsonify({'code': 404, 'message': '省份不存在'}), 404

        existing_city = City.query.filter_by(city_name=city_name).first()
        if existing_city:
            city_id = existing_city.city_id
        else:
            new_city = City(
                city_name=city_name,
                province_id=province_id
            )
            db.session.add(new_city)
            db.session.flush()
            city_id = new_city.city_id

        pending.status = 'approved'
        pending.updated_at = datetime.utcnow()

        db.session.commit()

        return jsonify({
            'code': 200,
            'message': '审核通过，城市已添加',
            'city_id': city_id
        })

    except Exception as e:
        db.session.rollback()
        return jsonify({'code': 500, 'message': f'审核失败: {str(e)}'}), 500


def svc_reject_location(location_id):
    """拒绝该位置"""
    try:
        pending = PendingLocation.query.get(location_id)
        if not pending:
            return jsonify({'code': 404, 'message': '记录不存在'}), 404

        pending.status = 'rejected'
        pending.updated_at = datetime.utcnow()

        db.session.commit()

        return jsonify({
            'code': 200,
            'message': '已拒绝'
        })

    except Exception as e:
        db.session.rollback()
        return jsonify({'code': 500, 'message': f'操作失败: {str(e)}'}), 500


def svc_batch_approve(location_ids, province_id):
    """批量审核通过（使用相同省份）"""
    try:
        approved_count = 0

        for location_id in location_ids:
            pending = PendingLocation.query.get(location_id)
            if not pending or pending.status != 'pending':
                continue

            city_name = pending.city_candidate or pending.location_name

            existing_city = City.query.filter_by(city_name=city_name).first()
            if existing_city:
                city_id = existing_city.city_id
            else:
                new_city = City(
                    city_name=city_name,
                    province_id=province_id
                )
                db.session.add(new_city)
                db.session.flush()
                city_id = new_city.city_id

            pending.status = 'approved'
            approved_count += 1

        db.session.commit()

        return jsonify({
            'code': 200,
            'message': f'批量审核完成，通过{approved_count}个'
        })

    except Exception as e:
        db.session.rollback()
        return jsonify({'code': 500, 'message': f'批量审核失败: {str(e)}'}), 500
