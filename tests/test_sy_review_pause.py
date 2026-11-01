import base64
import os
import sys
import tempfile
import threading
import time

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "nodes"))
import _sy_pause_api as api
import sy_review_pause as m


def refuses(fn, *a, **k):
    try:
        fn(*a, **k)
    except ValueError as e:
        return str(e)
    return None


class FakeEvent:
    """An event that never really waits: wait() returns the flag at once."""
    def __init__(self):
        self.flag = False

    def set(self):
        self.flag = True

    def wait(self, timeout=None):
        return self.flag


def run():
    n = 0
    # ---- normalize_kept
    assert api.normalize_kept([0, 2], 3) == [0, 2]; n += 1
    assert api.normalize_kept([2, 0, 2, 0], 3) == [0, 2]; n += 1
    assert api.normalize_kept([], 3) == []; n += 1
    assert api.normalize_kept((1,), 2) == [1]; n += 1
    msg = refuses(api.normalize_kept, [3], 3)
    assert msg and "picture 4" in msg and "3 pictures" in msg; n += 1
    assert "picture 1 does not exist" in refuses(api.normalize_kept, [0], 0); n += 1
    assert "only 1 picture " in refuses(api.normalize_kept, [1], 1) + " "; n += 1
    assert "whole numbers" in refuses(api.normalize_kept, ["1"], 3); n += 1
    assert "whole numbers" in refuses(api.normalize_kept, [1.5], 3); n += 1
    assert "whole numbers" in refuses(api.normalize_kept, [True], 3); n += 1
    assert "does not exist" in refuses(api.normalize_kept, [-1], 3); n += 1
    assert "list" in refuses(api.normalize_kept, "1,2", 3); n += 1
    assert "list" in refuses(api.normalize_kept, None, 3); n += 1
    # ---- kept_text
    assert api.kept_text([0, 2]) == "1,3"; n += 1
    assert api.kept_text([]) == ""; n += 1
    assert api.kept_text(range(4)) == "1,2,3,4"; n += 1
    assert m.kept_all(3) == "1,2,3" and m.kept_all(0) == ""; n += 1
    # ---- check_answer
    pend = {"count": 3, "draw": True}
    ok = api.check_answer({"id": "x", "action": "continue", "kept": [2, 0], "text": "hi"}, pend)
    assert ok == {"action": "continue", "kept": [0, 2], "text": "hi", "mask_png": None}; n += 1
    assert api.check_answer({"action": "stop"}, pend)["kept"] == []; n += 1
    assert api.check_answer({"action": "continue", "kept": [0]}, pend)["text"] is None; n += 1
    try:
        api.check_answer({"action": "continue"}, None)
        assert False
    except api.UnknownPause as e:
        assert "not waiting" in str(e); n += 1
    assert "action must" in refuses(api.check_answer, {"action": "go"}, pend); n += 1
    assert "action must" in refuses(api.check_answer, {}, pend); n += 1
    assert "JSON object" in refuses(api.check_answer, [1], pend); n += 1
    assert "does not exist" in refuses(api.check_answer, {"action": "continue", "kept": [5]}, pend); n += 1
    assert "too long" in refuses(api.check_answer, {"action": "continue", "kept": [0], "text": "a" * 200001}, pend); n += 1
    assert api.check_answer({"action": "continue", "kept": [0], "text": "a" * 200000}, pend)["text"] == "a" * 200000; n += 1
    assert "must be a string" in refuses(api.check_answer, {"action": "continue", "kept": [0], "text": 5}, pend); n += 1
    b64 = base64.b64encode(b"abc").decode()
    assert api.check_answer({"action": "continue", "kept": [0], "mask_png_base64": b64}, pend)["mask_png"] == b"abc"; n += 1
    assert "does not take" in refuses(api.check_answer, {"action": "continue", "kept": [0], "mask_png_base64": b64}, {"count": 3, "draw": False}); n += 1
    assert "not valid base64" in refuses(api.check_answer, {"action": "continue", "kept": [0], "mask_png_base64": "@@@@"}, pend); n += 1
    assert "too big" in refuses(api.check_answer, {"action": "continue", "kept": [0], "mask_png_base64": "A" * (6 * 1024 * 1024)}, pend); n += 1
    big = base64.b64encode(b"x" * (4 * 1024 * 1024 + 10)).decode()
    assert "too big" in refuses(api.check_answer, {"action": "continue", "kept": [0], "mask_png_base64": big}, pend); n += 1
    # ---- decide_timeout
    assert api.decide_timeout(0, 10 ** 9, 0, api.TIMEOUT_MODES[0]) is None; n += 1
    assert api.decide_timeout(100, 100 + 59, 1, api.TIMEOUT_MODES[0]) is None; n += 1
    assert api.decide_timeout(100, 100 + 60, 1, api.TIMEOUT_MODES[0]) == "continue"; n += 1
    assert api.decide_timeout(100, 100 + 61, 1, api.TIMEOUT_MODES[1]) == "stop"; n += 1
    assert api.decide_timeout(0, 1440 * 60, 1440, api.TIMEOUT_MODES[1]) == "stop"; n += 1
    assert api.decide_timeout(0, 1440 * 60 - 1, 1440, api.TIMEOUT_MODES[1]) is None; n += 1
    assert "wait_limit_minutes" in refuses(api.decide_timeout, 0, 1, -1, api.TIMEOUT_MODES[0]); n += 1
    assert "wait_limit_minutes" in refuses(api.decide_timeout, 0, 1, 1441, api.TIMEOUT_MODES[0]); n += 1
    assert "wait_limit_minutes" in refuses(api.decide_timeout, 0, 1, 1.5, api.TIMEOUT_MODES[0]); n += 1
    assert "on_timeout" in refuses(api.decide_timeout, 0, 1, 1, "whatever"); n += 1
    # ---- PendingStore
    store = api.PendingStore(event_factory=FakeEvent, clock=lambda: 5.0)
    a = store.create("12", {"count": 2})
    assert a.token.startswith("12-") and a.info["id"] == a.token and a.started == 5.0; n += 1
    assert store.get(a.token) is a and store.get("nope") is None; n += 1
    b = store.create("13", {"count": 1})
    assert a.token != b.token and len(store.list_open()) == 2; n += 1
    assert store.answer(a.token, {"action": "continue"}) is True and a.event.flag and a.answer == {"action": "continue"}; n += 1
    assert store.answer(a.token, {"action": "stop"}) is False and a.answer["action"] == "continue"; n += 1
    assert store.answer("nope", {}) is False; n += 1
    assert [i["id"] for i in store.list_open()] == [b.token]; n += 1
    c = store.create("13", {"count": 4})
    assert store.get(b.token) is None and store.get(c.token) is c; n += 1
    assert store.remove(c.token) is True and store.remove(c.token) is False; n += 1
    assert store.remove(a.token) and store.list_open() == []; n += 1
    # ---- threads: a helper answers after a short delay
    ts = api.PendingStore()
    rec = ts.create("7", {"count": 3})
    threading.Timer(0.15, lambda: ts.answer(rec.token, {"action": "continue", "kept": [1]})).start()
    t0 = time.monotonic()
    kind, res = api.wait_for_answer(rec, 0, api.TIMEOUT_MODES[0], lambda: None, poll=0.02)
    assert kind == "answer" and res["kept"] == [1] and time.monotonic() - t0 < 5; n += 1
    # many threads answering at once: exactly one wins
    rec2 = ts.create("8", {"count": 1})
    wins = []
    def shout(i):
        if ts.answer(rec2.token, {"action": "continue", "kept": [], "who": i}):
            wins.append(i)
    th = [threading.Thread(target=shout, args=(i,)) for i in range(20)]
    [x.start() for x in th]
    [x.join() for x in th]
    assert len(wins) == 1 and rec2.answer["who"] == wins[0]; n += 1
    # many creates from threads give different tokens
    toks = []
    def mk(i):
        toks.append(ts.create("n%d" % i, {}).token)
    th = [threading.Thread(target=mk, args=(i,)) for i in range(20)]
    [x.start() for x in th]
    [x.join() for x in th]
    assert len(set(toks)) == 20 and len(ts.list_open()) >= 20; n += 1
    # ---- wait_for_answer: timeout and cancel
    clock = {"t": 0.0}
    rec3 = api.PendingStore(event_factory=FakeEvent, clock=lambda: clock["t"]).create("9", {})
    polls = []
    def tick():
        polls.append(1)
        clock["t"] += 30.0
    kind, res = api.wait_for_answer(rec3, 1, api.TIMEOUT_MODES[0], tick, poll=0, clock=lambda: clock["t"])
    assert (kind, res) == ("timeout", "continue") and len(polls) == 2; n += 1
    clock["t"] = 0.0
    kind, res = api.wait_for_answer(rec3, 1, api.TIMEOUT_MODES[1], tick, poll=0, clock=lambda: clock["t"])
    assert (kind, res) == ("timeout", "stop"); n += 1
    class Cancelled(BaseException):
        pass
    def cancel():
        raise Cancelled()
    try:
        api.wait_for_answer(rec3, 0, api.TIMEOUT_MODES[0], cancel, poll=0)
        assert False
    except Cancelled:
        n += 1
    # ---- node helpers
    assert m.NEED_SOMETHING in refuses(m.check_inputs, None, "", None, False); n += 1
    assert m.NEED_SOMETHING in refuses(m.check_inputs, None, None, None, False); n += 1
    assert m.check_inputs(None, "hello", None, False) is True; n += 1
    assert m.check_inputs(object(), "", None, True) is False; n += 1
    assert m.check_inputs(None, "", object(), False) is False; n += 1
    assert "needs a picture" in refuses(m.check_inputs, None, "x", None, True); n += 1
    assert m.review_count(3) == 3 and m.review_count(16) == 16 and m.review_count(40) == 16 and m.review_count(0) == 0; n += 1
    assert m.final_kept([1], 3, 3) == [1]; n += 1
    assert m.final_kept([0], 16, 20) == [0, 16, 17, 18, 19]; n += 1
    msg = m.open_message("Hello", 2, [{"filename": "a"}], "txt", True, False, (8, 6), None)
    assert msg["count"] == 2 and msg["size"] == [8, 6] and msg["has_text"] is True and msg["draw"] is False and msg["mask"] is True; n += 1
    assert m.open_message("", 0, [], None, False, False, (1, 1))["message"] == m.DEFAULT_MESSAGE; n += 1
    assert len(m.open_message("x" * 5000, 0, [], "", False, False, (1, 1))["message"]) == 2000; n += 1
    # ---- node declaration
    cls = m.SYReviewPause
    it = cls.INPUT_TYPES()
    assert list(m.NODE_CLASS_MAPPINGS) == ["SYReviewPause"] and m.NODE_DISPLAY_NAME_MAPPINGS["SYReviewPause"] == "Review Pause SY"; n += 1
    assert cls.CATEGORY == "SY/Utility" and cls.RETURN_NAMES == ("image", "text", "mask", "kept", "answer"); n += 1
    assert it["hidden"] == {"unique_id": "UNIQUE_ID"} and it["required"]["enabled"][1]["default"] is True; n += 1
    assert it["required"]["wait_limit_minutes"][1]["max"] == 1440 and set(it["optional"]) == {"image", "text", "mask"}; n += 1
    assert cls.IS_CHANGED() != cls.IS_CHANGED() ; n += 1   # NaN never equals itself
    assert refuses(cls().run, True, "m", False, 0, api.TIMEOUT_MODES[0], None, "", None) == m.NEED_SOMETHING; n += 1
    assert "on_timeout" in refuses(cls().run, True, "m", False, 0, "later", None, "x", None); n += 1

    # ---- torch part (only when torch is installed)
    try:
        import torch
        from PIL import Image
        import io
    except ImportError:
        torch = None
    if torch is not None:
        node = cls()
        tmp = tempfile.mkdtemp(prefix="sy_review_test_")
        m._preview_dir = lambda: tmp
        sent = []
        answer_plan = {}

        def fake_open(info):
            sent.append(info)
            plan = dict(answer_plan)
            threading.Timer(0.05, lambda: api.STORE.answer(info["id"], plan)).start()

        m.send_open = fake_open
        m.check_interrupt = lambda: None
        img = torch.rand(4, 12, 20, 3)
        # disabled: everything passes unchanged
        out = node.run(False, "m", False, 0, api.TIMEOUT_MODES[0], img, "abc", None, "1")
        assert out[0] is img and out[1] == "abc" and out[3] == "1,2,3,4" and out[4] == "passed through"; n += 1
        assert out[2].shape == (1, 12, 20) and float(out[2].sum()) == 0.0; n += 1
        mk = torch.ones(1, 12, 20)
        assert node.run(False, "m", False, 0, api.TIMEOUT_MODES[0], img, "", mk, "1")[2] is mk; n += 1
        assert node.run(False, "m", False, 0, api.TIMEOUT_MODES[0], None, "only text", None, "1")[3] == ""; n += 1
        assert node.run(False, "m", False, 0, api.TIMEOUT_MODES[0], None, "", torch.zeros(7, 5), "1")[2].shape == (1, 7, 5); n += 1
        assert not sent; n += 1
        # a real pause answered by the helper: keep pictures 2 and 4, edit the text
        answer_plan.update({"action": "continue", "kept": [1, 3], "text": "better words"})
        out = node.run(True, "Please check", False, 0, api.TIMEOUT_MODES[0], img, "old words", None, "5")
        assert torch.equal(out[0], img[[1, 3]]) and out[1] == "better words" and out[3] == "2,4" and out[4] == "continue"; n += 1
        assert len(sent) == 1 and sent[0]["count"] == 4 and len(sent[0]["images"]) == 4 and sent[0]["message"] == "Please check"; n += 1
        assert sent[0]["images"][0]["type"] == "temp" and sent[0]["images"][0]["subfolder"] == "sy_review" and sent[0]["draw"] is False; n += 1
        assert os.listdir(tmp) == [] ; n += 1                     # previews cleaned up
        assert api.STORE.list_open() == []; n += 1                # pause removed
        # text not changed: the old text stays
        answer_plan.clear()
        answer_plan.update({"action": "continue", "kept": [0, 1, 2, 3]})
        out = node.run(True, "m", False, 0, api.TIMEOUT_MODES[0], img, "same", None, "5")
        assert out[1] == "same" and out[0].shape == img.shape and torch.equal(out[0], img); n += 1
        # picture order stays
        answer_plan.clear()
        answer_plan.update({"action": "continue", "kept": [3, 0]})
        out = node.run(True, "m", False, 0, api.TIMEOUT_MODES[0], img, "", None, "5")
        assert torch.equal(out[0], img[[0, 3]]) and out[3] == "1,4"; n += 1
        # stop and empty selection
        answer_plan.clear()
        answer_plan.update({"action": "stop", "kept": [0]})
        assert refuses(node.run, True, "m", False, 0, api.TIMEOUT_MODES[0], img, "", None, "5") == "You pressed Stop in Review Pause SY."; n += 1
        answer_plan.clear()
        answer_plan.update({"action": "continue", "kept": []})
        assert refuses(node.run, True, "m", False, 0, api.TIMEOUT_MODES[0], img, "", None, "5") == "You kept no pictures. Keep at least one or press Stop."; n += 1
        # text-only pause: no pictures needed
        answer_plan.clear()
        answer_plan.update({"action": "continue", "kept": [], "text": "fixed"})
        out = node.run(True, "m", False, 0, api.TIMEOUT_MODES[0], None, "broken", None, "6")
        assert out[0] is None and out[1] == "fixed" and out[3] == "" and sent[-1]["count"] == 0; n += 1
        # more than 16 pictures: the extras are always kept
        big_img = torch.rand(18, 4, 4, 3)
        answer_plan.clear()
        answer_plan.update({"action": "continue", "kept": [2]})
        out = node.run(True, "m", False, 0, api.TIMEOUT_MODES[0], big_img, "", None, "7")
        assert out[3] == "3,17,18" and out[0].shape[0] == 3 and sent[-1]["count"] == 16; n += 1
        # drawn mask arrives as a decoded PIL picture
        buf = io.BytesIO()
        tiny = Image.new("L", (2, 2), 0)
        tiny.putpixel((1, 0), 255)
        tiny.save(buf, "PNG")
        png = buf.getvalue()
        dm = api.decode_mask(png, (2, 2))
        assert dm.mode == "L" and dm.getpixel((1, 0)) == 255 and dm.getpixel((0, 0)) == 0; n += 1
        assert api.decode_mask(png, (20, 12)).size == (20, 12); n += 1
        rgba = Image.new("RGBA", (2, 2), (255, 255, 255, 0))
        rgba.putpixel((0, 1), (255, 255, 255, 255))
        buf = io.BytesIO()
        rgba.save(buf, "PNG")
        dm = api.decode_mask(buf.getvalue(), (2, 2))
        assert dm.getpixel((0, 1)) == 255 and dm.getpixel((1, 1)) == 0; n += 1
        assert "readable PNG" in refuses(api.decode_mask, b"not a picture", (2, 2)); n += 1
        answer_plan.clear()
        answer_plan.update({"action": "continue", "kept": [0, 1, 2, 3], "mask": api.decode_mask(png, (20, 12))})
        out = node.run(True, "m", True, 0, api.TIMEOUT_MODES[0], img, "", None, "8")
        assert out[2].shape == (1, 12, 20) and sent[-1]["draw"] is True and sent[-1]["size"] == [20, 12]; n += 1
        assert 0.0 <= float(out[2].min()) and float(out[2].max()) == 1.0; n += 1
        # starting mask preview is saved and cleaned up, mask is kept when nothing is drawn
        answer_plan.clear()
        answer_plan.update({"action": "continue", "kept": [0]})
        out = node.run(True, "m", True, 0, api.TIMEOUT_MODES[0], img, "", mk, "9")
        assert sent[-1]["mask_preview"]["type"] == "temp" and out[2] is mk and os.listdir(tmp) == []; n += 1
        # timeout: continue with everything / stop
        answer_plan.clear()
        real_wait = api.wait_for_answer
        api.wait_for_answer = lambda rec, lim, mode, chk, **k: ("timeout", api.decide_timeout(0, 10 ** 6, lim, mode))
        m.send_open = lambda info: sent.append(info)
        closed = []
        m.send_close = lambda token: closed.append(token)
        out = node.run(True, "m", False, 1, api.TIMEOUT_MODES[0], img, "t", None, "10")
        assert out[0] is img and out[4] == "timed out" and out[3] == "1,2,3,4"; n += 1
        assert len(closed) == 1 and closed[0] == sent[-1]["id"]; n += 1  # the browser is told to close the window
        assert "set to stop" in refuses(node.run, True, "m", False, 1, api.TIMEOUT_MODES[1], img, "t", None, "10"); n += 1
        api.wait_for_answer = real_wait
        assert api.STORE.list_open() == [] and os.listdir(tmp) == []; n += 1
        # cancel button: the interrupt goes through and cleans up
        class Interrupted(BaseException):
            pass
        def boom():
            raise Interrupted()
        m.check_interrupt = boom
        m.send_open = lambda info: sent.append(info)
        try:
            node.run(True, "m", False, 0, api.TIMEOUT_MODES[0], img, "", None, "11")
            assert False
        except Interrupted:
            n += 1
        assert api.STORE.list_open() == [] and os.listdir(tmp) == []; n += 1
        # refusals through the node
        assert refuses(node.run, True, "m", True, 0, api.TIMEOUT_MODES[0], None, "x", None, "1") is not None; n += 1
        assert "needs a picture" in refuses(node.run, True, "m", True, 0, api.TIMEOUT_MODES[0], None, "x", None, "1"); n += 1
    return n
