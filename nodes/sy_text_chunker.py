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


def pick_chunk(chunks, index):
    """Pure function. index counts from 0; a bad index is an error, not a wrap."""
    index = int(index)
    if index < 0 or index >= len(chunks):
        raise ValueError("index %d is out of range: the text has %d chunks (use 0 to %d)" % (index, len(chunks), len(chunks) - 1))
    return chunks[index]


class SYTextChunker:
    DESCRIPTION = "Splits a long text into pieces of at most a set number of characters, with overlap. Gives you one piece by index, and the piece count."
    CATEGORY = category("Text")
    FUNCTION = "run"
    RETURN_TYPES = ("STRING", "INT")
    RETURN_NAMES = ("chunk", "count")

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "text": ("STRING", {"multiline": True, "default": "", "tooltip": "The long text to split."}),
                "max_chars": ("INT", {"default": 1000, "min": 1, "max": 1000000, "tooltip": "Longest allowed piece, in characters."}),
                "overlap": ("INT", {"default": 100, "min": 0, "max": 999999, "tooltip": "Characters repeated at the start of the next piece. Less than max_chars."}),
                "index": ("INT", {"default": 0, "min": 0, "max": 1000000, "tooltip": "Which piece to output, counting from 0."}),
            }
        }

    def run(self, text, max_chars, overlap, index):
        chunks = split_chunks(text, max_chars, overlap)
        return (pick_chunk(chunks, index), len(chunks))


NODE_CLASS_MAPPINGS = {}
NODE_DISPLAY_NAME_MAPPINGS = {}
register(NODE_CLASS_MAPPINGS, NODE_DISPLAY_NAME_MAPPINGS, "TextChunker", SYTextChunker)
NODE_DISPLAY_NAME_MAPPINGS["SYTextChunker"] = "Text Chunker SY"
