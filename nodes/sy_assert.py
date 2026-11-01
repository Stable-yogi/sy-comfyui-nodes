"""Assert SY: stops the run with a clear message when a yes/no value is no."""
try:
    from ._sy_common import category, register
except ImportError:  # run as a plain file by the selftest
    from _sy_common import category, register

DEFAULT_MESSAGE = "Assert failed: the value was no."
MAX_MESSAGE = 500


def check_assert(condition, message="", enabled=True):
    """Pure function. Returns True when the condition is yes. Raises ValueError with the message when it is no.
    With enabled off the check is skipped and True is returned (pass-through)."""
    if not enabled:
        return True
    if not isinstance(condition, bool):
        raise ValueError("condition must be yes or no (True or False), got %r." % (condition,))
    if condition:
        return True
    text = message.strip() if isinstance(message, str) else ""
    raise ValueError((text or DEFAULT_MESSAGE)[:MAX_MESSAGE])


def assert_info(condition, enabled=True):
    """Pure function. One plain sentence about what the check did."""
    if not enabled:
        return "Check is switched off: nothing was tested."
    return "Check passed: the value was yes." if condition else "Check failed."


class SYAssert:
    DESCRIPTION = "Stops the whole run with your message when the value is no. Use it to catch a wrong setting before the slow part starts. Has an on/off switch, so you can leave it in the workflow."
    CATEGORY = category("Logic")
    FUNCTION = "run"
    OUTPUT_NODE = True
    RETURN_TYPES = ("BOOLEAN", "STRING")
    RETURN_NAMES = ("passed", "info")

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "condition": ("BOOLEAN", {"default": True, "forceInput": True, "tooltip": "Must be yes for the run to go on. No stops the run."}),
                "message": ("STRING", {"default": DEFAULT_MESSAGE, "multiline": False, "tooltip": "The text shown when the run stops. Say what is wrong and how to fix it."}),
            },
            "optional": {
                "enabled": ("BOOLEAN", {"default": True, "tooltip": "Off skips the check and lets the run go on. Handy to test without deleting the node."}),
            },
        }

    def run(self, condition, message, enabled=True):
        passed = check_assert(condition, message, enabled)
        return (passed, assert_info(condition, enabled))


NODE_CLASS_MAPPINGS = {}
NODE_DISPLAY_NAME_MAPPINGS = {}
register(NODE_CLASS_MAPPINGS, NODE_DISPLAY_NAME_MAPPINGS, "Assert", SYAssert)
