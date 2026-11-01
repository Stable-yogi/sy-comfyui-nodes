import json
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "nodes"))
import sy_chat_prompt_builder as m


def run():
    n = 0
    assert m.build_chat_prompt("Be brief.", "Hi", "", "plain") == "System: Be brief.\n\nUser: Hi"; n += 1
    assert m.build_chat_prompt("", "Hi", "", "plain") == "User: Hi"; n += 1
    assert m.build_chat_prompt("S", "U", "A", "plain").endswith("Assistant: A"); n += 1
    t = m.build_chat_prompt("S", "U", "", "chat tags")
    assert t == "<|system|>\nS\n<|user|>\nU\n<|assistant|>\n", repr(t); n += 1
    t = m.build_chat_prompt("S", "U", "A", "chat tags")
    assert t.endswith("<|assistant|>\nA"); n += 1
    msgs = json.loads(m.build_chat_prompt('S "q"', "U\nline", "A", "json messages"))
    assert [x["role"] for x in msgs] == ["system", "user", "assistant"]; n += 1
    assert msgs[0]["content"] == 'S "q"' and msgs[1]["content"] == "U\nline"; n += 1
    msgs = json.loads(m.build_chat_prompt("", "U", "", "json messages"))
    assert len(msgs) == 1; n += 1
    for bad in (("S", "  ", "", "plain"), ("S", "U", "", "nope"), ("S", 5, "", "plain")):
        try:
            m.build_chat_prompt(*bad)
            raise SystemExit("bad args must raise")
        except ValueError:
            n += 1
    assert m.SYChatPromptBuilder().run("S", "U", "plain")[0] == "System: S\n\nUser: U"; n += 1
    assert m.build_chat_prompt("S", "U", "", "chatml") == "<|im_start|>system\nS<|im_end|>\n<|im_start|>user\nU<|im_end|>\n<|im_start|>assistant\n"; n += 1
    assert m.build_chat_prompt("", "U", "A", "chatml") == "<|im_start|>user\nU<|im_end|>\n<|im_start|>assistant\nA"; n += 1
    assert m.prompt_info("abcdefgh", "plain") == "Style plain, 8 characters, about 2 tokens."; n += 1
    assert m.prompt_info("", "plain") == "Style plain, 0 characters, about 0 tokens."; n += 1
    assert m.SYChatPromptBuilder().run("S", "U", "plain")[1].startswith("Style plain, 18 characters"); n += 1
    assert m.SYChatPromptBuilder.RETURN_NAMES == ("prompt", "info") and "chatml" in m.STYLES; n += 1
    return n
