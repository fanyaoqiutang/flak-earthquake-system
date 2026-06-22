地震信息管理系统 (Flask Earthquake System)
项目简介
本项目是基于 Flask + Vue3 开发的前后端分离地震预警科普管理平台，面向普通用户与后台管理员双角色，整合地震数据查询、多维度统计、科普文章自动爬取、用户订阅预警、AI 智能问答、留言反馈等完整业务功能。
核心功能
双角色权限管控：管理员、普通用户独立登录鉴权，接口访问权限隔离
地震数据管理：地震信息增删改查，支持省份、震级、时间段多条件筛选
科普文章模块：爬虫自动抓取地震局官方科普内容，自动分类、分页展示
用户订阅预警：用户自选省份订阅，对应区域地震自动生成站内预警消息
多维数据统计：分省份 / 城市 / 震级 / 时间统计，对接 ECharts 可视化图表
AI 科普问答：接入 DeepSeek 大模型，仅回复防震减灾相关专业问题
辅助功能：用户留言交流、问题反馈、后台内容审核
技术栈
后端
Web 框架：Flask 2.x
ORM：SQLAlchemy，数据库 SQLite
身份认证：Flask-Login + Session + Token 双重校验
爬虫工具：requests、BeautifulSoup4
跨域：Flask-CORS
第三方接口：DeepSeek 对话 API
前端
基础框架：Vue3 + Vite
UI 组件库：Element Plus
网络请求：Axios
路由：Vue Router4
可视化图表：ECharts 6.x
项目目录结构
plaintext
flak-earthquake-system/        # 后端根目录
├── app.py                     # 项目入口
├── models.py                  # 全系统数据库模型类
├── crawl_science_data.py      # 科普爬虫脚本
├── crawl_earthquake_catalog.py# 地震数据爬虫
├── routes/                    # 路由分层
│   ├── admin_routes.py        # 管理员接口
│   ├── user_routes.py         # 用户接口
│   ├── science_routes.py      # 科普接口
│   └── common_routes.py       # 公共查询接口
├── services/                  # 业务逻辑层
│   ├── admin_service.py
│   ├── user_service.py
│   └── science_service.py
├── .env                       # 环境变量配置（API密钥等）
├── README.md
├── API_DOCUMENTATION.md       # 接口文档
├── DATABASE_DESIGN.md         # 数据库设计文档
├── DEVELOPMENT_GUIDE.md       # 开发规范指南
└── CHANGELOG.md               # 更新日志

earthquake-frontend/           # Vue前端项目
├── src/
│   ├── API/                   # 接口统一封装
│   ├── views/                 # 页面视图
│   ├── components/            # 公共组件
│   └── router/                # 路由配置
└── package.json
快速部署启动
后端环境
安装依赖
bash
运行
pip install flask flask-sqlalchemy flask-login flask-cors python-dotenv requests beautifulsoup4
新建.env 文件，填入 DeepSeek 密钥
plaintext
DEEPSEEK_API_KEY=你的密钥
启动后端服务
bash
运行
python app.py
后端地址：http://localhost:5000
前端环境
bash
运行
cd earthquake-frontend
npm install
npm run dev
前端地址：http://localhost:5173
默认测试账号
管理员
账号：admin 密码：123456
普通用户
账号：testuser 密码：123456
爬虫使用
抓取地震局科普文章
bash
运行
python crawl_science_data.py
抓取公开地震目录数据
bash
运行
python crawl_earthquake_catalog.py