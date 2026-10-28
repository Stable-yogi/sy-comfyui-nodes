"""Assert SY: stops the run with a clear message when a yes/no value is no."""
try:
    from ._sy_common import category, register
except ImportError:  # run as a plain file by the selftest
    from _sy_common import category, register

DEFAULT_MESSAGE = "Assert failed: the value was no."
MAX_MESSAGE = 500


def check_assert(condition, message=""):
    """Pure function. Returns True when the condition is yes. Raises ValueError with the message when it is no."""
    if not isinstance(condition, bool):
        raise ValueError("condition must be yes or no (True or False), got %r." % (condition,))
    if condition:
        return True
    text = message.strip() if isinstance(message, str) else ""
    raise ValueError((text or DEFAULT_MESSAGE)[:MAX_MESSAGE])


class SYAssert:
    DESCRIPTION = "Stops the whole run with your message when the value is no. Use it to catch a wrong setting before the slow part starts."
    CATEGORY = category("Logic")
    FUNCTION = "run"
    OUTPUT_NODE = True
    RETURN_TYPES = ("BOOLEAN",)
    RETURN_NAMES = ("passed",)

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "condition": ("BOOLEAN", {"default": True, "forceInput": True, "tooltip": "Must be yes for the run to go on. No stops the run."}),
                "message": ("STRING", {"default": DEFAULT_MESSAGE, "multiline": False, "tooltip": "The text shown when the run stops."}),
            }
        }

    def run(self, condition, message):
        return (check_assert(condition, message),)


NODE_CLASS_MAPPINGS = {}
NODE_DISPLAY_NAME_MAPPINGS = {}
register(NODE_CLASS_MAPPINGS, NODE_DISPLAY_NAME_MAPPINGS, "Assert", SYAssert)
