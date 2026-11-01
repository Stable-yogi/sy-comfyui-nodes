"""Text Chunker SY: splits a long text into pieces of at most N characters, with an overlap, and gives one piece by index."""
try:
    from ._sy_common import category, register
except ImportError:  # run as a plain file by the selftest
    from _sy_common import category, register


def split_chunks(text, max_chars, overlap=0):
    """Pure function. Returns a list of chunks, each at most max_chars long.
    A cut is moved back to the last space when that space is in the second half of the piece, so words stay whole."""
    if not isinstance(text, str):
        raise ValueError("text must be a string, got %s" % type(text).__name__)
    max_chars = int(max_chars)
    overlap = int(overlap)
    if max_chars < 1:
        raise ValueError("max_chars must be at least 1, got %d" % max_chars)
    if overlap < 0:
        raise ValueError("overlap must be 0 or more, got %d" % overlap)
    if overlap >= max_chars:
        raise ValueError("overlap (%d) must be smaller than max_chars (%d)" % (overlap, max_chars))
    if text == "":
        raise ValueError("text is empty: there is nothing to split")
    size = len(text)
    chunks = []
    start = 0
    while True:
        end = min(start + max_chars, size)
        if end < size:
            cut = max(text.rfind(" ", start, end), text.rfind("\n", start, end))
            if cut > start + max_chars // 2:
                end = cut + 1
        chunks.append(text[start:end])
        if end >= size:
            break
        nxt = end - overlap
        start = nxt if nxt > start else end
    return chunks


INDEX_MODES = ("stop with an error", "wrap around", "stay on the last")


def resolve_index(count, index, index_mode=INDEX_MODES[0]):
    """Pure function. Turns the wanted index into a real piece number (or raises a plain error)."""
    index = int(index)
    if index_mode not in INDEX_MODES:
        raise ValueError("index_mode must be one of: %s" % ", ".join(INDEX_MODES))
    if 0 <= index < count:
        return index
    if index < 0:
        raise ValueError("index %d is negative: use 0 to %d" % (index, count - 1))
    if index_mode == INDEX_MODES[1]:
        return index % count
    if index_mode == INDEX_MODES[2]:
        return count - 1
    raise ValueError("index %d is out of range: the text has %d chunks (use 0 to %d, or set index_mode to wrap around)" % (index, count, count - 1))


def pick_chunk(chunks, index, index_mode=INDEX_MODES[0]):
    """Pure function. index counts from 0; by default a bad index is an error, not a wrap."""
    return chunks[resolve_index(len(chunks), index, index_mode)]


def chunk_info(chunks, index, real_index, overlap):
    """Pure function. One plain line: which piece, how big, and the longest/shortest piece."""
    line = "Piece %d of %d (%d characters, overlap %d)" % (real_index + 1, len(chunks), len(chunks[real_index]), overlap)
    if real_index != int(index):
        line += "; index %d was moved to %d" % (int(index), real_index)
    return line


class SYTextChunker:
    DESCRIPTION = ("Splits a long text into pieces of at most a set number of characters, with overlap. Gives you one piece by index, the piece count "
                   "and all pieces as a list. An index too big can wrap around instead of stopping.")
    CATEGORY = category("Text")
    FUNCTION = "run"
    RETURN_TYPES = ("STRING", "INT", "STRING", "STRING")
    RETURN_NAMES = ("chunk", "count", "all_chunks", "info")
    OUTPUT_IS_LIST = (False, False, True, False)

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "text": ("STRING", {"multiline": True, "default": "", "tooltip": "The long text to split."}),
                "max_chars": ("INT", {"default": 1000, "min": 1, "max": 1000000, "tooltip": "Longest allowed piece, in characters."}),
                "overlap": ("INT", {"default": 100, "min": 0, "max": 999999, "tooltip": "Characters repeated at the start of the next piece. Less than max_chars."}),
                "index": ("INT", {"default": 0, "min": 0, "max": 1000000, "tooltip": "Which piece to output, counting from 0."}),
            },
            "optional": {
                "index_mode": (list(INDEX_MODES), {"default": INDEX_MODES[0], "tooltip": "If index is past the last piece: stop with an error, start again at 0, or stay on the last piece."}),
            },
        }

    def run(self, text, max_chars, overlap, index, index_mode=INDEX_MODES[0]):
        chunks = split_chunks(text, max_chars, overlap)
        real = resolve_index(len(chunks), index, index_mode)
        return (chunks[real], len(chunks), chunks, chunk_info(chunks, index, real, overlap))


NODE_CLASS_MAPPINGS = {}
NODE_DISPLAY_NAME_MAPPINGS = {}
register(NODE_CLASS_MAPPINGS, NODE_DISPLAY_NAME_MAPPINGS, "TextChunker", SYTextChunker)
NODE_DISPLAY_NAME_MAPPINGS["SYTextChunker"] = "Text Chunker SY"
