"""Date Parts SY: splits a date into year, month, day, weekday, day of year and week number."""
import datetime

try:
    from ._sy_common import category, register
except ImportError:  # run as a plain file by the selftest
    from _sy_common import category, register

MODES = ("now", "from_text")
WEEKDAYS = ("Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday")


def date_parts(mode, date_text, today=None):
    """Pure function. Returns (year, month, day, weekday_name, day_of_year, week_number)."""
    if mode == "now":
        d = today if today is not None else datetime.date.today()
    elif mode == "from_text":
        try:
            d = datetime.datetime.strptime(str(date_text).strip(), "%Y-%m-%d").date()
        except ValueError:
            raise ValueError("date_text must look like 2026-10-28 (year-month-day), got %r" % (date_text,))
    else:
        raise ValueError("mode must be now or from_text, got %r" % (mode,))
    return (d.year, d.month, d.day, WEEKDAYS[d.weekday()], d.timetuple().tm_yday, d.isocalendar()[1])


class SYDateParts:
    DESCRIPTION = "Splits a date into year, month, day, weekday name, day of the year and week number. Use today or type a date."
    CATEGORY = category("Utility")
    FUNCTION = "run"
    RETURN_TYPES = ("INT", "INT", "INT", "STRING", "INT", "INT")
    RETURN_NAMES = ("year", "month", "day", "weekday", "day_of_year", "week_number")

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "mode": (list(MODES), {"default": "now", "tooltip": "now uses today's date. from_text reads the date you type."}),
                "date_text": ("STRING", {"default": "2026-01-01", "multiline": False, "tooltip": "Date as YYYY-MM-DD. Only used in from_text mode."}),
            }
        }

    @classmethod
    def IS_CHANGED(cls, mode, date_text):
        return float("nan") if mode == "now" else date_text

    def run(self, mode, date_text):
        return date_parts(mode, date_text)


NODE_CLASS_MAPPINGS = {}
NODE_DISPLAY_NAME_MAPPINGS = {}
register(NODE_CLASS_MAPPINGS, NODE_DISPLAY_NAME_MAPPINGS, "DateParts", SYDateParts)
