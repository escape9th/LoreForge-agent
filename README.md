# LoreForge

LoreForge 是一个证据驱动的创作研究 Agent Demo。

它面向动漫、游戏和原创世界观创作：输入一个创作需求，系统会拆解研究问题，检索演示资料，提取证据，生成创作蓝图，并核验哪些事实有来源支持。

## 运行

项目默认只使用 Python 标准库，不需要 API Key。

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

## 工作流

```text
plan -> gather -> extract -> draft -> verify
```

- `plan`：把创作需求拆成研究问题。
- `gather`：从受控资料源检索并去重。
- `extract`：把资料保存成可引用的证据。
- `draft`：分别生成资料事实和原创提案。
- `verify`：检查事实声明是否能被证据支持。

## 为什么不是普通聊天机器人

普通聊天机器人只返回文本，很难回答“这句话从哪里来”。LoreForge 把来源、证据、事实、原创提案和执行轨迹拆开保存。模型可以生成想法，但不能把没有证据的想法自动伪装成事实。

第一版使用确定性的 Demo Provider，是为了让项目在没有付费模型和网络的情况下可复现。后续可以把 `ModelProvider` 替换成 OpenAI-compatible、Ollama 或其他模型适配器，把 `SearchProvider` 替换成真实搜索服务。

## 项目结构

```text
src/loreforge/
├── domain.py       # 数据契约
├── demo.py         # Demo 搜索和模型适配器
├── workflow.py     # 有边界的 Agent 工作流
├── verification.py # 事实声明核验
├── reporting.py    # Markdown/JSON 报告
└── cli.py          # 命令行入口
```

## 当前限制

- Demo 资料是内置的，不是实时联网搜索。
- 核验使用可解释的关键词重叠算法，不等同于完整事实核查。
- 第一版只有一次生成和一次核验，没有多 Agent 协作。
- 没有数据库和 Web 前端，先保持 Demo 小而完整。

## 学习文档

完整中文教学请阅读 [`docs/学习手册.md`](docs/学习手册.md)。
