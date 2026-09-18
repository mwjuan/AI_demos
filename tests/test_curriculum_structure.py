from __future__ import annotations

import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
STAGES = tuple(range(1, 7))
REQUIRED_HEADINGS = {
    "## 阶段定位",
    "## 前置知识",
    "## 课程列表",
    "## 必做实验",
    "## 主线项目增量",
    "## 闯关标准",
}
LINK_PATTERN = re.compile(r"\[[^]]+\]\(([^)]+)\)")
LESSON_PATTERN = re.compile(r"\bS(\d{2})-L(\d{2})\b")


def stage_readme(stage: int) -> Path:
    return ROOT / "curriculum" / f"stage-{stage:02d}" / "README.md"


def test_all_six_stage_readmes_exist_with_required_sections() -> None:
    for stage in STAGES:
        path = stage_readme(stage)
        assert path.is_file(), f"missing stage README: {path}"
        text = path.read_text(encoding="utf-8")
        assert REQUIRED_HEADINGS <= set(text.splitlines()), path
        assert f"S{stage:02d}-GATE" in text


def test_lesson_ids_are_unique_and_belong_to_their_stage() -> None:
    seen: set[str] = set()
    for stage in STAGES:
        text = stage_readme(stage).read_text(encoding="utf-8")
        ids = [match.group(0) for match in LESSON_PATTERN.finditer(text)]
        assert ids, f"stage {stage:02d} has no lesson IDs"
        for lesson_id in ids:
            assert lesson_id.startswith(f"S{stage:02d}-"), lesson_id
        unique_in_file = set(ids)
        assert not (seen & unique_in_file), f"duplicate lesson IDs: {seen & unique_in_file}"
        seen.update(unique_in_file)


def test_root_and_roadmap_link_to_every_stage() -> None:
    root_readme = (ROOT / "README.md").read_text(encoding="utf-8")
    roadmap = (ROOT / "notes" / "ROADMAP.md").read_text(encoding="utf-8")
    for stage in STAGES:
        directory = f"stage-{stage:02d}"
        assert directory in root_readme
        assert directory in roadmap


def test_local_markdown_links_resolve() -> None:
    documents = [
        ROOT / "README.md",
        ROOT / "notes" / "ROADMAP.md",
        ROOT / "curriculum" / "README.md",
        ROOT / "curriculum" / "COVERAGE.md",
        *(stage_readme(stage) for stage in STAGES),
    ]

    for document in documents:
        text = document.read_text(encoding="utf-8")
        for raw_target in LINK_PATTERN.findall(text):
            target = raw_target.split("#", 1)[0]
            if not target or "://" in target or target.startswith("mailto:"):
                continue
            resolved = (document.parent / target).resolve()
            assert resolved.exists(), f"broken link in {document}: {raw_target}"


def test_coverage_matrix_maps_every_stage_and_role_direction() -> None:
    text = (ROOT / "curriculum" / "COVERAGE.md").read_text(encoding="utf-8")
    for stage in STAGES:
        assert f"| {stage} " in text
        assert f"S{stage:02d}-L01" in text
    assert "能力产出" in text
    assert "岗位方向" in text
