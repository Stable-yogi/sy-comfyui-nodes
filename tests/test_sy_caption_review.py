import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "nodes"))
import sy_caption_review as m


def run():
    r = m.review_caption
    ok, rep = r("a red fox runs across a snowy field", 5, 75, 3, "")
    assert ok and rep.startswith("OK") and "8 words" in rep
    ok, rep = r("a fox", 5, 75, 3, "")
    assert not ok and "too short: 2 words, at least 5" in rep
    ok, rep = r("fox", 2, 75, 3, "")
    assert not ok and "1 word," in rep
    ok, rep = r("", 1, 75, 3, "")
    assert not ok and "too short: 0 words" in rep
    assert r("one two three four five", 5, 75, 3, "")[0]               # exactly at the minimum
    assert not r("one two three four", 5, 75, 3, "")[0]
    assert r("one two three", 1, 3, 3, "")[0]                          # exactly at the maximum
    ok, rep = r("one two three four", 1, 3, 3, "")
    assert not ok and "too long: 4 words, at most 3" in rep
    ok, rep = r("red car red house red tree red sky", 1, 75, 3, "")
    assert not ok and 'repeated word: "red" appears 4 times (limit 3)' in rep
    assert r("red car red house red tree and sky", 1, 75, 3, "")[0]    # 3 times is allowed
    assert r("the cat and the dog and the bird and the fox", 1, 75, 3, "")[0]   # small words may repeat
    ok, rep = r("a very very tall tree", 1, 75, 3, "")
    assert not ok and 'doubled word: "very very"' in rep
    ok, rep = r("a dog with a blurry tag on grass", 1, 75, 3, "blurry, watermark")
    assert not ok and 'banned word: "blurry"' in rep
    assert r("a dog with a blurrytag on grass", 1, 75, 3, "blurry")[0]     # whole words only
    assert not r("A Dog, WATERMARK!", 1, 75, 3, "watermark")[0]        # case and punctuation ignored
    assert not r("a photo of low quality stuff", 1, 75, 3, "low quality")[0]   # phrases
    assert r("a photo of low stuff quality", 1, 75, 3, "low quality")[0]
    assert not r("one two blurry", 1, 75, 3, "gore\nblurry")[0]            # new line list
    ok, rep = r("fox fox fox fox", 5, 75, 3, "fox")
    assert not ok and "4 problems" in rep and rep.count("\n- ") == 4
    assert m.parse_banned(" a, b\n\n c ,,") == ["a", "b", "c"]
    assert m.words_of("Don't stop, it's fine!") == ["don't", "stop", "it's", "fine"]
    for args in ((5, 3, 3), (-1, 5, 3), (1, 0, 3), (1, 5, 0)):
        try:
            r("x", *args)
            raise SystemExit("bad limits must raise")
        except ValueError:
            pass
    assert m.SYCaptionReview().run("a red fox runs home", 5, 75, 3, "") == (True, "OK: 5 words, no problems.")
    return 28
