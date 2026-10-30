"""Base64 Text SY: turns a text into base64 code and back."""
import base64
import binascii

try:
    from ._sy_common import category, register
except ImportError:  # run as a plain file by the selftest
    from _sy_common import category, register

MODES = ("encode", "decode")


def base64_text(text, mode, url_safe):
    """Pure function. encode: text to base64 text. decode: base64 text back to text (padding may be missing)."""
    if mode not in MODES:
        raise ValueError("mode must be one of: %s, got %r" % (", ".join(MODES), mode))
    if mode == "encode":
        raw = text.encode("utf-8")
        data = base64.urlsafe_b64encode(raw) if url_safe else base64.b64encode(raw)
        return data.decode("ascii")
    body = "".join(text.split())
    if url_safe:
        body = body.replace("-", "+").replace("_", "/")
    body += "=" * (-len(body) % 4)
    try:
        raw = base64.b64decode(body.encode("ascii"), validate=True)
        return raw.decode("utf-8")
    except (binascii.Error, UnicodeError, ValueError):
        raise ValueError("text is not valid base64 (or does not hold readable UTF-8 text); check the text and the url_safe setting")


class SYBase64Text:
    DESCRIPTION = "Turns a text into base64 code, or turns base64 code back into the text."
    CATEGORY = category("Text")
    FUNCTION = "run"
    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("text",)

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "text": ("STRING", {"multiline": True, "default": "", "tooltip": "The text to encode, or the base64 code to decode."}),
                "mode": (list(MODES), {"default": "encode", "tooltip": "encode makes base64 code; decode turns it back into text."}),
                "url_safe": ("BOOLEAN", {"default": False, "tooltip": "On: use the web-address-safe letters (- and _ instead of + and /)."}),
            }
        }

    def run(self, text, mode, url_safe):
        return (base64_text(text, mode, url_safe),)


NODE_CLASS_MAPPINGS = {}
NODE_DISPLAY_NAME_MAPPINGS = {}
register(NODE_CLASS_MAPPINGS, NODE_DISPLAY_NAME_MAPPINGS, "Base64Text", SYBase64Text)
NODE_DISPLAY_NAME_MAPPINGS["SYBase64Text"] = "Base64 Text SY"
