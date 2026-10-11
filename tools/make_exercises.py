"""Builds src/exercises from src/solutions: same signatures and docstrings, empty bodies.

    python tools/make_exercises.py           rewrite src/exercises (only files you haven't edited are safe!)
    python tools/make_exercises.py --check   fail if src/exercises is out of date (CI runs this)
    python tools/make_exercises.py --new     only create exercise files that don't exist yet

Every public function and method becomes `raise NotImplementedError("Your turn: write this one")`.
Imports, constants and private helpers (names starting with "_") are copied as they are.
"""

import ast
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SOLUTIONS = ROOT / "src" / "solutions"
EXERCISES = ROOT / "src" / "exercises"
STUB = 'raise NotImplementedError("Your turn: write this one")'


def _stub_function(node, lines, indent):
    """Keep the decorators, signature and docstring of `node`; replace the body with STUB."""
    start = (node.decorator_list[0].lineno if node.decorator_list else node.lineno) - 1
    body0 = node.body[0]
    has_doc = isinstance(body0, ast.Expr) and isinstance(body0.value, ast.Constant) and isinstance(body0.value.value, str)
    keep_to = body0.end_lineno if has_doc else node.body[0].lineno - 1
    out = lines[start:keep_to]
    out.append(" " * (indent + 4) + STUB)
    return out


def _stub_class(node, lines):
    out = lines[(node.decorator_list[0].lineno if node.decorator_list else node.lineno) - 1:node.body[0].lineno - 1]
    for i, item in enumerate(node.body):
        if i:
            out.append("")
        if isinstance(item, (ast.FunctionDef, ast.AsyncFunctionDef)):
            out += _stub_function(item, lines, item.col_offset)
        else:
            out += lines[item.lineno - 1:item.end_lineno]
    return out


def exercise_source(solution_path: Path, topic: str) -> str:
    text = solution_path.read_text()
    lines = text.splitlines()
    tree = ast.parse(text)
    kind = solution_path.stem
    out = [
        f"# Exercise file. Fill in each function, then run: sh run-tests.sh --mine -k {topic}",
        f"# Stuck? Ask Claude for a hint (see claude/PROMPTS.md), or read src/solutions/{topic}/{kind}.py",
        "",
    ]
    prev_end = None
    for node in tree.body:
        start = (node.decorator_list[0].lineno if getattr(node, "decorator_list", None) else node.lineno)
        if prev_end is not None:
            gap = start - prev_end - 1
            out += [""] * min(gap, 2)
        public = not getattr(node, "name", "_").startswith("_")
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) and public:
            out += _stub_function(node, lines, 0)
        elif isinstance(node, ast.ClassDef) and public:
            out += _stub_class(node, lines)
        else:
            out += lines[start - 1:node.end_lineno]
        prev_end = node.end_lineno
    return "\n".join(out) + "\n"


def expected_files():
    files = {EXERCISES / "__init__.py": ""}
    for sol in sorted(SOLUTIONS.glob("*/*.py")):
        topic = sol.parent.name
        target = EXERCISES / topic / sol.name
        files[target] = "" if sol.name == "__init__.py" else exercise_source(sol, topic)
    return files


def main(argv):
    files = expected_files()
    if "--check" in argv:
        stale = [p for p, src in files.items() if not p.exists() or p.read_text() != src]
        if stale:
            print("src/exercises is out of date. Run: python tools/make_exercises.py")
            for p in stale:
                print("  ", p.relative_to(ROOT))
            return 1
        print(f"src/exercises is up to date ({len(files)} files)")
        return 0
    only_new = "--new" in argv
    for path, src in files.items():
        if only_new and path.exists():
            continue
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(src)
    print(f"wrote {len(files)} files under src/exercises")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
