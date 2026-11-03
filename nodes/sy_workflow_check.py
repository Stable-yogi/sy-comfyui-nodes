"""Workflow Check SY: reads a workflow text and lists the nodes and model files this PC does not have."""
import json

try:
    from ._sy_common import category, register, safe_join
except ImportError:  # run as a plain file by the selftest
    from _sy_common import category, register, safe_join

MODEL_ENDINGS = (".safetensors", ".ckpt", ".pt", ".pth", ".gguf", ".bin", ".onnx", ".sft", ".pkl", ".vae")
SKIP_TYPES = ("Note", "MarkdownNote", "Reroute", "PrimitiveNode")
MAX_STRING = 300
NOT_A_WORKFLOW = "This does not look like a ComfyUI workflow: %s"


def _flatten_strings(value, out):
    """Collect plain strings from a list of widget values, one level of nesting deep."""
    if isinstance(value, str):
        out.append(value)
    elif isinstance(value, dict):
        out.extend(v for v in value.values() if isinstance(v, str))
    elif isinstance(value, (list, tuple)):
        for v in value:
            if isinstance(v, str):
                out.append(v)
            elif isinstance(v, dict):
                out.extend(x for x in v.values() if isinstance(x, str))
    return out


def _widgets_of(raw):
    """Turn widgets_values (a list, or a dict in some nodes) into a list."""
    if isinstance(raw, dict):
        return list(raw.values())
    if isinstance(raw, list):
        return list(raw)
    return []


def _node_entry(n):
    return {"type": n["type"], "widgets": _widgets_of(n.get("widgets_values"))}


def _read(text):
    """Returns (nodes, subgraph_ids). Raises ValueError with a plain message."""
    if not isinstance(text, str) or not text.strip():
        raise ValueError("The workflow text is empty: paste the text of a saved workflow, or give a file name.")
    try:
        data = json.loads(text)
    except ValueError as e:
        raise ValueError(NOT_A_WORKFLOW % ("the text is not valid JSON (%s)" % e))
    if not isinstance(data, dict):
        raise ValueError(NOT_A_WORKFLOW % "the top level is not an object")
    nodes = []
    sub_ids = set()
    if isinstance(data.get("nodes"), list):
        for n in data["nodes"]:
            if isinstance(n, dict) and isinstance(n.get("type"), str):
                nodes.append(_node_entry(n))
        defs = data.get("definitions")
        subs = defs.get("subgraphs") if isinstance(defs, dict) else None
        if isinstance(subs, list):
            for sg in subs:
                if not isinstance(sg, dict):
                    continue
                if isinstance(sg.get("id"), str):
                    sub_ids.add(sg["id"])
                for n in sg.get("nodes") or []:
                    if isinstance(n, dict) and isinstance(n.get("type"), str):
                        nodes.append(_node_entry(n))
        return nodes, sub_ids
    api = [v for v in data.values() if isinstance(v, dict) and isinstance(v.get("class_type"), str)]
    if api:
        for v in api:
            inputs = v.get("inputs")
            widgets = [x for x in inputs.values() if isinstance(x, str)] if isinstance(inputs, dict) else []
            nodes.append({"type": v["class_type"], "widgets": widgets})
        return nodes, sub_ids
    if "nodes" in data:
        raise ValueError(NOT_A_WORKFLOW % "'nodes' is not a list")
    raise ValueError(NOT_A_WORKFLOW % "it has neither a 'nodes' list nor API-format entries with 'class_type'")


def parse_workflow(text):
    """Pure function. Returns a list of {"type": str, "widgets": list} from either workflow format."""
    return _read(text)[0]


def workflow_subgraph_ids(text):
    """Pure function. Returns the sorted ids of the subgraphs defined inside the workflow."""
    return sorted(_read(text)[1])


def _is_skipped(node_type):
    return node_type in SKIP_TYPES or node_type.startswith("workflow/")


def count_types(nodes, subgraph_ids=()):
    """Pure function. {type: how many nodes} for the types that must be installed."""
    counts = {}
    ids = set(subgraph_ids)
    for n in nodes:
        t = n["type"]
        if _is_skipped(t) or t in ids:
            continue
        counts[t] = counts.get(t, 0) + 1
    return counts


def find_missing_nodes(types, installed):
    """Pure function. Sorted unique list of types that are not installed."""
    have = set(installed)
    return sorted({t for t in types if t not in have})


def model_candidates(nodes):
    """Pure function. Sorted unique widget strings that look like a model file name."""
    found = set()
    for n in nodes:
        if _is_skipped(n["type"]):  # notes and reroutes only carry text, not loaders
            continue
        for s in _flatten_strings(n.get("widgets") or [], []):
            if len(s) > MAX_STRING or "\n" in s or "\r" in s:
                continue
            if s.strip().lower().endswith(MODEL_ENDINGS):
                found.add(s.strip())
    return sorted(found)


def _norm(path):
    return str(path).replace("\\", "/").strip().lower()


def _base(path):
    return _norm(path).rsplit("/", 1)[-1]


def find_missing_models(candidates, installed_files):
    """Pure function. Candidates with no installed file of the same path or the same base name."""
    full = set()
    bases = set()
    for f in installed_files:
        full.add(_norm(f))
        bases.add(_base(f))
    return sorted(c for c in candidates if _norm(c) not in full and _base(c) not in bases)


def build_report(node_count, missing_counts, missing_models, unreadable_folders=0):
    """Pure function. Plain-words report."""
    nm, mm = len(missing_counts), len(missing_models)
    if nm == 0 and mm == 0:
        lines = ["All good: %d nodes read. 0 node types missing, 0 model files missing." % node_count]
    else:
        lines = ["%d nodes read. %d node types missing, %d model files missing." % (node_count, nm, mm)]
    if nm:
        lines.append("")
        lines.append("Missing node types:")
        for t in sorted(missing_counts):
            c = missing_counts[t]
            lines.append("  %s (used by %d node%s)" % (t, c, "" if c == 1 else "s"))
        lines.append("Hint: install the pack that provides it, or replace the node.")
    if mm:
        lines.append("")
        lines.append("Missing model files:")
        for name in missing_models:
            lines.append("  " + name)
    if unreadable_folders:
        lines.append("")
        lines.append("%d folders could not be read, so models in them may be reported as missing." % unreadable_folders)
    lines.append("")
    lines.append("Note: model names that are only typed inside a text prompt are not checked.")
    return "\n".join(lines)


def check_workflow(text, installed_nodes, installed_files, unreadable_folders=0):
    """Pure function. Returns (report, missing_nodes_text, missing_models_text, problem_count)."""
    nodes, sub_ids = _read(text)
    counts = count_types(nodes, sub_ids)
    missing_types = find_missing_nodes(counts.keys(), installed_nodes)
    missing_counts = {t: counts[t] for t in missing_types}
    missing_models = find_missing_models(model_candidates(nodes), installed_files)
    report = build_report(len(nodes), missing_counts, missing_models, unreadable_folders)
    return report, "\n".join(missing_types), "\n".join(missing_models), len(missing_types) + len(missing_models)


def read_workflow_file(name, input_dir):
    """Read a workflow file by a relative name inside input_dir. Refuses '..' and absolute paths."""
    name = "" if name is None else str(name).strip()
    if not name:
        raise ValueError("Give a workflow_file name, or paste the workflow text into workflow_json.")
    parts = name.replace("\\", "/").split("/")
    if ".." in parts:
        raise ValueError("workflow_file must not contain '..': use a file name inside the input folder.")
    if name.startswith(("/", "\\")) or (len(name) > 1 and name[1] == ":"):
        raise ValueError("workflow_file must be a name inside the input folder, not a full path: %r" % name)
    path = safe_join(input_dir, name)
    try:
        with open(path, "r", encoding="utf-8-sig") as f:
            return f.read()
    except OSError as e:
        raise ValueError("Cannot read the workflow file %r from the input folder: %s" % (name, e.strerror or e))


class SYWorkflowCheck:
    DESCRIPTION = ("Paste a workflow before you load it. Lists the node types and model files that are missing on this PC. "
                   "It never loads or runs anything.")
    CATEGORY = category("Utility")
    FUNCTION = "run"
    RETURN_TYPES = ("STRING", "STRING", "STRING", "INT")
    RETURN_NAMES = ("report", "missing_nodes", "missing_models", "problem_count")

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "workflow_json": ("STRING", {"default": "", "multiline": True, "tooltip": "The text of a workflow saved from ComfyUI (normal or API format)."}),
            },
            "optional": {
                "workflow_file": ("STRING", {"default": "", "multiline": False, "tooltip": "A file name in the input folder. Used only when the text box is empty."}),
            },
        }

    def run(self, workflow_json, workflow_file=""):
        try:
            import folder_paths  # inside ComfyUI only
            import nodes as comfy_nodes
        except ImportError:
            raise ValueError("Workflow Check SY reads ComfyUI's own lists of installed nodes and models, so it only runs inside ComfyUI.")
        text = workflow_json
        if not str(text or "").strip():
            text = read_workflow_file(workflow_file, folder_paths.get_input_directory())
        installed_nodes = sorted(comfy_nodes.NODE_CLASS_MAPPINGS.keys())
        files = []
        unreadable = 0
        for folder in list(folder_paths.folder_names_and_paths.keys()):
            try:
                files.extend(folder_paths.get_filename_list(folder))
            except Exception:
                unreadable += 1
        return check_workflow(text, installed_nodes, files, unreadable)


NODE_CLASS_MAPPINGS = {}
NODE_DISPLAY_NAME_MAPPINGS = {}
register(NODE_CLASS_MAPPINGS, NODE_DISPLAY_NAME_MAPPINGS, "WorkflowCheck", SYWorkflowCheck)
NODE_DISPLAY_NAME_MAPPINGS["SYWorkflowCheck"] = "Workflow Check SY"
