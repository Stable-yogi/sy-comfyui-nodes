"""SY Master Fit: makes a copy of the master workflow that fits ONE computer, so you can load it and press Run.

File names (models, VAE, checkpoints) differ on every computer. This reads the lists from a running ComfyUI, swaps each
name that is not in the list (same file name in another folder first, else the first entry), picks a test picture
from the input folder, and puts a small notes.txt there for Load Text SY.

Use:  py -3.12 sy_master_fit.py --port 8188 [--in StableYogi-SY-Test-1-Text.json --out StableYogi-SY-Test-1-Text-fitted.json]
No --in = every StableYogi-SY-Test-*.json next to this script (the four test workflows); each gets a "-fitted" copy.
Reads ComfyUI only through its HTTP API on 127.0.0.1.
"""
import argparse
import glob
import json
import urllib.request

HERE = __file__.rsplit("\\", 1)[0] if "\\" in __file__ else __file__.rsplit("/", 1)[0]
MUTE = set()  # a node type listed here is muted (skipped by Run)
SET = {"SYEmptyLatent": {"latent_type": "flux 16ch /8"}}  # 16 channels, like the Krea 2 VAE


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--port", type=int, default=8188)
    ap.add_argument("--in", dest="src", default=None)
    ap.add_argument("--out", default=None)
    a = ap.parse_args()
    info = json.load(urllib.request.urlopen("http://127.0.0.1:%d/object_info" % a.port, timeout=120))
    if a.src:
        jobs = [(a.src, a.out or a.src.replace(".json", "-fitted.json"))]
    else:
        jobs = [(f, f.replace(".json", "-fitted.json")) for f in sorted(glob.glob(HERE + "/StableYogi-SY-Test-*.json")) if not f.endswith("-fitted.json")]
        jobs = jobs or [(HERE + "/StableYogi-SY-Master-Test.json", HERE + "/StableYogi-SY-Master-Test-fitted.json")]
    pics = (info.get("LoadImage", {}).get("input", {}).get("required", {}).get("image") or [[]])[0]
    png = next((x for x in pics if x.lower().endswith(".png")), pics[0] if pics else "")
    crlf = chr(13) + chr(10)
    body = crlf.join(["--b", 'Content-Disposition: form-data; name="image"; filename="notes.txt"', "Content-Type: text/plain", "", "SY master test notes",
                      "--b", 'Content-Disposition: form-data; name="overwrite"', "", "true", "--b--", ""]).encode("utf-8")
    rq = urllib.request.Request("http://127.0.0.1:%d/upload/image" % a.port, data=body)
    rq.add_header("Content-Type", "multipart/form-data; boundary=b")
    urllib.request.urlopen(rq, timeout=30).read()
    for src, out in jobs:
        wf = json.load(open(src, encoding="utf-8"))
        swapped, muted = [], []
        for n in wf["nodes"]:
            names = [i["name"] for i in n.get("inputs", []) if i.get("widget")]
            vals = n.get("widgets_values")
            if not isinstance(vals, list) or len(names) > len(vals):
                continue
            spec = info.get(n["type"])
            allin = {}
            if spec:
                allin = dict(spec["input"].get("required", {}))
                allin.update(spec["input"].get("optional", {}))
            for k, name in enumerate(names):
                if name in SET.get(n["type"], {}):
                    vals[k] = SET[n["type"]][name]
                s = allin.get(name)
                if not s or not isinstance(s[0], list) or not s[0] or vals[k] in s[0]:
                    continue
                # only file lists: a mixed-up position (hidden extra boxes) must never rewrite a plain choice
                if not (isinstance(vals[k], str) and any(str(x).lower().endswith((".safetensors", ".ckpt", ".pt", ".pth", ".gguf", ".png", ".jpg", ".jpeg", ".webp")) for x in s[0][:5])):
                    continue
                base = str(vals[k]).replace("\\", "/").split("/")[-1]
                pick = next((x for x in s[0] if str(x).replace("\\", "/").split("/")[-1] == base), s[0][0])
                swapped.append("%s.%s: %r -> %r" % (n["type"], name, vals[k], pick))
                vals[k] = pick
            if n["type"] == "SYImageMetadataReader" and png and vals:
                swapped.append("SYImageMetadataReader.file: %r -> %r" % (vals[0], png))
                vals[0] = png
            if n["type"] in MUTE:
                n["mode"] = 2
                muted.append(n["type"])
        json.dump(wf, open(out, "w", encoding="utf-8"), indent=1)
        print(chr(10).join(["swapped: " + s for s in swapped] + ["muted: " + m for m in muted]))
        print("wrote", out)


if __name__ == "__main__":
    main()
