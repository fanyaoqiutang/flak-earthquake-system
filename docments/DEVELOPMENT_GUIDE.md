开发指南
一、整体分层架构（MVC）
1、Model 层：models.py，所有数据表实体定义
2、Route 路由层：routes 文件夹，按模块拆分蓝图，统一 url 前缀
3、Service 业务层：services 文件夹，复杂逻辑抽离，路由只做参数接收与返回
4、视图层：Vue 前端页面，Flask 仅提供接口，无服务端模板页面
后端代码规范
1、全部路由使用 Blueprint 蓝图模块化拆分
python
运行
from flask import Blueprint
user_bp = Blueprint("user", __name__, url_prefix="/api/user")
2、复杂业务统一写入 service，路由只做参数校验
3、数据库统一使用 SQLAlchemy ORM，禁止原生 SQL 拼接（防注入）
4、所有入参增加类型捕获，非法参数返回 400 提示
5、密码统一使用 werkzeug 哈希加密，明文不入库
前端代码规范
1、页面组件大驼峰命名 AiChat.vue
2、所有接口统一封装至 src/API 文件夹，页面不直接写 axios 请求
3、路由集中在 router/index.js 统一管理
4、分页、弹窗等公共功能抽离通用组件
二、权限鉴权机制
1、普通用户：Flask-Login 全局 current_user + session 缓存
2、管理员：独立 session 标记 is_admin + 64 位 token 双重校验
3、所有后台接口第一行调用 verify_admin () 拦截无权限访问
4、数据隔离：普通用户仅能查询、修改自身订阅、预警；管理员全局操作
三、爬虫开发规范
1、请求增加 headers 模拟浏览器，请求间隔 2 秒防封禁
2、多选择器匹配网页正文，自动过滤导航、脚本、广告标签
3、入库前标题查重，避免重复文章
4、根据标题关键词自动划分科普分类，不存在则自动新建分类
四、数据库更新流程
1、修改 models 内字段 / 表结构
2、开发环境直接删除 sqlite 数据库文件
3、重启 app.py，程序自动 create_all () 生成新表
4、正式环境使用数据库迁移工具
五、异常处理规范
1、数据库操作增加 try-except，出错执行 rollback 回滚
2、网络请求（爬虫 / AI 接口）区分超时、连接、解析三类异常
3、关键业务代码添加打印日志，方便调试排查
六、部署生产环境
1、更换生产数据库 MySQL/PostgreSQL
2、配置独立 SECRET_KEY，关闭 Flask 调试模式
3、使用 gunicorn WSGI 服务启动后端
4、前端执行 npm run build 打包 dist，部署 Nginx