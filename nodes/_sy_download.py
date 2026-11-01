"""Model Downloader SY: the safe download helper behind the Model Downloader SY node.

This is the ONLY SY file that talks to the internet (audited exception, listed in ALLOW in tests/run_selftest.py and in the
standard). It runs ONLY when the user presses a button in the node: never when a workflow is queued, never when it loads.
Allowed sites: Hugging Face, Civitai and GitHub. Allowed files: .safetensors and .gguf. Nothing is ever overwritten.
The logic is pure functions; the network part takes an `opener` so the tests can fake it (no real download in tests).
"""
import hashlib
import os
import re
import shutil
import threading
import time
import urllib.error
import urllib.parse
import urllib.request
import uuid

ALLOWED_FOLDERS = ("checkpoints", "diffusion_models", "unet", "vae", "loras", "text_encoders", "clip", "clip_vision",
                   "controlnet", "upscale_models", "embeddings", "vae_approx", "style_models", "gligen", "diffusers",
                   "model_patches")
FOLDER_ALIASES = {"unet": "diffusion_models", "clip": "text_encoders"}  # old ComfyUI folder names
ALLOWED_EXTENSIONS = (".safetensors", ".gguf")

# Sites a user may type in a link: the host must be exactly one of these, or end with one of the dot-suffixes.
ALLOWED_HOSTS = ("huggingface.co", "hf.co", "civitai.com", "github.com")
ALLOWED_SUFFIXES = (".huggingface.co", ".hf.co", ".civitai.com")
# Storage sites those sites may hand us to while downloading (redirect only, never typed by the user).
STORAGE_HOSTS = ("objects.githubusercontent.com", "release-assets.githubusercontent.com", "raw.githubusercontent.com",
                 "cdn-lfs.huggingface.co", "cdn-lfs-us-1.hf.co")

MAX_REDIRECTS = 5
MAX_PARALLEL = 3
MAX_ROWS = 60
EXTRA_FREE_BYTES = 1024 ** 3  # keep 1 GB free after the download
TIMEOUT = 30
CHUNK = 1024 * 1024
USER_AGENT = "SY-Nodes-Model-Downloader (Stable Yogi)"
SHA_RE = re.compile(r"^[0-9a-fA-F]{64}$")
PART_RE = re.compile(r"^[A-Za-z0-9._\-()+\[\], ]+$")
RESERVED = {"con", "prn", "aux", "nul", "com1", "com2", "com3", "com4", "com5", "com6", "com7", "com8", "com9",
            "lpt1", "lpt2", "lpt3", "lpt4", "lpt5", "lpt6", "lpt7", "lpt8", "lpt9"}
HINT_LOGIN = "This file needs a login. Use Open in browser, sign in there and download it yourself."


class DownloadError(Exception):
    """A plain-words reason why a download was refused or stopped."""


# ---------------------------------------------------------------- pure helpers

def format_size(n):
    """1536 -> '1.5 KB'. None or a bad number -> 'unknown size'."""
    try:
        n = float(n)
    except (TypeError, ValueError):
        return "unknown size"
    if n < 0:
        return "unknown size"
    for unit in ("B", "KB", "MB", "GB"):
        if n < 1024 or unit == "GB":
            return ("%d B" % n) if unit == "B" else ("%.1f %s" % (n, unit))
        n /= 1024.0
    return "%.1f GB" % n


def enough_space(free, size):
    """True when the drive keeps 1 GB free after the file is stored. An unknown size is not enough."""
    try:
        return int(free) >= int(size) + EXTRA_FREE_BYTES and int(size) > 0
    except (TypeError, ValueError):
        return False


def _looks_like_ip(host):
    if ":" in host:
        return True
    return bool(re.fullmatch(r"[0-9.]+", host)) or bool(re.fullmatch(r"(0x[0-9a-f]+\.?)+", host))


def host_allowed(host):
    """True for the sites a user may type: exact match or a listed dot-suffix. Never a substring match."""
    host = str(host or "").lower()
    if not host or _looks_like_ip(host):
        return False
    return host in ALLOWED_HOSTS or any(host.endswith(s) for s in ALLOWED_SUFFIXES)


def _storage_host_ok(host):
    host = str(host or "").lower()
    if host in STORAGE_HOSTS:
        return True
    # Civitai hands out files from its own Cloudflare storage hosts: they all start with 'civitai-'.
    return host.startswith("civitai-") and host.endswith(".r2.cloudflarestorage.com")


def _check_url(url, allow_storage):
    if not isinstance(url, str) or not url.strip():
        return False, "The link is empty."
    if url != url.strip() or re.search(r"[\s\\\x00-\x1f]", url):
        return False, "The link has spaces or strange characters in it."
    try:
        p = urllib.parse.urlsplit(url)
        host = p.hostname
        port = p.port
    except ValueError:
        return False, "The link is not a valid web address."
    if p.scheme != "https":
        return False, "Only https links are allowed (the link must start with https://)."
    if "@" in p.netloc or p.username is not None or p.password is not None:
        return False, "Links with a user name or password in them are not allowed."
    if not host:
        return False, "The link has no web site name."
    host = host.lower()
    if _looks_like_ip(host):
        return False, "Links to a number address (IP address) are not allowed."
    if port not in (None, 443):
        return False, "Links with a special port number are not allowed."
    if host_allowed(host) or (allow_storage and _storage_host_ok(host)):
        return True, ""
    return False, "This web site is not allowed. Only Hugging Face, Civitai and GitHub links work."


def validate_url(url):
    """(ok, reason). https only; the host must be Hugging Face, Civitai or GitHub; no tricks."""
    return _check_url(url, False)


def redirect_ok(from_url, to_url):
    """(ok, reason). A redirect may only go to https and to an allowed site or one of its known storage hosts."""
    ok, why = _check_url(from_url, True)
    if not ok:
        return False, why
    ok, why = _check_url(to_url, True)
    if not ok:
        return False, "The site tried to send the download somewhere else that is not allowed. " + why
    return True, ""


def target_dir_name(folder):
    """The ComfyUI folder name for a row. Unknown names are refused with the list of allowed ones."""
    name = str(folder or "").strip().lower()
    if name not in ALLOWED_FOLDERS:
        raise ValueError("Unknown folder '%s'. Allowed folders: %s." % (folder, ", ".join(ALLOWED_FOLDERS)))
    return FOLDER_ALIASES.get(name, name)


def safe_file_name(name):
    """The file name (one sub folder level at most) or a ValueError in plain words."""
    s = str(name or "").strip()
    if not s:
        raise ValueError("The file name is empty.")
    if len(s) > 200:
        raise ValueError("The file name is too long.")
    if "\\" in s:
        raise ValueError("The file name must not contain a backslash. Use / for a sub folder.")
    if s.startswith("/") or re.match(r"^[A-Za-z]:", s) or ":" in s:
        raise ValueError("The file name must not be a full path or contain a drive letter.")
    parts = s.split("/")
    if len(parts) > 2:
        raise ValueError("Only one sub folder level is allowed in the file name.")
    for part in parts:
        if not part:
            raise ValueError("The file name has an empty part.")
        if part.startswith(".") or ".." in part:
            raise ValueError("The file name must not start with a dot or contain '..'.")
        if part != part.rstrip(". "):
            raise ValueError("A file or folder name must not end with a dot or a space.")
        if not PART_RE.match(part):
            raise ValueError("The file name has a character that is not allowed. Use letters, numbers and - _ . ( ) + only.")
        if part.split(".")[0].lower() in RESERVED:
            raise ValueError("That file name is reserved by Windows.")
    ext = os.path.splitext(parts[-1])[1].lower()
    if ext not in ALLOWED_EXTENSIONS:
        raise ValueError("Only .safetensors and .gguf files are allowed.")
    return s


def validate_row(row):
    """(clean_row, '') when the row is fine, (None, reason) when it is refused."""
    if not isinstance(row, dict):
        return None, "The row is not valid."
    try:
        canon = target_dir_name(row.get("folder"))
        file = safe_file_name(row.get("file"))
    except ValueError as e:
        return None, str(e)
    url = str(row.get("url") or "").strip()
    ok, why = validate_url(url)
    if not ok:
        return None, why
    sha = str(row.get("sha256") or "").strip()
    if sha and not SHA_RE.match(sha):
        return None, "The checksum (sha256) must be 64 letters and numbers (0-9, a-f)."
    note = re.sub(r"[\x00-\x1f]", " ", str(row.get("note") or "")).strip()[:200]
    clean = {"folder": str(row.get("folder")).strip().lower(), "dir": canon, "file": file, "url": url, "note": note}
    if sha:
        clean["sha256"] = sha.lower()
    return clean, ""


def validate_rows(rows):
    """List of problems (empty list = fine): empty list, too many rows, bad rows, duplicate rows."""
    if not isinstance(rows, (list, tuple)) or not rows:
        return ["The list is empty. Add at least one model."]
    if len(rows) > MAX_ROWS:
        return ["The list is too long (at most %d models)." % MAX_ROWS]
    problems, seen = [], set()
    for i, r in enumerate(rows, 1):
        clean, why = validate_row(r)
        if not clean:
            problems.append("Row %d: %s" % (i, why))
            continue
        key = (clean["dir"], clean["file"].lower())
        if key in seen:
            problems.append("Row %d: %s is in the list twice." % (i, clean["file"]))
        seen.add(key)
    return problems


def parse_list_text(text):
    """Text box -> (rows, problems). One model per line: folder | file | link | optional note | optional sha256.
    Empty lines and lines starting with # are skipped. A bad line is refused with its line number."""
    rows, problems, seen = [], [], set()
    for no, line in enumerate(str(text or "").splitlines(), 1):
        s = line.strip()
        if not s or s.startswith("#"):
            continue
        parts = [p.strip() for p in s.split("|")]
        if len(parts) < 3 or len(parts) > 5:
            problems.append("Line %d: write it as  folder | file name | link | note (the note is optional)." % no)
            continue
        raw = {"folder": parts[0], "file": parts[1], "url": parts[2], "note": parts[3] if len(parts) > 3 else "",
               "sha256": parts[4] if len(parts) > 4 else ""}
        clean, why = validate_row(raw)
        if not clean:
            problems.append("Line %d: %s" % (no, why))
            continue
        key = (clean["dir"], clean["file"].lower())
        if key in seen:
            problems.append("Line %d: %s is in the list twice." % (no, clean["file"]))
            continue
        seen.add(key)
        out = {"folder": clean["folder"], "file": clean["file"], "url": clean["url"], "note": clean["note"]}
        if clean.get("sha256"):
            out["sha256"] = clean["sha256"]
        rows.append(out)
        if len(rows) > MAX_ROWS:
            problems.append("The list is too long (at most %d models)." % MAX_ROWS)
            break
    if not rows and not problems:
        problems.append("The list is empty. Add at least one model.")
    return rows, problems


# ---------------------------------------------------------------- folders on disk

def _default_paths(canon):
    import folder_paths  # inside the function: the selftest runs without ComfyUI
    return folder_paths.get_folder_paths(canon)


def target_path(folder, file, paths_fn=_default_paths):
    """Full path of the file in the right ComfyUI models folder. Refuses anything that leaves that folder."""
    canon = target_dir_name(folder)
    name = safe_file_name(file)
    paths = paths_fn(canon)
    if not paths:
        raise ValueError("ComfyUI has no folder for '%s'." % folder)
    base = os.path.realpath(paths[0])
    full = os.path.realpath(os.path.join(base, *name.split("/")))
    if os.path.commonpath([base, full]) != base:
        raise ValueError("The file would be saved outside the models folder. Refused.")
    return full


def disk_free(path):
    d = os.path.dirname(path) if not os.path.isdir(path) else path
    while d and not os.path.isdir(d):
        parent = os.path.dirname(d)
        if parent == d:
            break
        d = parent
    return shutil.disk_usage(d).free


def check_installed(folder, file, paths_fn=_default_paths):
    path = target_path(folder, file, paths_fn)
    if os.path.isfile(path):
        return {"installed": True, "size": os.path.getsize(path)}
    return {"installed": False, "size": 0}


# ---------------------------------------------------------------- network (thin; the opener is a parameter)

class _Resp:
    def __init__(self, raw):
        self.raw = raw
        self.status = getattr(raw, "status", None) or getattr(raw, "code", 0)
        self.headers = raw.headers

    def read(self, n=-1):
        return self.raw.read(n)

    def close(self):
        try:
            self.raw.close()
        except OSError:
            pass


class _NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        return None  # we follow redirects ourselves, checking every step


def real_opener(url, method="GET", headers=None, timeout=TIMEOUT):
    """The real internet call. Never follows a redirect by itself. Tests pass a fake with the same shape."""
    req = urllib.request.Request(url, method=method, headers=dict(headers or {}))
    op = urllib.request.build_opener(_NoRedirect)
    try:
        return _Resp(op.open(req, timeout=timeout))
    except urllib.error.HTTPError as e:  # 3xx, 401, 403, 404 ... are answers, not crashes
        return _Resp(e)


def _header(resp, name):
    try:
        return resp.headers.get(name)
    except AttributeError:
        return None


def fetch(url, opener, method="GET", extra=None):
    """Open a link and follow at most 5 redirects, each one re-checked. Returns (response, final_url)."""
    ok, why = validate_url(url)
    if not ok:
        raise DownloadError(why)
    headers = {"User-Agent": USER_AGENT, "Accept": "*/*"}
    headers.update(extra or {})
    cur = url
    for _ in range(MAX_REDIRECTS + 1):
        try:
            resp = opener(cur, method, headers, TIMEOUT)
        except DownloadError:
            raise
        except Exception as e:
            raise DownloadError("Could not reach the site (%s)." % (type(e).__name__,))
        status = int(resp.status or 0)
        if status in (301, 302, 303, 307, 308):
            loc = _header(resp, "Location")
            resp.close()
            if not loc:
                raise DownloadError("The site sent a redirect without a target.")
            new = urllib.parse.urljoin(cur, loc)
            ok, why = redirect_ok(cur, new)
            if not ok:
                raise DownloadError(why)
            cur = new
            continue
        return resp, cur
    raise DownloadError("The site redirected too many times (more than %d)." % MAX_REDIRECTS)


def _judge(resp, final_url):
    """Plain refusal for answers that are not a model file. Returns None when the answer is fine."""
    status = int(resp.status or 0)
    if status in (401, 403):
        return HINT_LOGIN
    path = urllib.parse.urlsplit(final_url).path.lower()
    ctype = (_header(resp, "Content-Type") or "").lower()
    if "login" in path or "sign-in" in path:
        return HINT_LOGIN
    if "text/html" in ctype:
        return "The link opens a web page, not a model file. Use Open in browser to check it."
    if status not in (200, 206):
        return "The site answered with error %d." % status
    return None


def remote_size(url, opener):
    """Size of the remote file in bytes, from HEAD (or a one-byte range request). Raises DownloadError with a reason."""
    resp, final = fetch(url, opener, "HEAD")
    try:
        status = int(resp.status or 0)
        if status in (400, 404, 405, 501):  # some servers do not like HEAD: ask for one byte instead
            resp.close()
            resp, final = fetch(url, opener, "GET", {"Range": "bytes=0-0"})
            status = int(resp.status or 0)
        why = _judge(resp, final)
        if why:
            raise DownloadError(why)
        rng = _header(resp, "Content-Range")
        if rng and "/" in rng and rng.split("/")[-1].strip().isdigit():
            return int(rng.split("/")[-1])
        length = _header(resp, "Content-Length")
        if status == 206 and not rng:
            return None
        return int(length) if length and str(length).isdigit() else None
    finally:
        resp.close()


def plan_rows(rows, opener=real_opener, paths_fn=_default_paths, free_fn=disk_free):
    """Check every row without downloading: refusal text, installed or not, remote size, free disk space."""
    problems = validate_rows(rows)
    if problems and (not isinstance(rows, (list, tuple)) or not rows or len(rows) > MAX_ROWS):
        return {"ok": False, "error": problems[0], "rows": [], "total": 0, "free": 0}
    out, total, min_free = [], 0, None
    for i, raw in enumerate(rows):
        item = {"index": i, "ok": False, "installed": False, "size": None, "free": None, "error": ""}
        clean, why = validate_row(raw)
        if not clean:
            item["error"] = why
            out.append(item)
            continue
        item.update(folder=clean["folder"], file=clean["file"], url=clean["url"])
        try:
            path = target_path(clean["folder"], clean["file"], paths_fn)
            item["target"] = os.path.dirname(path)
            if os.path.isfile(path):
                item.update(installed=True, size=os.path.getsize(path), error="Already installed.")
                out.append(item)
                continue
            item["free"] = free_fn(path)
            size = remote_size(clean["url"], opener)
            item["size"] = size
            if size is None:
                item["error"] = "The site did not say how big the file is, so it cannot be checked. Use Open in browser."
            elif not enough_space(item["free"], size):
                item["error"] = "Not enough free disk space: needs %s plus 1 GB spare, %s free." % (
                    format_size(size), format_size(item["free"]))
            else:
                item["ok"] = True
                total += size
                min_free = item["free"] if min_free is None else min(min_free, item["free"])
        except (DownloadError, ValueError, OSError) as e:
            item["error"] = str(e)
        out.append(item)
    total_ok = bool(out) and min_free is not None and enough_space(min_free, total)
    return {"ok": True, "rows": out, "total": total, "total_text": format_size(total), "total_ok": total_ok,
            "free": min_free or 0, "free_text": format_size(min_free or 0)}


# ---------------------------------------------------------------- download jobs

_lock = threading.Lock()
JOBS = {}


def _new_job(row, dest):
    return {"id": uuid.uuid4().hex[:12], "row": row, "dest": dest, "state": "waiting", "done": 0, "total": 0,
            "message": "", "cancel": False, "started": time.time()}


def _forget_old_jobs():
    if len(JOBS) > 60:
        for k in sorted(JOBS, key=lambda j: JOBS[j]["started"])[:20]:
            if JOBS[k]["state"] not in ("waiting", "downloading"):
                del JOBS[k]


def _finish(job, state, message):
    job["state"] = state
    job["message"] = message


def _remove_own_part(part, made):
    if made:
        try:
            os.remove(part)
        except OSError:
            pass


def run_download(job, opener=real_opener, free_fn=disk_free):
    """The worker. Writes <file>.part, then renames it. Never overwrites. Runs in a thread (the tests call it directly)."""
    row, dest = job["row"], job["dest"]
    part = dest + ".part"
    made = False
    try:
        job["state"] = "downloading"
        resp, final = fetch(row["url"], opener, "GET")
        try:
            why = _judge(resp, final)
            if why:
                raise DownloadError(why)
            length = _header(resp, "Content-Length")
            total = int(length) if length and str(length).isdigit() else 0
            if total <= 0:
                raise DownloadError("The site did not say how big the file is. Use Open in browser.")
            job["total"] = total
            os.makedirs(os.path.dirname(dest), exist_ok=True)
            if not enough_space(free_fn(dest), total):
                raise DownloadError("Not enough free disk space: needs %s plus 1 GB spare." % format_size(total))
            if os.path.exists(dest):
                raise DownloadError("Already installed.")
            if os.path.exists(part):
                raise DownloadError("An unfinished download file is in the way: %s. Remove it yourself and try again." % os.path.basename(part))
            sha = hashlib.sha256()
            with open(part, "xb") as f:
                made = True
                while True:
                    if job["cancel"]:
                        raise _Cancelled()
                    chunk = resp.read(CHUNK)
                    if not chunk:
                        break
                    f.write(chunk)
                    sha.update(chunk)
                    job["done"] += len(chunk)
        finally:
            resp.close()
        if job["done"] != total:
            raise DownloadError("The download ended early (%s of %s). Nothing was kept." % (format_size(job["done"]), format_size(total)))
        want = row.get("sha256")
        if want and sha.hexdigest() != want.lower():
            raise DownloadError("The file does not match its checksum (sha256), so it was not kept.")
        if os.path.exists(dest):
            raise DownloadError("Already installed.")
        os.rename(part, dest)
        made = False
        _finish(job, "done", "Installed.")
    except _Cancelled:
        _remove_own_part(part, made)
        _finish(job, "cancelled", "Download cancelled. The unfinished file was removed.")
    except DownloadError as e:
        _remove_own_part(part, made)
        _finish(job, "error", str(e))
    except OSError as e:
        _remove_own_part(part, made)
        _finish(job, "error", "Could not save the file (%s)." % (e.strerror or type(e).__name__))
    except Exception as e:  # never leave a job stuck on 'downloading'
        _remove_own_part(part, made)
        _finish(job, "error", "The download failed (%s)." % type(e).__name__)


class _Cancelled(Exception):
    pass


def start_download(row, opener=real_opener, paths_fn=_default_paths, free_fn=disk_free, threaded=True):
    """Check the row, then start the download in the background. Returns {'id': ...} or raises ValueError (plain words)."""
    clean, why = validate_row(row)
    if not clean:
        raise ValueError(why)
    dest = target_path(clean["folder"], clean["file"], paths_fn)
    if os.path.isfile(dest):
        raise ValueError("Already installed.")
    with _lock:
        active = [j for j in JOBS.values() if j["state"] in ("waiting", "downloading")]
        if any(os.path.normcase(j["dest"]) == os.path.normcase(dest) for j in active):
            raise ValueError("This file is already being downloaded.")
        if len(active) >= MAX_PARALLEL:
            raise ValueError("%d downloads are running already. Wait until one is finished." % MAX_PARALLEL)
        _forget_old_jobs()
        job = _new_job(clean, dest)
        JOBS[job["id"]] = job
    if threaded:
        threading.Thread(target=run_download, args=(job, opener, free_fn), daemon=True).start()
    return {"id": job["id"]}


def job_status(job_id):
    job = JOBS.get(str(job_id))
    if not job:
        raise ValueError("Unknown download.")
    return {"id": job["id"], "state": job["state"], "done": job["done"], "total": job["total"],
            "message": job["message"], "file": job["row"]["file"]}


def cancel_download(job_id):
    job = JOBS.get(str(job_id))
    if not job:
        raise ValueError("Unknown download.")
    if job["state"] in ("waiting", "downloading"):
        job["cancel"] = True
    return job_status(job_id)


# ---------------------------------------------------------------- web routes

_routes_done = False


def register_routes():
    """Add the /sy/download routes to the ComfyUI server. Safe to call twice. Does nothing outside ComfyUI.
    Nothing here runs by itself: every route is called by a button press in the node."""
    global _routes_done
    if _routes_done:
        return True
    try:
        import asyncio
        from aiohttp import web
        from server import PromptServer
    except Exception:  # not running inside ComfyUI (selftest, plain import)
        return False
    routes = PromptServer.instance.routes

    def answer(fn, blocking=False):
        async def handler(request):
            try:
                if blocking:
                    data = await asyncio.get_running_loop().run_in_executor(None, lambda: fn(request))
                else:
                    data = fn(request)
                return web.json_response(data)
            except ValueError as e:
                return web.json_response({"error": str(e)}, status=400)
            except Exception as e:
                return web.json_response({"error": "Something went wrong (%s)." % type(e).__name__}, status=500)
        return handler

    async def body_of(request):
        try:
            data = await request.json()
        except Exception:
            raise ValueError("The request was not understood.")
        return data if isinstance(data, dict) else {}

    def post(fn, blocking=False):
        async def handler(request):
            try:
                data = await body_of(request)
                if blocking:
                    out = await asyncio.get_running_loop().run_in_executor(None, lambda: fn(data))
                else:
                    out = fn(data)
                return web.json_response(out)
            except ValueError as e:
                return web.json_response({"error": str(e)}, status=400)
            except Exception as e:
                return web.json_response({"error": "Something went wrong (%s)." % type(e).__name__}, status=500)
        return handler

    def _check(request):
        q = request.rel_url.query
        return check_installed(q.get("folder", ""), q.get("file", ""))

    def _status(request):
        return job_status(request.rel_url.query.get("id", ""))

    routes.get("/sy/download/check")(answer(_check))
    routes.get("/sy/download/status")(answer(_status))
    routes.post("/sy/download/plan")(post(lambda d: plan_rows(d.get("rows")), blocking=True))
    routes.post("/sy/download/start")(post(lambda d: start_download(d.get("row"))))
    routes.post("/sy/download/cancel")(post(lambda d: cancel_download(d.get("id"))))
    _routes_done = True
    return True
