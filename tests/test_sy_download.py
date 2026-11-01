import hashlib
import os
import sys
import tempfile

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "nodes"))
import _sy_download as d

GB = 1024 ** 3
HF = "https://huggingface.co/org/repo/resolve/main/model.safetensors"
CIV = "https://civitai.com/api/download/models/1"
CIV_STORE = "https://civitai-store.r2.cloudflarestorage.com/m"


class FakeResp:
    def __init__(self, status=200, headers=None, body=b"", on_read=None):
        self.status = status
        self.headers = headers or {}
        self.body = body
        self.pos = 0
        self.on_read = on_read
        self.closed = False

    def read(self, n=-1):
        if self.on_read:
            self.on_read()
        n = len(self.body) if n is None or n < 0 else n
        out = self.body[self.pos:self.pos + n]
        self.pos += len(out)
        return out

    def close(self):
        self.closed = True


def opener_for(resp_by_url, calls=None):
    def op(url, method, headers, timeout):
        if calls is not None:
            calls.append((url, method))
        r = resp_by_url[url]
        return r() if callable(r) else r
    return op


def body_opener(body, ctype="application/octet-stream", url=HF):
    h = {"Content-Length": str(len(body)), "Content-Type": ctype}
    return opener_for({url: lambda: FakeResp(200, dict(h), body)})


def run():
    n = 0

    def ok(cond, msg=""):
        nonlocal n
        assert cond, msg
        n += 1

    good = {"folder": "checkpoints", "file": "m.safetensors", "url": HF, "note": "x"}

    # --- validate_url
    ok(d.validate_url(HF)[0])
    ok(d.validate_url(CIV)[0])
    ok(d.validate_url("https://github.com/o/r/releases/download/v1/a.gguf")[0])
    ok(not d.validate_url("http://huggingface.co/a/b.safetensors")[0], "http")
    ok(not d.validate_url("https://huggingface.co.evil.com/a/b.safetensors")[0], "lookalike")
    ok(not d.validate_url("https://evil.com/huggingface.co/a.safetensors")[0], "path trick")
    ok(not d.validate_url("https://evilhuggingface.co/a.safetensors")[0], "substring")
    ok(not d.validate_url("https://huggingface.co@evil.com/a.safetensors")[0], "userinfo")
    ok(not d.validate_url("https://user:pw@huggingface.co/a.safetensors")[0], "userinfo 2")
    ok(not d.validate_url("https://127.0.0.1/a.safetensors")[0], "ip")
    ok(not d.validate_url("https://[::1]/a.safetensors")[0], "ipv6")
    ok(not d.validate_url("https://2130706433/a.safetensors")[0], "decimal ip")
    ok(not d.validate_url("")[0] and not d.validate_url(None)[0], "empty")
    ok(not d.validate_url("ftp://huggingface.co/a.safetensors")[0], "ftp")
    ok(not d.validate_url("https://huggingface.co:8080/a.safetensors")[0], "port")
    ok(not d.validate_url("https://huggingface.co/a b.safetensors")[0], "space")
    ok(not d.validate_url("https://huggingface.co\\@evil.com/a")[0], "backslash")
    ok(d.validate_url("https://cdn-lfs.huggingface.co/x")[0], "hf subdomain")
    ok(not d.validate_url("https://objects.githubusercontent.com/x")[0], "storage host not typable")

    # --- host_allowed
    ok(d.host_allowed("HuggingFace.co") and d.host_allowed("a.hf.co") and not d.host_allowed("hf.co.evil.com"))
    ok(not d.host_allowed("") and not d.host_allowed("10.0.0.1") and not d.host_allowed("raw.githubusercontent.com"))

    # --- redirect_ok
    ok(d.redirect_ok(HF, "https://cdn-lfs.huggingface.co/repos/a")[0])
    ok(d.redirect_ok(HF, "https://cdn-lfs-us-1.hf.co/repos/a")[0])
    ok(d.redirect_ok("https://github.com/o/r/releases/download/v/a.gguf", "https://objects.githubusercontent.com/a")[0])
    ok(d.redirect_ok("https://github.com/o/r/releases/download/v/a.gguf", "https://release-assets.githubusercontent.com/a")[0])
    ok(d.redirect_ok(CIV, CIV_STORE)[0])
    ok(not d.redirect_ok(HF, "https://evil.com/a")[0], "redirect to evil")
    ok(not d.redirect_ok(HF, "http://huggingface.co/a")[0], "redirect to http")
    ok(not d.redirect_ok(HF, "https://r2.cloudflarestorage.com/a")[0], "any cloudflare")
    ok(not d.redirect_ok(HF, "https://huggingface.co.evil.com/a")[0], "redirect lookalike")

    # --- folder and file names
    ok(d.target_dir_name("checkpoints") == "checkpoints" and d.target_dir_name(" LoRAs ") == "loras")
    ok(d.target_dir_name("unet") == "diffusion_models" and d.target_dir_name("clip") == "text_encoders")
    try:
        d.target_dir_name("custom_nodes")
        ok(False, "unknown folder accepted")
    except ValueError as e:
        ok("Allowed folders" in str(e) and "checkpoints" in str(e))
    ok(d.safe_file_name("a.safetensors") == "a.safetensors" and d.safe_file_name("sub/a.gguf") == "sub/a.gguf")
    for bad in ("", "../a.safetensors", "a/../b.safetensors", "/etc/a.safetensors", "C:/a.safetensors", "C:a.safetensors",
                "a\\b.safetensors", ".hidden.safetensors", "a/b/c.safetensors", "a.ckpt", "a.safetensors.exe",
                "a//b.safetensors", "con.safetensors", "sub /a.safetensors", "x" * 300 + ".safetensors",
                "a<b>.safetensors", "..safetensors"):
        try:
            d.safe_file_name(bad)
            ok(False, "accepted %r" % bad)
        except ValueError:
            ok(True)

    # --- validate_row
    c, why = d.validate_row(good)
    ok(c and not why and c["dir"] == "checkpoints")
    ok(d.validate_row(dict(good, sha256="ab" * 32))[0]["sha256"] == "ab" * 32)
    ok(d.validate_row(dict(good, sha256="xyz"))[0] is None)
    ok(d.validate_row(dict(good, folder="nope"))[0] is None)
    ok(d.validate_row(dict(good, file="m.exe"))[0] is None)
    ok(d.validate_row(dict(good, url="http://huggingface.co/a"))[0] is None)
    ok(d.validate_row("text")[0] is None)

    # --- validate_rows / parse_list_text
    ok(d.validate_rows([]) and d.validate_rows(None))
    ok(d.validate_rows([good]) == [])
    ok(any("twice" in p for p in d.validate_rows([good, dict(good, file="M.safetensors")])), "duplicate")
    rows, probs = d.parse_list_text("# comment\n\nloras | a.safetensors | %s | my lora\ncheckpoints | b.gguf | %s\n" % (HF, HF))
    ok(len(rows) == 2 and not probs and rows[0]["note"] == "my lora" and rows[1]["note"] == "")
    rows, probs = d.parse_list_text("loras | a.safetensors | %s\nbad line\nloras | a.exe | %s" % (HF, HF))
    ok(len(rows) == 1 and probs[0].startswith("Line 2") and probs[1].startswith("Line 3"))
    rows, probs = d.parse_list_text("loras | a.safetensors | %s\nLoras | A.safetensors | %s" % (HF, HF))
    ok(len(rows) == 1 and "Line 2" in probs[0] and "twice" in probs[0])
    ok(d.parse_list_text("")[1] and d.parse_list_text("# only a comment")[1])
    rows, probs = d.parse_list_text("loras | a.safetensors | https://evil.com/a | n")
    ok(not rows and "Line 1" in probs[0])
    rows, probs = d.parse_list_text("loras | a.safetensors | %s | n | %s" % (HF, "cd" * 32))
    ok(rows[0]["sha256"] == "cd" * 32)

    # --- sizes and space
    ok(d.format_size(0) == "0 B" and d.format_size(1536) == "1.5 KB" and d.format_size(5 * GB) == "5.0 GB")
    ok(d.format_size(None) == "unknown size" and d.format_size(-1) == "unknown size")
    ok(d.enough_space(3 * GB, 2 * GB) and not d.enough_space(2 * GB, 2 * GB))
    ok(not d.enough_space(10 * GB, None) and not d.enough_space(10 * GB, 0) and not d.enough_space(None, 5))

    # --- fetch: redirects
    calls = []
    op = opener_for({
        HF: FakeResp(302, {"Location": "https://cdn-lfs.huggingface.co/x"}),
        "https://cdn-lfs.huggingface.co/x": FakeResp(200, {"Content-Length": "5"}, b"12345"),
    }, calls)
    resp, final = d.fetch(HF, op)
    ok(final == "https://cdn-lfs.huggingface.co/x" and resp.status == 200 and len(calls) == 2)
    evil = opener_for({HF: FakeResp(302, {"Location": "https://evil.com/x"})})
    try:
        d.fetch(HF, evil)
        ok(False)
    except d.DownloadError:
        ok(True)
    loop = opener_for({HF: lambda: FakeResp(302, {"Location": HF})})
    try:
        d.fetch(HF, loop)
        ok(False)
    except d.DownloadError as e:
        ok("too many" in str(e))
    try:
        d.fetch("https://evil.com/a", evil)
        ok(False)
    except d.DownloadError:
        ok(True)

    # --- remote_size
    ok(d.remote_size(HF, body_opener(b"x" * 10)) == 10)
    try:
        d.remote_size(HF, opener_for({HF: FakeResp(200, {"Content-Type": "text/html; charset=utf-8", "Content-Length": "9"})}))
        ok(False)
    except d.DownloadError as e:
        ok("web page" in str(e))
    try:
        d.remote_size(HF, opener_for({HF: FakeResp(403)}))
        ok(False)
    except d.DownloadError as e:
        ok("login" in str(e))
    login = opener_for({CIV: FakeResp(302, {"Location": "https://civitai.com/login?x=1"}),
                        "https://civitai.com/login?x=1": FakeResp(200, {"Content-Type": "text/html"})})
    try:
        d.remote_size(CIV, login)
        ok(False)
    except d.DownloadError as e:
        ok("login" in str(e))

    # --- downloads with a fake opener, in a temp folder
    with tempfile.TemporaryDirectory() as tmp:
        paths = lambda canon: [os.path.join(tmp, canon)]  # noqa: E731
        free = lambda p: 100 * GB  # noqa: E731
        row = dict(good, dir="checkpoints")
        dest = d.target_path("checkpoints", "m.safetensors", paths)
        ok(dest.startswith(os.path.realpath(tmp)))
        ok(d.check_installed("checkpoints", "m.safetensors", paths) == {"installed": False, "size": 0})
        body = b"abcdefgh" * 1000
        job = d._new_job(row, dest)
        d.run_download(job, body_opener(body), free)
        ok(job["state"] == "done" and job["done"] == len(body), job["message"])
        ok(os.path.isfile(dest) and not os.path.exists(dest + ".part") and open(dest, "rb").read() == body)
        ok(d.check_installed("checkpoints", "m.safetensors", paths)["installed"])
        # never overwrite
        job = d._new_job(row, dest)
        d.run_download(job, body_opener(b"other" * 100), free)
        ok(job["state"] == "error" and "Already" in job["message"] and open(dest, "rb").read() == body)
        # start_download refuses an installed file and a bad row
        try:
            d.start_download(row, body_opener(body), paths, free, threaded=False)
            ok(False)
        except ValueError as e:
            ok("Already installed" in str(e))
        try:
            d.start_download(dict(row, url="https://evil.com/a"), body_opener(body), paths, free, threaded=False)
            ok(False)
        except ValueError:
            ok(True)
        # sha256 right and wrong
        dest2 = d.target_path("checkpoints", "s.safetensors", paths)
        job = d._new_job(dict(row, file="s.safetensors", sha256=hashlib.sha256(body).hexdigest()), dest2)
        d.run_download(job, body_opener(body), free)
        ok(job["state"] == "done" and os.path.isfile(dest2))
        row3 = dict(row, file="t.safetensors")
        dest3 = d.target_path("checkpoints", "t.safetensors", paths)
        job = d._new_job(dict(row3, sha256="0" * 64), dest3)
        d.run_download(job, body_opener(body), free)
        ok(job["state"] == "error" and "checksum" in job["message"] and not os.path.exists(dest3) and not os.path.exists(dest3 + ".part"))
        # html page refused
        dest4 = d.target_path("loras", "h.safetensors", paths)
        job = d._new_job(dict(row, file="h.safetensors"), dest4)
        d.run_download(job, body_opener(b"<html>", "text/html"), free)
        ok(job["state"] == "error" and "web page" in job["message"] and not os.path.exists(dest4) and not os.path.exists(dest4 + ".part"))
        # login needed
        job = d._new_job(row3, dest3)
        d.run_download(job, opener_for({HF: FakeResp(401)}), free)
        ok(job["state"] == "error" and "login" in job["message"])
        # not enough space
        job = d._new_job(row3, dest3)
        d.run_download(job, body_opener(body), lambda p: 1000)
        ok(job["state"] == "error" and "disk space" in job["message"] and not os.path.exists(dest3 + ".part"))
        # ended early
        job = d._new_job(row3, dest3)
        short = opener_for({HF: lambda: FakeResp(200, {"Content-Length": str(len(body) + 50), "Content-Type": "application/octet-stream"}, body)})
        d.run_download(job, short, free)
        ok(job["state"] == "error" and "early" in job["message"] and not os.path.exists(dest3) and not os.path.exists(dest3 + ".part"))
        # a foreign .part is not touched
        open(dest3 + ".part", "wb").write(b"mine")
        job = d._new_job(row3, dest3)
        d.run_download(job, body_opener(body), free)
        ok(job["state"] == "error" and open(dest3 + ".part", "rb").read() == b"mine")
        os.remove(dest3 + ".part")
        # cancel while downloading
        big = b"z" * (3 * d.CHUNK)
        job = d._new_job(row3, dest3)
        d.JOBS[job["id"]] = job
        reads = []

        def cancel_on_second_read():
            reads.append(1)
            if len(reads) == 2:
                d.cancel_download(job["id"])
        cop = opener_for({HF: lambda: FakeResp(200, {"Content-Length": str(len(big)), "Content-Type": "application/octet-stream"}, big, cancel_on_second_read)})
        d.run_download(job, cop, free)
        ok(job["state"] == "cancelled" and not os.path.exists(dest3) and not os.path.exists(dest3 + ".part"))
        ok(d.job_status(job["id"])["state"] == "cancelled")
        # start_download: one per file, max 3 in parallel
        d.JOBS.clear()
        r1 = d.start_download(dict(good, file="p1.safetensors"), None, paths, free, threaded=False)
        ok(d.job_status(r1["id"])["state"] == "waiting")
        try:
            d.start_download(dict(good, file="p1.safetensors"), None, paths, free, threaded=False)
            ok(False)
        except ValueError as e:
            ok("already being" in str(e))
        d.start_download(dict(good, file="p2.safetensors"), None, paths, free, threaded=False)
        d.start_download(dict(good, file="p3.safetensors"), None, paths, free, threaded=False)
        try:
            d.start_download(dict(good, file="p4.safetensors"), None, paths, free, threaded=False)
            ok(False)
        except ValueError as e:
            ok("3 downloads" in str(e))
        d.cancel_download(r1["id"])
        ok(d.JOBS[r1["id"]]["cancel"] is True)
        try:
            d.job_status("nope")
            ok(False)
        except ValueError:
            ok(True)
        d.JOBS.clear()
        # plan_rows
        op = body_opener(body)
        plan = d.plan_rows([dict(good, file="n1.safetensors"), dict(good, file="m.safetensors"), dict(good, file="x.exe")], op, paths, free)
        ok(plan["ok"] and plan["rows"][0]["ok"] and plan["rows"][0]["size"] == len(body))
        ok(plan["rows"][1]["installed"] is True and not plan["rows"][1]["ok"])
        ok(plan["rows"][2]["error"] and not plan["rows"][2]["ok"])
        ok(plan["total"] == len(body) and plan["total_ok"])
        plan = d.plan_rows([dict(good, file="n1.safetensors")], op, paths, lambda p: 1000)
        ok("disk space" in plan["rows"][0]["error"] and not plan["total_ok"])
        ok(d.plan_rows([], op, paths, free)["ok"] is False)
        # a path that leaves the models folder is refused
        try:
            d.target_path("checkpoints", "../x.safetensors", paths)
            ok(False)
        except ValueError:
            ok(True)
    ok(d.register_routes() in (True, False))
    return n


if __name__ == "__main__":
    print("checks:", run())
