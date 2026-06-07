from flask import Blueprint, request, jsonify
from flask_login import login_required, current_user
from models import db, ScienceCategory, EarthQuakePopular, AdminOperationLog
from functools import wraps

science_bp = Blueprint('science', __name__, url_prefix='/api/science')


# 管理员验证装饰器
def admin_required(f):
    @wraps(f)
    @login_required
    def decorated_function(*args, **kwargs):
        if not hasattr(current_user, 'admin_id'):
            return jsonify({'code': 403, 'message': '需要管理员权限'}), 403
        return f(*args, **kwargs)

    return decorated_function


# ========== 用户端接口（公开） ==========

@science_bp.route('/categories', methods=['GET'])
def get_categories():
    """获取所有分类"""
    categories = ScienceCategory.query.order_by(ScienceCategory.sort_order).all()
    return jsonify({
        'code': 200,
        'data': [{
            'category_id': c.category_id,
            'category_name': c.category_name,
            'category_icon': c.category_icon,
            'sort_order': c.sort_order
        } for c in categories]
    })


@science_bp.route('/articles', methods=['GET'])
def get_articles():
    """获取文章列表（可按分类筛选）"""
    category_id = request.args.get('category_id', type=int)

    query = EarthQuakePopular.query.filter_by(is_active=1)

    if category_id:
        query = query.filter_by(category_id=category_id)

    articles = query.order_by(EarthQuakePopular.create_time.desc()).all()

    return jsonify({
        'code': 200,
        'data': [{
            'article_id': a.id,
            'category_id': a.category_id,
            'category_name': a.category.category_name if a.category else '未分类',
            'title': a.title,
            'summary': a.summary,
            'icon': a.icon,
            'view_count': a.view_count,
            'create_time': a.create_time.strftime('%Y-%m-%d %H:%M:%S')
        } for a in articles]
    })


@science_bp.route('/articles/<int:article_id>', methods=['GET'])
def get_article_detail(article_id):
    """获取文章详情"""
    article = EarthQuakePopular.query.get_or_404(article_id)

    # 增加浏览量
    article.view_count += 1
    db.session.commit()

    return jsonify({
        'code': 200,
        'data': {
            'article_id': article.id,
            'category_id': article.category_id,
            'category_name': article.category.category_name if article.category else '未分类',
            'title': article.title,
            'content': article.content,
            'summary': article.summary,
            'icon': article.icon,
            'view_count': article.view_count,
            'source': article.source,
            'create_time': article.create_time.strftime('%Y-%m-%d %H:%M:%S'),
            'update_time': article.update_time.strftime('%Y-%m-%d %H:%M:%S') if article.update_time else ''
        }
    })


# ========== 管理员接口（需要权限） ==========

@science_bp.route('/admin/categories', methods=['POST'])
@admin_required
def create_category():
    """创建分类"""
    data = request.get_json()

    if not data.get('category_name'):
        return jsonify({'code': 400, 'message': '分类名称不能为空'}), 400

    if ScienceCategory.query.filter_by(category_name=data['category_name']).first():
        return jsonify({'code': 400, 'message': '分类已存在'}), 400

    category = ScienceCategory(
        category_name=data['category_name'],
        category_icon=data.get('category_icon', ''),
        sort_order=data.get('sort_order', 0)
    )
    db.session.add(category)
    db.session.commit()

    # 记录日志
    log = AdminOperationLog(
        admin_id=current_user.admin_id,
        operation='创建科普分类',
        target_earthquake_id=category.category_id
    )
    db.session.add(log)
    db.session.commit()

    return jsonify({'code': 200, 'message': '分类创建成功', 'data': {
        'category_id': category.category_id,
        'category_name': category.category_name
    }})


@science_bp.route('/admin/categories/<int:category_id>', methods=['PUT'])
@admin_required
def update_category(category_id):
    """更新分类"""
    category = ScienceCategory.query.get_or_404(category_id)
    data = request.get_json()

    if 'category_name' in data:
        existing = ScienceCategory.query.filter_by(category_name=data['category_name']).first()
        if existing and existing.category_id != category_id:
            return jsonify({'code': 400, 'message': '分类名称已存在'}), 400
        category.category_name = data['category_name']

    if 'category_icon' in data:
        category.category_icon = data['category_icon']

    if 'sort_order' in data:
        category.sort_order = data['sort_order']

    db.session.commit()

    return jsonify({'code': 200, 'message': '分类更新成功'})


@science_bp.route('/admin/categories/<int:category_id>', methods=['DELETE'])
@admin_required
def delete_category(category_id):
    """删除分类"""
    category = ScienceCategory.query.get_or_404(category_id)

    # 删除该分类下的所有文章
    EarthQuakePopular.query.filter_by(category_id=category_id).delete()
    db.session.delete(category)
    db.session.commit()

    return jsonify({'code': 200, 'message': '分类删除成功'})


@science_bp.route('/admin/articles', methods=['POST'])
@admin_required
def create_article():
    """创建文章"""
    data = request.get_json()

    if not all([data.get('title'), data.get('content'), data.get('category_id')]):
        return jsonify({'code': 400, 'message': '标题、内容和分类不能为空'}), 400

    # 检查分类是否存在
    if not ScienceCategory.query.get(data['category_id']):
        return jsonify({'code': 400, 'message': '分类不存在'}), 400

    article = EarthQuakePopular(
        category_id=data['category_id'],
        title=data['title'],
        content=data['content'],
        summary=data.get('summary', ''),
        icon=data.get('icon', '')
    )
    db.session.add(article)
    db.session.commit()

    return jsonify({'code': 200, 'message': '文章创建成功', 'data': {
        'article_id': article.id
    }})


@science_bp.route('/admin/articles/<int:article_id>', methods=['PUT'])
@admin_required
def update_article(article_id):
    """更新文章"""
    article = EarthQuakePopular.query.get_or_404(article_id)
    data = request.get_json()

    if 'title' in data:
        article.title = data['title']
    if 'content' in data:
        article.content = data['content']
    if 'summary' in data:
        article.summary = data['summary']
    if 'icon' in data:
        article.icon = data['icon']
    if 'category_id' in data:
        if not ScienceCategory.query.get(data['category_id']):
            return jsonify({'code': 400, 'message': '分类不存在'}), 400
        article.category_id = data['category_id']
    if 'is_active' in data:
        article.is_active = data['is_active']

    db.session.commit()

    return jsonify({'code': 200, 'message': '文章更新成功'})


@science_bp.route('/admin/articles/<int:article_id>', methods=['DELETE'])
@admin_required
def delete_article(article_id):
    """删除文章"""
    article = EarthQuakePopular.query.get_or_404(article_id)
    db.session.delete(article)
    db.session.commit()

    return jsonify({'code': 200, 'message': '文章删除成功'})


@science_bp.route('/admin/articles', methods=['GET'])
@admin_required
def admin_get_articles():
    """管理员获取文章列表（包含未启用的）"""
    category_id = request.args.get('category_id', type=int)

    query = EarthQuakePopular.query

    if category_id:
        query = query.filter_by(category_id=category_id)

    articles = query.order_by(EarthQuakePopular.create_time.desc()).all()

    return jsonify({
        'code': 200,
        'data': [{
            'article_id': a.id,
            'category_id': a.category_id,
            'category_name': a.category.category_name if a.category else '未分类',
            'title': a.title,
            'summary': a.summary,
            'icon': a.icon,
            'is_active': a.is_active,
            'view_count': a.view_count,
            'create_time': a.create_time.strftime('%Y-%m-%d %H:%M:%S')
        } for a in articles]
    })
