# 核心技术路线分析

基于对 OMR 引擎、乐谱编辑器、排版引擎、电商平台 API、搜索引擎五个关键技术领域的深度调研，形成以下技术路线分析。

---

## 1. OMR 引擎选型

### 1.1 候选方案对比

| 引擎 | Stars | 最新版本 | 输出格式 | 安装方式 | 硬件需求 | 许可证 | 精度 |
|------|-------|---------|---------|---------|---------|--------|------|
| **HOMR** | ~活跃 | v0.6.0 (2026.01) | MusicXML | `pip install homr` | CPU/GPU | AGPL-3.0 | 中高 |
| **SMT++** | ~活跃 | 研究版 | **kern** | 手动构建 | GPU 必需 | MIT | CER 3.9%（最佳文档化） |
| **LEGATO** | 新 | 2025.06 | **ABC** | 手动构建 | GPU（943M 参数） | MIT | SOTA，比前代降低 68% 错误 |
| **oemer** | ~稳定 | 维护中 | MusicXML | `pip install oemer` | CPU/GPU | MIT | 一般（已被 HOMR 取代） |
| **TrOMR** | 研究 | 2023 | 自定义格式 | 手动构建 | GPU | Apache-2.0 | 良好（HOMR 的基础） |

### 1.2 关键发现

**HOMR 是目前最适合生产部署的选择：**
- 唯一支持 `pip install` 一键安装的成熟方案
- 直接输出 MusicXML，无需格式转换
- CPU 可运行（GPU 加速可选），降低硬件门槛
- 基于 oemer 分割 + TrOMR Transformer 识别的混合架构
- **局限**：仅处理高/低音谱号的音高和节奏，不识别力度、表情记号、歌词

**LEGATO 是精度最高的方案但部署复杂：**
- 943M 参数模型，需要大显存 GPU
- 输出 ABC 记谱法，需要 ABC→MusicXML 额外转换
- 首个支持多页乐谱端到端处理的模型
- 较新（2025.06），社区验证不足

**SMT++ 精度文档化最好但输出格式不理想：**
- 输出 kern 格式，需要 kern→MusicXML 转换（music21 可处理）
- CER 3.9% 的量化精度是各引擎中最透明的
- MIT 许可证，无商用限制

### 1.3 推荐方案

```
Phase 1（MVP）：HOMR 作为主引擎
  优势：pip 安装、MusicXML 直出、CPU 可运行、开发最快
  劣势：精度非 SOTA、AGPL 许可证需注意合规
  应对：LLM 后处理弥补精度、服务端部署无 AGPL 分发问题

Phase 2（精度提升）：HOMR + LEGATO 双引擎
  HOMR 处理简单谱 → 快速出结果
  LEGATO 处理复杂谱 → 更高精度
  根据置信度分数决定用哪个引擎的结果

Phase 3（自主化）：基于 SMT++ 或 LEGATO 微调自有模型
  积累审核校正数据作为训练集
  MIT 许可证允许商业微调
```

### 1.4 所有引擎的共同缺陷

- **不识别歌词**：声乐谱需要额外 OCR（Tesseract/PaddleOCR）提取歌词
- **不识别力度/表情**：p, f, mf, cresc. 等需要 LLM 辅助识别或人工补充
- **手写谱支持极差**：所有引擎主要针对印刷谱训练

---

## 2. Web 乐谱编辑器选型

### 2.1 核心发现

**真正支持浏览器内编辑（非仅渲染）的方案极少。** 大多数库只做渲染，构建编辑功能需要从零开发碰撞检测、拖拽、序列化等，工作量以月计。

### 2.2 候选方案对比

| 方案 | 类型 | 编辑能力 | MusicXML 支持 | 许可证 | 成本 |
|------|------|---------|-------------|--------|------|
| **Flat.io Embed** | 商业 iframe | 完整 WYSIWYG | 导入/导出 | 商业 | 免费(<200用户/月) |
| **Smoosic** | 开源编辑器 | 完整编辑 | 导入/导出 | MIT | 免费 |
| **Soundslice** | 商业编辑器 | 完整编辑+音频同步 | 支持 | 商业 | 按用户付费 |
| OSMD | 开源渲染 | **只读** | 导入 | BSD-3 | 免费 |
| VexFlow | 开源渲染 | **只读** | 无 | MIT | 免费 |
| abcjs | 开源渲染 | **只读**（ABC） | 无 | MIT | 免费 |
| AlphaTab | 开源渲染 | **只读** | 支持 | MPL-2.0 | 免费 |

### 2.3 推荐方案

```
方案 A（推荐，最快上线）：Flat.io Embed
  右侧编辑面板：Flat.io iframe 嵌入，完整编辑能力
  左侧对照面板：OSMD 渲染原图或图片查看器
  优势：开发量最小（几天），编辑体验最好
  劣势：依赖第三方服务，无法自建部署
  适用：MVP 阶段，管理员数量少（<200/月免费）

方案 B（长期，自主可控）：Smoosic
  右侧编辑面板：Smoosic 集成，MusicXML 编辑
  左侧对照面板：图片查看器（缩放、平移）
  优势：MIT 开源，完全自主，可深度定制
  劣势：社区小（~100 stars），需更多集成开发
  适用：Phase 2+，需要深度定制编辑体验时

方案 C（备选）：OSMD + 自建编辑层
  在 OSMD 渲染层上自建交互逻辑
  工作量极大（2-3个月），不推荐作为初期方案
```

### 2.4 编辑器架构设计

```
┌─────────────────────────────────────────────────────┐
│                    审核编辑器页面                       │
├──────────────────────┬──────────────────────────────┤
│                      │                              │
│   左侧：图片查看器    │   右侧：Flat.io / Smoosic    │
│   <img> + 缩放/平移   │   MusicXML 编辑器            │
│                      │                              │
│   实现：              │   数据流：                     │
│   - Leaflet.js 或     │   1. 后端传 MusicXML          │
│     OpenSeadragon    │   2. 编辑器加载渲染            │
│   - 支持高分辨率      │   3. 管理员编辑               │
│     图片分片加载      │   4. 导出修改后的 MusicXML     │
│                      │   5. 后端重新生成 LilyPond+PDF │
│                      │                              │
├──────────────────────┴──────────────────────────────┤
│  工具栏 + 元信息表单（曲名、作者、调号、售价...）       │
└─────────────────────────────────────────────────────┘
```

---

## 3. 数据管线与格式转换

### 3.1 关键约束

**LilyPond → MusicXML 反向转换在实践中不可行。** 目前没有生产可用的工具。这是整个架构设计的核心约束。

### 3.2 推荐数据流

**MusicXML 作为唯一的"真相来源"（Source of Truth）：**

```
OMR 引擎（HOMR）
    │
    ▼ MusicXML
music21 加载 + 校验
    │
    ├── 导出 MusicXML ──→ Web 编辑器（Flat.io/Smoosic）
    │                          │
    │                     管理员编辑
    │                          │
    │                     导出修改后 MusicXML
    │                          │
    ├── ← ─────────────────────┘
    │
    ├── music21 → LilyPond (.ly) ──→ lilypond 渲染 ──→ PDF/PNG
    │
    ├── music21 → MIDI ──→ 在线播放
    │
    └── 存储 MusicXML 到数据库/OSS
```

### 3.3 各环节技术细节

#### music21 — 数据中枢

```python
import music21

# 从 MusicXML 加载
score = music21.converter.parse('score.musicxml')

# 音乐理论校验
analysis = score.analyze('key')          # 调性分析
for part in score.parts:
    for measure in part.getElementsByClass('Measure'):
        # 检查拍子是否对齐
        total = sum(n.duration.quarterLength for n in measure.notesAndRests)
        expected = measure.timeSignature.barDuration.quarterLength

# 导出 LilyPond
score.write('lilypond', 'output.ly')

# 导出 MIDI
score.write('midi', 'output.mid')

# 导出回 MusicXML
score.write('musicxml', 'output.musicxml')
```

- **性能**：单谱处理 1-3 秒，可接受
- **校验能力**：调性分析、平行五度检测、节拍对齐检查、和声分析
- **格式支持**：MusicXML、kern、MIDI、LilyPond、ABC 多向转换

#### LilyPond — 渲染引擎

```python
import subprocess

# 通过 subprocess 调用
subprocess.run([
    'lilypond',
    '--pdf',          # 输出 PDF
    '--png',          # 输出 PNG
    '-dresolution=300',  # PNG 分辨率
    '-o', 'output',   # 输出文件名
    'input.ly'        # 输入文件
], check=True)
```

- **安装**：`pip install lilypond`（Python wrapper）或 Docker `jeandeaual/lilypond`
- **速度**：1 页 2-5 秒，5 页 8-15 秒
- **稳定版**：2.24.4
- **注意**：`musicxml2ly`（LilyPond 自带转换器）质量一般，推荐用 music21 转换

#### 水印方案

```
推荐：PDF 后处理水印
  1. LilyPond 渲染干净 PDF（master 版）
  2. 用 ReportLab + PyPDF2 叠加水印层
  3. 存储：无水印 PDF（付费下载）+ 带水印 PDF（预览）

优势：渲染一次，水印按需叠加，灵活控制水印样式和位置
```

### 3.4 完整的打谱管线

```
输入图片
    │
    ▼
[1] 图片预处理
    │  OpenCV: 灰度化、二值化、倾斜校正、去噪
    │
    ▼
[2] HOMR OMR 识别
    │  pip install homr
    │  输入: 图片  输出: MusicXML
    │
    ▼
[3] music21 加载 + LLM 校验
    │  music21 解析 MusicXML
    │  Claude API: 校验拍子对齐、调号正确性、修正明显错误
    │  输出: 校正后的 MusicXML
    │
    ▼
[4] music21 → LilyPond 转换
    │  score.write('lilypond', 'output.ly')
    │
    ▼
[5] LilyPond 渲染
    │  lilypond --pdf --png -o output output.ly
    │  输出: PDF + PNG
    │
    ▼
[6] 水印处理
    │  ReportLab + PyPDF2: 生成带水印预览版
    │
    ▼
[7] 生成审核任务
    │  存储: MusicXML（可编辑源）、LilyPond（排版源）、PDF（输出）
    │  推送管理员通知
```

---

## 4. 淘宝开放平台集成

### 4.1 关键发现

| 维度 | 现实情况 |
|------|---------|
| **开发门槛** | 高。需企业支付宝认证、逐个 API 申请权限 |
| **自动发货** | 无原生虚拟商品自动发货。需自建：监听订单→发送内容→调用发货 API |
| **消息推送** | 通过 TMC（淘宝消息通道）接收订单推送，非 HTTP Webhook |
| **客服 AI** | 无官方 LLM 接入通道。千牛插件开发或第三方桥接（后者有违规风险） |
| **敏感数据** | 涉及敏感数据的 API 必须部署在阿里云聚石塔 |
| **费用** | API 按日调用量和订单量收费 |
| **Python SDK** | 仅社区维护，非官方 |
| **虚拟商品风险** | 版权投诉风险高（赔偿可达 8-10万+），品类选择错误可能导致店铺处罚 |

### 4.2 推荐策略

```
Phase 1（MVP）：不对接淘宝，先做乐谱网
  理由：
  - 淘宝对接开发量大（认证+API+聚石塔部署），ROI 不确定
  - 乐谱网可完全自主控制用户体验和支付流程
  - 先验证业务模型再投入渠道建设

Phase 2（渠道扩展）：淘宝手动+半自动
  - 淘宝店铺手动上架热门乐谱
  - 用千牛手动发货（PDF 直接发送）
  - 收集客户需求数据，验证淘宝渠道的量

Phase 3（全自动化）：淘宝 API 全对接
  前提：月订单量 > 100单，值得投入自动化开发
  实现：TMC 监听订单 → 自动查库 → 自动发货 → taobao.logistics.dummy.send
```

### 4.3 替代渠道评估

| 平台 | API 友好度 | 虚拟商品支持 | 流量 | 推荐优先级 |
|------|-----------|------------|------|-----------|
| **有赞** | 高（API 完善） | 完善 | 需自带流量 | Phase 1 备选 |
| **拼多多** | 中 | 支持 | 大 | Phase 2 |
| **闲鱼** | 低（无 API） | 不适合 | 大 | 不推荐 |
| **微信小程序** | 高 | 完善 | 需推广 | Phase 2 |

---

## 5. 搜索引擎选型

### 5.1 推荐：Meilisearch

**Meilisearch 是最适合本项目的搜索方案**，原因：

| 需求 | Meilisearch 支持 |
|------|-----------------|
| 中文分词 | 内置中文分词器，开箱即用 |
| 同义词映射 | 原生 Synonyms API |
| 模糊匹配 | 内置 typo tolerance |
| 分面过滤 | Faceted search 原生支持 |
| 自动补全 | 即时搜索（as-you-type） |
| 部署复杂度 | 单二进制文件，几乎零配置 |
| 资源消耗 | 100K 文档仅需 1-4 GB RAM |
| Python SDK | 官方 meilisearch-python |

### 5.2 与备选方案对比

| 方案 | 中文 | 同义词 | 模糊 | 分面 | 资源 | 运维 |
|------|------|--------|------|------|------|------|
| **Meilisearch** | 内置 | 原生 | 原生 | 原生 | 1-4GB | 极简 |
| Elasticsearch | IK插件 | 原生 | 原生 | 原生 | 4-8GB | 复杂 |
| Typesense | **无** | 原生 | 原生 | 原生 | 低 | 简单 |
| PostgreSQL | zhparser | 自建 | pg_trgm | 自建 | 已有 | 无额外 |

- **Elasticsearch**：功能最全但运维重，100K 规模完全杀鸡用牛刀
- **Typesense**：不支持中文分词，直接排除
- **PostgreSQL**：同义词、自动补全、分面搜索全部需要自建，开发量大

### 5.3 多语言乐谱标题处理

```json
{
  "id": "score_001",
  "title_zh": "致爱丽丝",
  "title_en": "Für Elise",
  "title_pinyin": "zhi ai li si",
  "title_aliases": ["献给爱丽丝", "给爱丽丝", "For Elise"],
  "composer": "贝多芬",
  "composer_en": "Beethoven",
  "instrument": "钢琴",
  "genre": "古典",
  "difficulty": 3
}
```

配置同义词 API：
```python
client.index('scores').update_synonyms({
    "致爱丽丝": ["献给爱丽丝", "给爱丽丝"],
    "贝多芬": ["Beethoven"],
    "肖邦": ["Chopin", "萧邦"],
})
```

### 5.4 搜索无结果 → 定制打谱的衔接

```python
results = client.index('scores').search(query)
if results['estimatedTotalHits'] == 0:
    # 展示 "找不到？帮你找！" 入口
    # 搜索词自动填充到定制表单
    # 同时记录搜索日志，用于主动抓取优先级排序
    log_zero_result_query(query)
```

---

## 6. 整体技术架构（修订版）

### 6.1 技术栈总览

```
┌──────────── 前端 ────────────┐
│                               │
│  乐谱网：Next.js + TS         │
│  管理后台：React + Ant Design  │
│  编辑器：Flat.io Embed (MVP)  │
│         → Smoosic (长期)      │
│  图片查看：OpenSeadragon       │
│                               │
├──────────── 后端 ────────────┤
│                               │
│  API：Python FastAPI           │
│  任务队列：Celery + Redis      │
│  调度器：Celery Beat           │
│  搜索：Meilisearch             │
│                               │
├──────── 核心引擎 ────────────┤
│                               │
│  OMR：HOMR (pip install)       │
│  数据中枢：music21             │
│  排版渲染：LilyPond            │
│  LLM 后处理：Claude API        │
│  图片预处理：OpenCV + Pillow   │
│  水印：ReportLab + PyPDF2      │
│  抓取：Playwright + BS4        │
│                               │
├──────── 数据存储 ────────────┤
│                               │
│  数据库：PostgreSQL            │
│  缓存/队列：Redis              │
│  搜索：Meilisearch             │
│  文件：阿里云 OSS              │
│                               │
├──────── 部署 ────────────────┤
│                               │
│  容器化：Docker Compose        │
│  反向代理：Nginx               │
│  SSL：Let's Encrypt            │
│                               │
└───────────────────────────────┘
```

### 6.2 核心数据格式流

```
                    MusicXML（Source of Truth）
                    ┌───────────┐
                    │           │
           ┌───────┤  music21  ├───────┐
           │       │           │       │
           ▼       └─────┬─────┘       ▼
     LilyPond (.ly)      │          MIDI (.mid)
           │              │              │
           ▼              │              ▼
     LilyPond 引擎        │          Web 播放器
           │              │
           ▼              ▼
     PDF / PNG        Web 编辑器
           │         (Flat.io/Smoosic)
           ▼              │
     水印处理              │
     ├── 预览版(水印)      │
     └── 购买版(无水印)    ▼
                     修改后 MusicXML
                     → 回到 music21 重新导出
```

### 6.3 关键架构决策记录

| 决策 | 选择 | 替代方案 | 理由 |
|------|------|---------|------|
| Source of Truth 格式 | MusicXML | LilyPond / kern | LilyPond→MusicXML 无工具；MusicXML 是 Web 编辑器的标准格式 |
| OMR 引擎 | HOMR | SMT++ / LEGATO | pip 安装、MusicXML 直出、CPU 可运行 |
| 乐谱编辑器 | Flat.io→Smoosic | OSMD+自建 / VexFlow | 完整编辑能力开箱即用 vs. 自建需数月 |
| 搜索引擎 | Meilisearch | Elasticsearch | 中文开箱即用、资源消耗低、运维简单 |
| 渲染引擎 | LilyPond | MuseScore CLI | 出版级质量、开源、业界标准 |
| 数据中枢 | music21 | 自建转换器 | 成熟库、多格式支持、内置音乐理论校验 |
| 淘宝对接 | Phase 2 手动→Phase 3 自动 | Phase 1 即对接 | API 对接开发量大、先验证业务模型 |
| 水印方式 | PDF 后处理 | LilyPond 原生 | 一次渲染、按需水印、灵活控制 |

---

## 7. 风险矩阵与应对

### 7.1 技术风险

| 风险 | 影响 | 概率 | 应对 |
|------|------|------|------|
| HOMR 识别精度不足 | 管理员工作量大 | 高 | LLM 后处理补偿 + 低置信度标红 + Phase 2 引入 LEGATO |
| HOMR 不识别歌词 | 声乐谱缺失歌词 | 确定 | PaddleOCR 做歌词区域 OCR + 手动映射到音符 |
| HOMR 不识别力度记号 | 乐谱信息不完整 | 确定 | MVP 阶段接受，管理员手动补充。Phase 2 LLM 识别 |
| music21 LilyPond 导出质量 | 排版不理想 | 中 | 自定义 LilyPond 模板 + 后处理脚本修正常见问题 |
| Flat.io 服务不可用 | 编辑器瘫痪 | 低 | Smoosic 作为备选随时可切换 |
| LilyPond 渲染慢 | 用户等待 | 低 | 异步队列 + 结果缓存 + 预渲染 |

### 7.2 业务风险

| 风险 | 影响 | 概率 | 应对 |
|------|------|------|------|
| 乐谱版权纠纷 | 法律赔偿 8-10万+ | 中 | 优先 IMSLP 公共领域；自行排版产生新版面权；用户协议免责 |
| 淘宝店铺处罚 | 封店 | 中 | 正确选择虚拟商品类目；Phase 1 不依赖淘宝 |
| 一天交付无法兑现 | 客户投诉、差评 | 中 | AI 大幅减少人工量；优先级队列；高峰期动态调整承诺 |

---

## 8. 开发路线图（修订版）

### Phase 1: MVP — 乐谱网 + 打谱引擎（8-10 周）

```
第 1-2 周：基础设施
  - Docker Compose 环境搭建（PostgreSQL + Redis + Meilisearch + LilyPond）
  - FastAPI 项目脚手架 + 数据模型
  - Next.js 乐谱网项目脚手架

第 3-4 周：核心引擎
  - HOMR 集成（pip install + 封装调用接口）
  - music21 数据管线（MusicXML → LilyPond → PDF）
  - LLM 后处理（Claude API 校验）
  - 水印生成

第 5-6 周：乐谱网
  - Meilisearch 搜索集成
  - 乐谱浏览/详情/预览页面
  - 用户注册/登录（手机号 + 微信）
  - 订单 + 支付（微信支付 + 支付宝）

第 7-8 周：管理后台
  - 任务列表（三类 Tab 分离）
  - 审核编辑器 v1（Flat.io Embed + 图片查看器）
  - 乐谱库 CRUD
  - 审核完成 → 入库 → 通知

第 9-10 周：联调 + 上线
  - 端到端测试
  - 定制打谱流程（上传 → OMR → 审核 → 交付）
  - 部署上线
```

### Phase 2: 渠道扩展 + 主动抓取（6-8 周）
- 淘宝店铺手动上架 + 半自动发货
- 主动抓取调度器 + IMSLP 爬虫
- 主动入库/打谱任务流程
- 网络乐谱抓取（客户驱动）+ 水印确认

### Phase 3: 体验优化（4-6 周）
- Smoosic 替换 Flat.io（自主编辑器）
- 搜索增强（同义词库、热门推荐）
- MIDI 播放预览
- 乐谱网会员系统
- 淘宝 API 全自动化（如果订单量达标）

### Phase 4: 规模化（持续）
- OMR 引擎升级（LEGATO 集成）
- 基于审核数据微调自有模型
- 主动抓取智能化（搜索日志驱动）
- 移调工具、批量打谱、API 开放

---

## 9. MVP 最小依赖清单

```yaml
# docker-compose.yml 核心服务
services:
  api:          # FastAPI 后端
    image: python:3.11
    depends_on: [postgres, redis, meilisearch]

  web:          # Next.js 前端
    image: node:20

  admin:        # React 管理后台
    image: node:20

  postgres:     # 数据库
    image: postgres:16

  redis:        # 缓存 + Celery broker
    image: redis:7

  meilisearch:  # 搜索引擎
    image: getmeili/meilisearch:latest

  lilypond:     # 排版渲染
    image: jeandeaual/lilypond

  celery:       # 异步任务 worker
    image: python:3.11  # 共用 API 镜像
    command: celery -A app worker

  celery-beat:  # 定时调度
    image: python:3.11
    command: celery -A app beat

# Python 核心依赖
dependencies:
  - fastapi + uvicorn       # Web 框架
  - celery + redis          # 任务队列
  - sqlalchemy + alembic    # ORM + 迁移
  - homr                    # OMR 引擎
  - music21                 # 音乐数据处理
  - lilypond (pip)          # 排版渲染
  - meilisearch             # 搜索客户端
  - anthropic               # Claude API
  - pillow                  # 图片处理/水印
  - reportlab + pypdf2      # PDF 水印
  - opencv-python           # 图片预处理
  - playwright              # 网页抓取
  - oss2                    # 阿里云 OSS

# 前端核心依赖
  - next.js + react         # 乐谱网
  - ant-design              # 管理后台 UI
  - flat-embed (npm)        # 乐谱编辑器
  - openseadragon           # 图片查看器
```
