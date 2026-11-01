"""Done Alert SY: passes a value through and tells the browser to play a sound / show a note when the run reaches it."""
import json

try:
    from ._sy_common import category, register
except ImportError:  # run as a plain file by the selftest
    from _sy_common import category, register


class _Any(str):
    """Matches every ComfyUI type name."""

    def __ne__(self, other):
        return False


ANY = _Any("*")

SOUNDS = ("beep", "two beeps", "chime", "none")
DEFAULT_MESSAGE = "Your workflow is finished."
MAX_MESSAGE = 200


def _flag(value, name):
    if isinstance(value, bool):
        return value
    raise ValueError("'%s' must be on or off." % name)


def clean_settings(message=DEFAULT_MESSAGE, sound="chime", show_message=True, desktop_notice=False,
                   volume=0.4, only_when_idle=True):
    """Check the settings and return a clean dict. Bad input raises ValueError with a plain sentence."""
    if message is None:
        message = ""
    if not isinstance(message, str):
        raise ValueError("The message must be text.")
    message = " ".join(message.split())
    if len(message) > MAX_MESSAGE:
        message = message[:MAX_MESSAGE].rstrip()
    if not message:
        message = DEFAULT_MESSAGE
    if sound not in SOUNDS:
        raise ValueError("Sound must be one of: %s." % ", ".join(SOUNDS))
    if isinstance(volume, bool) or not isinstance(volume, (int, float)):
        raise ValueError("Volume must be a number between 0 and 1.")
    if volume != volume:
        raise ValueError("Volume must be a number between 0 and 1.")
    volume = round(min(1.0, max(0.0, float(volume))), 3)
    return {
        "message": message,
        "sound": sound,
        "show_message": _flag(show_message, "show_message"),
        "desktop_notice": _flag(desktop_notice, "desktop_notice"),
        "volume": volume,
        "only_when_idle": _flag(only_when_idle, "only_when_idle"),
    }


def alert_payload(message=DEFAULT_MESSAGE, sound="chime", show_message=True, desktop_notice=False,
                  volume=0.4, only_when_idle=True):
    """The ui dict the browser reads: one JSON text of the clean settings."""
    s = clean_settings(message, sound, show_message, desktop_notice, volume, only_when_idle)
    return {"sy_alert": [json.dumps(s, sort_keys=True)]}


class SYDoneAlert:
    DESCRIPTION = ("Put this at the end of a workflow. When the run gets here it plays a sound and shows a note, "
                   "so you can leave the screen. The value passes through unchanged.")
    CATEGORY = category("Utility")
    FUNCTION = "run"
    RETURN_TYPES = (ANY,)
    RETURN_NAMES = ("anything",)
    OUTPUT_NODE = True

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "anything": (ANY, {"tooltip": "Any value. It is passed on unchanged; the alert fires once this value is ready."}),
                "message": ("STRING", {"default": DEFAULT_MESSAGE, "tooltip": "The note shown on screen when the run is finished."}),
                "sound": (list(SOUNDS), {"default": "chime", "tooltip": "Which sound to play. None plays no sound."}),
                "show_message": ("BOOLEAN", {"default": True, "tooltip": "Show the note in the corner of the screen for a few seconds."}),
                "desktop_notice": ("BOOLEAN", {"default": False, "tooltip": "Asks the browser for permission to show a system notice when the tab is in the background."}),
                "volume": ("FLOAT", {"default": 0.4, "min": 0.0, "max": 1.0, "step": 0.05, "tooltip": "How loud the sound is, from 0 (silent) to 1 (full)."}),
                "only_when_idle": ("BOOLEAN", {"default": True, "tooltip": "Only alert when this is the last node of the run: waits until the queue is empty."}),
            },
        }

    @classmethod
    def VALIDATE_INPUTS(cls, input_types=None, **kwargs):
        # The wildcard input has no fixed type; accept any link.
        return True

    def run(self, anything, message=DEFAULT_MESSAGE, sound="chime", show_message=True, desktop_notice=False,
            volume=0.4, only_when_idle=True):
        payload = alert_payload(message, sound, show_message, desktop_notice, volume, only_when_idle)
        return {"ui": payload, "result": (anything,)}


NODE_CLASS_MAPPINGS = {}
NODE_DISPLAY_NAME_MAPPINGS = {}
register(NODE_CLASS_MAPPINGS, NODE_DISPLAY_NAME_MAPPINGS, "DoneAlert", SYDoneAlert)
NODE_DISPLAY_NAME_MAPPINGS["SYDoneAlert"] = "Done Alert SY"
