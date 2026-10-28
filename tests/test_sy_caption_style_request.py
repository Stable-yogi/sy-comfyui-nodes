import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "nodes"))
import sy_caption_style_request as m


def run():
    n = 0
    assert len(m.STYLE_NAMES) == 4; n += 1
    for s in m.STYLE_NAMES:
        t = m.caption_request(s)
        assert str(m.DEFAULT_WORDS[s]) in t and t.endswith("Reply with the caption only.") and "{" not in t
        n += 1
    assert "at most 15 words" in m.caption_request("short", 15); n += 1
    assert "comma separated" in m.caption_request("tags"); n += 1
    assert "Begin the caption with the exact word or phrase: sksfox" in m.caption_request("training caption", 0, " sksfox "); n += 1
    assert "The main subject is: a fox." in m.caption_request("short", 0, "", "a fox"); n += 1
    assert "Also: mention sky" in m.caption_request("short", 0, "", "", "mention sky"); n += 1
    assert "Begin the caption" not in m.caption_request("short"); n += 1
    for call in (lambda: m.caption_request("poem"), lambda: m.caption_request("short", -1), lambda: m.caption_request("short", 0, 5)):
        try:
            call()
            raise SystemExit("bad args must raise")
        except ValueError:
            n += 1
    assert "caption" in m.SYCaptionStyleRequest().run("short", 0)[0]; n += 1
    return n
