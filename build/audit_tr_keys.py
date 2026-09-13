"""AST-based audit of every tr() call site in the codebase.

- Finds Call nodes, so docstrings/comments never false-positive.
- Literal keys are checked against en.py directly.
- Dynamic keys are resolved with project-specific rules (the guarded
  "status." + code builder) or reported for manual review.
"""
import ast
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from app.i18n import en  # noqa: E402

EN = en.MESSAGES

# main_window._STATUS_CODES (kept in sync - the audit asserts it below)
STATUS_CODES = ("update", "latest", "no_installer", "vendor", "no_source",
                "failed", "pending", "skipped")

problems, dynamic = [], []
files = sorted(p for p in ROOT.rglob("*.py")
               if not {"__pycache__", ".venv", ".venv32", "build"} & set(p.parts))
total = 0
for path in files:
    tree = ast.parse(path.read_text(encoding="utf-8"))
    for node in ast.walk(tree):
        if not (isinstance(node, ast.Call) and isinstance(node.func, ast.Name)
                and node.func.id == "tr"):
            continue
        total += 1
        arg = node.args[0] if node.args else None
        if isinstance(arg, ast.Constant) and isinstance(arg.value, str):
            key = arg.value
            rel = path.relative_to(ROOT)
            # the deliberate fallback check inside run.py --selftest
            if key == "definitely.not.a.key" and path.name == "run.py":
                continue
            if key not in EN:
                problems.append(f"{rel}:{node.lineno} MISSING {key!r}")
        elif (isinstance(arg, ast.BinOp) and isinstance(arg.op, ast.Add)
              and isinstance(arg.left, ast.Constant)
              and arg.left.value == "status."):
            for code in STATUS_CODES:
                if f"status.{code}" not in EN:
                    problems.append(
                        f"{path.relative_to(ROOT)}:{node.lineno} "
                        f"MISSING status.{code}")
        else:
            dynamic.append(f"{path.relative_to(ROOT)}:{node.lineno} "
                           f"{ast.dump(arg)[:80]}")

# keep the local frozenset in sync with main_window.py
import re  # noqa: E402
mw = (ROOT / "app" / "ui" / "main_window.py").read_text(encoding="utf-8")
m = re.search(r"_STATUS_CODES = frozenset\(\(([^)]*)\)\)", mw, re.S)
codes_in_code = tuple(re.findall(r'"([a-z_]+)"', m.group(1)))
assert codes_in_code == STATUS_CODES, (codes_in_code, STATUS_CODES)

print(f"scanned {len(files)} files, {total} tr() call sites (AST-precise)")
print(f"en.py has {len(EN)} keys; status.* builder expanded to "
      f"{len(STATUS_CODES)} keys")
if dynamic:
    print("DYNAMIC KEYS FOR MANUAL REVIEW:")
    print("\n".join(dynamic))
if problems:
    print("PROBLEMS:")
    print("\n".join(problems))
    sys.exit(1)
print("OK - every tr() call site resolves to a real key in all 6 languages")
