# PaperCoach

PaperCoach 是一个面向论文精读的本地 Web 应用。它用 Python/FastAPI 提供后端服务，用静态 HTML/CSS/JavaScript 提供中文阅读界面，目标是把论文阅读拆成“阅读导航、引导提问、回答反馈、阶段笔记”的分阶段流程。

当前项目优先服务 Agent / LLM Agent 方向论文阅读，但整体框架也可以用于其它研究论文。

## 功能

- PDF 上传与解析：提取论文标题、作者、页数、章节文本与页面图片。
- Zotero 本地导入：支持从本机 Zotero storage 中导入 PDF 路径，同时保留普通 PDF 上传方式。
- 分阶段阅读导航：围绕背景、问题、核心想法、系统架构、方法、实验、结果、局限、思考推进。
- 苏格拉底式引导问题：每个阶段给出应回读的位置、阅读目标、重点关注点和问题。
- 回答反馈：支持本地规则评分，也可接入 DeepSeek/OpenAI 兼容接口生成反馈。
- 中文前端阅读器：支持单页/连续阅读、页码跳转、左右栏拖拽、阶段笔记与 AI 阅读教练。

## 技术栈

- Python 3.11，推荐 `3.11.9`
- FastAPI
- Uvicorn
- Pydantic / pydantic-settings
- PyMuPDF
- OpenAI Python SDK，使用 OpenAI-compatible API 调用 DeepSeek 或 OpenAI
- 原生 HTML/CSS/JavaScript

## 快速开始

创建并激活环境：

```powershell
conda create -n papercoach python=3.11.9
conda activate papercoach
```

安装依赖：

```powershell
pip install -r requirements.txt
pip install -r requirements-dev.txt
```

复制环境变量模板：

```powershell
copy .env.example .env
```

启动服务：

```powershell
python -m papercoach
```

浏览器打开：

```text
http://127.0.0.1:8000/
```

## LLM 配置

默认支持本地规则反馈，也可以接入 DeepSeek 或 OpenAI-compatible 服务。

`.env` 示例：

```env
PAPERCOACH_HOST=127.0.0.1
PAPERCOACH_PORT=8000
PAPERCOACH_DATA_DIR=data

PAPERCOACH_LLM_PROVIDER=deepseek
PAPERCOACH_DEEPSEEK_API_KEY=sk-your-key-here
PAPERCOACH_DEEPSEEK_BASE_URL=https://api.deepseek.com
PAPERCOACH_DEEPSEEK_MODEL=deepseek-v4-flash
```

不要提交真实 `.env`。项目已经通过 `.gitignore` 忽略 `.env`、上传论文、运行会话和截图。

## 测试

运行测试：

```powershell
$env:PYTHONUTF8='1'
$env:PYTHONIOENCODING='utf-8'
python -m pytest -q
```

运行编译检查：

```powershell
python -m compileall -q papercoach tests
```

## 项目结构

```text
papercoach/
  agents/       # 阅读导航、问题生成、回答评价、博客片段构建
  api/          # FastAPI 路由
  core/         # 常量与 ID 工具
  schemas/      # Pydantic 数据模型
  services/     # PDF 解析、论文存储、会话、检索、LLM 客户端
  storage/      # JSON 文件存储
  web/          # 中文前端页面
packages/
  prompts/      # Agent 提示词模板
tests/          # 单元测试
```

## 常用接口

- `GET /`：中文 Web 页面
- `GET /api/health`：健康检查
- `POST /api/papers`：上传 PDF
- `POST /api/papers/import-zotero`：从本地 Zotero PDF 路径导入
- `GET /api/papers`：论文列表
- `GET /api/papers/{paper_id}`：论文详情
- `GET /api/papers/{paper_id}/pages/{page_number}/image`：渲染论文页面图片
- `POST /api/sessions`：创建阅读会话
- `POST /api/sessions/{session_id}/navigation`：生成阶段阅读导航
- `POST /api/sessions/{session_id}/answers`：提交回答并获取反馈

## 说明

`PaperCoach.md` 保留为更完整的项目设计文档；`README.md` 用于 GitHub 首页展示和快速上手。
