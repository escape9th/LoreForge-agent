# LoreForge API 与运行历史设计

**日期：** 2026-09-12  
**目标版本：** v0.3.0  
**状态：** 已批准，进入实现

## 背景

LoreForge 当前已经具备可复现的 Agent 工作流、资料库适配器、OpenAI-compatible 模型适配器和命令行入口。下一步需要把一次运行变成可复盘、可被其他程序调用的工程能力，同时保留默认 Demo 不依赖外部服务的特点。

## 目标

1. 为每次研究运行提供 SQLite 持久化记录。
2. 通过服务层复用同一套工作流，避免 CLI 和 API 各自实现业务逻辑。
3. 提供 FastAPI HTTP 接口：
   - `GET /health`
   - `POST /runs`
   - `GET /runs`
   - `GET /runs/{run_id}`
4. 提供结构化评测入口，使评测逻辑可以被命令行和 API 共同调用。
5. 让所有新增行为都有单元测试和 API 集成测试。

## 非目标

- 本版本不加入实时联网搜索。
- 本版本不加入向量数据库、用户认证、任务队列或前端。
- 本版本不要求安装运行服务器才能使用基础 CLI Demo。
- 本版本不改变已有的 `plan -> gather -> extract -> draft -> verify` 工作流协议。

## 架构

```text
CLI / FastAPI
     |
RunService
     |
run_research(...)
     |
Providers + Verification
     |
ResearchPackage
     |
RunRepository(SQLite)
```

### 服务层

`RunService` 负责组合配置、Provider 和仓储：

- 接收用户 prompt；
- 调用现有 `run_research`；
- 保存完整 JSON 运行包；
- 返回领域对象；
- 提供分页列表和单次运行读取。

工作流本身继续保持纯业务职责，不直接依赖 SQLite 或 FastAPI。

### 持久化

SQLite 只保存一张 `runs` 表：

- `run_id`：主键；
- `prompt`：原始需求；
- `title`：蓝图标题；
- `created_at`：运行创建时间；
- `payload_json`：完整 `ResearchPackage.to_dict()` JSON。

完整 JSON 作为快照保存，避免为了查询字段把领域结构拆成大量耦合表。列表接口只读取摘要字段，详情接口再反序列化完整快照。

### HTTP 接口

请求和响应使用普通 JSON，不强制引入 Pydantic 模型到领域层：

- `POST /runs` 请求体：`{"prompt": "...", "corpus": "optional/path"}`；
- 成功响应：`{"run_id": "...", "title": "...", "verification": {...}}`；
- `GET /runs?limit=20` 返回最近运行摘要；
- `GET /runs/{run_id}` 返回完整 `ResearchPackage`；
- 空 prompt 返回 `422`；
- 不存在的 run 返回 `404`；
- `GET /health` 返回 `{"status": "ok", "version": "..."}`。

API 默认使用 Demo Provider。若环境变量配置了模型 Provider，则服务层沿用 `Settings.from_env()` 的选择逻辑。

## 错误处理

- 仓储在初始化时自动创建数据库和表。
- JSON 快照损坏时抛出明确的 `ValueError`，不返回静默空数据。
- API 将业务输入错误映射为 `422`，资源不存在映射为 `404`。
- Provider 网络异常不吞掉，由 FastAPI 返回 `500`，后续版本再增加错误分类和重试。

## 测试策略

- `tests/test_repository.py`：SQLite 初始化、保存、列表、读取、不存在记录。
- `tests/test_service.py`：服务层运行并持久化，读取出的快照与原始运行一致。
- `tests/test_api.py`：健康检查、创建运行、列表、详情、404、空 prompt。
- 保持现有 18 个测试全部通过。
- 增加 `python -m compileall` 和评测脚本作为发布前检查。

## 版本与文档

- `pyproject.toml` 升级到 `0.3.0`。
- `docs/CHANGELOG.md` 增加 v0.3.0。
- README 增加服务启动方式、接口示例、数据库说明和新的关键词：
  `FastAPI`、`SQLite`、`REST API`、`observability`、`run history`、`Agent platform`、`智能体平台`、`运行记录`。
