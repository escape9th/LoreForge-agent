# LoreForge

![CI](https://github.com/escape9th/LoreForge-agent/actions/workflows/ci.yml/badge.svg)


**中文 Agent / AI Agent / LLM / RAG / Tool Calling / Function Calling / 创作研究 / 游戏世界观 / Worldbuilding**

LoreForge 是一个证据驱动、可离线复现的创作研究 Agent。

它面向动漫、游戏和原创世界观创作：输入一个创作需求，Agent 会拆解研究问题，自主选择检索与来源读取工具，提取证据，生成创作蓝图，并核验哪些事实有来源支持。每次工具调用都会留下结构化轨迹。

它面向动漫、游戏和原创世界观创作：输入一个创作需求，系统会拆解研究问题，检索演示资料，提取证据，生成创作蓝图，并核验哪些事实有来源支持。
说直白一点，这玩意在你自己那蓬勃地 宛如热气腾腾的狗屎的创作欲在自慰式自嗨后，能比你的读者或用户先一步感受到那股不对劲的臭味，进而用犀利的言语将你的幻想打碎后强行进入作品创作的伟大的冷静的不可多得的贤者时刻。
因为大概率没人会真的点开这个b仓库，所以我就相当于告诉我自己这个经常写卡壳的且被主编狠狠退回的蠢货这里有个工具可用了。

## 运行

项目默认只使用 Python 标准库，不需要 API Key。

English overview: [`README.en.md`](README.en.md)

最简单的运行方式不需要安装第三方依赖：

```powershell
python scripts\run_demo.py run "设计一个受海洋灾变影响的漂浮城市游戏世界观" --out demo-output
```

如果你在完整 Python 开发环境中，也可以创建虚拟环境并安装本项目：

```powershell
python -m venv .venv
.\.venv\Scripts\python -m pip install -e .
.\.venv\Scripts\python -m loreforge run "设计一个受海洋灾变影响的漂浮城市游戏世界观" --out demo-output
```

输出目录中会有：

- Markdown 研究创作包
- JSON 运行记录
- 完整 Tool Calling 输入、结果与状态

查看 JSON 摘要：

```powershell
python scripts\run_demo.py inspect demo-output\<run-id>.json
```

运行测试：

```powershell
python -m pytest -q
```

运行评测：

```powershell
python evaluation\run_evaluation.py
```

### 保存运行历史

给 `run` 命令提供 SQLite 路径后，完整的研究包会保存到数据库：

```powershell
python scripts\run_demo.py run "设计一个资源冲突的游戏任务线" `
  --out demo-output --db data\loreforge.sqlite3
python scripts\run_demo.py history --db data\loreforge.sqlite3
python scripts\run_demo.py show <run-id> --db data\loreforge.sqlite3
```

数据库只保存运行摘要和完整 JSON 快照，方便调试、复盘和后续接入 Web 工作台。

### 启动 FastAPI 服务

API 是可选依赖，不影响默认 Demo：

```powershell
.\.venv\Scripts\python -m pip install -e ".[api]"
uvicorn loreforge.api:create_app --factory --reload
```

主要接口：

```text
GET  /health
POST /runs       {"prompt": "设计一个原创游戏世界观", "max_tool_calls": 6}
GET  /runs
GET  /runs/{run_id}
```

服务默认使用 `loreforge.db` 保存历史，也可以通过 `LOREFORGE_HISTORY_DB` 指定数据库路径。

### 使用自己的资料库

资料库是一个 JSON 数组，每个元素至少包含 `source_id`、`title`、`url` 和 `text`：

```powershell
python scripts\run_demo.py run "分析这个世界观的能源系统" --corpus examples\corpus.json
```

### 接入 OpenAI-compatible 模型

设置以下环境变量后，CLI 会自动切换到真实模型 Provider：

```powershell
$env:LOREFORGE_MODEL_ENDPOINT = "https://your-provider.example/v1/chat/completions"
$env:LOREFORGE_MODEL_API_KEY = "your-api-key"
$env:LOREFORGE_MODEL_NAME = "your-model-name"
$env:LOREFORGE_MAX_TOOL_CALLS = "6"
python scripts\run_demo.py run "设计一个原创游戏世界观"
```

不设置这些变量时，系统继续使用无需联网的 Demo Provider。

## Agent 工作流

```text
plan -> decide tool -> execute tool -> gather -> extract -> draft -> verify
```

- `plan`：把创作需求拆成研究问题。
- `decide/execute`：模型按 JSON Schema 选择工具，代码校验参数并执行。
- `gather`：从受控资料源检索并去重。
- `extract`：把资料保存成可引用的证据。
- `draft`：分别生成资料事实和原创提案。
- `verify`：检查事实声明是否能被证据支持。

## 关键词

`AI Agent` `LLM` `RAG` `Agent workflow` `creative writing` `worldbuilding`
`Tool Calling` `Function Calling` `Agent tools` `Agent observability`
`game development` `anime` `knowledge grounding` `citation` `evaluation`
`中文 Agent` `中文大模型` `智能体` `检索增强生成` `游戏世界观` `小说创作`
`动漫创作` `可观测性` `结构化输出`

## 为什么不是普通聊天机器人

普通聊天机器人只返回文本，很难回答“这句话从哪里来”。LoreForge 把来源、证据、事实、原创提案和执行轨迹拆开保存。模型可以生成想法，但不能把没有证据的想法自动伪装成事实。

默认使用确定性的 Demo Provider，是为了让项目在没有付费模型和网络的情况下可复现。配置环境变量后，同一条执行链会切换到 OpenAI-compatible 模型，由模型返回标准 `tool_calls`。`SearchProvider` 也可以替换成搜索 API、向量数据库或 MCP 服务。

## 项目结构

```text
src/loreforge/
├── domain.py       # 数据契约
├── demo.py         # Demo 搜索和模型适配器
├── workflow.py     # 有边界的 Agent 工作流
├── tools.py        # 工具协议、注册中心与内置工具
├── toolcalling.py  # 有调用上限的模型-工具循环
├── verification.py # 事实声明核验
├── reporting.py    # Markdown/JSON 报告
├── repository.py    # SQLite 运行历史
├── service.py       # CLI/API 共用服务层
├── api.py           # FastAPI HTTP 接口
├── evaluation.py    # 共享结构化评测
└── cli.py           # 命令行入口
```

## 当前限制

- Demo 资料是内置的，不是实时联网搜索。
- 核验使用可解释的关键词重叠算法，不等同于完整事实核查。
- 当前检索是透明的词项召回，没有接入向量数据库或 reranker。
- 当前是单 Agent 工具循环，没有多 Agent 协作。
- API 目前没有认证、任务队列和 Web 前端，适合作为本地研究服务和二次开发基础。

## 学习文档


完整中文教学请阅读 [`docs/项目完全解读与面试手册.md`](docs/项目完全解读与面试手册.md)。

## GitHub Topics 建议

建议在仓库设置中添加这些与真实功能对应的 Topics：

`ai-agent` `llm` `rag` `agent-workflow` `creative-writing` `worldbuilding`
`game-development` `knowledge-grounding` `citation` `evaluation` `python`
`fastapi` `sqlite` `rest-api` `run-history` `observability`
`tool-calling` `function-calling` `agent-tools` `agent-trace`
`中文agent` `中文大模型` `智能体` `智能体平台` `检索增强生成`
`游戏世界观` `小说创作` `运行记录` `可观测性`

完整中文教学请阅读 [`docs/学习手册.md`](docs/学习手册.md)。
## 去成为下一个唐家三少吧蠢货。

