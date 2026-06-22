数据库设计文档
数据库：SQLite，ORM 框架 SQLAlchemy
全部数据表结构
1. user 用户表
表格
字段名	数据类型	约束	说明
user_id	int	主键自增	用户唯一 ID
user_account	varchar	唯一、非空	登录账号
password	varchar	非空	加密哈希密码
phone	varchar	可空	绑定手机号
status	varchar	默认正常	账号状态：正常 / 禁用 / 已注销
last_active_time	datetime	可空	最后活跃时间
alert_frequency	varchar	默认实时预警	预警推送频率
alert_methods	json	数组	通知方式
2. Admin 管理员表
表格
字段	约束	说明
admin_id	主键	管理员 ID
admin_account	唯一	后台账号
password	哈希存储	加密密码
admin_key	密钥	后台注册校验密钥
3. province 省份表
province_id (主键)、province_name、region（七大区域）
4. city 城市表
city_id (主键)、province_id (外键)、city_name
5. earthquake_info 地震信息表
earthquake_id、city_id (外键)、earthquake_time、latitude、longitude、depth、magnitude、earthquake_message
6. science_category 科普分类表
category_id、category_name、category_icon、sort_order
7. earthquake_popular 科普文章表
id、category_id (外键)、title、summary、content、source、is_active、create_time
8. user_subscribe_province 用户订阅表
id、user_id、province_id、subscribe_time
9. user_earthquake_alert 用户预警表
id、user_id、earthquake_id、is_read、create_time
10. user_feedback 用户反馈表
id、user_id、feedback_type、content、priority、status、submit_time、handle_time
11. chat_message 聊天留言表
id、user_id、content、create_time、status
12. admin_operation_log 管理员操作日志
log_id、admin_id、operation、target_earthquake_id、create_time
外键关联说明
1、city.province_id → province.province_id
2、earthquake_info.city_id → city.city_id
3、user_subscribe_province.user_id → user.user_id
4、user_earthquake_alert.user_id → user.user_id
5、earthquake_popular.category_id → science_category.category
6、d所有删除操作支持级联清理关联数据