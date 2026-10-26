"""Find things that look like secrets in text files.

Used by tools/wiki_lint.py, by the Claude Code hook in .claude/hooks/guard_secrets.py, and as a git pre-commit check.

    python tools/scan_secrets.py                 # scan wiki/
    python tools/scan_secrets.py raw notes.md    # scan these files or folders
    python tools/scan_secrets.py --staged        # what is staged for commit: names and contents (pre-commit hook)

Exit code 1 when something is found. Values are masked in the output, so the report itself is safe to paste.
A line that contains `secret-scan: ignore` is skipped; use it for documentation that shows a fake example.
Add your own patterns to PATTERNS, for example the way your team names AES keys in C sources.
With --staged, file names are also checked against .claude/hooks/secret_paths.txt, the list the Claude Code hook uses.
"""
import fnmatch
import os
import re
import subprocess
import sys

PATTERNS = [
    ("private key block", re.compile(r"-----BEGIN (?:RSA |EC |DSA |OPENSSH |ENCRYPTED |PGP )?PRIVATE KEY(?: BLOCK)?-----")),
    ("AWS access key", re.compile(r"\bAKIA[0-9A-Z]{16}\b")),
    ("GitHub token", re.compile(r"\bgh[pousr]_[A-Za-z0-9]{36,}\b")),
    ("Anthropic API key", re.compile(r"\bsk-ant-[A-Za-z0-9_-]{20,}")),
    ("API key (sk-)", re.compile(r"\bsk-[A-Za-z0-9]{32,}\b")),
    ("Slack token", re.compile(r"\bxox[abposr]-[A-Za-z0-9-]{10,}")),
    # Key words count as words inside names too: DEVICE_AES_KEY, aes_key_iv, BootKey. Hence the look-arounds
    # instead of \b, which would treat the underscore in DEVICE_AES_KEY as part of one long word.
    ("password or token assignment", re.compile(
        r"(?i)(?<![a-z0-9])(?:password|passwd|pwd|secret|token|api[_-]?key|aes[_-]?key|private[_-]?key|client[_-]?secret)"
        r"(?![a-z0-9])\s*[:=]\s*['\"]?(?!<|\$\{|%|\*{3})[^\s'\"<>]{8,}")),
    ("hex key near a key word", re.compile(
        r"(?i)(?:aes|key|iv|nonce|secret|cmac|hmac)(?![a-z])[^\n]{0,40}?"
        r"(?<![0-9a-f])(?:[0-9a-f]{32}|[0-9a-f]{48}|[0-9a-f]{64})(?![0-9a-f])")),
    ("byte array near a key word", re.compile(
        r"(?i)(?<![a-z0-9])(?:aes|key|iv|secret)[a-z0-9_]*\s*(?:\[[^\]]*\])?\s*=\s*\{\s*(?:0x[0-9a-f]{1,2}\s*,\s*){15,}")),
    ("connection string with password", re.compile(r"(?i)\b(?:password|pwd)=[^;\s]{6,};")),
]

TEXT_EXT = {".md", ".txt", ".c", ".h", ".cpp", ".hpp", ".cc", ".cs", ".py", ".js", ".ts", ".json", ".yaml", ".yml",
            ".toml", ".ini", ".cfg", ".conf", ".xml", ".sh", ".ps1", ".bat", ".cmake", ".env", ""}
IGNORE = "secret-scan: ignore"


def mask(s):
    s = s.strip()
    return s[:4] + "..." + s[-2:] if len(s) > 10 else "..."


# Strict mode, for wiki pages: a bare 128-, 192- or 256-bit hex value is treated as a key even without a key word
# nearby. In code that would flag hashes and test vectors; in a wiki it should never appear. A git commit (40 hex)
# does not match. A checksum you do want on a page gets `secret-scan: ignore` on its line.
STRICT_PATTERNS = PATTERNS + [
    ("bare hex key", re.compile(r"(?<![0-9a-fA-F])(?:[0-9a-fA-F]{32}|[0-9a-fA-F]{48}|[0-9a-fA-F]{64})(?![0-9a-fA-F])")),
]


def is_wiki_path(path):
    """True for files under a wiki/ folder, which get the strict checks."""
    return "wiki" in [p for p in path.replace("\\", "/").lower().split("/")[:-1]]


def scan_text(text, name="<text>", strict=False):
    """Return a list of (name, line_number, rule, masked_match)."""
    found = []
    for n, line in enumerate(text.splitlines(), 1):
        if IGNORE in line:
            continue
        for rule, rx in (STRICT_PATTERNS if strict else PATTERNS):
            m = rx.search(line)
            if m:
                found.append((name, n, rule, mask(m.group(0))))
                break
    return found


def scan_file(path, strict=None):
    if os.path.splitext(path)[1].lower() not in TEXT_EXT:
        return []
    try:
        with open(path, encoding="utf-8", errors="replace") as f:
            return scan_text(f.read(), path, is_wiki_path(path) if strict is None else strict)
    except OSError:
        return []


def walk(paths):
    for p in paths:
        if os.path.isdir(p):
            for root, dirs, files in os.walk(p):
                dirs[:] = [d for d in dirs if d not in {".git", "node_modules", ".venv", "__pycache__"}]
                for f in files:
                    yield os.path.join(root, f)
        elif os.path.isfile(p):
            yield p


def protected_names(paths):
    """Files whose name matches .claude/hooks/secret_paths.txt, the same list the Claude Code hook uses."""
    root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    try:
        with open(os.path.join(root, ".claude", "hooks", "secret_paths.txt"), encoding="utf-8") as f:
            globs = [l.strip() for l in f if l.strip() and not l.lstrip().startswith("#")]
    except OSError:
        return []
    allow = [g[1:].lower() for g in globs if g.startswith("!")]
    deny = [g.lower().strip("/") for g in globs if not g.startswith("!")]
    hits = []
    for p in paths:
        parts = p.replace("\\", "/").lower().split("/")
        base = parts[-1]
        if any(fnmatch.fnmatch(base, a) for a in allow):
            continue
        for g in deny:
            if ("/" in g and g.split("/", 1)[0] in parts[:-1]) or ("/" not in g and fnmatch.fnmatch(base, g)):
                hits.append((p, g))
                break
    return hits


def staged_files():
    out = subprocess.run(["git", "diff", "--cached", "--name-only", "--diff-filter=ACM"],
                         capture_output=True, text=True, check=False).stdout
    return [f for f in out.splitlines() if f]


def main(argv):
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    staged = "--staged" in argv
    targets = staged_files() if staged else ([a for a in argv if not a.startswith("--")] or ["wiki"])
    names = protected_names(targets) if staged else []
    for path, glob in names:
        print(f"{path}: protected file name (pattern '{glob}'), never commit it")
    found = [hit for f in walk(targets) for hit in scan_file(f)]
    for name, n, rule, masked in found:
        print(f"{name}:{n}: possible {rule} ({masked})")
    if found or names:
        print(f"\n{len(found) + len(names)} problem(s). Remove them, or mark a fake example with '{IGNORE}'.")
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
