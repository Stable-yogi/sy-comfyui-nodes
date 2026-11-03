import json
import os
import sys
import tempfile

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "nodes"))
import sy_workflow_check as m


def _refused(fn, *args, part=""):
    try:
        fn(*args)
    except ValueError as e:
        assert part in str(e), str(e)
        return
    raise SystemExit("expected ValueError")


def run():
    n = 0
    normal = json.dumps({"nodes": [
        {"id": 1, "type": "CheckpointLoaderSimple", "widgets_values": ["Models/Big.SAFETENSORS"]},
        {"id": 2, "type": "FancyNode", "widgets_values": [1, "x"]},
        {"id": 3, "type": "FancyNode", "widgets_values": []},
        {"id": 4, "type": "Note", "widgets_values": ["see thing.ckpt"]},
        {"id": 5, "type": "Reroute"},
    ]})
    report, mn, mm, count = m.check_workflow(normal, ["CheckpointLoaderSimple"], ["other.safetensors"])
    assert mn == "FancyNode" and mm == "Models/Big.SAFETENSORS" and count == 2
    n += 1
    assert report.startswith("5 nodes read. 1 node types missing, 1 model files missing.")
    n += 1
    assert "FancyNode (used by 2 nodes)" in report and "install the pack" in report
    n += 1
    assert "typed inside a text prompt" in report
    n += 1
    # base name match, slash styles, case
    r = m.check_workflow(normal, ["CheckpointLoaderSimple", "FancyNode"], ["sub\\big.safetensors"])
    assert r[3] == 0 and r[0].startswith("All good:")
    n += 2
    # API format
    api = json.dumps({"1": {"class_type": "KSampler", "inputs": {"model": ["2", 0], "sampler_name": "euler"}},
                      "2": {"class_type": "UNETLoader", "inputs": {"unet_name": "flux.gguf"}}})
    nodes = m.parse_workflow(api)
    assert [x["type"] for x in nodes] == ["KSampler", "UNETLoader"]
    n += 1
    assert m.model_candidates(nodes) == ["flux.gguf"]
    n += 1
    r = m.check_workflow(api, ["KSampler"], [])
    assert r[1] == "UNETLoader" and r[2] == "flux.gguf" and r[3] == 2
    n += 1
    # subgraph id is not missing, nodes inside subgraphs are read
    sg = json.dumps({"nodes": [{"type": "abc-123", "widgets_values": []}],
                     "definitions": {"subgraphs": [{"id": "abc-123", "nodes": [
                         {"type": "VAELoader", "widgets_values": ["ae.sft"]}]}]}})
    r = m.check_workflow(sg, ["VAELoader"], ["ae.sft"])
    assert r[1] == "" and r[3] == 0
    n += 1
    assert m.workflow_subgraph_ids(sg) == ["abc-123"]
    n += 1
    assert len(m.parse_workflow(sg)) == 2
    n += 1
    # front-end only types are skipped
    skipped = json.dumps({"nodes": [{"type": t} for t in ("Note", "MarkdownNote", "Reroute", "PrimitiveNode", "workflow/My Group")]})
    assert m.check_workflow(skipped, [], [])[3] == 0
    n += 1
    # widgets as dict
    wd = json.dumps({"nodes": [{"type": "X", "widgets_values": {"model": "a.pth", "n": 3}}]})
    assert m.model_candidates(m.parse_workflow(wd)) == ["a.pth"]
    n += 1
    # candidate filters
    cand = [{"type": "X", "widgets": ["a\nb.pt", "z" * 301 + ".pt", "ok.PT", "plain.txt", 5, "ok.PT"]}]
    assert m.model_candidates(cand) == ["ok.PT"]
    n += 1
    for ext in m.MODEL_ENDINGS:
        assert m.model_candidates([{"type": "X", "widgets": ["f" + ext]}]) == ["f" + ext]
    n += 1
    # missing functions
    assert m.find_missing_nodes(["B", "A", "B", "C"], ["C"]) == ["A", "B"]
    n += 1
    assert m.find_missing_models(["x/y.pt"], ["Y.PT"]) == []
    n += 1
    assert m.find_missing_models(["y.pt"], ["a/b.pt"]) == ["y.pt"]
    n += 1
    assert "2 folders could not be read" in m.check_workflow(skipped, [], [], 2)[0]
    n += 1
    # refusals
    _refused(m.parse_workflow, "", part="empty")
    _refused(m.parse_workflow, "   ", part="empty")
    n += 2
    for bad in ("not json", "[1,2]", '{"a": 1}'):
        _refused(m.parse_workflow, bad, part="This does not look like a ComfyUI workflow")
        n += 1
    # file reading
    with tempfile.TemporaryDirectory() as d:
        with open(os.path.join(d, "w.json"), "w", encoding="utf-8") as f:
            f.write(api)
        assert m.read_workflow_file("w.json", d) == api
        n += 1
        _refused(m.read_workflow_file, "../w.json", d, part="..")
        _refused(m.read_workflow_file, os.path.join(d, "w.json"), d, part="full path")
        _refused(m.read_workflow_file, "/etc/w.json", d, part="full path")
        _refused(m.read_workflow_file, "", d, part="workflow_file")
        _refused(m.read_workflow_file, "missing.json", d, part="Cannot read")
        n += 5
    # node shape
    assert m.SYWorkflowCheck.RETURN_TYPES == ("STRING", "STRING", "STRING", "INT")
    assert m.NODE_DISPLAY_NAME_MAPPINGS["SYWorkflowCheck"] == "Workflow Check SY"
    n += 2
    return n
