from __future__ import annotations

import json
from pathlib import Path

from .domain import ResearchPackage


def render_markdown(package: ResearchPackage) -> str:
    blueprint = package.blueprint
    verification = package.verification
    lines = [
        f"# {blueprint.title}",
        "",
        f"> 研究需求：{package.brief.prompt}",
        "",
        "## 核心概念",
        blueprint.sections["核心概念"],
        "",
        "## 研究问题",
    ]
    lines.extend(f"- {question.text}" for question in package.questions)
    lines.extend(["", "## 证据与来源"])
    for source in package.sources:
        lines.extend(
            [
                f"### {source.title}",
                f"- URL: {source.url}",
                f"- 证据：{source.text}",
                "",
            ]
        )
    lines.extend(["## 资料支持的事实"])
    lines.extend(
        f"- [{item.status}] {item.claim}"
        for item in verification.items
    )
    lines.extend(["", "## 原创创作提案"])
    lines.extend(f"- {claim.text}" for claim in blueprint.proposals)
    lines.extend(
        [
            "",
            "## 其他设计",
            f"- 玩法钩子：{blueprint.sections['玩法钩子']}",
            f"- 叙事冲突：{blueprint.sections['叙事冲突']}",
            "",
            "## 执行轨迹",
        ]
    )
    lines.extend(f"- `{event.stage}`：{event.detail}" for event in package.trace)
    lines.extend(["", "## 工具调用轨迹"])
    if package.tool_trace:
        for event in package.tool_trace:
            lines.extend(
                [
                    f"### `{event.tool_name}` · {event.status}",
                    f"- 输入：`{json.dumps(event.arguments, ensure_ascii=False)}`",
                    f"- 结果：`{json.dumps(event.result, ensure_ascii=False)}`",
                    "",
                ]
            )
    else:
        lines.append("- 本次运行没有调用工具。")
    lines.extend(
        [
            "",
            "## 核验统计",
            f"- 已核验：{verification.checked_claims}",
            f"- 有证据支持：{verification.supported_claims}",
            f"- 待验证：{verification.unverified_claims}",
        ]
    )
    return "\n".join(lines) + "\n"


def write_reports(package: ResearchPackage, output_dir: str | Path) -> tuple[Path, Path]:
    directory = Path(output_dir)
    directory.mkdir(parents=True, exist_ok=True)
    markdown_path = directory / f"{package.brief.run_id}.md"
    json_path = directory / f"{package.brief.run_id}.json"
    markdown_path.write_text(render_markdown(package), encoding="utf-8")
    json_path.write_text(
        json.dumps(package.to_dict(), ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    return markdown_path, json_path
