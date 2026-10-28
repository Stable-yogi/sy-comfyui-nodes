import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "nodes"))
import sy_image_metadata_reader as m


def run():
    n = 0
    assert m.extract_metadata({"prompt": "{\"1\": {}}", "workflow": "{\"nodes\": []}", "other": "x"}) == ("{\"1\": {}}", "{\"nodes\": []}"); n += 1
    assert m.extract_metadata({}) == ("", ""); n += 1
    assert m.extract_metadata(None) == ("", ""); n += 1
    assert m.extract_metadata({"prompt": 5, "workflow": b"x"}) == ("", ""); n += 1
    try:
        m.extract_metadata({"prompt": "x" * 11}, limit=10)
        raise SystemExit("long text must raise")
    except ValueError:
        n += 1
    assert m.SYImageMetadataReader.RETURN_TYPES == ("STRING", "STRING"); n += 1
    return n
