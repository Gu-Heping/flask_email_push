# Flask 推送服务 - 邮件模块

> 注：本文档由AI生成，部分内容可能不符合实际情况，有疑问可以直接来问我

---

> 基于 Flask + Celery + Redis 的多渠道推送平台（开发中）  
> 本人负责：**邮件推送模块**（Email Push Service）

---

## 项目概述

本项目旨在构建一个可扩展的消息推送平台，支持多种推送渠道：

- **邮件推送**（Email）✅ 已实现
- **更多渠道**（可扩展）

当前进度：**邮件推送模块已完成核心功能**，包括异步任务、签名校验、失败重试与简易 DLQ。

---

## 技术栈

| 组件 | 技术 | 说明 |
|------|------|------|
| **Web 框架** | Flask 3.x | 轻量级 WSGI 框架 |
| **任务队列** | Celery 5.x | 异步任务处理 |
| **消息代理** | Redis 7.x | Celery broker & result backend |
| **数据库** | SQLite（开发）| 通知记录存储（可迁移至 PostgreSQL） |
| **邮件服务** | Flask-Mailing | 异步邮件发送（支持 SMTP） |
| **API 风格** | RESTful | Flask-RESTful + 原生路由 |

---

## 项目结构

```
flask_test/
├── app/
│   ├── __init__.py           # Flask 应用工厂 + Celery 初始化
│   ├── config.py             # 统一配置（数据库、Celery、邮件、签名密钥）
│   ├── extensions.py         # 扩展实例（db, migrate, mail）
│   ├── email_service/        # 邮件推送模块 ✅
│   │   ├── __init__.py
│   │   ├── routes.py         # POST /api/v1/push/email
│   │   └── models.py
│   ├── notification/         # 通知管理模块（开发中）
│   │   ├── routes.py         # POST /api/v1/notifications
│   │   └── models.py
│   ├── tasks/                # Celery 任务
│   │   ├── email_tasks.py    # send_email 任务（带重试 & DLQ）
│   │   └── other_tasks.py
│   ├── main/                 # 主页蓝图
│   ├── yuque/                # 语雀集成（规划中）
│   └── test/                 # 测试模块
├── static/                   # 静态资源
├── templates/                # 模板文件
├── run.py                    # Flask 启动入口
├── celery_worker.py          # Celery Worker 启动入口
├── test_mail.py              # 邮件功能本地测试脚本
├── requirements.txt          # 依赖清单（待补充）
└── README.md                 # 本文档
```

---

## 核心功能：邮件推送模块

### 接口说明

**端点**: `POST /api/v1/push/email`

**请求头**:
```http
Content-Type: application/json
X-Timestamp: 1739820000               # 可选：Unix 时间戳（秒）
X-Signature: sha256=<hex>             # 可选：HMAC-SHA256 签名（配置后强制校验）
```

**请求体**:
```json
{
  "to": "user@example.com",           // 或 ["user1@x.com", "user2@x.com"]
  "subject": "邮件主题",
  "content": "邮件正文（纯文本）"
}
```

**响应**:
- `202 Accepted` - 成功入队
  ```json
  {
    "code": "ACCEPTED",
    "message": "邮件发送已入队",
    "task_id": "abc-123-def",
    "to": ["user@example.com"]
  }
  ```
- `400 Bad Request` - 参数错误
- `401 Unauthorized` - 签名校验失败

### 签名机制（可选启用）

**配置环境变量**:
```bash
PUSH_SIGNING_SECRET=your-secret-key       # 启用签名校验
PUSH_SIGNATURE_TOLERANCE=300              # 时间窗口（秒），默认 300
```

**签名算法**:
1. 构造签名串：`{timestamp}.{原始请求体字节}`
2. 计算 HMAC：`HMAC_SHA256(secret, 签名串)`
3. 发送头：`X-Signature: sha256=<十六进制摘要>`

**Python 示例**:
```python
import hmac, hashlib, time, json

secret = b'your-secret-key'
timestamp = str(int(time.time()))
body = json.dumps({"to":"user@x.com","subject":"测试","content":"内容"}).encode('utf-8')
base = f"{timestamp}.".encode('utf-8') + body
sig = hmac.new(secret, base, hashlib.sha256).hexdigest()

print(f"X-Timestamp: {timestamp}")
print(f"X-Signature: sha256={sig}")
```

### 失败重试与 DLQ

- **自动重试**: 最多 5 次，指数退避（1s, 2s, 4s, ...），最大延迟 60s
- **死信队列（DLQ）**: 达到最大重试后，任务详情写入日志（可扩展为 Redis List 或数据库）
- **DLQ 格式**:
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

## 快速开始

### 1. 环境准备

**系统要求**:
- Python 3.10（建议）
- Redis 6.0+（Windows 可用 Memurai 或 WSL 安装）

**安装依赖**:
```bash
pip install -r requirements.txt
```

### 2. 配置环境变量

在项目根目录创建 `.env` 文件：
```env
# 调试模式
DEBUG=True

# 邮件配置（126 邮箱示例，需替换为你的邮箱和授权码）
EMAIL_PASSWORD=your-email-auth-code

# 推送签名（可选）
PUSH_SIGNING_SECRET=your-secret-key
PUSH_SIGNATURE_TOLERANCE=300
```

### 3. 启动 Redis

**Windows（Memurai）**:
```bash
memurai.exe
```

**Linux/macOS**:
```bash
redis-server
```

### 4. 启动 Flask 应用

```bash
python run.py
```

访问: `http://localhost:5000`

### 5. 启动 Celery Worker

**Windows（必须用 solo 池）**:
```powershell
celery -A celery_worker.celery worker -P solo --loglevel=info
```

**Linux/macOS**:
```bash
celery -A celery_worker.celery worker --loglevel=info
```

---

## API 使用示例

### 示例 1: 发送邮件（无签名）

```bash
curl -X POST http://localhost:5000/api/v1/push/email \
  -H "Content-Type: application/json" \
  -d '{
    "to": "user@example.com",
    "subject": "系统通知",
    "content": "您有新的消息待查看"
  }'
```

**响应**:
```json
{
  "code": "ACCEPTED",
  "message": "邮件发送已入队",
  "task_id": "d7f8a123-...",
  "to": ["user@example.com"]
}
```

### 示例 2: 批量发送（带签名）

**生成签名**（Python）:
```python
import hmac, hashlib, time, json, requests

secret = b'your-secret-key'
timestamp = str(int(time.time()))
payload = {"to":["a@x.com","b@x.com"],"subject":"周报","content":"本周进展..."}
body = json.dumps(payload).encode('utf-8')
base = f"{timestamp}.".encode('utf-8') + body
sig = hmac.new(secret, base, hashlib.sha256).hexdigest()

resp = requests.post(
    'http://localhost:5000/api/v1/push/email',
    headers={
        'Content-Type': 'application/json',
        'X-Timestamp': timestamp,
        'X-Signature': f'sha256={sig}'
    },
    json=payload
)
print(resp.status_code, resp.json())
```

### 示例 3: 常见错误

**参数不全**:
```json
// 请求
{"to": "user@x.com", "subject": "标题"}

// 响应 400
{"code": "INVALID_PARAMS", "message": "必须提供 to/subject/content"}
```

**签名校验失败**（配置 PUSH_SIGNING_SECRET 后）:
```json
// 响应 401
{"code": "UNAUTHORIZED", "message": "签名校验失败"}
```

**请求过期**:
```json
// 响应 401
{"code": "UNAUTHORIZED", "message": "请求已过期"}
```

---

## 配置说明

### app/config.py 核心配置

```python
class Config:
    # 数据库
    SQLALCHEMY_DATABASE_URI = 'sqlite:///app/app.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # 邮件（126 邮箱）
    MAIL_SERVER = 'smtp.126.com'
    MAIL_PORT = 465
    MAIL_USE_SSL = True
    MAIL_USERNAME = 'peace0824@126.com'
    MAIL_PASSWORD = os.environ.get('EMAIL_PASSWORD')
    MAIL_DEFAULT_SENDER = 'peace0824@126.com'
    
    # Celery
    CELERY_BROKER_URL = 'redis://localhost:6379/0'
    CELERY_RESULT_BACKEND = 'redis://localhost:6379/0'
    CELERY_INCLUDE = [
        'app.tasks.email_tasks',
        'app.tasks.other_tasks'
    ]
    
    # 推送签名
    PUSH_SIGNING_SECRET = os.environ.get('PUSH_SIGNING_SECRET', '')
    PUSH_SIGNATURE_TOLERANCE = int(os.environ.get('PUSH_SIGNATURE_TOLERANCE', 300))
```

---

## 测试与验证

### 本地邮件测试脚本

项目根目录已提供 `test_mail.py`：
```bash
python test_mail.py
```

成功后会打印：
```
邮件已发送到: user@example.com
```

### 查看 Celery 任务日志

启动 Celery worker 后，控制台会显示任务执行情况：
```
[2025-10-18 10:30:00,123: INFO/MainProcess] Task app.tasks.email_tasks.send_email[abc-123] received
[2025-10-18 10:30:02,456: INFO/MainProcess] 邮件已发送到: user@example.com
[2025-10-18 10:30:02,789: INFO/MainProcess] Task app.tasks.email_tasks.send_email[abc-123] succeeded in 2.5s
```

### 失败重试验证

1. 故意配置错误的 SMTP 密码
2. 发送邮件请求
3. 观察 Celery 日志显示自动重试（1s, 2s, 4s, ...）
4. 达到最大重试后，控制台打印 DLQ 信息：
   ```
   [DLQ][email] {"subject":"测试","recipients":["user@x.com"],"body":"内容","error":"SMTPException..."}
   ```

---

## 可扩展功能（Roadmap）

### 短期（邮件模块增强）

- [ ] HTML 邮件支持（已预留 `html` 参数）
- [ ] 邮件模板系统（Jinja2 变量渲染）
- [ ] DLQ 管理接口：
  - `GET /api/v1/push/email/dlq` - 查询死信队列
  - `POST /api/v1/push/email/replay` - 重投失败任务
- [ ] 限频策略（同一收件人/主题合并发送）
- [ ] 监控面板（Flower / Prometheus）

### 中期（其他推送渠道）

- [ ] Webhook 推送：`POST /api/v1/push/webhook`
  - 支持 POST/GET/PUT 方法
  - 自定义 Headers 与 Body
  - 签名校验（X-Signature）
  - 重试与 DLQ
- [ ] RSS 订阅：`GET /api/v1/push/rss?tag=xxx`
  - 基于 feedgen 生成 RSS/Atom
  - 按标签/分类过滤

### 长期（平台化）

- [ ] 统一推送管理后台
- [ ] 多租户支持（API Key + 配额管理）
- [ ] Webhook 事件回调（推送成功/失败通知）
- [ ] 批量推送优化（分片、限流、合并）

---

## 部署建议

### 生产环境配置

1. **数据库**: 迁移至 PostgreSQL/MySQL
   ```python
   SQLALCHEMY_DATABASE_URI = 'postgresql://user:pass@localhost/dbname'
   ```

2. **Redis**: 使用持久化配置，开启 AOF
   ```bash
   appendonly yes
   appendfsync everysec
   ```

3. **Celery Worker**: 使用 prefork 池（Linux）或 gevent（Windows）
   ```bash
   celery -A celery_worker.celery worker --pool=prefork --concurrency=4 --loglevel=info
   ```

4. **反向代理**: Nginx + Gunicorn
   ```bash
   gunicorn -w 4 -b 127.0.0.1:8000 run:app
   ```

5. **监控**: Flower（Celery 监控）
   ```bash
   celery -A celery_worker.celery flower --port=5555
   ```

### Docker 部署（推荐）

```dockerfile
# Dockerfile（示例）
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:5000", "run:app"]
```

```yaml
# docker-compose.yml（示例）
version: '3.8'
services:
  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
  
  web:
    build: .
    ports:
      - "5000:5000"
    env_file: .env
    depends_on:
      - redis
  
  celery:
    build: .
    command: celery -A celery_worker.celery worker --loglevel=info
    env_file: .env
    depends_on:
      - redis
```

---

## 安全建议

1. **签名密钥管理**: 使用强随机字符串，定期轮换
   ```bash
   python -c "import secrets; print(secrets.token_urlsafe(32))"
   ```

2. **HTTPS 强制**: 生产环境必须使用 HTTPS，避免签名泄露

3. **速率限制**: 使用 Flask-Limiter 防止 API 滥用
   ```python
   from flask_limiter import Limiter
   limiter = Limiter(app, key_func=lambda: request.remote_addr)
   @limiter.limit("10 per minute")
   ```

4. **敏感数据脱敏**: 日志/DLQ 中避免记录完整邮箱地址与内容

---

## 常见问题

### Q1: Windows 上 Celery 启动失败？
**A**: Windows 必须使用 `solo` 或 `gevent` 池：
```powershell
celery -A celery_worker.celery worker -P solo --loglevel=info
```

### Q2: 邮件发送失败但无报错？
**A**: 检查：
1. 环境变量 `EMAIL_PASSWORD` 是否设置
2. 邮箱是否开启 SMTP 服务并获取授权码
3. Celery worker 是否正常运行
4. 查看 Celery 日志是否有异常

### Q3: 签名校验总是失败？
**A**: 排查：
1. 客户端与服务端 `PUSH_SIGNING_SECRET` 是否一致
2. 时间戳是否在 300 秒窗口内
3. 签名串构造是否正确（`{timestamp}.{原始body字节}`）
4. 是否使用了相同的哈希算法（HMAC-SHA256）

### Q4: 如何禁用签名校验？
**A**: 不设置 `PUSH_SIGNING_SECRET` 环境变量即可，接口会跳过签名验证。

---

## 贡献指南

本人负责邮件模块，欢迎提交 Issue 和 PR：

- **Bug 修复**: 邮件发送异常、重试逻辑问题等
- **功能增强**: HTML 邮件、模板系统、DLQ 管理等
- **文档完善**: API 示例、配置说明、部署指南等

---

## 许可证

MIT License

---

## 联系方式

- **项目负责**: 邮件推送模块
- **技术栈**: Flask + Celery + Redis + Flask-Mailing
- **当前状态**: ✅ 核心功能已完成，可扩展开发中

---

**更新日期**: 2025-10-18  
**文档版本**: v1.0.0
