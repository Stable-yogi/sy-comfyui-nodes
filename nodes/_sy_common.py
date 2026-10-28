"""Shared helpers for every SY node. Pure Python. Never import comfy here."""
import json
import os

_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_THEME_PATH = os.path.join(_ROOT, "js", "sy_theme.json")

PREFIX = "SY"                 # class id prefix: SYSeed
SUFFIX = " SY"                # display name suffix: "Seed SY"
CATEGORY_ROOT = "SY"          # menu folder: SY/Image
GROUPS = ("Image", "Text", "Values", "Logic", "Resize", "Utility", "Editors", "Notes")

_theme_cache = None


def theme():
    """Return the parsed palette file. One source of truth for colours."""
    global _theme_cache
    if _theme_cache is None:
        with open(_THEME_PATH, "r", encoding="utf-8") as f:
            _theme_cache = json.load(f)
    return _theme_cache


def category(group):
    if group not in GROUPS:
        raise ValueError("unknown SY group: %r (allowed: %s)" % (group, ", ".join(GROUPS)))
    return "%s/%s" % (CATEGORY_ROOT, group)


def class_id(name):
    return PREFIX + name


def display_name(name):
    return name + SUFFIX


def register(mappings_cls, mappings_name, name, cls):
    """Add one node to the two ComfyUI mapping dicts using the SY naming rules."""
    mappings_cls[class_id(name)] = cls
    mappings_name[class_id(name)] = display_name(name)


def safe_join(base_dir, *parts):
    """Join parts under base_dir. Refuse any result that leaves base_dir (path guard)."""
    base = os.path.realpath(base_dir)
    target = os.path.realpath(os.path.join(base, *parts))
    if os.path.commonpath([base, target]) != base:
        raise ValueError("path leaves the allowed folder: %s" % target)
    return target
