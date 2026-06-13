import sys
import os
import json
import difflib

# Add the body/mcp directory to sys.path to import blmcp
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../body/mcp")))

from blmcp.tools_helpers.rst_parse_docs import (
    data_dir,
    doctree_for_path,
    find_definition_in_doctree,
    list_doctree_definitions,
)

_DOC_EXT = ".rst"
_SUMMARY_CHAR_THRESHOLD = 32 * 1024

# ---------------------------------------------------------------------------
# Logic ported from get_python_api_docs.py

def _line_bounds_from_index(content: str, index: int) -> tuple[int, int]:
    beg = content.rfind("\n", 0, index) + 1
    end = content.find("\n", index)
    if end == -1:
        end = len(content)
    return beg, end

def _resolve_inside(api_path: str, stem: str) -> str | None:
    candidate = os.path.join(api_path, "{:s}{:s}".format(stem, _DOC_EXT))
    candidate_path = os.path.realpath(candidate)
    if not candidate_path.startswith(api_path + os.sep):
        return None
    if not os.path.isfile(candidate_path):
        return None
    return candidate_path

def _list_direct_child_identifiers(api_path: str, identifier: str) -> list[str]:
    prefix = identifier + "."
    expected_dot_count = prefix.count(".")
    children: list[str] = []
    for name in os.listdir(api_path):
        if not name.endswith(_DOC_EXT) or not name.startswith(prefix):
            continue
        stem = name[:-len(_DOC_EXT)]
        if stem.count(".") != expected_dot_count:
            continue
        children.append(stem)
    children.sort()
    return children

def _list_identifiers_containing_component(api_path: str, identifier: str) -> list[str]:
    buckets: list[set[tuple[str, ...]]] = []
    for name in os.listdir(api_path):
        if not name.endswith(_DOC_EXT):
            continue
        parts = tuple(name[:-len(_DOC_EXT)].split("."))
        if identifier not in parts:
            continue
        while len(buckets) <= len(parts):
            buckets.append(set())
        buckets[len(parts)].add(parts)
    for depth in range(len(buckets) - 1, 1, -1):
        buckets[depth] = {
            t for t in buckets[depth]
            if not any(t[:k] in buckets[k] for k in range(1, depth))
        }
    return sorted(".".join(t) for bucket in buckets for t in bucket)

def _summarize_rst_for_size(identifier: str, path: str, size: int) -> str:
    defs = list_doctree_definitions(doctree_for_path(path))
    header = (
        "File too large to inline ({:d} KB, threshold {:d} KB); "
        "definitions listed below. Query individual members as "
        "`{:s}.<name>`:\n\n"
    ).format(size // 1024, _SUMMARY_CHAR_THRESHOLD // 1024, identifier)
    if not defs:
        return header + "(no top-level definitions found)"
    return header + "\n".join("- {:s}".format(d) for d in defs)

def _list_top_level_modules(api_path: str) -> list[str]:
    names = os.listdir(api_path)
    rst_names = {name for name in names if name.endswith(_DOC_EXT)}
    firsts = sorted({n[:-len(_DOC_EXT)].split(".", 1)[0] for n in rst_names})
    modules: list[str] = []
    for first in firsts:
        prefix = first + "."
        root_rst = first + _DOC_EXT
        if any(name != root_rst and name.startswith(prefix) for name in rst_names):
            modules.append(first)
            continue
        if root_rst not in rst_names:
            continue
        root_path = os.path.join(api_path, root_rst)
        with open(root_path, encoding="utf-8", errors="replace") as fh:
            head = fh.read(4096)
        if head.startswith(".. module::") or "\n.. module::" in head:
            modules.append(first)
    return modules

def _filter_submodules_by_tail(submodules: list[str], tail: str) -> list[str]:
    tail_chars = set(tail)
    keep = [s for s in submodules if tail_chars.issubset(s.rsplit(".", 1)[-1])]
    keep.sort(key=lambda candidate: (-difflib.SequenceMatcher(a=tail, b=candidate.rsplit(".", 1)[-1]).ratio(), candidate))
    return keep

_LITERALINCLUDE_PREFIX = ".. literalinclude::"
_LINES_OPTION_PREFIX = ":lines:"

def _lines_option_after(content: str, start: int) -> str | None:
    pos = start
    while pos < len(content):
        line_end = content.find("\n", pos)
        if line_end == -1:
            line_end = len(content)
        stripped = content[pos:line_end].lstrip()
        if not stripped or not stripped.startswith(":"):
            return None
        if stripped.startswith(_LINES_OPTION_PREFIX):
            return stripped[len(_LINES_OPTION_PREFIX):].strip()
        pos = line_end + 1
    return None

def _apply_lines_spec(text: str, spec: str) -> str:
    source = text.splitlines(keepends=True)
    total = len(source)
    out: list[str] = []
    for part in spec.split(","):
        part = part.strip()
        if not part: continue
        lo, sep, hi = part.partition("-")
        try:
            lo_i = int(lo) if lo else 1
            hi_i = int(hi) if hi else total
        except ValueError: continue
        if not sep: hi_i = lo_i
        out.extend(source[max(0, lo_i - 1):hi_i])
    return "".join(out)

def _collect_examples(content: str, api_path: str) -> list[dict[str, str]]:
    examples: list[dict[str, str]] = []
    seen = set()
    pos = 0
    while (index := content.find(_LITERALINCLUDE_PREFIX, pos)) != -1:
        beg, end = _line_bounds_from_index(content, index)
        pos = end + 1
        if content[beg:index].strip(): continue
        tokens = content[index + len(_LITERALINCLUDE_PREFIX):end].split()
        if not tokens: continue
        filepath_rel = tokens[0].removeprefix("./")
        lines_spec = _lines_option_after(content, end + 1)
        target_path = os.path.realpath(os.path.join(api_path, filepath_rel))
        if not target_path.startswith(api_path + os.sep): continue
        dedup_key = (target_path, lines_spec)
        if dedup_key in seen: continue
        seen.add(dedup_key)
        try:
            with open(target_path, encoding="utf-8", errors="replace") as fh:
                example_content = fh.read()
        except OSError: continue
        if lines_spec is not None:
            example_content = _apply_lines_spec(example_content, lines_spec)
        examples.append({"path": filepath_rel, "content": example_content})
    return examples

def get_docs(identifier: str) -> dict:
    api_path = os.path.join(data_dir(), "api")
    if identifier == "*" or identifier.endswith(".*"):
        if identifier == "*":
            submodules = _list_top_level_modules(api_path)
        else:
            submodules = _list_direct_child_identifiers(api_path, identifier[:-2])
        return {"kind": "namespace", "found": True, "identifier": identifier, "submodules": submodules}

    if (candidate_path := _resolve_inside(api_path, identifier)) is not None:
        with open(candidate_path, encoding="utf-8", errors="replace") as fh:
            content = fh.read()
        if len(content) > _SUMMARY_CHAR_THRESHOLD:
            return {"kind": "exact", "found": True, "identifier": identifier, "content": _summarize_rst_for_size(identifier, candidate_path, len(content)), "examples": []}
        return {"kind": "exact", "found": True, "identifier": identifier, "content": content, "examples": _collect_examples(content, api_path)}

    if (submodules := _list_direct_child_identifiers(api_path, identifier)):
        return {"kind": "namespace", "found": True, "identifier": identifier, "submodules": submodules}

    parts = identifier.split(".")
    for strip_count in range(1, len(parts)):
        prefix = ".".join(parts[:-strip_count])
        tail = ".".join(parts[-strip_count:])
        prefix_path = _resolve_inside(api_path, prefix)
        if prefix_path is None: continue
        doctree = doctree_for_path(prefix_path)
        if (rendered := find_definition_in_doctree(doctree, tail)):
            return {"kind": "definition", "found": True, "identifier": identifier, "content": rendered, "examples": _collect_examples(rendered, api_path)}
        return {
            "kind": "partial", "found": False, "identifier": identifier, "parent": prefix, "available": list_doctree_definitions(doctree),
            "submodules": _filter_submodules_by_tail(_list_direct_child_identifiers(api_path, prefix), tail)
        }

    if (suggestions := _list_identifiers_containing_component(api_path, identifier)):
        return {"kind": "suggestions", "found": False, "identifier": identifier, "suggestions": suggestions}

    return {"kind": "missing", "found": False, "identifier": identifier}

if __name__ == "__main__":
    if len(sys.argv) > 1:
        print(json.dumps(get_docs(sys.argv[1])))
