"""Date Parts SY: splits a date into year, month, day, weekday, day of year and week number."""
import datetime

try:
    from ._sy_common import category, register
except ImportError:  # run as a plain file by the selftest
    from _sy_common import category, register

MODES = ("now", "from_text")
WEEKDAYS = ("Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday")


MONTHS = ("January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December")
DATE_FORMATS = ["YYYY-MM-DD", "YYYYMMDD", "YYYY/MM/DD", "DD.MM.YYYY", "DD-MM-YYYY", "Month D, YYYY"]
_INPUT_PATTERNS = ("%Y-%m-%d", "%Y%m%d", "%Y/%m/%d", "%Y.%m.%d")
MAX_OFFSET = 36500


def _resolve_date(mode, date_text, today, offset_days=0):
    if mode == "now":
        d = today if today is not None else datetime.date.today()
    elif mode == "from_text":
        text = str(date_text).strip()
        d = None
        for pattern in _INPUT_PATTERNS:
            try:
                d = datetime.datetime.strptime(text, pattern).date()
                break
            except ValueError:
                continue
        if d is None:
            raise ValueError("date_text must look like 2026-10-28 (year-month-day; 20261028 and 2026/10/28 also work), got %r" % (date_text,))
    else:
        raise ValueError("mode must be now or from_text, got %r" % (mode,))
    offset = int(offset_days)
    if abs(offset) > MAX_OFFSET:
        raise ValueError("offset_days must be between -%d and %d, got %d" % (MAX_OFFSET, MAX_OFFSET, offset))
    if offset:
        try:
            d = d + datetime.timedelta(days=offset)
        except OverflowError:
            raise ValueError("offset_days %d moves the date outside the years 1 to 9999" % offset)
    return d


def format_date(d, date_format="YYYY-MM-DD"):
    """Pure function. Writes a date in one of DATE_FORMATS."""
    if date_format not in DATE_FORMATS:
        raise ValueError("date_format must be one of: %s, got %r" % (", ".join(DATE_FORMATS), date_format))
    y, mo, da = "%04d" % d.year, "%02d" % d.month, "%02d" % d.day
    if date_format == "YYYY-MM-DD":
        return "%s-%s-%s" % (y, mo, da)
    if date_format == "YYYYMMDD":
        return y + mo + da
    if date_format == "YYYY/MM/DD":
        return "%s/%s/%s" % (y, mo, da)
    if date_format == "DD.MM.YYYY":
        return "%s.%s.%s" % (da, mo, y)
    if date_format == "DD-MM-YYYY":
        return "%s-%s-%s" % (da, mo, y)
    return "%s %d, %s" % (MONTHS[d.month - 1], d.day, y)


def date_parts(mode, date_text, today=None, offset_days=0):
    """Pure function. Returns (year, month, day, weekday_name, day_of_year, week_number)."""
    d = _resolve_date(mode, date_text, today, offset_days)
    return (d.year, d.month, d.day, WEEKDAYS[d.weekday()], d.timetuple().tm_yday, d.isocalendar()[1])


def date_extras(mode, date_text, today=None, offset_days=0, date_format="YYYY-MM-DD"):
    """Pure function. Returns (date_text, month_name, is_weekend, info) for the same date as date_parts."""
    d = _resolve_date(mode, date_text, today, offset_days)
    text = format_date(d, date_format)
    weekend = d.weekday() >= 5
    left = (datetime.date(d.year, 12, 31) - d).days
    info = "%s, %s (day %d of the year, week %d, %d days left in %d)." % (
        WEEKDAYS[d.weekday()], text, d.timetuple().tm_yday, d.isocalendar()[1], left, d.year)
    if int(offset_days):
        info += " Moved %+d days from the %s date." % (int(offset_days), "current" if mode == "now" else "typed")
    return text, MONTHS[d.month - 1], weekend, info


class SYDateParts:
    DESCRIPTION = ("Splits a date into year, month, day, weekday name, day of the year and week number. Use today or type a date "
                   "(2026-10-28, 20261028 and 2026/10/28 all work). Optional offset_days moves the date (-1 is yesterday). "
                   "Also gives the date written in a format you pick, the month name, a weekend flag and an info line.")
    CATEGORY = category("Utility")
    FUNCTION = "run"
    RETURN_TYPES = ("INT", "INT", "INT", "STRING", "INT", "INT", "STRING", "STRING", "BOOLEAN", "STRING")
    RETURN_NAMES = ("year", "month", "day", "weekday", "day_of_year", "week_number", "date_text", "month_name", "is_weekend", "info")

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "mode": (list(MODES), {"default": "now", "tooltip": "now uses today's date. from_text reads the date you type."}),
                "date_text": ("STRING", {"default": "2026-01-01", "multiline": False, "tooltip": "Date as YYYY-MM-DD. Only used in from_text mode."}),
            },
            "optional": {
                "offset_days": ("INT", {"default": 0, "min": -MAX_OFFSET, "max": MAX_OFFSET, "tooltip": "Move the date by this many days. -1 is yesterday, 7 is next week."}),
                "date_format": (DATE_FORMATS, {"default": "YYYY-MM-DD", "tooltip": "How the date_text output is written."}),
            },
        }

    @classmethod
    def IS_CHANGED(cls, mode, date_text, offset_days=0, date_format="YYYY-MM-DD"):
        return float("nan") if mode == "now" else "%s|%s|%s" % (date_text, offset_days, date_format)

    def run(self, mode, date_text, offset_days=0, date_format="YYYY-MM-DD"):
        return date_parts(mode, date_text, None, offset_days) + date_extras(mode, date_text, None, offset_days, date_format)


NODE_CLASS_MAPPINGS = {}
NODE_DISPLAY_NAME_MAPPINGS = {}
register(NODE_CLASS_MAPPINGS, NODE_DISPLAY_NAME_MAPPINGS, "DateParts", SYDateParts)
NODE_DISPLAY_NAME_MAPPINGS["SYDateParts"] = "Date Parts SY"
