import os
import sys
import tempfile

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "nodes"))
import _sy_seed_vault as h
import sy_seed_vault as m


def _raises(fn, *a, **k):
    try:
        fn(*a, **k)
    except ValueError as e:
        return str(e)
    return None


def _add(es, seed, rating, when, coll="c", prompt="", note="", tags="", mx=500, keep=True):
    return h.add_entry(es, coll, seed, rating, prompt, note, tags, when, mx, keep)


def run():
    n = 0
    es = _add([], 5, 3, "2026-01-01T00:00:00", note="first", tags="Red, blue")
    assert len(es) == 1 and es[0]["count"] == 1 and es[0]["tags"] == ["red", "blue"]
    n += 2
    # re-save updates, counts, keeps old note/tags when empty
    es2 = _add(es, 5, 5, "2026-02-01T00:00:00")
    assert len(es2) == 1 and es2[0]["count"] == 2 and es2[0]["rating"] == 5
    assert es2[0]["note"] == "first" and es2[0]["tags"] == ["red", "blue"] and es2[0]["saved_at"].startswith("2026-02")
    assert es[0]["count"] == 1   # input list not changed
    n += 3
    # different prompt = different entry
    assert len(_add(es2, 5, 3, "2026-02-02T00:00:00", prompt="x")) == 2
    n += 1
    # ranking order: rating, count, newer, seed
    r = []
    r = _add(r, 1, 4, "2026-01-01T00:00:00")
    r = _add(r, 2, 5, "2026-01-02T00:00:00")
    r = _add(r, 3, 4, "2026-01-03T00:00:00")
    r = _add(r, 1, 4, "2026-01-04T00:00:00")   # seed 1 count 2, rating 4
    r = _add(r, 9, 1, "2026-01-05T00:00:00", coll="other")
    ranked = h.rank_entries(r, "c")
    assert [e["seed"] for e in ranked] == [2, 1, 3]
    n += 1
    t = _add(_add([], 7, 3, "2026-01-01T00:00:00"), 8, 3, "2026-01-02T00:00:00")
    assert [e["seed"] for e in h.rank_entries(t, "c")] == [8, 7]   # newer first
    n += 1
    # seed_at_rank
    assert h.seed_at_rank(ranked, 0) == 2 and h.seed_at_rank(ranked, 1) == 2
    assert h.seed_at_rank(ranked, 2) == 1 and h.seed_at_rank(ranked, 9) == 0 and h.seed_at_rank([], 0) == 0
    n += 4
    # trimming
    big = []
    for i in range(10):
        big = _add(big, i, 1 if i < 3 else 4, "2026-01-%02dT00:00:00" % (i + 1), mx=500)
    cut = h.trim_entries(big, 8, True)
    assert sorted(e["seed"] for e in cut) == [2, 3, 4, 5, 6, 7, 8, 9]    # dropped seeds 0 and 1 (low, oldest)
    cut2 = h.trim_entries(big, 8, False)
    assert sorted(e["seed"] for e in cut2) == [2, 3, 4, 5, 6, 7, 8, 9]
    mixed = [dict(e) for e in big]
    mixed[0]["rating"] = 5   # oldest but best
    c3 = h.trim_entries(mixed, 9, True)
    assert 0 in [e["seed"] for e in c3]
    c4 = h.trim_entries(mixed, 9, False)
    assert 0 not in [e["seed"] for e in c4]
    n += 4
    # adding at the limit keeps the new entry
    full = _add(_add([], 1, 5, "2026-01-01T00:00:00", mx=10), 2, 0, "2026-01-02T00:00:00", mx=10)
    for i in range(3, 12):
        full = _add(full, i, 5, "2026-01-%02dT00:00:00" % i, mx=10)
    last = _add(full, 99, 0, "2026-03-01T00:00:00", mx=10)
    assert len(last) == 10 and 99 in [e["seed"] for e in last]
    n += 1
    # markdown
    md = h.ranking_markdown(h.rank_entries(_add([], 123456, 4, "2026-01-01T00:00:00", note="nice", tags="a,b", prompt="a cat"), "c"), "c")
    lines = md.split("\n")
    assert lines[0] == "## c (1 saved)"
    assert lines[1] == "1. seed 123456 ★★★★☆ - nice (tags: a, b)"
    assert lines[2] == "    prompt: a cat"
    n += 3
    longp = _add([], 1, 1, "2026-01-01T00:00:00", prompt="x" * 400)
    assert h.ranking_markdown(longp, "c").split("\n")[2] == "    prompt: " + "x" * 300 + "..."
    plain = h.ranking_markdown(_add([], 4, 0, "2026-01-01T00:00:00"), "c").split("\n")
    assert plain == ["## c (1 saved)", "1. seed 4 ☆☆☆☆☆"]
    many = []
    for i in range(60):
        many = _add(many, i, 3, "2026-01-01T00:00:%02d" % i)
    assert len(h.ranking_markdown(h.rank_entries(many, "c"), "c").split("\n")) == 51
    n += 3
    # tags
    assert h.parse_tags(" A, b;c  a\nD ") == ["a", "b", "c", "d"] and h.parse_tags("") == []
    n += 1
    # validation
    for args in (("  ", 1, 1, 500), ("x" * 81, 1, 1, 500), ("c", -1, 1, 500), ("c", 2 ** 63, 1, 500),
                 ("c", 1, 6, 500), ("c", 1, -1, 500), ("c", 1, 1, 9), ("c", 1, 1, 5001)):
        assert _raises(h.validate_inputs, *args), args
        n += 1
    assert _raises(h.validate_inputs, "c", 1, 1, 500, "p" * 20001)
    assert h.validate_inputs(" ok ", 2 ** 63 - 1, 5, 10, "p" * 20000) == "ok"
    n += 2
    # files
    with tempfile.TemporaryDirectory() as tmp:
        p = h.vault_path(tmp)
        assert p.endswith(os.path.join("sy", "seed_vault.json"))
        assert h.load_vault(p) == []
        n += 2
        h.save_vault(p, es2)
        assert h.load_vault(p) == es2 and not os.path.exists(p + ".tmp")
        n += 2
        bad = os.path.join(tmp, "sy", "bad.json")
        with open(bad, "w", encoding="utf-8") as f:
            f.write("{not json")
        msg = _raises(h.load_vault, bad)
        assert msg and "damaged" in msg
        assert open(bad, encoding="utf-8").read() == "{not json"
        n += 2
        # node core with a temp path
        best, md2, cnt, info = m.vault_run(p, "save", "looks", 42, 5, 500, True, 0, prompt="p", note="n", tags="t",
                                           now_text="2026-05-01T00:00:00")
        assert best == 42 and cnt == 1 and md2.startswith("## looks (1 saved)") and "Saved" in info
        n += 2
        before = open(p, "rb").read()
        best, md3, cnt, info = m.vault_run(p, "show", "looks", 7, 0, 500, True, 1)
        assert best == 42 and cnt == 1 and open(p, "rb").read() == before
        n += 2
        assert m.vault_run(p, "show", "nothing", 1, 1, 500, True, 0)[0] == 0
        assert m.vault_run(p, "show", "looks", 1, 1, 500, True, 5)[0] == 0
        n += 2
        with open(p, "w", encoding="utf-8") as f:
            f.write("oops")
        assert _raises(m.vault_run, p, "save", "looks", 1, 1, 500, True, 0)
        assert open(p, encoding="utf-8").read() == "oops"
        n += 2
        assert _raises(m.vault_run, p, "bogus", "looks", 1, 1, 500, True, 0)
        n += 0
        assert _raises(m.vault_run, p, "show", "looks", 1, 1, 500, True, 51)
        n += 2
    # export and table view
    assert h.export_filename("My Looks!") == "my_looks.md" and h.export_filename("../../x") == "x.md"
    assert h.export_filename("   ") == "seeds.md" and h.export_filename("é") == "seeds.md" and h.export_filename("a" * 90) == "a" * 60 + ".md"
    n += 4
    ex = _add(_add([], 9, 5, "2026-01-01T00:00:00", prompt="line1\nline2", note="good", tags="a,b"), 3, 2, "2026-01-02T00:00:00")
    md4 = h.export_markdown(h.rank_entries(ex, "c"), "c", "NOW")
    assert md4.startswith("# c\n\nExported NOW. 2 saved.") and "## 1. seed 9 ★★★★★" in md4 and "> line1\n> line2" in md4
    assert "- tags: a, b" in md4 and "- note: good" in md4 and md4.index("seed 9") < md4.index("seed 3")
    assert h.export_markdown([], "c").startswith("# c\n\n0 saved.")
    n += 4
    vr = h.view_rows(h.rank_entries(ex, "c"))
    assert [r["seed"] for r in vr] == ["9", "3"] and vr[0]["rank"] == 1 and vr[0]["tags"] == ["a", "b"] and vr[0]["prompt"] == "line1 line2"
    assert len(h.view_rows(h.rank_entries(_add(ex, 1, 1, "2026-01-03T00:00:00"), "c"), limit=2)) == 2
    assert h.list_collections(_add(ex, 4, 3, "2026-01-03T00:00:00", coll="Zed")) == [{"name": "c", "count": 2}, {"name": "Zed", "count": 1}]
    n += 3
    with tempfile.TemporaryDirectory() as tmp:
        out = os.path.join(tmp, "output")
        ep = h.export_path("My Looks", out)
        assert ep == os.path.join(os.path.realpath(out), "sy_seed_vault", "my_looks.md")
        n += 1
        vp = os.path.join(tmp, "v", "seed_vault.json")
        m.vault_run(vp, "save", "looks", 42, 5, 500, True, 0, prompt="p", now_text="2026-05-01T00:00:00")
        m.vault_run(vp, "save", "looks", 43, 2, 500, True, 0, now_text="2026-05-02T00:00:00")
        before = open(vp, "rb").read()
        best, _, cnt, info = m.vault_run(vp, "export", "looks", 1, 1, 500, True, 0, now_text="2026-05-03T00:00:00", export_to=ep)
        assert best == 42 and cnt == 2 and "Exported 2" in info and open(vp, "rb").read() == before
        txt = open(ep, encoding="utf-8").read()
        assert txt.index("seed 42") < txt.index("seed 43") and "Exported 2026-05-03T00:00:00. 2 saved." in txt and not os.path.exists(ep + ".tmp")
        n += 4
        h.OVERRIDE_DIR = os.path.join(tmp, "ud")
        try:
            assert h.view_data("") == {"collections": [], "collection": "", "rows": []}
            h.save_vault(h.vault_path(), _add([], 5, 4, "2026-01-01T00:00:00", coll="Zed"))
            vd = h.view_data("")
            assert vd["collection"] == "Zed" and vd["rows"][0]["seed"] == "5" and vd["collections"] == [{"name": "Zed", "count": 1}]
            assert h.view_data("nope")["rows"] == []
        finally:
            h.OVERRIDE_DIR = None
        n += 4
    cls = m.SYSeedVault
    assert cls.OUTPUT_NODE is True and cls.IS_CHANGED() != cls.IS_CHANGED()   # nan never equals itself
    assert cls.RETURN_NAMES == ("best_seed", "ranking", "count", "info")
    n += 2
    return n
