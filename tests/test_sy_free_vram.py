import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "nodes"))
import sy_free_vram as m


def run():
    assert m.describe_status(1000, 2234) == "freed 1234 MiB"
    assert m.describe_status(2000, 2000) == "nothing freed"
    assert m.describe_status(3000, 1000) == "nothing freed"
    assert m.describe_status(0, 1) == "freed 1 MiB"
    node = m.SYFreeVRAM()
    obj = object()
    out = node.run(obj, False)
    assert out[0] is obj and out[1] == "disabled"
    out = node.run(7, True)  # comfy is not importable in the selftest
    assert out[0] == 7 and isinstance(out[1], str) and out[1]
    assert (m.ANY != "MODEL") is False
    cid = m.SYFreeVRAM.IS_CHANGED()
    assert cid != cid
    return 9
