"""Date Add SY: adds days, weeks, months, years or business days to a date."""
import datetime

try:
    from ._sy_common import category, register
except ImportError:  # run as a plain file by the selftest
    from _sy_common import category, register

UNITS = ("days", "weeks", "months", "years", "business days")
FORMATS = ("YYYY-MM-DD", "DD/MM/YYYY", "D Month YYYY", "weekday, D Month YYYY")
MONTH_NAMES = ("January", "February", "March", "April", "May", "June", "July", "August",
               "September", "October", "November", "December")
WEEKDAY_NAMES = ("Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday")


def parse_date(text, today=None):
    """Pure function. Reads YYYY-MM-DD, DD/MM/YYYY or the word today. Returns a datetime.date.
    today is only for tests; leave it out to use the local date."""
    if not isinstance(text, str) or text.strip() == "":
        raise ValueError("date is empty: type YYYY-MM-DD, DD/MM/YYYY or today")
    s = text.strip()
    if s.lower() == "today":
        return today if today is not None else datetime.date.today()
    try:
        if "-" in s:
            parts = s.split("-")
            if len(parts) != 3 or len(parts[0]) != 4:
                raise ValueError
            y, mo, d = (int(p) for p in parts)
        elif "/" in s:
            parts = s.split("/")
            if len(parts) != 3 or len(parts[2]) != 4:
                raise ValueError
            d, mo, y = (int(p) for p in parts)
        else:
            raise ValueError
        return datetime.date(y, mo, d)
    except ValueError:
        raise ValueError("cannot read the date %r as a real date: use YYYY-MM-DD or DD/MM/YYYY (for example 2026-01-31) or today" % s) from None


def _last_day(y, m):
    nxt = datetime.date(y + (m == 12), m % 12 + 1, 1)
    return (nxt - datetime.timedelta(days=1)).day


def _add_months(y, m, d, months):
    total = y * 12 + (m - 1) + months
    ny, nm = divmod(total, 12)
    nm += 1
    if ny < 1 or ny > 9999:
        raise ValueError("the result is outside the years 1 to 9999: use a smaller amount")
    return datetime.date(ny, nm, min(d, _last_day(ny, nm)))


def add_to_date(y, m, d, amount, unit):
    """Pure function. Returns a datetime.date. Months and years clamp the day to the last day of the month
    (31 Jan + 1 month = 28 or 29 Feb). Business days skip Saturday and Sunday; holidays are not known."""
    if unit not in UNITS:
        raise ValueError("unit must be one of: %s (got %r)" % (", ".join(UNITS), unit))
    amount = int(amount)
    start = datetime.date(y, m, d)
    try:
        if unit == "days":
            return start + datetime.timedelta(days=amount)
        if unit == "weeks":
            return start + datetime.timedelta(weeks=amount)
        if unit == "months":
            return _add_months(y, m, d, amount)
        if unit == "years":
            return _add_months(y, m, d, amount * 12)
        step = 1 if amount >= 0 else -1
        cur, left = start, abs(amount)
        while left > 0:
            cur += datetime.timedelta(days=step)
            if cur.weekday() < 5:
                left -= 1
        return cur
    except OverflowError:
        raise ValueError("the result is outside the years 1 to 9999: use a smaller amount") from None


def format_date(dt, fmt):
    """Pure function. Writes a date in one of the output formats (English names)."""
    if fmt == "YYYY-MM-DD":
        return "%04d-%02d-%02d" % (dt.year, dt.month, dt.day)
    if fmt == "DD/MM/YYYY":
        return "%02d/%02d/%04d" % (dt.day, dt.month, dt.year)
    if fmt == "D Month YYYY":
        return "%d %s %d" % (dt.day, MONTH_NAMES[dt.month - 1], dt.year)
    if fmt == "weekday, D Month YYYY":
        return "%s, %d %s %d" % (WEEKDAY_NAMES[dt.weekday()], dt.day, MONTH_NAMES[dt.month - 1], dt.year)
    raise ValueError("output_format must be one of: %s (got %r)" % (", ".join(FORMATS), fmt))


def date_add(date_text, amount, unit, output_format, today=None):
    """Pure function. Returns (date_text, weekday, day_of_year, days_between)."""
    start = parse_date(date_text, today)
    end = add_to_date(start.year, start.month, start.day, amount, unit)
    text = format_date(end, output_format)
    return (text, WEEKDAY_NAMES[end.weekday()], end.timetuple().tm_yday, (end - start).days)


class SYDateAdd:
    DESCRIPTION = ("Adds days, weeks, months, years or business days to a date. Months and years stay on the last "
                   "day of a short month. Business days skip weekends but not holidays.")
    CATEGORY = category("Values")
    FUNCTION = "run"
    RETURN_TYPES = ("STRING", "STRING", "INT", "INT")
    RETURN_NAMES = ("date", "weekday", "day_of_year", "days_between")

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "date": ("STRING", {"default": "2026-01-31", "tooltip": "The start date: YYYY-MM-DD, DD/MM/YYYY, or the word today."}),
                "amount": ("INT", {"default": 7, "min": -100000, "max": 100000, "tooltip": "How many units to add. A negative number goes back in time."}),
                "unit": (list(UNITS), {"default": "days", "tooltip": "What the amount counts. Business days skip Saturday and Sunday."}),
                "output_format": (list(FORMATS), {"default": "YYYY-MM-DD", "tooltip": "How the result date is written."}),
            }
        }

    @classmethod
    def IS_CHANGED(cls, date, amount, unit, output_format):
        # "today" changes by itself every day, so run again when the local date changes
        if isinstance(date, str) and date.strip().lower() == "today":
            return datetime.date.today().isoformat()
        return ""

    def run(self, date, amount, unit, output_format):
        return date_add(date, amount, unit, output_format)


NODE_CLASS_MAPPINGS = {}
NODE_DISPLAY_NAME_MAPPINGS = {}
register(NODE_CLASS_MAPPINGS, NODE_DISPLAY_NAME_MAPPINGS, "DateAdd", SYDateAdd)
NODE_DISPLAY_NAME_MAPPINGS["SYDateAdd"] = "Date Add SY"
