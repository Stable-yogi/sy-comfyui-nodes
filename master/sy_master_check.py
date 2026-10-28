"""SY Master Check: runs the SY test prompts on a ComfyUI server and tells which SY node works and which one does not.

There are four test prompts (Text, Picture, Tools, Numbers and logic). Together they hold every SY node.
ComfyUI stops a prompt at the first broken node. So this script sends a prompt, takes the broken node and everything
behind it out, sends it again, and repeats. Nodes that already passed come back from ComfyUI's cache, so each round is fast.

WHAT COUNTS AS A PASS (each part, and all parts together):
  - every SY node of the part ran, or says "needs a file" (a model or file this computer does not have: not a fault)
  - no node is broken, and no node waits behind a broken one
  - no SY node that this ComfyUI knows is missing from the four prompts
  One part not clean = the whole check is NOT CLEAN.

Use:  py -3.12 sy_master_check.py --port 8188 [--prompt prompt_1_text.json ...] [--report master_report.md]
No --prompt = all prompt_*.json next to this script (else master_prompt.json).
Reads only through the ComfyUI HTTP API on 127.0.0.1. Writes nothing in ComfyUI except what a normal run writes.
"""
import argparse
import glob
import json
import os
import sys
import time
import urllib.error
import urllib.request
import uuid

HERE = os.path.dirname(os.path.abspath(__file__))
SOFT_WORDS = ("were found", "found in the input folder", "no checkpoints", "could not auto-find")  # "needs a file", not a fault


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
    except (urllib.error.URLError, OSError):  # nothing listens on that port
        return 0, {}


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


def fit_lists(prompt, info):
    """A saved file name that is not in this computer's list is swapped for one that is (same file name in another folder
    first, else the first entry). Returns a list of what was swapped, for the report."""
    done = []
    for nid, n in prompt.items():
        spec = info.get(n["class_type"])
        if not spec:
            continue
        allin = dict(spec["input"].get("required", {}))
        allin.update(spec["input"].get("optional", {}))
        for name, v in list(n["inputs"].items()):
            s = allin.get(name)
            if isinstance(v, list) or not s or not isinstance(s[0], list) or not s[0] or v in s[0]:
                continue
            base = str(v).replace("\\", "/").split("/")[-1]
            pick = next((x for x in s[0] if str(x).replace("\\", "/").split("/")[-1] == base), s[0][0])
            n["inputs"][name] = pick
            done.append("%s.%s: %r -> %r" % (n["class_type"], name, v, pick))
    return done


def make_notes(port):
    """Load Text SY reads notes.txt from the input folder: make a small one (ComfyUI keeps it in the input folder)."""
    boundary = "----symaster"
    body = ("--%s\r\nContent-Disposition: form-data; name=\"image\"; filename=\"notes.txt\"\r\nContent-Type: text/plain\r\n\r\n"
            "SY master test notes\r\n--%s\r\nContent-Disposition: form-data; name=\"overwrite\"\r\n\r\ntrue\r\n--%s--\r\n" % (boundary, boundary, boundary)).encode("utf-8")
    req = urllib.request.Request("http://127.0.0.1:%d/upload/image" % port, data=body)
    req.add_header("Content-Type", "multipart/form-data; boundary=" + boundary)
    try:
        urllib.request.urlopen(req, timeout=30).read()
    except Exception as e:  # the Load Text node will then report the missing file
        print("note: could not create notes.txt:", e)


def run_one(port, prompt, info, max_rounds, deadline):
    """Run one prompt, taking broken nodes out round by round. Returns a dict with removed, live, ran_ok, rounds, fail."""
    removed = {}  # id -> reason
    for nid, n in prompt.items():
        if n["class_type"] not in info:
            removed[nid] = "node class not found in this ComfyUI"  # a class this ComfyUI does not know is broken by definition
    for nid in dependents(prompt, set(removed)) - set(removed):
        removed[nid] = "waits for a broken node"
    live = {k: v for k, v in prompt.items() if k not in removed}
    rounds, ran_ok = 0, False
    while live and rounds < max_rounds:
        rounds += 1
        code, res = call(port, "/prompt", {"prompt": live, "client_id": str(uuid.uuid4())})
        if code != 200:
            bad = {}
            for nid, ne in (res.get("node_errors") or {}).items():
                msg = "; ".join(e.get("message", "") + (" " + e.get("details", "") if e.get("details") else "") for e in ne.get("errors", []))
                bad[nid] = "check failed: " + msg
            if not bad:
                return {"fail": "ComfyUI refused the prompt: " + json.dumps(res)[:300], "removed": removed, "live": live, "ran_ok": False, "rounds": rounds}
        else:
            pid = res["prompt_id"]
            bad = {}
            while True:
                time.sleep(1)
                c, h = call(port, "/history/" + pid)
                if pid in h and h[pid].get("status", {}).get("completed") is not None:
                    st = h[pid]["status"]
                    if st.get("completed"):
                        ran_ok = True
                    else:
                        for kind, d in st.get("messages", []):
                            if kind == "execution_error":
                                bad[str(d.get("node_id"))] = "%s: %s" % (d.get("exception_type", "error"), str(d.get("exception_message", "")).strip()[:300])
                    break
                if time.time() > deadline:
                    return {"fail": "took more than one hour", "removed": removed, "live": live, "ran_ok": False, "rounds": rounds}
            if ran_ok:
                break
            if not bad:
                return {"fail": "the prompt stopped with no error message", "removed": removed, "live": live, "ran_ok": False, "rounds": rounds}
        for nid, why in bad.items():
            removed[nid] = why
        for nid in dependents(live, set(bad)) - set(bad):
            removed.setdefault(nid, "waits for a broken node")
        live = {k: v for k, v in prompt.items() if k not in removed}
    return {"fail": None, "removed": removed, "live": live, "ran_ok": ran_ok, "rounds": rounds}


def part_name(path):
    b = os.path.basename(path)
    return b.replace("prompt_", "").replace("master_prompt", "all nodes").replace(".json", "").replace("_", " ")


def check_parts(port, paths, report_path, max_rounds=250):
    """Run every prompt in `paths`. Writes the report. Returns (verdict, headline_lines, parts) where parts is a list of
    (name, ok, why, sy_count) - one row per prompt - for a caller (the 3-hour watcher) that wants one line per part."""
    code, info = call(port, "/object_info")
    if code != 200:
        return "ERROR", ["FAIL: no ComfyUI answers on port %d" % port], []
    sy_types = sorted(k for k, v in info.items() if k.startswith("SY") and "sy-comfyui-nodes" in str(v.get("python_module", "sy-comfyui-nodes")))
    pics = (info.get("LoadImage", {}).get("input", {}).get("required", {}).get("image") or [[]])[0]
    png = next((p for p in pics if p.lower().endswith(".png")), pics[0] if pics else "")  # the test picture: first picture in the input folder
    make_notes(port)
    t0 = time.time()
    deadline = t0 + 3600
    body, parts, fitted_all = [], [], []
    sy_seen, sy_pass, total_rounds = set(), set(), 0
    verdict = "PASS"
    for path in paths:
        prompt = json.load(open(path, encoding="utf-8"))
        for n in prompt.values():
            if n["class_type"] == "LoadImage" and png:
                n["inputs"]["image"] = png
            if n["class_type"] == "SYImageMetadataReader" and png:
                n["inputs"]["file"] = png
        fitted_all += fit_lists(prompt, info)
        r = run_one(port, prompt, info, max_rounds, deadline)
        total_rounds += r["rounds"]
        name = part_name(path)
        title = lambda n: (n.get("_meta") or {}).get("title") or n["class_type"]
        sy_in = {n["class_type"] for n in prompt.values() if n["class_type"].startswith("SY")}
        sy_seen |= sy_in
        if r["fail"]:
            verdict = "ERROR"
            parts.append((name, False, r["fail"], len(sy_in)))
            body += ["## %s: ERROR" % name, "", r["fail"], ""]
            continue
        removed, live = r["removed"], r["live"]
        roots = {nid: why for nid, why in removed.items() if why != "waits for a broken node"}
        needs_file = {nid: why for nid, why in roots.items() if any(w in why for w in SOFT_WORDS)}
        failed = {nid: why for nid, why in roots.items() if nid not in needs_file}
        sy_run = {n["class_type"] for n in live.values() if n["class_type"].startswith("SY")} if r["ran_ok"] else set()
        sy_failed = {prompt[k]["class_type"] for k in roots if prompt[k]["class_type"].startswith("SY")}
        not_run = sorted(sy_in - sy_run - sy_failed)
        sy_pass |= sy_run
        ok = not failed and not not_run
        if not ok and verdict == "PASS":
            verdict = "NOT CLEAN"
        why = ""
        if failed:
            why = "; ".join("%s: %s" % (prompt[k]["class_type"], v) for k, v in sorted(failed.items()))[:600]
        elif not_run:
            why = "not reached: " + ", ".join(not_run)[:300]
        parts.append((name, ok, why, len(sy_in)))
        body += ["## %s: %s" % (name, "PASS" if ok else "NOT CLEAN"), "",
                 "SY node types: %d. Ran: %d. Broken: %d. Need a file: %d. Not reached: %d. Rounds: %d." % (len(sy_in), len(sy_run), len(failed), len(needs_file), len(not_run), r["rounds"]), ""]
        if failed:
            body += ["Broken nodes:", ""] + ["- %s (%s, id %s): %s" % (title(prompt[nid]), prompt[nid]["class_type"], nid, w) for nid, w in sorted(failed.items(), key=lambda x: prompt[x[0]]["class_type"])] + [""]
        if needs_file:
            body += ["Needs a file on this computer (not a fault):", ""] + ["- %s (%s): %s" % (title(prompt[nid]), prompt[nid]["class_type"], w) for nid, w in sorted(needs_file.items())] + [""]
        if not_run:
            body += ["Not reached (a node in front of them was broken): " + ", ".join(not_run), ""]
    missing = sorted(set(sy_types) - sy_seen)
    if missing:
        if verdict == "PASS":
            verdict = "NOT CLEAN"
        parts.append(("coverage", False, "in ComfyUI but in no test prompt (add them): " + ", ".join(missing), len(missing)))
    else:
        parts.append(("coverage", True, "", len(sy_types)))
    head = ["# SY Master Check", "", "Result: " + verdict, "",
            "Server port: %d. Prompts: %d. Rounds: %d. Time: %.0f s." % (port, len(paths), total_rounds, time.time() - t0),
            "SY node types in this ComfyUI: %d. In the test prompts: %d. Ran: %d." % (len(sy_types), len(sy_seen), len(sy_pass)), ""]
    if fitted_all:
        head += ["## Names swapped for files this computer has", ""] + ["- " + f for f in fitted_all] + [""]
    if missing:
        head += ["## In ComfyUI but not in any test prompt (add them)", "", ", ".join(missing), ""]
    open(report_path, "w", encoding="utf-8").write("\n".join(head + body) + "\n")
    return verdict, head[:7], parts


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--port", type=int, default=8188)
    ap.add_argument("--prompt", action="append", help="a test prompt file; repeat for more. Default: every prompt_*.json here")
    ap.add_argument("--report", default=os.path.join(HERE, "master_report.md"))
    ap.add_argument("--max-rounds", type=int, default=250)
    a = ap.parse_args()
    paths = a.prompt or sorted(glob.glob(os.path.join(HERE, "prompt_*.json"))) or [os.path.join(HERE, "master_prompt.json")]
    verdict, head, parts = check_parts(a.port, paths, a.report, a.max_rounds)
    print("\n".join(head))
    for name, ok, why, n in parts:
        print("%-5s %-22s %3d nodes %s" % ("PASS" if ok else "FAIL", name, n, ("- " + why) if why else ""))
    print("report:", a.report)
    return {"PASS": 0, "NOT CLEAN": 1}.get(verdict, 2)


if __name__ == "__main__":
    sys.exit(main())
