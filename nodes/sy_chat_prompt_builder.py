"""Chat Prompt Builder SY: joins a system text, a user text and an optional assistant text into one STRING for any LLM node."""
import json

try:
    from ._sy_common import category, register
except ImportError:  # run as a plain file by the selftest
    from _sy_common import category, register

STYLES = ("plain", "chat tags", "json messages")


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
    messages = []
    if system:
        messages.append({"role": "system", "content": system})
    messages.append({"role": "user", "content": user})
    if assistant:
        messages.append({"role": "assistant", "content": assistant})
    return json.dumps(messages, ensure_ascii=False, indent=2)


class SYChatPromptBuilder:
    DESCRIPTION = "Joins a system text, a user text and an optional assistant text into one text for any LLM node. It does not call an LLM."
    CATEGORY = category("Text")
    FUNCTION = "run"
    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("prompt",)

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "system": ("STRING", {"multiline": True, "default": "", "tooltip": "Standing instructions for the model. Can be empty."}),
                "user": ("STRING", {"multiline": True, "default": "", "tooltip": "What you ask the model. Must not be empty."}),
                "style": (list(STYLES), {"default": "plain", "tooltip": "plain labels, chat tags, or a JSON list of messages."}),
            },
            "optional": {
                "assistant": ("STRING", {"multiline": True, "default": "", "tooltip": "Optional start of the answer, to steer the model."}),
            },
        }

    def run(self, system, user, style, assistant=""):
        return (build_chat_prompt(system, user, assistant, style),)


NODE_CLASS_MAPPINGS = {}
NODE_DISPLAY_NAME_MAPPINGS = {}
register(NODE_CLASS_MAPPINGS, NODE_DISPLAY_NAME_MAPPINGS, "ChatPromptBuilder", SYChatPromptBuilder)
NODE_DISPLAY_NAME_MAPPINGS["SYChatPromptBuilder"] = "Chat Prompt Builder SY"
