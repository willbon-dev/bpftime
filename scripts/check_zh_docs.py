#!/usr/bin/env python3
from __future__ import annotations

import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def all_source_docs() -> list[Path]:
    docs: list[Path] = []
    for path in ROOT.rglob("*"):
        if not path.is_file():
            continue
        name = path.name.lower()
        if path.name.endswith("_zh.md"):
            continue
        if path.suffix.lower() != ".md":
            continue
        if name.startswith("readme") or "readme" in name or path.name.endswith(".md"):
            docs.append(path)
    return sorted(docs)


def zh_path(src: Path) -> Path:
    return src.with_name(f"{src.stem}_zh.md")


def extract_relative_md_links(text: str) -> list[str]:
    pattern = re.compile(r"(?<!!)\[[^\]]*\]\(([^)#]+\.md(?:#[^)]+)?)\)")
    return pattern.findall(text)


def main() -> int:
    docs = all_source_docs()
    missing = [p for p in docs if not zh_path(p).exists()]

    print(f"source_docs={len(docs)}")
    print(f"missing_zh={len(missing)}")
    for path in missing[:200]:
        print(f"MISSING {path.relative_to(ROOT)} -> {zh_path(path).relative_to(ROOT)}")

    checked = 0
    bad_links = 0
    for src in docs:
        zh = zh_path(src)
        if not zh.exists():
            continue
        text = zh.read_text(encoding="utf-8", errors="ignore")
        for target in extract_relative_md_links(text):
            checked += 1
            base = target.split("#", 1)[0]
            if base.endswith("_zh.md"):
                continue
            target_src = (src.parent / base).resolve()
            if target_src.exists() and zh_path(target_src).exists():
                bad_links += 1
                print(
                    f"LINK {zh.relative_to(ROOT)} still points to {target}; "
                    f"expected *_zh.md target is available"
                )
    print(f"checked_relative_md_links={checked}")
    print(f"links_not_rewritten_when_zh_exists={bad_links}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
