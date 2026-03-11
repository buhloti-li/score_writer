# 自动化打谱服务平台 — 架构设计文档

---

## 1. 开发平台与运行环境

### 1.1 开发环境

| 维度 | 选型 | 说明 |
|------|------|------|
| **操作系统** | Linux (Ubuntu 22.04 LTS) | 服务器统一使用 Ubuntu |
| **容器化** | Docker + Docker Compose | 开发/测试/生产环境一致 |
| **版本控制** | Git + GitHub | 代码托管与 CI/CD |
| **CI/CD** | GitHub Actions | 自动测试、构建、部署 |
| **包管理（Python）** | uv / Poetry | 依赖锁定与虚拟环境 |
| **包管理（Node）** | pnpm | 快速、节省磁盘 |
| **代码规范** | Ruff (Python) + ESLint + Prettier (TS) | 统一代码风格 |

### 1.2 生产部署环境

```
初期（Phase 1-2）：单机部署
├── 阿里云 ECS 2-4 台
│   ├── 应用服务器：4C8G（API + Web + 管理后台）
│   ├── GPU 服务器：GPU 实例（OMR 推理）— 可按需启停
│   └── 数据服务器：4C16G（PostgreSQL + Redis + Meilisearch）
├── 阿里云 OSS：文件存储
├── 阿里云 CDN：静态资源加速
└── 域名 + SSL（Let's Encrypt）

规模化（Phase 3+）：容器编排
├── Kubernetes (ACK) 或 Docker Swarm
├── GPU 节点池：按需扩缩容
├── 负载均衡：SLB
└── 日志/监控：Grafana + Loki + Prometheus
```

---

## 2. 开发语言与技术栈

### 2.1 语言选型

```
┌─────────────────────────────────────────────────────┐
│                    技术栈全景                          │
├──────────────┬──────────────────────────────────────┤
│              │                                      │
│   Python     │  后端 API、OMR 引擎、任务队列、        │
│   3.11+      │  数据处理、网络抓取、LLM 集成          │
│              │                                      │
├──────────────┼──────────────────────────────────────┤
│              │                                      │
│  TypeScript  │  乐谱网前端（Next.js）、               │
│   5.x+       │  管理后台前端（React）                 │
│              │                                      │
├──────────────┼──────────────────────────────────────┤
│              │                                      │
│   SQL        │  数据库 Schema、迁移脚本               │
│              │  (PostgreSQL 16)                      │
│              │                                      │
├──────────────┼──────────────────────────────────────┤
│              │                                      │
│  LilyPond    │  乐谱排版 DSL（领域特定语言）           │
│              │  由 music21 自动生成                   │
│              │                                      │
└──────────────┴──────────────────────────────────────┘
```

### 2.2 后端技术栈（Python）

| 组件 | 技术 | 版本 | 用途 |
|------|------|------|------|
| **Web 框架** | FastAPI | 0.110+ | 高性能异步 API |
| **ASGI 服务器** | Uvicorn | 0.29+ | 生产部署 |
| **ORM** | SQLAlchemy | 2.0+ | 数据库访问 |
| **数据迁移** | Alembic | 1.13+ | Schema 版本管理 |
| **数据校验** | Pydantic | 2.0+ | 请求/响应模型 |
| **任务队列** | Celery | 5.3+ | 异步任务处理 |
| **定时调度** | Celery Beat | — | 主动抓取调度 |
| **OMR 引擎** | HOMR | 0.6+ | 乐谱光学识别 |
| **音乐处理** | music21 | 9.x | 格式转换与校验 |
| **LLM** | anthropic (SDK) | 0.40+ | Claude API 后处理 |
| **图片处理** | OpenCV + Pillow | — | 预处理与水印 |
| **PDF 水印** | ReportLab + PyPDF2 | — | PDF 叠加水印 |
| **网络抓取** | Playwright + BS4 | — | 乐谱抓取 |
| **搜索客户端** | meilisearch-python | — | 搜索引擎交互 |
| **OSS** | oss2 | — | 阿里云文件存储 |
| **认证** | python-jose + passlib | — | JWT + 密码哈希 |
| **测试** | pytest + httpx | — | 单元测试与集成测试 |

### 2.3 前端技术栈（TypeScript）

| 组件 | 技术 | 用途 |
|------|------|------|
| **乐谱网** | Next.js 14+ (App Router) | SSR/SSG，SEO 友好 |
| **管理后台** | React 18+ + Ant Design 5 | 成熟后台 UI 框架 |
| **乐谱编辑器** | Flat.io Embed (MVP) → Smoosic (长期) | 乐谱 WYSIWYG 编辑 |
| **乐谱渲染（只读）** | OSMD (OpenSheetMusicDisplay) | 用户端乐谱预览 |
| **图片查看** | OpenSeadragon | 高分辨率原图查看 |
| **状态管理** | Zustand | 轻量状态管理 |
| **请求** | TanStack Query (React Query) | 数据获取与缓存 |
| **表单** | React Hook Form + Zod | 表单校验 |
| **样式** | Tailwind CSS (乐谱网) + Ant Design (管理后台) | UI 样式 |
| **支付** | 支付宝/微信支付 SDK | 在线支付 |
| **测试** | Vitest + Playwright | 单元测试 + E2E |

### 2.4 基础设施

| 组件 | 技术 | 用途 |
|------|------|------|
| **数据库** | PostgreSQL 16 | 业务数据存储 |
| **缓存/消息** | Redis 7 | 缓存 + Celery Broker |
| **搜索引擎** | Meilisearch | 全文检索（中文友好） |
| **排版引擎** | LilyPond 2.24 | 出版级乐谱渲染 |
| **文件存储** | 阿里云 OSS | 乐谱文件存储 |
| **反向代理** | Nginx | 请求路由与静态资源 |
| **SSL** | Let's Encrypt (Certbot) | HTTPS 证书 |
| **容器** | Docker + Docker Compose | 环境标准化 |

---

## 3. 系统架构设计

### 3.1 整体架构（C4 — Context 层）

```
                    ┌─────────┐     ┌─────────┐
                    │  买家    │     │  用户    │
                    │ (淘宝)  │     │(乐谱网) │
                    └────┬────┘     └────┬────┘
                         │               │
                    ┌────┴────┐     ┌────┴────┐
                    │ 淘宝平台 │     │ 乐谱网   │
                    │ (TOP API)│     │ (Next.js)│
                    └────┬────┘     └────┬────┘
                         │               │
                         └──────┬────────┘
                                │
                    ┌───────────┴───────────┐
                    │                       │
                    │   打谱服务平台          │
                    │   (FastAPI 后端)       │
                    │                       │
                    └───────────┬───────────┘
                                │
              ┌────────┬────────┼────────┬────────┐
              │        │        │        │        │
         ┌────┴──┐ ┌──┴───┐ ┌──┴──┐ ┌──┴───┐ ┌──┴──┐
         │  IMSLP │ │Claude│ │支付宝│ │微信  │ │ OSS │
         │ (抓取) │ │ API  │ │     │ │支付  │ │     │
         └───────┘ └──────┘ └─────┘ └─────┘ └─────┘

                    ┌─────────┐
                    │  管理员  │
                    └────┬────┘
                         │
                    ┌────┴────┐
                    │ 管理后台 │
                    │ (React) │
                    └─────────┘
```

### 3.2 应用架构（C4 — Container 层）

```
┌─────────────────────────────────────────────────────────────────────┐
│                           Nginx (反向代理)                           │
│   ┌─────────────────┬──────────────────┬──────────────────────────┐ │
│   │ score.example.com│ admin.example.com│ api.example.com          │ │
│   └────────┬────────┴────────┬─────────┴──────────┬──────────────┘ │
└────────────┼────────────────┼─────────────────────┼────────────────┘
             │                │                     │
             ▼                ▼                     ▼
┌────────────────┐ ┌────────────────┐  ┌──────────────────────────────┐
│                │ │                │  │                              │
│  乐谱网 前端   │ │  管理后台 前端  │  │      FastAPI 后端             │
│  (Next.js)    │ │  (React SPA)   │  │                              │
│                │ │                │  │  ┌────────────────────────┐  │
│  - SSR/SSG    │ │  - Ant Design  │  │  │     API Router         │  │
│  - SEO 优化   │ │  - Flat.io 编辑│  │  │                        │  │
│  - 支付集成   │ │  - 任务管理    │  │  │  /api/v1/scores        │  │
│                │ │                │  │  │  /api/v1/orders        │  │
│  Port: 3000   │ │  Port: 3001    │  │  │  /api/v1/tasks         │  │
│                │ │                │  │  │  /api/v1/users         │  │
└────────────────┘ └────────────────┘  │  │  /api/v1/search        │  │
                                       │  │  /api/v1/admin         │  │
                                       │  └────────────────────────┘  │
                                       │                              │
                                       │  Port: 8000                  │
                                       └──────────┬───────────────────┘
                                                  │
                    ┌─────────────────────────────┼─────────────────────┐
                    │                             │                     │
                    ▼                             ▼                     ▼
          ┌──────────────┐             ┌──────────────┐     ┌──────────────┐
          │              │             │              │     │              │
          │  Celery      │             │  Celery      │     │  Meilisearch │
          │  Worker      │             │  Beat        │     │              │
          │              │             │  (定时调度)   │     │  - 乐谱索引  │
          │  - OMR 任务  │             │              │     │  - 中文分词  │
          │  - 渲染任务  │             │  - 主动抓取   │     │  - 同义词   │
          │  - 抓取任务  │             │  - 队列检查   │     │              │
          │  - 通知任务  │             │  - 定时统计   │     │  Port: 7700  │
          │              │             │              │     │              │
          └──────┬───────┘             └──────────────┘     └──────────────┘
                 │
     ┌───────────┼───────────┐
     ▼           ▼           ▼
┌─────────┐ ┌─────────┐ ┌─────────┐
│         │ │         │ │         │
│ HOMR    │ │LilyPond │ │ Claude  │
│ (OMR)   │ │ (渲染)  │ │  API    │
│         │ │         │ │ (LLM)   │
└─────────┘ └─────────┘ └─────────┘
```

### 3.3 数据架构

```
┌──────────────────────────────────────────────────────────────┐
│                                                              │
│                     PostgreSQL 16                             │
│                                                              │
│  ┌────────────────────────────────────────────────────────┐  │
│  │  核心业务表                                              │  │
│  │                                                        │  │
│  │  users          ── 用户（买家 + 管理员）                  │  │
│  │  composers      ── 作曲家（版权状态数据库）               │  │
│  │  scores         ── 乐谱库                               │  │
│  │  orders         ── 订单                                 │  │
│  │  tasks          ── 打谱/入库任务                         │  │
│  │  taobao_products── 淘宝商品映射                          │  │
│  │  crawl_results  ── 抓取结果缓存                          │  │
│  │  search_logs    ── 搜索日志（零结果记录）                 │  │
│  └────────────────────────────────────────────────────────┘  │
│                                                              │
└──────────────────────────────────────────────────────────────┘

┌──────────────┐    ┌──────────────┐    ┌──────────────────────┐
│              │    │              │    │                      │
│  Redis 7     │    │ Meilisearch  │    │  阿里云 OSS          │
│              │    │              │    │                      │
│  - 会话缓存  │    │  - scores    │    │  /scores/            │
│  - API 限流  │    │    索引      │    │    ├── {id}/          │
│  - Celery    │    │              │    │    │   ├── source.ly  │
│    Broker    │    │  - composers │    │    │   ├── output.pdf │
│  - 任务结果  │    │    索引      │    │    │   ├── preview.pdf│
│              │    │              │    │    │   ├── thumb.png  │
│              │    │              │    │    │   ├── score.xml  │
│              │    │              │    │    │   └── score.mid  │
│              │    │              │    │  /uploads/            │
│              │    │              │    │    └── {task_id}/     │
│              │    │              │    │        └── originals/ │
└──────────────┘    └──────────────┘    └──────────────────────┘
```

### 3.4 核心数据流

#### 3.4.1 已有乐谱购买流程

```
用户(浏览器)          Next.js(SSR)         FastAPI           PostgreSQL    OSS
    │                    │                   │                  │           │
    │  GET /scores/xxx   │                   │                  │           │
    │ ──────────────→   │  GET /api/scores/x │                  │           │
    │                    │ ──────────────→   │  SELECT score    │           │
    │                    │                   │ ──────────────→ │           │
    │                    │                   │ ← score data    │           │
    │                    │ ← score JSON      │                  │           │
    │ ← 渲染页面(预览)   │                   │                  │           │
    │                    │                   │                  │           │
    │  POST /orders      │                   │                  │           │
    │ ──────────────→   │                   │                  │           │
    │                    │ POST /api/orders   │                  │           │
    │                    │ ──────────────→   │ INSERT order     │           │
    │                    │                   │ ──────────────→ │           │
    │                    │ ← order + 支付URL │                  │           │
    │ ← 跳转支付         │                   │                  │           │
    │                    │                   │                  │           │
    │  (支付回调)        │                   │                  │           │
    │                    │                   │ UPDATE order     │           │
    │                    │                   │  status=paid     │           │
    │                    │                   │ ──────────────→ │           │
    │                    │                   │                  │  签名URL  │
    │                    │                   │ ────────────────────────→  │
    │                    │                   │ ← 临时下载链接   │           │
    │ ← 下载 PDF         │                   │                  │           │
```

#### 3.4.2 AI 打谱管线

```
┌──────────────────────────────────────────────────────────────────┐
│                    Celery Worker — 打谱管线                       │
│                                                                  │
│  ┌──────────┐    ┌──────────┐    ┌──────────┐    ┌──────────┐  │
│  │  Step 1   │    │  Step 2   │    │  Step 3   │    │  Step 4   │ │
│  │  图片预处理│ →  │  HOMR     │ →  │  LLM     │ →  │ music21  │  │
│  │           │    │  OMR      │    │  后处理   │    │  转换    │  │
│  │  OpenCV:  │    │           │    │           │    │          │  │
│  │  - 灰度化 │    │  输入:图片│    │  Claude:  │    │  MusicXML│  │
│  │  - 二值化 │    │  输出:    │    │  - 拍子   │    │     ↓    │  │
│  │  - 去噪   │    │  MusicXML │    │    校验   │    │ LilyPond │  │
│  │  - 校正   │    │           │    │  - 调号   │    │   (.ly)  │  │
│  │           │    │           │    │    修正   │    │          │  │
│  └──────────┘    └──────────┘    │  - 节奏   │    └────┬─────┘  │
│                                  │    修复   │         │        │
│                                  └──────────┘         │        │
│                                                       ▼        │
│  ┌──────────┐    ┌──────────┐    ┌──────────────────────────┐  │
│  │  Step 7   │    │  Step 6   │    │  Step 5                  │ │
│  │  创建审核 │ ←  │  水印处理 │ ←  │  LilyPond 渲染           │  │
│  │  任务     │    │           │    │                          │  │
│  │           │    │  ReportLab│    │  lilypond --pdf --png    │  │
│  │  通知管理 │    │  + PyPDF2 │    │  -dresolution=300        │  │
│  │  员审核   │    │           │    │  → PDF + PNG             │  │
│  │           │    │  → 预览PDF│    │                          │  │
│  └──────────┘    └──────────┘    └──────────────────────────┘  │
│                                                                  │
└──────────────────────────────────────────────────────────────────┘
```

### 3.5 后端分层架构

```
┌──────────────────────────────────────────────────────────────┐
│                        API Layer (FastAPI Router)             │
│                                                              │
│  scores.py  orders.py  tasks.py  users.py  search.py  admin │
└─────────────────────────────┬────────────────────────────────┘
                              │
┌─────────────────────────────┴────────────────────────────────┐
│                      Service Layer                            │
│                                                              │
│  ScoreService    OrderService    TaskService    UserService   │
│  SearchService   CrawlService   OMRService     AuthService   │
│  TaobaoService   PaymentService NotifyService                │
└─────────────────────────────┬────────────────────────────────┘
                              │
┌─────────────────────────────┴────────────────────────────────┐
│                    Repository Layer (DAL)                     │
│                                                              │
│  ScoreRepo  OrderRepo  TaskRepo  UserRepo  ComposerRepo     │
│                                                              │
│  底层：SQLAlchemy 2.0 async session                          │
└─────────────────────────────┬────────────────────────────────┘
                              │
┌─────────────────────────────┴────────────────────────────────┐
│                     Infrastructure                           │
│                                                              │
│  PostgreSQL    Redis    Meilisearch    OSS    External APIs   │
└──────────────────────────────────────────────────────────────┘
```

### 3.6 后端项目结构

```
backend/
├── alembic/                    # 数据库迁移
│   ├── versions/
│   └── env.py
├── app/
│   ├── __init__.py
│   ├── main.py                 # FastAPI 应用入口
│   ├── config.py               # 配置管理（Pydantic Settings）
│   ├── deps.py                 # 依赖注入（DB session, 当前用户等）
│   │
│   ├── api/                    # API 路由层
│   │   ├── v1/
│   │   │   ├── scores.py       # 乐谱 CRUD + 搜索
│   │   │   ├── orders.py       # 订单管理
│   │   │   ├── tasks.py        # 任务管理
│   │   │   ├── users.py        # 用户注册/登录
│   │   │   ├── search.py       # 搜索 API
│   │   │   ├── upload.py       # 文件上传
│   │   │   └── admin.py        # 管理员专用 API
│   │   └── deps.py
│   │
│   ├── models/                 # SQLAlchemy 模型
│   │   ├── user.py
│   │   ├── score.py
│   │   ├── composer.py
│   │   ├── order.py
│   │   ├── task.py
│   │   └── crawl_result.py
│   │
│   ├── schemas/                # Pydantic Schema
│   │   ├── user.py
│   │   ├── score.py
│   │   ├── order.py
│   │   └── task.py
│   │
│   ├── services/               # 业务逻辑层
│   │   ├── score_service.py
│   │   ├── order_service.py
│   │   ├── task_service.py
│   │   ├── search_service.py
│   │   ├── auth_service.py
│   │   ├── payment_service.py
│   │   └── notify_service.py
│   │
│   ├── repositories/           # 数据访问层
│   │   ├── base.py
│   │   ├── score_repo.py
│   │   ├── order_repo.py
│   │   └── task_repo.py
│   │
│   ├── engine/                 # 核心引擎
│   │   ├── omr/                # OMR 引擎封装
│   │   │   ├── homr_engine.py
│   │   │   └── preprocessor.py # 图片预处理
│   │   ├── music/              # 音乐处理
│   │   │   ├── converter.py    # music21 格式转换
│   │   │   ├── validator.py    # 音乐理论校验
│   │   │   └── lilypond.py     # LilyPond 渲染
│   │   ├── llm/                # LLM 后处理
│   │   │   └── postprocessor.py
│   │   ├── crawl/              # 网络抓取
│   │   │   ├── imslp.py
│   │   │   ├── musescore.py
│   │   │   └── scheduler.py   # 主动抓取调度
│   │   └── watermark.py        # 水印处理
│   │
│   ├── tasks/                  # Celery 异步任务
│   │   ├── celery_app.py
│   │   ├── omr_tasks.py        # 打谱任务
│   │   ├── render_tasks.py     # 渲染任务
│   │   ├── crawl_tasks.py      # 抓取任务
│   │   └── notify_tasks.py     # 通知任务
│   │
│   └── utils/                  # 工具函数
│       ├── oss.py              # OSS 操作
│       ├── copyright.py        # 版权检查
│       └── security.py         # 安全相关
│
├── tests/
│   ├── unit/
│   ├── integration/
│   └── conftest.py
│
├── docker-compose.yml
├── Dockerfile
├── pyproject.toml
└── alembic.ini
```

### 3.7 前端项目结构

```
# 乐谱网（Next.js）
web/
├── src/
│   ├── app/                    # App Router
│   │   ├── layout.tsx
│   │   ├── page.tsx            # 首页
│   │   ├── scores/
│   │   │   ├── page.tsx        # 搜索/分类浏览
│   │   │   └── [id]/
│   │   │       └── page.tsx    # 乐谱详情
│   │   ├── order/
│   │   │   ├── page.tsx        # 订单列表
│   │   │   └── [id]/page.tsx   # 订单详情
│   │   ├── custom/
│   │   │   └── page.tsx        # 定制打谱
│   │   ├── user/
│   │   │   ├── login/page.tsx
│   │   │   ├── register/page.tsx
│   │   │   └── profile/page.tsx
│   │   └── api/                # Next.js API Routes (BFF)
│   │       └── payment/
│   │           └── callback/route.ts
│   ├── components/
│   │   ├── ScoreCard.tsx
│   │   ├── ScorePreview.tsx    # OSMD 乐谱预览
│   │   ├── SearchBar.tsx
│   │   ├── PaymentButton.tsx
│   │   └── ...
│   ├── lib/
│   │   ├── api.ts              # API 客户端
│   │   └── auth.ts
│   └── styles/
├── package.json
└── next.config.ts

# 管理后台（React SPA）
admin/
├── src/
│   ├── pages/
│   │   ├── Dashboard.tsx       # 仪表盘
│   │   ├── tasks/
│   │   │   ├── TaskList.tsx    # 任务列表（Tab 分类）
│   │   │   └── TaskReview.tsx  # 审核编辑器
│   │   ├── scores/
│   │   │   ├── ScoreList.tsx   # 乐谱库管理
│   │   │   └── ScoreEdit.tsx   # 乐谱编辑
│   │   ├── orders/
│   │   │   └── OrderList.tsx
│   │   └── settings/
│   ├── components/
│   │   ├── ReviewEditor/       # 审核编辑器组件
│   │   │   ├── index.tsx
│   │   │   ├── ImageViewer.tsx # 左侧原图查看器
│   │   │   ├── ScoreEditor.tsx # 右侧 Flat.io/Smoosic
│   │   │   └── Toolbar.tsx
│   │   └── ...
│   ├── lib/
│   └── styles/
├── package.json
└── vite.config.ts
```

---

## 4. 关键设计决策

### 4.1 同步 vs 异步

| 操作 | 处理方式 | 理由 |
|------|---------|------|
| 乐谱搜索 | 同步 | 需要即时响应 (<1s) |
| 乐谱详情查询 | 同步 | 需要即时响应 |
| 用户注册/登录 | 同步 | 需要即时响应 |
| 订单创建 | 同步 | 需要即时返回支付 URL |
| OMR 打谱 | **异步 (Celery)** | 耗时长（分钟级） |
| LilyPond 渲染 | **异步 (Celery)** | 耗时 2-15 秒 |
| LLM 后处理 | **异步 (Celery)** | 依赖外部 API |
| 网络抓取 | **异步 (Celery)** | 耗时且可能失败 |
| 淘宝商品同步 | **异步 (Celery)** | 依赖外部 API |
| 水印生成 | **异步 (Celery)** | CPU 密集 |

### 4.2 API 设计原则

```
RESTful API 规范：

GET    /api/v1/scores                   # 搜索/列表
GET    /api/v1/scores/{id}              # 详情
POST   /api/v1/scores                   # 创建（管理员）
PUT    /api/v1/scores/{id}              # 更新（管理员）
DELETE /api/v1/scores/{id}              # 删除（管理员）

POST   /api/v1/orders                   # 创建订单
GET    /api/v1/orders/{id}              # 订单详情
POST   /api/v1/orders/{id}/pay          # 发起支付

GET    /api/v1/tasks                    # 任务列表
GET    /api/v1/tasks/{id}               # 任务详情
POST   /api/v1/tasks/{id}/approve       # 审核通过
POST   /api/v1/tasks/{id}/reject        # 审核拒绝

POST   /api/v1/upload/images            # 上传乐谱图片
POST   /api/v1/custom                   # 提交定制需求

GET    /api/v1/search?q={keyword}       # 搜索（代理 Meilisearch）

POST   /api/v1/auth/login               # 登录
POST   /api/v1/auth/register            # 注册
POST   /api/v1/auth/refresh             # 刷新 Token

# 管理员专用
GET    /api/v1/admin/dashboard           # 仪表盘数据
GET    /api/v1/admin/tasks               # 管理任务（含筛选）
PUT    /api/v1/admin/tasks/{id}/assign   # 分配任务
POST   /api/v1/admin/scores/import       # 批量导入
```

### 4.3 认证与授权

```
┌───────────────────────────────────────────────────────┐
│                  认证方案：JWT                          │
│                                                       │
│  Access Token:  有效期 30 分钟, 存内存/Cookie           │
│  Refresh Token: 有效期 7 天, 存 HttpOnly Cookie         │
│                                                       │
│  角色权限：                                             │
│  ┌──────────┬───────────────────────────────────────┐ │
│  │ customer │ 搜索、浏览、购买、下载、管理个人订单     │ │
│  │ admin    │ customer 权限 + 任务审核、乐谱管理、    │ │
│  │          │ 订单管理、数据统计、系统设置             │ │
│  └──────────┴───────────────────────────────────────┘ │
│                                                       │
│  API 鉴权中间件：                                      │
│  - 公开接口：搜索、浏览、乐谱详情（预览）               │
│  - 登录接口：购买、下载、个人中心                       │
│  - 管理接口：/api/v1/admin/* + /api/v1/tasks/*        │
└───────────────────────────────────────────────────────┘
```

### 4.4 Source of Truth — MusicXML

```
核心约束：MusicXML 是唯一的"真相来源"

原因：
1. LilyPond → MusicXML 反向转换无生产可用工具
2. Web 编辑器（Flat.io / Smoosic）以 MusicXML 为标准格式
3. music21 以 MusicXML 为最佳支持格式

规则：
- 所有修改操作在 MusicXML 上进行
- LilyPond 源码、PDF、MIDI 均从 MusicXML 单向生成
- 每次编辑后重新走 MusicXML → music21 → LilyPond → PDF 管线
- 数据库/OSS 中同时存储 MusicXML 和生成的 LilyPond，但 MusicXML 为主
```

---

## 5. Docker Compose 服务编排

```yaml
# docker-compose.yml（开发环境）
version: "3.9"

services:
  # ========== 后端 API ==========
  api:
    build: ./backend
    ports: ["8000:8000"]
    environment:
      - DATABASE_URL=postgresql+asyncpg://user:pass@postgres:5432/scorewriter
      - REDIS_URL=redis://redis:6379/0
      - MEILISEARCH_URL=http://meilisearch:7700
      - OSS_ENDPOINT=...
      - ANTHROPIC_API_KEY=...
    depends_on: [postgres, redis, meilisearch]
    volumes: ["./backend:/app"]

  # ========== Celery Worker ==========
  celery-worker:
    build: ./backend
    command: celery -A app.tasks.celery_app worker -l info -c 4
    environment: *api-env  # 共享 API 环境变量
    depends_on: [postgres, redis]

  celery-beat:
    build: ./backend
    command: celery -A app.tasks.celery_app beat -l info
    depends_on: [redis]

  # ========== 前端 ==========
  web:
    build: ./web
    ports: ["3000:3000"]
    environment:
      - NEXT_PUBLIC_API_URL=http://localhost:8000

  admin:
    build: ./admin
    ports: ["3001:3001"]

  # ========== 基础设施 ==========
  postgres:
    image: postgres:16-alpine
    ports: ["5432:5432"]
    environment:
      POSTGRES_DB: scorewriter
      POSTGRES_USER: user
      POSTGRES_PASSWORD: pass
    volumes: ["pgdata:/var/lib/postgresql/data"]

  redis:
    image: redis:7-alpine
    ports: ["6379:6379"]

  meilisearch:
    image: getmeili/meilisearch:v1.6
    ports: ["7700:7700"]
    environment:
      MEILI_MASTER_KEY: dev-master-key
    volumes: ["msdata:/meili_data"]

  # ========== LilyPond 渲染服务 ==========
  lilypond:
    image: jeandeaual/lilypond:latest
    # 由 Celery worker 通过 subprocess/API 调用

volumes:
  pgdata:
  msdata:
```

---

## 6. 安全设计

```
┌──────────────────────────────────────────────────────────────┐
│                        安全防线                               │
├──────────────────────────────────────────────────────────────┤
│                                                              │
│  网络层                                                      │
│  ├── HTTPS 全站加密（Let's Encrypt）                          │
│  ├── Nginx rate limiting（API 限流）                          │
│  ├── CORS 白名单（仅允许自有域名）                             │
│  └── 防 DDoS（阿里云安全组 / WAF）                            │
│                                                              │
│  应用层                                                      │
│  ├── JWT 认证 + RBAC 授权                                    │
│  ├── 请求参数校验（Pydantic 强类型）                           │
│  ├── SQL 注入防护（SQLAlchemy 参数化查询）                     │
│  ├── XSS 防护（React 自动转义 + CSP 头）                      │
│  ├── CSRF 防护（SameSite Cookie + CSRF Token）                │
│  └── 文件上传校验（类型 + 大小 + 内容检查）                    │
│                                                              │
│  数据层                                                      │
│  ├── 密码 bcrypt 哈希存储                                    │
│  ├── 敏感数据加密（手机号、支付信息）                          │
│  ├── 数据库定期备份（每日 + 增量）                             │
│  └── 乐谱文件 OSS 私有访问（签名 URL，有效期 1 小时）          │
│                                                              │
│  运维层                                                      │
│  ├── 容器最小权限原则（non-root 运行）                        │
│  ├── 密钥管理（环境变量 / 阿里云 KMS）                        │
│  ├── 日志审计（操作日志 + 访问日志）                           │
│  └── 依赖漏洞扫描（Dependabot / Safety）                     │
│                                                              │
└──────────────────────────────────────────────────────────────┘
```

---

## 7. 监控与可观测性

```
┌─────────────────────────────────────────────────────────────┐
│                    监控体系（Phase 2+）                       │
│                                                             │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐   │
│  │ Prometheus│  │  Grafana  │  │   Loki   │  │ Sentry   │   │
│  │ (指标)   │→│ (可视化)  │  │ (日志)   │  │ (异常)   │   │
│  └──────────┘  └──────────┘  └──────────┘  └──────────┘   │
│                                                             │
│  核心监控指标：                                               │
│  ├── API 响应时间 (P50/P95/P99)                              │
│  ├── OMR 处理时间与成功率                                     │
│  ├── Celery 队列深度与延迟                                    │
│  ├── 订单转化率                                              │
│  ├── 搜索零结果率                                            │
│  ├── 主动抓取成功率                                          │
│  └── 数据库连接池 / Redis 内存使用                            │
│                                                             │
│  告警规则：                                                   │
│  ├── 客户任务超 12 小时未审核 → 管理员通知                    │
│  ├── OMR 连续失败 3 次 → 告警                                │
│  ├── API 5xx 错误率 > 1% → 告警                             │
│  └── 磁盘使用率 > 80% → 告警                                │
└─────────────────────────────────────────────────────────────┘
```
