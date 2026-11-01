"""System Prompt Presets SY: ready-made system prompts for LLM nodes, with a custom text that overrides the choice."""
try:
    from ._sy_common import category, register
except ImportError:  # run as a plain file by the selftest
    from _sy_common import category, register

PRESETS = {
    "prompt enhancer": "You rewrite short image ideas into one rich, concrete image prompt. Describe subject, setting, light, colour and mood. Keep the original idea. Reply with the prompt only.",
    "caption writer": "You describe pictures in plain, accurate sentences. Say only what is visible. Do not guess names, feelings or backstory. Reply with the caption only.",
    "translator": "You translate the user's text into English. Keep the meaning, tone and any names. Do not add notes. Reply with the translation only.",
    "summariser": "You summarise the user's text in a few clear sentences. Keep the key facts and drop the rest. Reply with the summary only.",
    "tag generator": "You turn the user's text into a comma separated list of short lowercase tags. No sentences. Reply with the tags only.",
    "negative prompt writer": "You write a negative prompt for an image model. List flaws to avoid as short comma separated phrases. Reply with the list only.",
    "story writer": "You write a short story scene from the user's idea. Use simple vivid words. Reply with the scene only.",
    "video prompt writer": "You turn the user's idea into a video prompt. Describe the subject, the action, the camera move and the light in a few sentences. Reply with the prompt only.",
    "proofreader": "You fix spelling, grammar and punctuation in the user's text. Keep the voice and meaning. Reply with the corrected text only.",
    "idea brainstormer": "You give ten short, different ideas for the user's topic as a numbered list. One line each. No extra talk.",
    "json formatter": "You turn the user's text into valid JSON. Use clear key names. Reply with the JSON only and nothing around it.",
    "friendly helper": "You are a friendly helper. Answer in plain words, be short and be honest when you do not know.",
}
PRESET_NAMES = tuple(PRESETS)


NO_CHATTER = "Do not add greetings, explanations, markdown or code fences. Output the answer only."


def system_prompt(preset, custom="", no_chatter=False, reply_language="", extra_rules=""):
    """Pure function. A non-empty custom text wins over the chosen preset.
    Then, if asked, extra rules, a reply language and the no-chatter rule are added at the end."""
    return system_prompt_info(preset, custom, no_chatter, reply_language, extra_rules)[0]


def system_prompt_info(preset, custom="", no_chatter=False, reply_language="", extra_rules=""):
    """Pure function. Returns (system_prompt, info)."""
    for value in (custom, reply_language, extra_rules):
        if not isinstance(value, str):
            raise ValueError("custom, reply_language and extra_rules must be text, got %s" % type(value).__name__)
    if custom.strip():
        text = custom.strip()
        source = "your custom text"
    else:
        if preset not in PRESETS:
            raise ValueError("unknown preset %r: pick one of %s" % (preset, ", ".join(PRESET_NAMES)))
        text = PRESETS[preset]
        source = "preset '%s'" % preset
    added = []
    if extra_rules.strip():
        text += " " + extra_rules.strip()
        added.append("extra rules")
    lang = " ".join(reply_language.split()).strip(" .")
    if lang:
        text += " Reply in %s." % lang
        added.append("reply language %s" % lang)
    if no_chatter:
        text += " " + NO_CHATTER
        added.append("no-chatter rule")
    info = "System prompt from %s" % source
    if added:
        info += " plus " + ", ".join(added)
    info += "; %d characters, about %d tokens" % (len(text), -(-len(text) // 4))
    return text, info


class SYSystemPromptPresets:
    DESCRIPTION = ("Gives a ready-made system prompt for an LLM node. Type your own text in custom and it replaces the choice. "
                   "Can add a no-chatter rule (no greetings or code fences), a reply language and your own extra rules.")
    CATEGORY = category("Text")
    FUNCTION = "run"
    RETURN_TYPES = ("STRING", "STRING")
    RETURN_NAMES = ("system_prompt", "info")

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "preset": (list(PRESET_NAMES), {"default": PRESET_NAMES[0], "tooltip": "Which ready-made system prompt to use."}),
            },
            "optional": {
                "custom": ("STRING", {"multiline": True, "default": "", "tooltip": "Your own system prompt. If not empty it replaces the preset."}),
                "no_chatter": ("BOOLEAN", {"default": False, "tooltip": "On: tell the model to skip greetings, explanations and code fences."}),
                "reply_language": ("STRING", {"default": "", "tooltip": "Language of the answer, for example 'English' or 'German'. Empty adds nothing."}),
                "extra_rules": ("STRING", {"multiline": True, "default": "", "tooltip": "Your own extra lines, added after the preset, for example 'Keep it under 50 words.'"}),
            },
        }

    def run(self, preset, custom="", no_chatter=False, reply_language="", extra_rules=""):
        return system_prompt_info(preset, custom, no_chatter, reply_language, extra_rules)


NODE_CLASS_MAPPINGS = {}
NODE_DISPLAY_NAME_MAPPINGS = {}
register(NODE_CLASS_MAPPINGS, NODE_DISPLAY_NAME_MAPPINGS, "SystemPromptPresets", SYSystemPromptPresets)
NODE_DISPLAY_NAME_MAPPINGS["SYSystemPromptPresets"] = "System Prompt Presets SY"
