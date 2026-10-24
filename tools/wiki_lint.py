"""Mechanical lint for the wiki: the checks a script can do. The `wiki` skill adds the checks that need reading.

    python tools/wiki_lint.py                  # report
    python tools/wiki_lint.py --stale-days 90  # pages not verified in 90 days count as stale
    python tools/wiki_lint.py --strict         # also fail on broken links (for CI)

Checks: broken [[links]], orphan pages, pages missing from index.md, missing frontmatter, entity and concept pages
without sources, source pages whose raw file is missing, stale pages, drafts, and anything that looks like a secret.
Exit code 1 on secrets (and with --strict on broken links).
"""
import datetime as dt
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from scan_secrets import scan_file  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
WIKI = os.path.join(ROOT, "wiki")
SPECIAL = {"index", "log", "review-queue"}
LINK = re.compile(r"\[\[([^\]|#]+)(?:#[^\]|]*)?(?:\|[^\]]*)?\]\]")
CODE = re.compile(r"```.*?```|`[^`\n]*`", re.S)


def links(text):
    """Wikilinks outside code blocks and inline code (examples in code are not links)."""
    return LINK.findall(CODE.sub("", text))


def frontmatter(text):
    if not text.startswith("---"):
        return {}
    end = text.find("\n---", 3)
    if end < 0:
        return {}
    meta, key = {}, None
    for line in text[3:end].splitlines():
        if re.match(r"^\s+-\s+", line) and key:
            meta.setdefault(key, [])
            if isinstance(meta[key], list):
                meta[key].append(line.split("-", 1)[1].strip())
            continue
        m = re.match(r"^([A-Za-z_][\w-]*):\s*(.*)$", line)
        if not m:
            continue
        key, val = m.group(1), m.group(2).strip()
        if val.startswith("[") and val.endswith("]"):
            meta[key] = [v.strip().strip("'\"") for v in val[1:-1].split(",") if v.strip()]
        else:
            meta[key] = val.strip("'\"") if val else []
    return meta


def pages():
    out = {}
    for root, dirs, files in os.walk(WIKI):
        dirs[:] = [d for d in dirs if not d.startswith((".", "_"))]
        for f in files:
            if f.endswith(".md") and f != "README.md":
                path = os.path.join(root, f)
                with open(path, encoding="utf-8", errors="replace") as fh:
                    text = fh.read()
                out[f[:-3].lower()] = {"path": path, "text": text, "meta": frontmatter(text)}
    return out


def main(argv):
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    stale_days = int(argv[argv.index("--stale-days") + 1]) if "--stale-days" in argv else 180
    strict = "--strict" in argv
    if not os.path.isdir(WIKI):
        print("No wiki/ folder next to tools/.")
        return 1

    ps = pages()
    names = set(ps)
    for name, p in ps.items():
        for alias in p["meta"].get("aliases") or []:
            names.add(str(alias).lower())

    rel = lambda p: os.path.relpath(p, ROOT).replace("\\", "/")
    broken, inbound = [], {n: 0 for n in ps}
    for name, p in ps.items():
        for target in links(p["text"]):
            t = target.strip().lower()
            if t in ps:
                if t != name:
                    inbound[t] += 1
            elif t not in names:
                broken.append((rel(p["path"]), target.strip()))

    index_links = {t.strip().lower() for t in links(ps["index"]["text"])} if "index" in ps else set()
    orphans = sorted(n for n, c in inbound.items() if c == 0 and n not in SPECIAL)
    not_in_index = sorted(n for n in ps if n not in SPECIAL and n not in index_links)

    missing_meta, no_sources, missing_raw, stale, drafts = [], [], [], [], []
    today = dt.date.today()
    for name, p in sorted(ps.items()):
        m = p["meta"]
        if name in SPECIAL:
            continue
        lack = [k for k in ("type", "status", "last_verified") if not m.get(k)]
        if lack:
            missing_meta.append((name, ", ".join(lack)))
        if m.get("type") in ("entity", "concept", "decision") and not m.get("sources"):
            no_sources.append(name)
        if m.get("type") == "source" and m.get("file") and not os.path.exists(os.path.join(ROOT, m["file"])):
            missing_raw.append((name, m["file"]))
        try:
            if today - dt.date.fromisoformat(str(m.get("last_verified"))) > dt.timedelta(days=stale_days):
                stale.append((name, m["last_verified"]))
        except ValueError:
            pass
        if m.get("status") == "draft":
            drafts.append(name)

    secrets = [hit for p in ps.values() for hit in scan_file(p["path"])]

    def section(title, items, fmt=str):
        print(f"\n## {title} ({len(items)})")
        for it in items[:50]:
            print(f"- {fmt(it)}")
        if len(items) > 50:
            print(f"- ... and {len(items) - 50} more")

    print(f"# Wiki lint · {today.isoformat()} · {len(ps)} pages")
    section("Possible secrets", secrets, lambda h: f"{rel(h[0])}:{h[1]} {h[2]} ({h[3]})")
    section("Broken links", broken, lambda b: f"{b[0]} → [[{b[1]}]]")
    section("Orphan pages (nothing links here)", orphans)
    section("Not in index.md", not_in_index)
    section("Missing frontmatter", missing_meta, lambda x: f"{x[0]}: {x[1]}")
    section("Entity, concept or decision without sources", no_sources)
    section("Source page whose raw file is missing", missing_raw, lambda x: f"{x[0]}: {x[1]}")
    section(f"Stale (not verified in {stale_days} days)", stale, lambda x: f"{x[0]}: {x[1]}")
    section("Drafts waiting for review", drafts)

    if secrets:
        print("\nFAIL: possible secrets in the wiki. Remove them before committing.")
        return 1
    if strict and broken:
        print("\nFAIL: broken links (--strict).")
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
