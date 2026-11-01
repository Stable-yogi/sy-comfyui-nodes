"""Chat Prompt Builder SY: joins a system text, a user text and an optional assistant text into one STRING for any LLM node."""
import json

try:
    from ._sy_common import category, register
except ImportError:  # run as a plain file by the selftest
    from _sy_common import category, register

STYLES = ("plain", "chat tags", "json messages", "chatml")


def build_chat_prompt(system, user, assistant="", style="plain"):
    """Pure function. Returns one string. It only builds text, it never calls an LLM."""
    for label, value in (("system", system), ("user", user), ("assistant", assistant)):
        if not isinstance(value, str):
            raise ValueError("%s must be text, got %s" % (label, type(value).__name__))
    if style not in STYLES:
        raise ValueError("style must be one of: %s (got %r)" % (", ".join(STYLES), style))
    system = system.strip()
    user = user.strip()
    assistant = assistant.strip()
    if not user:
        raise ValueError("user text is empty: write what you want to ask")
    if style == "plain":
        parts = []
        if system:
            parts.append("System: " + system)
        parts.append("User: " + user)
        if assistant:
            parts.append("Assistant: " + assistant)
        return "\n\n".join(parts)
    if style == "chat tags":
        parts = []
        if system:
            parts.append("<|system|>\n" + system)
        parts.append("<|user|>\n" + user)
        # With no assistant text the open tag tells the model it is its turn.
        parts.append("<|assistant|>\n" + assistant)
        return "\n".join(parts).rstrip("\n") + ("" if assistant else "\n")
    if style == "chatml":
        parts = []
        if system:
            parts.append("<|im_start|>system\n" + system + "<|im_end|>")
        parts.append("<|im_start|>user\n" + user + "<|im_end|>")
        # The open assistant turn tells the model it is its turn; assistant text is a head start for the answer.
        parts.append("<|im_start|>assistant\n" + assistant)
        return "\n".join(parts)
    messages = []
    if system:
        messages.append({"role": "system", "content": system})
    messages.append({"role": "user", "content": user})
    if assistant:
        messages.append({"role": "assistant", "content": assistant})
    return json.dumps(messages, ensure_ascii=False, indent=2)


def prompt_info(prompt, style):
    """Pure function. One plain line: style, size and a rough token count (about 4 letters per token)."""
    return "Style %s, %d characters, about %d tokens." % (style, len(prompt), (len(prompt) + 3) // 4)


class SYChatPromptBuilder:
    DESCRIPTION = ("Joins a system text, a user text and an optional assistant text into one text for any LLM node: plain labels, chat tags, "
                   "ChatML or a JSON message list. An info line gives the size and a rough token count. It does not call an LLM.")
    CATEGORY = category("Text")
    FUNCTION = "run"
    RETURN_TYPES = ("STRING", "STRING")
    RETURN_NAMES = ("prompt", "info")

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "system": ("STRING", {"multiline": True, "default": "", "tooltip": "Standing instructions for the model. Can be empty."}),
                "user": ("STRING", {"multiline": True, "default": "", "tooltip": "What you ask the model. Must not be empty."}),
                "style": (list(STYLES), {"default": "plain", "tooltip": "plain labels, chat tags, chatml, or a JSON list of messages."}),
            },
            "optional": {
                "assistant": ("STRING", {"multiline": True, "default": "", "tooltip": "Optional start of the answer, to steer the model."}),
            },
        }

    def run(self, system, user, style, assistant=""):
        prompt = build_chat_prompt(system, user, assistant, style)
        return (prompt, prompt_info(prompt, style))


NODE_CLASS_MAPPINGS = {}
NODE_DISPLAY_NAME_MAPPINGS = {}
register(NODE_CLASS_MAPPINGS, NODE_DISPLAY_NAME_MAPPINGS, "ChatPromptBuilder", SYChatPromptBuilder)
NODE_DISPLAY_NAME_MAPPINGS["SYChatPromptBuilder"] = "Chat Prompt Builder SY"
