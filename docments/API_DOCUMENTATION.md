基础通用规范
基础地址：http://localhost:5000/api
数据格式：统一 JSON
认证方式：Session Cookie + Token 双重鉴权
通用返回格式
成功示例
json
{
    "code": 200,
    "msg": "操作成功",
    "data": {}
}
失败示例
json
{
    "code": 401,
    "msg": "未登录，无访问权限",
    "data": null
}
状态码说明
200：正常；400：参数错误；401：未登录；403：权限不足；500：服务异常
一、公共接口 common_routes
GET /api/common/earthquakes
功能：分页查询地震数据，支持多条件筛选
请求参数
表格
参数	类型	是否必填	说明
page	int	否	页码，默认 1
per_page	int	否	每页条数，默认 20
province_name	str	否	省份模糊检索
mag_min	float	否	最低震级筛选
time	str	否	时间范围：24h/7d/30d/1y
GET /api/common/provinces
功能：查询全部省份列表
GET /api/common/earthquake-statistics
功能：多维度地震统计（时间趋势、震级分布、省份排行）
二、普通用户接口 user_routes
POST /api/user/register
功能：用户注册
请求体
json
{
    "user_account":"testuser",
    "password":"123456"
}
POST /api/user/login
功能：用户登录，返回用户 token
GET /api/user/info
功能：获取当前登录用户信息（需登录）
PUT /api/user/update-info
功能：修改用户手机号等基础信息
PUT /api/user/password
功能：修改登录密码
POST /api/user/subscribe
功能：订阅指定省份
json
{"province_id": 31}
GET /api/user/subscribe-list
功能：查询本人订阅省份
GET /api/user/alerts
功能：查询个人地震预警消息
PUT /api/user/alert-read/{alert_id}
功能：单条预警标记已读
PUT /api/user/all-alert-read
功能：全部预警一键已读
POST /api/user/feedback
功能：提交用户反馈
三、管理员接口 admin_routes
POST /api/admin/login
功能：管理员登录，需专属管理密钥
GET /api/admin/user-list
功能：查询全部用户，支持关键词 / 状态筛选
PUT /api/admin/user-status/{user_id}
功能：启用 / 禁用用户账号
DELETE /api/admin/user/{user_id}
功能：删除用户，级联清除订阅、留言、预警数据
POST /api/admin/earthquake
功能：新增地震记录
PUT /api/admin/earthquake/{eq_id}
功能：编辑地震信息
DELETE /api/admin/earthquake/{eq_id}
功能：删除地震记录
GET /api/admin/chat-list
功能：查看全部聊天留言
DELETE /api/admin/chat/{msg_id}
功能：删除违规聊天内容
GET /api/admin/feedback-list
功能：查看用户反馈
PUT /api/admin/feedback/{fb_id}
功能：标记反馈已处理
GET /api/admin/dashboard
功能：后台仪表盘总统计数据
四、科普模块 science_routes
GET /api/science/category
功能：获取科普分类列表
GET /api/science/article-list
功能：分页科普文章，支持分类、关键词筛选
GET /api/science/article/{art_id}
功能：单篇科普详情
五、AI 问答接口
POST /api/ai/chat
功能：地震科普 AI 对话
请求体
json
{
    "model":"deepseek-chat",
    "messages":[{"role":"user","content":"地震如何自救"}]
}