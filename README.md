# Flask 异步推送服务平台

[![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)](https://www.python.org/)
[![Flask](https://img.shields.io/badge/Flask-3.1.2-green.svg)](https://flask.palletsprojects.com/)
[![Celery](https://img.shields.io/badge/Celery-5.5.3-success.svg)](https://docs.celeryproject.org/)
[![Redis](https://img.shields.io/badge/Redis-7.x-red.svg)](https://redis.io/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

> 注：该项目文档由ai生成，如有问题可以直接来找我，另外现在该项目正运行在http://172.17.158.90:8000上，可以直接调用相关接口进行测试。

---

## 📖 项目简介

一个可扩展的异步消息推送服务平台，支持多渠道推送、任务队列、失败重试和死信队列（DLQ）等企业级特性。

### ✨ 核心特性

- ✅ **邮件推送** - 基于 SMTP 的异步邮件发送服务
- 🔐 **签名验证** - HMAC-SHA256 签名 + 时间戳防重放攻击
- ⚡ **异步任务** - Celery 分布式任务队列
- 🔄 **智能重试** - 指数退避 + 抖动机制，最多重试 5 次
- 💀 **死信队列** - 失败任务自动进入 DLQ，便于后续处理
- 📊 **通知记录** - SQLAlchemy ORM 持久化存储
- 🔌 **可扩展** - 模块化设计，支持快速添加新的推送渠道

### 🎯 应用场景

- 用户注册/登录通知
- 订单状态变更提醒
- 系统告警与监控
- 营销活动推送
- Webhook 事件转发

---

## 🏗️ 技术栈

| 组件 | 技术 | 版本 | 说明 |
|------|------|------|------|
| **Web 框架** | Flask | 3.1.2 | 轻量级 WSGI 框架 |
| **任务队列** | Celery | 5.5.3 | 分布式异步任务处理 |
| **消息代理** | Redis | 3.5.3 | Celery broker & result backend |
| **数据库** | SQLite / PostgreSQL | - | 通知记录存储（开发环境使用 SQLite） |
| **ORM** | SQLAlchemy | 2.0.44 | 数据库 ORM |
| **邮件服务** | Flask-Mailing | 0.2.3 | 异步邮件发送（支持 SMTP） |
| **数据库迁移** | Flask-Migrate | 4.1.0 | Alembic 数据库迁移工具 |
| **API 框架** | Flask-RESTful | 0.3.10 | RESTful API 支持 |

---

## 📁 项目结构

```
flask_test/
├── app/
│   ├── __init__.py              # Flask 应用工厂 + Celery 初始化
│   ├── config.py                # 统一配置（数据库、Celery、邮件、签名密钥）
│   ├── extensions.py            # Flask 扩展实例（db, migrate, mail）
│   │
│   ├── email_service/           # 📧 邮件推送模块（核心功能）
│   │   ├── __init__.py          # 蓝图注册
│   │   ├── routes.py            # API 路由（POST /api/v1/push/email）
│   │   └── models.py            # 数据模型（EmailNotification）
│   │
│   ├── notification/            # 🔔 通知管理模块
│   │   ├── __init__.py
│   │   ├── routes.py            # 通知查询接口
│   │   └── models.py            # 通知数据模型
│   │
│   ├── tasks/                   # ⚙️ Celery 异步任务
│   │   ├── __init__.py
│   │   ├── email_tasks.py       # 邮件发送任务（带重试 & DLQ）
│   │   └── other_tasks.py       # 其他异步任务
│   │
│   ├── main/                    # 🏠 主页蓝图
│   ├── yuque/                   # 📝 语雀集成（规划中）
│   └── test/                    # 🧪 测试模块
│
├── static/                      # 静态资源（CSS/JS）
├── templates/                   # Jinja2 模板
├── run.py                       # Flask 应用启动入口
├── celery_worker.py             # Celery Worker 启动脚本
├── test_mail.py                 # 邮件功能本地测试
├── requirements.txt             # Python 依赖清单
└── README.md                    # 项目文档
```

---

## 🚀 快速开始

### 环境要求

- Python 3.11+
- Redis 7.x
- SMTP 邮件服务（如 126 邮箱、QQ 邮箱等）

### 1. 克隆项目

```bash
git clone https://github.com/Gu-Heping/flask_test.git
cd flask_test
```

### 2. 创建虚拟环境并安装依赖

**Windows (PowerShell):**
```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

**Linux/macOS:**
```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 3. 配置环境变量

创建 `.env` 文件：

```env
# 应用配置
DEBUG=True

# 邮件配置
EMAIL_PASSWORD=your_smtp_auth_code

# 签名密钥（可选，留空则不启用签名验证）
PUSH_SIGNING_SECRET=your_secret_key_here

# 签名时间窗口（秒）
PUSH_SIGNATURE_TOLERANCE=300
```

### 4. 启动 Redis

**Windows:**
```powershell
redis-server
```

**Linux/macOS:**
```bash
redis-server
```

### 5. 初始化数据库

```bash
python run.py
```

首次运行会自动创建数据库表（`app.db`）。

### 6. 启动 Celery Worker

打开新终端窗口：

**Windows:**
```powershell
.\venv\Scripts\Activate.ps1
celery -A celery_worker.celery worker --loglevel=info --pool=solo
```

**Linux/macOS:**
```bash
source venv/bin/activate
celery -A celery_worker.celery worker --loglevel=info
```

### 7. 启动 Flask 应用

**开发环境（Windows）:**
```powershell
python run.py
```

然后使用 Waitress 运行（推荐用于 Windows 生产环境）：
```powershell
pip install waitress
waitress-serve --host=0.0.0.0 --port=5000 run:app
```

**生产环境（Linux/macOS）:**
```bash
# 使用 Gunicorn（仅支持 Unix 系统）
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 run:app
```

---

## 📡 API 文档

### 1. 发送邮件

**接口**: `POST /api/v1/push/email`

**请求头**:
```http
Content-Type: application/json
X-Timestamp: 1739820000               # 可选：Unix 时间戳（秒），启用签名时必填
X-Signature: sha256=<hex_digest>      # 可选：HMAC-SHA256 签名，启用签名时必填
```

**请求体**:
```json
{
  "to": "user@example.com",           // 单个收件人（字符串）
  "subject": "测试邮件",
  "content": "这是一封测试邮件"
}
```

或批量发送：
```json
{
  "to": ["user1@example.com", "user2@example.com"],  // 多个收件人（数组）
  "subject": "批量通知",
  "content": "重要系统更新通知"
}
```

**成功响应** (`202 Accepted`):
```json
{
  "code": "ACCEPTED",
  "message": "邮件发送已入队",
  "task_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
  "to": ["user@example.com"]
}
```

**错误响应**:

- `400 Bad Request` - 参数错误
  ```json
  {
    "code": "INVALID_PARAMS",
    "message": "必须提供 to/subject/content"
  }
  ```
- `401 Unauthorized` - 签名校验失败（启用签名时）
  ```json
  {
    "code": "UNAUTHORIZED",
    "message": "签名校验失败"
  }
  ```

### 2. 查询邮件通知记录

**接口**: `GET /api/v1/get/email`

**成功响应** (`200 OK`):
```json
[
  {
    "id": 1,
    "subject": "测试邮件",
    "to": "[\"user@example.com\"]",
    "content": "这是一封测试邮件",
    "pushed_at": "2025-10-23T10:30:00Z",
    "status": "sent"
  }
]
```

---

## 🔐 签名机制

### 配置环境变量

```bash
PUSH_SIGNING_SECRET=your-secret-key       # 启用签名校验
PUSH_SIGNATURE_TOLERANCE=300              # 时间窗口（秒），默认 300
```

### 签名算法

1. 构造签名串：`{timestamp}.{原始请求体字节}`
2. 计算 HMAC：`HMAC_SHA256(secret, 签名串)`
3. 发送头：`X-Signature: sha256=<十六进制摘要>`

### Python 示例

```python
import hmac
import hashlib
import time
import json

secret = b'your-secret-key'
timestamp = str(int(time.time()))
body = json.dumps({"to":"user@x.com","subject":"测试","content":"内容"}).encode('utf-8')
base = f"{timestamp}.".encode('utf-8') + body
sig = hmac.new(secret, base, hashlib.sha256).hexdigest()

print(f"X-Timestamp: {timestamp}")
print(f"X-Signature: sha256={sig}")
```

---

## 🧪 测试

### 本地邮件测试

```bash
python test_mail.py
```

此脚本会测试邮件配置是否正确，直接发送一封测试邮件。

### API 测试示例

#### 示例 1: 发送单个邮件（无签名）

```bash
curl -X POST http://localhost:5000/api/v1/push/email \
  -H "Content-Type: application/json" \
  -d '{
    "to": "user@example.com",
    "subject": "系统通知",
    "content": "您有新的消息待查看"
  }'
```

#### 示例 2: 批量发送（带签名）

```python
import hmac
import hashlib
import time
import json
import requests

# 配置
SECRET = b'your-secret-key'
API_URL = 'http://localhost:5000/api/v1/push/email'

# 构造请求体
payload = {
    "to": ["user1@example.com", "user2@example.com"],
    "subject": "批量通知",
    "content": "重要系统更新"
}
body = json.dumps(payload).encode('utf-8')
timestamp = str(int(time.time()))

# 生成签名
base = f"{timestamp}.".encode('utf-8') + body
signature = hmac.new(SECRET, base, hashlib.sha256).hexdigest()

# 发送请求
headers = {
    'Content-Type': 'application/json',
    'X-Timestamp': timestamp,
    'X-Signature': f'sha256={signature}'
}
response = requests.post(API_URL, data=body, headers=headers)
print(response.json())
```

---

## 🔄 失败重试与 DLQ

### 自动重试机制

- **最多重试**: 5 次
- **退避策略**: 指数退避（1s, 2s, 4s, 8s, 16s...）
- **最大延迟**: 60 秒
- **抖动**: 启用，避免惊群效应

### 死信队列（DLQ）

达到最大重试后，任务详情写入日志（可扩展为 Redis List 或数据库）：

```json
{
  "subject": "邮件主题",
  "recipients": ["user@x.com"],
  "body": "正文（截断至 2000 字）",
  "error": "SMTPException: ...",
  "trace": "Traceback..."
}
```

---

## 🚀 生产部署

### 1. 使用数据库迁移

初始化迁移：
```bash
flask db init
flask db migrate -m "Initial migration"
flask db upgrade
```

后续变更：
```bash
flask db migrate -m "描述本次变更"
flask db upgrade
```

### 2. 部署架构

**推荐架构**:
```
[Nginx] → [Gunicorn/Waitress] → [Flask App]
           ↓
        [Redis] ← [Celery Worker × N]
           ↓
        [PostgreSQL/MySQL]
```

**Windows 环境**:
- WSGI 服务器: Waitress
- Celery Worker: 使用 `--pool=solo`

**Linux/macOS 环境**:
- WSGI 服务器: Gunicorn
- Celery Worker: 默认 prefork 模式

### 3. 进程管理

**使用 Supervisor（Linux）**:

```ini
[program:flask_app]
command=/path/to/venv/bin/gunicorn -w 4 -b 127.0.0.1:5000 run:app
directory=/path/to/flask_test
user=www-data
autostart=true
autorestart=true
stderr_logfile=/var/log/flask_app.err.log
stdout_logfile=/var/log/flask_app.out.log

[program:celery_worker]
command=/path/to/venv/bin/celery -A celery_worker.celery worker --loglevel=info
directory=/path/to/flask_test
user=www-data
autostart=true
autorestart=true
stderr_logfile=/var/log/celery_worker.err.log
stdout_logfile=/var/log/celery_worker.out.log
```

### 4. Nginx 配置示例

```nginx
server {
    listen 80;
    server_name yourdomain.com;

    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

---

## 📊 监控与可观测性

### Celery 监控

**Flower（Celery Web 监控工具）**:
```bash
pip install flower
celery -A celery_worker.celery flower --port=5555
```

访问: `http://localhost:5555`

### 日志管理

**推荐工具**:
- **ELK Stack** (Elasticsearch + Logstash + Kibana)
- **Grafana + Loki**
- **Sentry** (错误追踪)

---

## 🛠️ 常见问题

### Q1: Windows 启动 Celery 报错？

**A**: Windows 不支持默认的 prefork 模式，使用：
```powershell
celery -A celery_worker.celery worker --pool=solo --loglevel=info
```

### Q2: 邮件发送失败？

**A**: 检查以下配置：
1. SMTP 服务器地址和端口
2. 邮箱授权码（不是登录密码）
3. 防火墙是否阻止 SMTP 端口（465/587）
4. Redis 是否正常运行

### Q3: 如何切换到 PostgreSQL？

**A**: 修改 `app/config.py`：
```python
SQLALCHEMY_DATABASE_URI = 'postgresql://user:password@localhost/dbname'
```

安装驱动：
```bash
pip install psycopg2-binary
```

### Q4: 如何禁用签名验证？

**A**: 删除或留空 `.env` 文件中的 `PUSH_SIGNING_SECRET`。

---

## 🔐 安全最佳实践

1. **签名验证**: 生产环境务必启用 `PUSH_SIGNING_SECRET`
2. **环境变量**: 敏感信息（邮箱密码、签名密钥）使用 `.env` 文件管理，不要提交到版本控制
3. **HTTPS**: 生产环境使用 HTTPS + Nginx 反向代理
4. **速率限制**: 使用 Flask-Limiter 添加接口限流
5. **日志审计**: 记录所有 API 调用和失败任务

---

## 🗺️ Roadmap

- [x] 邮件推送功能
- [x] 异步任务队列
- [x] 签名验证机制
- [x] 失败重试 & DLQ
- [ ] 短信推送模块
- [ ] 微信/钉钉通知
- [ ] 推送模板系统
- [ ] 用户权限管理
- [ ] Web 管理后台
- [ ] Docker 容器化
- [ ] 性能监控仪表盘

---

## 📄 许可证

本项目基于 [MIT License](LICENSE) 开源。

---

## 🤝 贡献指南

欢迎提交 Issue 和 Pull Request！

1. Fork 本仓库
2. 创建特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 打开 Pull Request

---

## 👨‍💻 作者

**Gu-Heping**

- GitHub: [@Gu-Heping](https://github.com/Gu-Heping)
- 项目链接: [flask_test](https://github.com/Gu-Heping/flask_test)

---

## 🙏 致谢

感谢以下开源项目：

- [Flask](https://flask.palletsprojects.com/) - Web 框架
- [Celery](https://docs.celeryproject.org/) - 分布式任务队列
- [Redis](https://redis.io/) - 高性能内存数据库
- [Flask-Mailing](https://github.com/waynerv/flask-mailing) - 异步邮件发送

---

<div align="center">
  
**⭐ 如果这个项目对你有帮助，请给个 Star！**

</div>
