import sys
import os
import json

# Add the body/mcp directory to sys.path to import blmcp
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../body/mcp")))

from blmcp.tools_helpers.rst_parse_docs import (
    data_dir,
    doctree_for_path,
    find_definition_in_doctree,
    list_doctree_definitions,
)
import difflib

_DOC_EXT = ".rst"
_SUMMARY_CHAR_THRESHOLD = 32 * 1024

# Re-implementing the core logic from get_python_api_docs.py to work standalone

def _resolve_inside(api_path: str, stem: str) -> str | None:
    candidate = os.path.join(api_path, "{:s}{:s}".format(stem, _DOC_EXT))
    candidate_path = os.path.realpath(candidate)
    if not candidate_path.startswith(api_path + os.sep):
        return None
    if not os.path.isfile(candidate_path):
        return None
    return candidate_path

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

def get_docs(identifier: str):
    api_path = os.path.join(data_dir(), "api")
    
    if identifier == "*":
        return {"kind": "namespace", "found": True, "identifier": identifier, "submodules": _list_top_level_modules(api_path)}

    if (candidate_path := _resolve_inside(api_path, identifier)) is not None:
        with open(candidate_path, encoding="utf-8", errors="replace") as fh:
            content = fh.read()
        return {"kind": "exact", "found": True, "identifier": identifier, "content": content}

    # Simplified intra-file lookup
    parts = identifier.split(".")
    for strip_count in range(1, len(parts)):
        prefix = ".".join(parts[:-strip_count])
        tail = ".".join(parts[-strip_count:])
        prefix_path = _resolve_inside(api_path, prefix)
        if prefix_path is None:
            continue
        doctree = doctree_for_path(prefix_path)
        if (rendered := find_definition_in_doctree(doctree, tail)):
            return {"kind": "definition", "found": True, "identifier": identifier, "content": rendered}
    
    return {"kind": "missing", "found": False, "identifier": identifier}

if __name__ == "__main__":
    if len(sys.argv) > 1:
        query = sys.argv[1]
        print(json.dumps(get_docs(query)))
