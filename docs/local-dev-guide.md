# 本地开发环境搭建指南（Windows + WSL）

本指南帮助你在 Windows + WSL2 环境下搭建完整的本地开发与测试环境。

---

## 1. 环境要求

### 1.1 硬件最低要求

| 项目 | 最低要求 | 推荐配置 | 说明 |
|------|---------|---------|------|
| **CPU** | 4 核 | 8 核+ | OMR 推理在 CPU 上运行较慢 |
| **内存** | 8 GB | 16 GB+ | Docker 容器 + OMR + music21 较吃内存 |
| **磁盘** | 20 GB 空闲 | 50 GB+ SSD | Docker 镜像 + 乐谱文件 + 数据库 |
| **GPU** | 无（CPU 可运行） | NVIDIA GPU (6GB+ VRAM) | 有 GPU 可加速 HOMR 推理 5-10 倍 |

### 1.2 软件前置条件

```
Windows 端：
├── Windows 10 (21H2+) 或 Windows 11
├── WSL2 已启用
├── Docker Desktop for Windows（启用 WSL2 后端）
└── VS Code + Remote - WSL 扩展（推荐）

WSL2 内：
├── Ubuntu 22.04 LTS（推荐）
├── Git
├── Python 3.11+
├── Node.js 20+ (LTS)
├── pnpm
└── Docker CLI（由 Docker Desktop 提供）
```

---

## 2. 一步步搭建

### 2.1 安装 WSL2 + Ubuntu

```powershell
# 在 Windows PowerShell (管理员) 中运行
wsl --install -d Ubuntu-22.04

# 安装完成后重启电脑，然后设置用户名和密码
```

### 2.2 安装 Docker Desktop

1. 下载安装 [Docker Desktop for Windows](https://www.docker.com/products/docker-desktop/)
2. 安装时勾选 **"Use WSL 2 instead of Hyper-V"**
3. 打开 Docker Desktop → Settings → Resources → WSL Integration → 启用你的 Ubuntu 发行版
4. 验证：

```bash
# 在 WSL2 Ubuntu 终端中
docker --version          # Docker version 24.x+
docker compose version    # Docker Compose version v2.x+
```

### 2.3 安装开发工具（在 WSL2 中）

```bash
# 更新系统
sudo apt update && sudo apt upgrade -y

# 安装基础工具
sudo apt install -y build-essential curl wget git unzip

# ========== Python 3.11+ ==========
sudo apt install -y python3.11 python3.11-venv python3.11-dev python3-pip

# 安装 uv（推荐的 Python 包管理器，极快）
curl -LsSf https://astral.sh/uv/install.sh | sh

# 验证
python3.11 --version
uv --version

# ========== Node.js 20 LTS ==========
curl -fsSL https://deb.nodesource.com/setup_20.x | sudo -E bash -
sudo apt install -y nodejs

# 安装 pnpm
npm install -g pnpm

# 验证
node --version     # v20.x
pnpm --version

# ========== LilyPond ==========
sudo apt install -y lilypond

# 验证
lilypond --version  # GNU LilyPond 2.22+ (Ubuntu 仓库版本)

# 如需最新版 (2.24)：
# 从 https://lilypond.org/download.html 下载 Linux 版本
```

### 2.4 克隆项目

```bash
# 在 WSL2 中，建议在 Linux 文件系统下开发（性能远优于 /mnt/c/）
cd ~
git clone <你的仓库地址> score_writer
cd score_writer
```

---

## 3. 启动服务

### 3.1 用 Docker Compose 一键启动基础设施

项目根目录下创建或使用已有的 `docker-compose.dev.yml`：

```bash
# 启动所有基础设施服务
docker compose -f docker-compose.dev.yml up -d

# 检查服务状态
docker compose -f docker-compose.dev.yml ps

# 预期输出：
# postgres      running   0.0.0.0:5432->5432/tcp
# redis         running   0.0.0.0:6379->6379/tcp
# meilisearch   running   0.0.0.0:7700->7700/tcp
```

### 3.2 启动后端 API（本机运行，便于调试）

```bash
cd backend

# 创建虚拟环境并安装依赖
uv venv --python 3.11
source .venv/bin/activate
uv pip install -r requirements.txt  # 或 uv pip install -e ".[dev]"

# 环境变量（创建 .env 文件）
cat > .env << 'EOF'
DATABASE_URL=postgresql+asyncpg://user:pass@localhost:5432/scorewriter
REDIS_URL=redis://localhost:6379/0
MEILISEARCH_URL=http://localhost:7700
MEILISEARCH_KEY=dev-master-key
ANTHROPIC_API_KEY=sk-ant-xxx  # 你的 Claude API Key
OSS_ENABLED=false             # 本地开发关闭 OSS，用本地文件存储
LOCAL_STORAGE_PATH=./storage  # 本地文件存储路径
SECRET_KEY=dev-secret-key-change-in-production
EOF

# 数据库迁移
alembic upgrade head

# 启动 API 服务
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# API 文档：http://localhost:8000/docs (Swagger UI)
```

### 3.3 启动 Celery Worker（另开终端）

```bash
cd backend
source .venv/bin/activate

# 启动 worker
celery -A app.tasks.celery_app worker -l info -c 2

# （可选）启动 beat 调度器（主动抓取用）
celery -A app.tasks.celery_app beat -l info
```

### 3.4 启动前端

```bash
# 乐谱网
cd web
pnpm install
pnpm dev    # http://localhost:3000

# 管理后台（另开终端）
cd admin
pnpm install
pnpm dev    # http://localhost:3001
```

### 3.5 服务访问地址汇总

启动后，所有服务在 WSL2 中的 localhost 端口可直接从 Windows 浏览器访问：

| 服务 | 地址 | 说明 |
|------|------|------|
| **乐谱网** | http://localhost:3000 | Next.js 前端 |
| **管理后台** | http://localhost:3001 | React 管理端 |
| **API 文档** | http://localhost:8000/docs | Swagger UI |
| **API (JSON)** | http://localhost:8000/redoc | ReDoc |
| **Meilisearch** | http://localhost:7700 | 搜索引擎 Web UI |
| **PostgreSQL** | localhost:5432 | 数据库（可用 DBeaver 连接） |
| **Redis** | localhost:6379 | 缓存 |

---

## 4. 各模块独立测试

你不需要启动全部服务就能测试单个模块。以下是各模块的独立测试方式：

### 4.1 测试 OMR 引擎（HOMR）— 仅需 Python

```bash
cd backend
source .venv/bin/activate

# 安装 HOMR
pip install homr

# 快速测试：输入一张乐谱图片，输出 MusicXML
python -c "
from homr import download_and_convert_image
result = download_and_convert_image('test_score.png')
print('OMR 识别完成，输出文件:', result)
"

# 或使用命令行
homr test_score.png -o output.musicxml
```

> **注意**：首次运行会下载模型文件（约 500MB），需要耐心等待。
> 无 GPU 时 CPU 推理每页约 30-120 秒，有 NVIDIA GPU 可加速到 5-15 秒。

### 4.2 测试 music21 格式转换 — 仅需 Python

```bash
python -c "
import music21

# 加载 MusicXML
score = music21.converter.parse('output.musicxml')

# 分析调性
key = score.analyze('key')
print(f'调性: {key}')

# 导出 LilyPond
score.write('lilypond', fp='output.ly')
print('LilyPond 文件已生成: output.ly')

# 导出 MIDI
score.write('midi', fp='output.mid')
print('MIDI 文件已生成: output.mid')
"
```

### 4.3 测试 LilyPond 渲染 — 仅需 LilyPond

```bash
# 从 music21 输出的 .ly 文件渲染 PDF
lilypond --pdf -o output output.ly

# 查看输出
ls output.pdf   # PDF 文件
```

### 4.4 测试完整打谱管线 — Python + LilyPond

```bash
python -c "
from homr import download_and_convert_image
import music21
import subprocess

# Step 1: OMR 识别
print('[1/4] OMR 识别中...')
download_and_convert_image('test_score.png')

# Step 2: music21 加载
print('[2/4] 加载 MusicXML...')
score = music21.converter.parse('test_score.musicxml')
key = score.analyze('key')
print(f'      检测到调性: {key}')

# Step 3: 导出 LilyPond
print('[3/4] 生成 LilyPond 源码...')
score.write('lilypond', fp='test_output.ly')

# Step 4: 渲染 PDF
print('[4/4] 渲染 PDF...')
subprocess.run(['lilypond', '--pdf', '-o', 'test_output', 'test_output.ly'], check=True)

print('完成! 输出文件: test_output.pdf')
"
```

### 4.5 测试 Meilisearch — 仅需 Docker

```bash
# 确保 meilisearch 容器运行
docker compose -f docker-compose.dev.yml up -d meilisearch

# 用 curl 测试
# 创建索引
curl -X POST 'http://localhost:7700/indexes' \
  -H 'Content-Type: application/json' \
  -H 'Authorization: Bearer dev-master-key' \
  --data '{ "uid": "scores", "primaryKey": "id" }'

# 添加测试数据
curl -X POST 'http://localhost:7700/indexes/scores/documents' \
  -H 'Content-Type: application/json' \
  -H 'Authorization: Bearer dev-master-key' \
  --data '[
    {"id": 1, "title_zh": "致爱丽丝", "title_en": "Für Elise", "composer": "贝多芬"},
    {"id": 2, "title_zh": "月光奏鸣曲", "title_en": "Moonlight Sonata", "composer": "贝多芬"},
    {"id": 3, "title_zh": "卡农", "title_en": "Canon in D", "composer": "帕赫贝尔"}
  ]'

# 搜索测试
curl 'http://localhost:7700/indexes/scores/search' \
  -H 'Authorization: Bearer dev-master-key' \
  --data '{ "q": "贝多芬" }'
```

### 4.6 测试 LLM 后处理 — 仅需 API Key

```bash
pip install anthropic

python -c "
import anthropic

client = anthropic.Anthropic()  # 自动读取 ANTHROPIC_API_KEY 环境变量

# 模拟 OMR 后处理校验
musicxml_snippet = '''
<measure number=\"1\">
  <note><pitch><step>C</step><octave>4</octave></pitch><duration>4</duration><type>quarter</type></note>
  <note><pitch><step>E</step><octave>4</octave></pitch><duration>4</duration><type>quarter</type></note>
  <note><pitch><step>G</step><octave>4</octave></pitch><duration>4</duration><type>quarter</type></note>
</measure>
'''

resp = client.messages.create(
    model='claude-sonnet-4-20250514',
    max_tokens=1024,
    messages=[{
        'role': 'user',
        'content': f'以下 MusicXML 片段来自 OMR 识别，拍号为 4/4。请检查每小节拍子总时值是否正确，指出错误：\n{musicxml_snippet}'
    }]
)
print(resp.content[0].text)
"
```

---

## 5. WSL2 特有注意事项

### 5.1 文件系统性能

```
⚠️ 关键提示：务必在 WSL2 Linux 文件系统下开发

✅ 推荐：~/projects/score_writer       （Linux 文件系统，快）
❌ 避免：/mnt/c/Users/xxx/score_writer  （Windows 文件系统，慢 5-10 倍）

原因：跨文件系统访问（Linux ↔ Windows）有巨大性能损耗，
     Docker 挂载 /mnt/c/ 下的卷尤其慢。
```

### 5.2 GPU 支持（可选，加速 OMR）

如果你有 NVIDIA GPU，可在 WSL2 中启用 CUDA：

```bash
# 1. 在 Windows 端安装最新的 NVIDIA GPU 驱动（不是 WSL2 专用驱动）
#    https://www.nvidia.com/download/index.aspx

# 2. WSL2 中验证
nvidia-smi   # 应该能看到 GPU 信息

# 3. 安装 CUDA toolkit（WSL2 中）
sudo apt install -y nvidia-cuda-toolkit

# 4. 安装 PyTorch GPU 版本
pip install torch torchvision --index-url https://download.pytorch.org/whl/cu121

# 5. HOMR 会自动检测并使用 GPU
```

### 5.3 端口转发

WSL2 的端口自动转发到 Windows，你可以直接在 Windows 浏览器中访问 `localhost:3000` 等端口。如果遇到端口无法访问：

```powershell
# Windows PowerShell 中检查
netsh interface portproxy show all

# 手动添加端口转发（一般不需要）
netsh interface portproxy add v4tov4 listenport=3000 listenaddress=0.0.0.0 connectport=3000 connectaddress=$(wsl hostname -I | awk '{print $1}')
```

### 5.4 VS Code 开发

```bash
# 在 WSL2 项目目录中直接打开 VS Code
cd ~/score_writer
code .

# VS Code 会自动以 Remote - WSL 模式打开
# 终端、调试器、插件都在 WSL2 中运行
```

### 5.5 WSL2 内存限制

Docker + 开发服务可能占用较多内存。可通过 `.wslconfig` 限制：

```
# Windows 用户目录下创建 %UserProfile%\.wslconfig
[wsl2]
memory=8GB        # 根据你的总内存调整（建议总内存的一半）
swap=4GB
processors=4
```

修改后需要重启 WSL：`wsl --shutdown`

---

## 6. 不同阶段的测试策略

### 6.1 Phase 1: 只测核心管线（不需要全部服务）

```
最小测试集（仅需 Python + LilyPond）：

1. 准备一张乐谱图片（从 IMSLP 下载）
2. HOMR 识别 → MusicXML
3. music21 校验 → LilyPond
4. LilyPond 渲染 → PDF
5. 对比原图和输出 PDF

所需环境：Python 3.11 + pip install homr music21 + apt install lilypond
无需：Docker、PostgreSQL、Redis、Node.js
```

### 6.2 Phase 2: 测试搜索和 API

```
加入 Docker 基础设施：

docker compose up -d postgres redis meilisearch
uvicorn app.main:app --reload

测试：API CRUD、搜索、任务创建
```

### 6.3 Phase 3: 全栈测试

```
启动所有服务，测试完整用户流程：

搜索乐谱 → 购买 → 下载
上传图片 → 创建任务 → OMR → 审核 → 交付
```

---

## 7. 常见问题

| 问题 | 解决方案 |
|------|---------|
| `docker: command not found` | Docker Desktop 中启用 WSL Integration |
| HOMR 下载模型超时 | 设置代理或手动下载模型文件 |
| LilyPond 中文歌词乱码 | 安装中文字体：`sudo apt install fonts-noto-cjk` |
| PostgreSQL 连接被拒 | 检查 Docker 容器是否运行：`docker ps` |
| WSL2 访问 localhost 失败 | 重启 Docker Desktop 或 `wsl --shutdown` |
| 内存不足 OOM Killed | 调整 `.wslconfig` 增加内存分配 |
| Node.js 依赖安装慢 | 使用国内镜像：`pnpm config set registry https://registry.npmmirror.com` |
| pip 安装慢 | 使用清华镜像：`pip config set global.index-url https://pypi.tuna.tsinghua.edu.cn/simple` |
| Git clone 慢 | 配置 Git 代理或使用 Gitee 镜像 |

---

## 8. 快速启动命令速查

```bash
# ===== 一次性环境搭建 =====
# 安装所有依赖（在 WSL2 Ubuntu 中）
sudo apt update && sudo apt install -y python3.11 python3.11-venv lilypond fonts-noto-cjk
curl -LsSf https://astral.sh/uv/install.sh | sh
curl -fsSL https://deb.nodesource.com/setup_20.x | sudo -E bash - && sudo apt install -y nodejs
npm install -g pnpm

# ===== 日常开发 =====
# 终端 1：基础设施
docker compose -f docker-compose.dev.yml up -d

# 终端 2：后端 API
cd backend && source .venv/bin/activate && uvicorn app.main:app --reload --port 8000

# 终端 3：Celery Worker
cd backend && source .venv/bin/activate && celery -A app.tasks.celery_app worker -l info

# 终端 4：乐谱网前端
cd web && pnpm dev

# 终端 5：管理后台
cd admin && pnpm dev

# ===== 快速测试打谱管线 =====
cd backend && source .venv/bin/activate
homr test_image.png -o result.musicxml
python -c "import music21; s=music21.converter.parse('result.musicxml'); s.write('lilypond','result.ly')"
lilypond --pdf -o result result.ly && echo '打开 result.pdf 查看结果'
```
