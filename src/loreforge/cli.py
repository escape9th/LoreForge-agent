from __future__ import annotations

import argparse
import json
from pathlib import Path

from .adapters import (
    CorpusSearchProvider,
    OpenAICompatibleModelProvider,
    OpenAICompatibleToolCallingProvider,
)
from .config import Settings
from .domain import ResearchPackage
from .repository import RunRepository
from .reporting import write_reports
from .service import RunService
from .workflow import run_research


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="loreforge",
        description="Evidence-backed creative research demo.",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)
    run_parser = subparsers.add_parser("run", help="运行一次研究创作任务")
    run_parser.add_argument("prompt", help="创作研究需求")
    run_parser.add_argument("--out", default="demo-output", help="输出目录")
    run_parser.add_argument(
        "--corpus",
        type=Path,
        help="自定义 JSON 资料库；不提供时使用内置 Demo 资料",
    )
    run_parser.add_argument(
        "--db",
        type=Path,
        help="SQLite 运行历史路径；提供后会保存本次运行",
    )
    run_parser.add_argument(
        "--max-tool-calls",
        type=int,
        default=None,
        help="单次运行最多调用工具的次数",
    )
    history_parser = subparsers.add_parser("history", help="查看最近的运行记录")
    history_parser.add_argument("--db", type=Path, required=True)
    history_parser.add_argument("--limit", type=int, default=20)
    show_parser = subparsers.add_parser("show", help="查看一条运行记录")
    show_parser.add_argument("run_id")
    show_parser.add_argument("--db", type=Path, required=True)
    inspect_parser = subparsers.add_parser("inspect", help="查看 JSON 运行摘要")
    inspect_parser.add_argument("file", type=Path)
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    if args.command == "run":
        settings = Settings.from_env()
        search = (
            CorpusSearchProvider.from_json(args.corpus)
            if args.corpus
            else None
        )
        model = (
            OpenAICompatibleModelProvider(
                endpoint=settings.model_endpoint,
                api_key=settings.model_api_key,
                model=settings.model_name,
            )
            if not settings.use_demo_model
            else None
        )
        tool_provider = (
            OpenAICompatibleToolCallingProvider(
                endpoint=settings.model_endpoint,
                api_key=settings.model_api_key,
                model=settings.model_name,
            )
            if not settings.use_demo_model
            else None
        )
        if args.db:
            package = RunService(RunRepository(args.db)).create_run(
                args.prompt,
                corpus=args.corpus,
                max_tool_calls=args.max_tool_calls,
            )
        else:
            package = run_research(
                args.prompt,
                search=search,
                model=model,
                tool_provider=tool_provider,
                max_tool_calls=args.max_tool_calls or settings.max_tool_calls,
            )
        markdown_path, json_path = write_reports(package, args.out)
        print(f"研究完成：{markdown_path}")
        print(f"运行记录：{json_path}")
        if args.db:
            print(f"数据库记录：{args.db}")
        return 0
    if args.command == "history":
        service = RunService(RunRepository(args.db))
        for summary in service.list_runs(args.limit):
            print(f"{summary.run_id} | {summary.title} | {summary.prompt}")
        return 0
    if args.command == "show":
        service = RunService(RunRepository(args.db))
        package: ResearchPackage | None = service.get_run(args.run_id)
        if package is None:
            print(f"未找到运行记录：{args.run_id}")
            return 1
        print(json.dumps(package.to_dict(), ensure_ascii=False, indent=2))
        return 0
    data = json.loads(args.file.read_text(encoding="utf-8"))
    print(f"需求：{data['brief']['prompt']}")
    print(f"来源：{len(data['sources'])}")
    print(f"事实核验：{data['verification']['supported_claims']}/"
          f"{data['verification']['checked_claims']} 条有证据支持")
    print(f"工具调用：{len(data.get('tool_trace', []))} 次")
    return 0
