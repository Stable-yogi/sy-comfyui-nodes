"""Helper for Seed Vault SY. Pure list logic plus two small file functions that take a path (no ComfyUI import at top level)."""
import hashlib
import json
import os

try:
    from ._sy_common import safe_join
except ImportError:  # run as a plain file by the selftest
    from _sy_common import safe_join

MAX_SEED = 2 ** 63 - 1
STAR_ON = "★"
STAR_OFF = "☆"
TOP_SHOWN = 50
PROMPT_CUT = 300
VAULT_FILE = "seed_vault.json"
OVERRIDE_DIR = None  # tests set this to a temp folder so the real ComfyUI folder is never touched


def validate_inputs(collection, seed, rating, max_entries, prompt=""):
    """Plain checks with plain messages. Returns the cleaned collection name."""
    name = str(collection or "").strip()
    if not name:
        raise ValueError("collection is empty: type a name such as 'my seeds'")
    if len(name) > 80:
        raise ValueError("collection is too long (%d characters): use at most 80" % len(name))
    if not 0 <= int(seed) <= MAX_SEED:
        raise ValueError("seed must be between 0 and %d, got %s" % (MAX_SEED, seed))
    if not 0 <= int(rating) <= 5:
        raise ValueError("rating must be from 0 to 5, got %s" % (rating,))
    if not 10 <= int(max_entries) <= 5000:
        raise ValueError("max_entries must be from 10 to 5000, got %s" % (max_entries,))
    if len(str(prompt or "")) > 20000:
        raise ValueError("prompt is too long (%d characters): use at most 20000" % len(str(prompt)))
    return name


def parse_tags(text):
    """Lowercase words split on commas, spaces or semicolons; no duplicates, order kept."""
    out = []
    for t in str(text or "").replace(";", ",").replace("\n", ",").replace(" ", ",").split(","):
        t = t.strip().lower()
        if t and t not in out:
            out.append(t)
    return out


def entry_id(collection, seed, prompt):
    raw = "%s|%d|%s" % (collection, int(seed), prompt)
    return hashlib.sha1(raw.encode("utf-8")).hexdigest()[:10]


def trim_entries(entries, max_entries, keep_best=True, protect_id=None):
    """Keeps at most max_entries. keep_best drops lowest rated then oldest; otherwise the oldest."""
    entries = list(entries)
    extra = len(entries) - int(max_entries)
    if extra <= 0:
        return entries
    pool = [e for e in entries if e["id"] != protect_id]
    if keep_best:
        pool.sort(key=lambda e: (e["rating"], e["saved_at"]))
    else:
        pool.sort(key=lambda e: e["saved_at"])
    drop = set(e["id"] for e in pool[:extra])
    return [e for e in entries if e["id"] not in drop]


def add_entry(entries, collection, seed, rating, prompt, note, tags, now_text, max_entries, keep_best):
    """Returns a NEW list. Same collection + seed + prompt is the same entry (updated, count + 1)."""
    prompt = str(prompt or "")
    note = str(note or "").strip()
    new_tags = parse_tags(tags) if not isinstance(tags, list) else parse_tags(",".join(tags))
    eid = entry_id(collection, seed, prompt)
    out = []
    found = False
    for e in entries:
        if e["id"] == eid:
            found = True
            e = dict(e)
            e["rating"] = int(rating)
            e["saved_at"] = now_text
            e["count"] = int(e.get("count", 1)) + 1
            if note:
                e["note"] = note
            if new_tags:
                e["tags"] = new_tags
        out.append(e)
    if not found:
        out.append({"id": eid, "collection": collection, "seed": int(seed), "rating": int(rating),
                    "prompt": prompt, "note": note, "tags": new_tags, "saved_at": now_text, "count": 1})
    return trim_entries(out, max_entries, keep_best, protect_id=eid)


def rank_entries(entries, collection):
    """Entries of one collection: higher rating, higher count, newer, then lower seed."""
    mine = [e for e in entries if e["collection"] == collection]
    mine.sort(key=lambda e: e["seed"])
    mine.sort(key=lambda e: e["saved_at"], reverse=True)
    mine.sort(key=lambda e: (e["rating"], e["count"]), reverse=True)
    return mine


def seed_at_rank(ranked, pick_rank):
    """pick_rank 0 or 1 = best seed, 2 = second best... Empty list or too high gives 0."""
    pick_rank = int(pick_rank)
    idx = 0 if pick_rank <= 0 else pick_rank - 1
    return int(ranked[idx]["seed"]) if 0 <= idx < len(ranked) else 0


def stars(rating):
    r = max(0, min(5, int(rating)))
    return STAR_ON * r + STAR_OFF * (5 - r)


def ranking_markdown(ranked, collection):
    lines = ["## %s (%d saved)" % (collection, len(ranked))]
    for n, e in enumerate(ranked[:TOP_SHOWN], 1):
        line = "%d. seed %d %s" % (n, e["seed"], stars(e["rating"]))
        note = " ".join(str(e.get("note", "")).split())
        if note:
            line += " - " + note
        if e.get("tags"):
            line += " (tags: %s)" % ", ".join(e["tags"])
        lines.append(line)
        prompt = " ".join(str(e.get("prompt", "")).split())
        if prompt:
            if len(prompt) > PROMPT_CUT:
                prompt = prompt[:PROMPT_CUT] + "..."
            lines.append("    prompt: " + prompt)
    return "\n".join(lines)


def vault_path(base_dir=None):
    """Path of seed_vault.json inside <user dir>/sy. ComfyUI is imported only here."""
    base = base_dir or OVERRIDE_DIR
    if not base:
        import folder_paths
        base = folder_paths.get_user_directory()
    return safe_join(base, "sy", VAULT_FILE)


def load_vault(path):
    """Missing file = empty vault. A damaged file raises and is left untouched."""
    if not os.path.exists(path):
        return []
    try:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        entries = data["entries"]
        if not isinstance(entries, list):
            raise TypeError("entries is not a list")
        for e in entries:
            for k in ("id", "collection", "seed", "rating", "saved_at", "count"):
                if k not in e:
                    raise KeyError(k)
    except (ValueError, KeyError, TypeError, OSError):
        raise ValueError("seed_vault.json is damaged; fix or remove it: %s" % path)
    return entries


def save_vault(path, entries):
    """Atomic write: a .tmp file first, then os.replace."""
    folder = os.path.dirname(path)
    os.makedirs(folder, exist_ok=True)
    tmp = path + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump({"version": 1, "entries": list(entries)}, f, indent=1, ensure_ascii=True)
    os.replace(tmp, path)
