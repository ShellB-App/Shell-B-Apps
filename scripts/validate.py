#!/usr/bin/env python3
"""Check every app in apps/<id>/ (app.json + index.html + assets) and build index.json.

An app is a self-contained Studio project: HTML, CSS, JavaScript and assets that run in Shell:B's sandboxed preview
frame with no network. This script checks what Shell:B's installer would refuse (file types, sizes, dotfiles, links
outside the folder) and the rule the preview enforces: nothing is loaded from the internet, only the folder's own
files and Shell:B's /vendor libraries. Standard library only; run from the repository root:

    python3 -I scripts/validate.py          # check + rebuild index.json
    python3 -I scripts/validate.py --check  # check only (CI); exits 1 on any error
"""
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
APPS = ROOT / "apps"
ID_RE = re.compile(r"^[a-z0-9][a-z0-9-]{1,39}$")
KINDS = ("dashboard", "website", "mobile", "deck", "print", "motion", "game", "design-system", "brand", "social", "email")
FILES = {".html", ".css", ".js", ".mjs", ".json", ".svg", ".png", ".jpg", ".jpeg", ".webp", ".gif", ".woff2", ".txt", ".md", ".csv", ".glb"}
PREVIEWS = (".jpg", ".jpeg", ".png", ".webp")
MAX_FILE, MAX_FOLDER = 2 * 2**20, 8 * 2**20
URL = re.compile(r"""(?:src|href|url\(|import\s*\(?|fetch\s*\(|new\s+WebSocket\s*\(|EventSource\s*\()\s*['"]?\s*(https?:)?//""", re.I)
VENDOR = ("tailwind.js", "chart.js", "mermaid.js", "marked.js", "three/", "draco/")


def _rel_ok(rel: str) -> bool:
    parts = rel.split("/")
    return all(p and not p.startswith(".") and p not in ("..",) for p in parts)


def check(path: Path) -> tuple[dict | None, list[str], list[str], list[str]]:
    """(app, errors, warnings, files)."""
    errors, warnings, files = [], [], []
    folder = path.name
    meta_path = path / "app.json"
    if not ID_RE.match(folder):
        errors.append(f"folder name {folder!r}: lowercase letters, digits and dashes only")
    try:
        spec = json.loads(meta_path.read_text())
    except (OSError, ValueError) as e:
        return None, [f"app.json: not valid JSON or missing: {e}"], [], []
    if not isinstance(spec, dict):
        return None, ["app.json must hold one object"], [], []
    if spec.get("id") not in (None, folder):
        errors.append(f"id {spec.get('id')!r} doesn't match the folder name {folder!r}")
    name = str(spec.get("name") or "").strip()
    if not name or len(name) > 40:
        errors.append("name: 1-40 characters")
    if not spec.get("blurb") or len(str(spec["blurb"])) > 200:
        errors.append("blurb: 1-200 characters")
    if spec.get("kind", "dashboard") not in KINDS:
        errors.append(f"kind must be one of {', '.join(KINDS)}")
    entry_file = str(spec.get("entry") or "index.html")
    if not (path / entry_file).is_file() or not _rel_ok(entry_file) or not entry_file.endswith(".html"):
        errors.append(f"entry {entry_file!r}: an .html file in the folder (index.html by default)")
    for key in ("author", "license"):
        if not spec.get(key):
            errors.append(f"{key} is required (license: an SPDX id such as MIT or CC0-1.0)")
    if not spec.get("version"):
        warnings.append("no version; start at \"1.0\"")
    tags = spec.get("tags", [])
    if not (isinstance(tags, list) and all(isinstance(t, str) and t for t in tags)):
        errors.append("tags: a list of short strings")
    for c in spec.get("credits") or []:
        if not isinstance(c, dict) or not c.get("what") or not c.get("license"):
            errors.append("credits: a list of {what, author?, license, url?}")

    total, preview = 0, None
    for p in sorted(path.rglob("*")):
        if p.is_dir():
            continue
        rel = str(p.relative_to(path))
        if p.is_symlink():
            errors.append(f"{rel}: symlinks are not allowed")
            continue
        if not _rel_ok(rel):
            errors.append(f"{rel}: dotfiles are not installed")
            continue
        if p.stem == "preview" and p.suffix.lower() in PREVIEWS and "/" not in rel:
            preview = rel
            if p.stat().st_size > 400 * 1024:
                errors.append("preview: at most 400 KB")
            continue
        if rel == "app.json":
            continue
        if p.suffix.lower() not in FILES:
            errors.append(f"{rel}: {p.suffix or 'no extension'} is not an allowed file type")
            continue
        size = p.stat().st_size
        total += size
        if size > MAX_FILE:
            errors.append(f"{rel}: larger than {MAX_FILE // 2**20} MB")
        files.append(rel)
        if p.suffix.lower() in (".html", ".css", ".js", ".mjs", ".svg"):
            text = p.read_text(errors="replace")
            for m in URL.finditer(text):
                line = text.count("\n", 0, m.start()) + 1
                errors.append(f"{rel}:{line}: loads something from the internet; bundle it in the folder or use /vendor")
            for m in re.finditer(r"""['"](/vendor/[^'"]+)['"]""", text):
                if not any(m.group(1)[8:].startswith(v) for v in VENDOR):
                    warnings.append(f"{rel}: {m.group(1)} is not one of Shell:B's vendored libraries ({', '.join(VENDOR)})")
            if p.suffix.lower() == ".html" and "<meta name=\"viewport\"" not in text and "<meta name='viewport'" not in text:
                warnings.append(f"{rel}: no viewport meta; it will look wrong on phones")
    if total > MAX_FOLDER:
        errors.append(f"the folder is larger than {MAX_FOLDER // 2**20} MB")
    if not preview:
        warnings.append("no preview.jpg/png; the gallery shows a blank tile")
    spec["_preview"], spec["_files"] = preview, files
    return spec, errors, warnings, files


def entry(folder: str, spec: dict) -> dict:
    return {"id": folder, "name": spec["name"], "blurb": spec["blurb"], "kind": spec.get("kind", "dashboard"),
            "entry": spec.get("entry", "index.html"), "author": spec["author"], "license": spec["license"],
            "version": spec.get("version", "1.0"), "tags": spec.get("tags", []), "path": f"apps/{folder}",
            "preview": f"apps/{folder}/{spec['_preview']}" if spec.get("_preview") else None, "files": spec["_files"]}


def main() -> int:
    check_only = "--check" in sys.argv
    items, failed = [], 0
    folders = sorted(p for p in APPS.iterdir() if p.is_dir() and not p.name.startswith("."))
    if not folders:
        print("no apps found under apps/<id>/")
        return 1
    for path in folders:
        spec, errors, warnings, files = check(path)
        for w in warnings:
            print(f"warning  {path.name}: {w}")
        for e in errors:
            print(f"ERROR    {path.name}: {e}")
        if errors or spec is None:
            failed += 1
            continue
        items.append(entry(path.name, spec))
        print(f"ok       {path.name} ({spec['name']}, {len(files)} files)")
    index = {"format": 1, "kind": "app", "items": sorted(items, key=lambda i: i["name"].lower())}
    if not check_only:
        (ROOT / "index.json").write_text(json.dumps(index, indent=1, ensure_ascii=False) + "\n")
        print(f"index.json: {len(items)} apps")
    elif (ROOT / "index.json").exists() and json.loads((ROOT / "index.json").read_text()) != index:
        print("ERROR    index.json is out of date: run scripts/validate.py and commit it")
        failed += 1
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
