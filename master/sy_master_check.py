"""SY Master Check: runs the SY Master Test prompt on a ComfyUI server and tells which SY node works and which one does not.

ComfyUI stops a prompt at the first broken node. So this script sends the prompt, takes the broken node and everything
behind it out, sends it again, and repeats. Nodes that already passed come back from ComfyUI's cache, so each round is fast.

Use:  py -3.12 sy_master_check.py --port 8188 [--prompt master_prompt.json] [--report report.md]
Reads only through the ComfyUI HTTP API on 127.0.0.1. Writes nothing in ComfyUI except what a normal run writes.
"""
import argparse
import json
import sys
import time
import urllib.error
import urllib.request
import uuid

HERE = __file__.rsplit("\\", 1)[0] if "\\" in __file__ else __file__.rsplit("/", 1)[0]


def call(port, path, data=None, timeout=120):
    req = urllib.request.Request("http://127.0.0.1:%d%s" % (port, path))
    if data is not None:
        req.data = json.dumps(data).encode("utf-8")
        req.add_header("Content-Type", "application/json")
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:
            return r.status, json.loads(r.read().decode("utf-8") or "{}")
    except urllib.error.HTTPError as e:
        try:
            return e.code, json.loads(e.read().decode("utf-8"))
        except Exception:
            return e.code, {}


def dependents(prompt, bad):
    """All node ids that read from a node in `bad`, directly or through other nodes."""
    out = set(bad)
    changed = True
    while changed:
        changed = False
        for nid, n in prompt.items():
            if nid in out:
                continue
            for v in n.get("inputs", {}).values():
                if isinstance(v, list) and len(v) == 2 and str(v[0]) in out:
                    out.add(nid)
                    changed = True
                    break
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--port", type=int, default=8188)
    ap.add_argument("--prompt", default=HERE + "/master_prompt.json")
    ap.add_argument("--report", default=HERE + "/master_report.md")
    ap.add_argument("--max-rounds", type=int, default=250)
    a = ap.parse_args()

    prompt = json.load(open(a.prompt, encoding="utf-8"))
    code, info = call(a.port, "/object_info")
    if code != 200:
        print("FAIL: no ComfyUI answers on port %d" % a.port)
        return 2
    sy_types = sorted(k for k in info if k.startswith("SY"))
    # the test picture: the first picture in this ComfyUI's input folder
    pics = (info.get("LoadImage", {}).get("input", {}).get("required", {}).get("image") or [[]])[0]
    png = next((p for p in pics if p.lower().endswith(".png")), pics[0] if pics else "")
    for n in prompt.values():
        if n["class_type"] == "LoadImage" and png:
            n["inputs"]["image"] = png
        if n["class_type"] == "SYImageMetadataReader" and png:
            n["inputs"]["file"] = png
    # Load Text SY reads notes.txt from the input folder: make a small one (ComfyUI keeps it in the input folder)
    boundary = "----symaster"
    body = ("--%s\r\nContent-Disposition: form-data; name=\"image\"; filename=\"notes.txt\"\r\nContent-Type: text/plain\r\n\r\n"
            "SY master test notes\r\n--%s\r\nContent-Disposition: form-data; name=\"overwrite\"\r\n\r\ntrue\r\n--%s--\r\n" % (boundary, boundary, boundary)).encode("utf-8")
    req = urllib.request.Request("http://127.0.0.1:%d/upload/image" % a.port, data=body)
    req.add_header("Content-Type", "multipart/form-data; boundary=" + boundary)
    try:
        urllib.request.urlopen(req, timeout=30).read()
    except Exception as e:  # the Load Text node will then report the missing file
        print("note: could not create notes.txt:", e)
    # a class this ComfyUI does not know is broken by definition
    removed = {}  # id -> reason
    for nid, n in prompt.items():
        if n["class_type"] not in info:
            removed[nid] = "node class not found in this ComfyUI"
    for nid in dependents(prompt, set(removed)) - set(removed):
        removed[nid] = "waits for a broken node"
    live = {k: v for k, v in prompt.items() if k not in removed}
    rounds = 0
    ran_ok = False
    t0 = time.time()
    while live and rounds < a.max_rounds:
        rounds += 1
        code, res = call(a.port, "/prompt", {"prompt": live, "client_id": str(uuid.uuid4())})
        if code != 200:
            bad = {}
            for nid, ne in (res.get("node_errors") or {}).items():
                msg = "; ".join(e.get("message", "") + (" " + e.get("details", "") if e.get("details") else "") for e in ne.get("errors", []))
                bad[nid] = "check failed: " + msg
            if not bad:
                print("FAIL: ComfyUI refused the prompt:", json.dumps(res)[:300])
                return 2
        else:
            pid = res["prompt_id"]
            bad = {}
            while True:
                time.sleep(1)
                c, h = call(a.port, "/history/" + pid)
                if pid in h and h[pid].get("status", {}).get("completed") is not None:
                    st = h[pid]["status"]
                    if st.get("completed"):
                        ran_ok = True
                    else:
                        for kind, d in st.get("messages", []):
                            if kind == "execution_error":
                                bad[str(d.get("node_id"))] = "%s: %s" % (d.get("exception_type", "error"), str(d.get("exception_message", "")).strip()[:300])
                    break
                if time.time() - t0 > 3600:
                    print("FAIL: took more than one hour")
                    return 2
            if ran_ok:
                break
            if not bad:
                print("FAIL: the prompt stopped with no error message")
                return 2
        for nid, why in bad.items():
            removed[nid] = why
        for nid in dependents(live, set(bad)) - set(bad):
            removed.setdefault(nid, "waits for a broken node")
        live = {k: v for k, v in prompt.items() if k not in removed}

    # report
    title = lambda n: (n.get("_meta") or {}).get("title") or n["class_type"]
    soft_words = ("were found", "found in the input folder", "no checkpoints")
    all_roots = {nid: why for nid, why in removed.items() if why != "waits for a broken node"}
    needs_file = {nid: why for nid, why in all_roots.items() if any(w in why for w in soft_words)}
    failed_roots = {nid: why for nid, why in all_roots.items() if nid not in needs_file}
    sy_run = {n["class_type"] for k, n in live.items() if n["class_type"].startswith("SY")} if ran_ok else set()
    sy_in_prompt = {n["class_type"] for n in prompt.values() if n["class_type"].startswith("SY")}
    sy_failed = {prompt[k]["class_type"] for k in all_roots if prompt[k]["class_type"].startswith("SY")}
    sy_not_run = sorted(sy_in_prompt - sy_run - sy_failed)
    lines = ["# SY Master Check", "", "Server port: %d. Rounds: %d. Time: %.0f s." % (a.port, rounds, time.time() - t0), "",
             "SY node types in this ComfyUI: %d. In the master prompt: %d." % (len(sy_types), len(sy_in_prompt)),
             "PASS: %d. BROKEN: %d. Need a file: %d. Not reached: %d." % (len(sy_run), len(failed_roots), len(needs_file), len(sy_not_run)), ""]
    if failed_roots:
        lines += ["## Broken nodes", ""]
        for nid, why in sorted(failed_roots.items(), key=lambda x: prompt[x[0]]["class_type"]):
            lines.append("- %s (%s, id %s): %s" % (title(prompt[nid]), prompt[nid]["class_type"], nid, why))
        lines.append("")
    if needs_file:
        lines += ["## Needs a file on this computer (not a fault)", ""]
        for nid, why in sorted(needs_file.items()):
            lines.append("- %s (%s): %s" % (title(prompt[nid]), prompt[nid]["class_type"], why))
        lines.append("")
    if sy_not_run:
        lines += ["## Not reached (a node in front of them was broken)", "", ", ".join(sy_not_run), ""]
    missing = sorted(set(sy_types) - sy_in_prompt)
    if missing:
        lines += ["## In ComfyUI but not in the master prompt (add them)", "", ", ".join(missing), ""]
    verdict = "PASS" if not failed_roots and not sy_not_run and not missing else "NOT CLEAN"
    lines.insert(2, "Result: " + verdict)
    open(a.report, "w", encoding="utf-8").write("\n".join(lines) + "\n")
    print("\n".join(lines[:8]))
    print("report:", a.report)
    return 0 if verdict == "PASS" else 1


if __name__ == "__main__":
    sys.exit(main())
