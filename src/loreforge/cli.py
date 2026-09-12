from __future__ import annotations

import argparse
import json
from pathlib import Path

from .adapters import CorpusSearchProvider, OpenAICompatibleModelProvider
from .config import Settings
from .reporting import write_reports
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
        package = run_research(args.prompt, search=search, model=model)
        markdown_path, json_path = write_reports(package, args.out)
        print(f"研究完成：{markdown_path}")
        print(f"运行记录：{json_path}")
        return 0
    data = json.loads(args.file.read_text(encoding="utf-8"))
    print(f"需求：{data['brief']['prompt']}")
    print(f"来源：{len(data['sources'])}")
    print(f"事实核验：{data['verification']['supported_claims']}/"
          f"{data['verification']['checked_claims']} 条有证据支持")
    return 0
