"""Edge Detect SY: turns a picture into a grey edge map (Sobel or Laplacian)."""
try:
    from ._sy_common import category, register
    from ._sy_image_ops import need_image, clamp01
except ImportError:  # run as a plain file by the selftest
    from _sy_common import category, register
    from _sy_image_ops import need_image, clamp01

METHODS = ("sobel", "laplacian")
SOBEL_X = [[-1.0, 0.0, 1.0], [-2.0, 0.0, 2.0], [-1.0, 0.0, 1.0]]
SOBEL_Y = [[-1.0, -2.0, -1.0], [0.0, 0.0, 0.0], [1.0, 2.0, 1.0]]
LAPLACE = [[0.0, -1.0, 0.0], [-1.0, 4.0, -1.0], [0.0, -1.0, 0.0]]


def luma(r, g, b):
    """Pure function. Brightness of one colour (weights 0.2126, 0.7152, 0.0722)."""
    return 0.2126 * r + 0.7152 * g + 0.0722 * b


def convolve_2d(grid, kernel):
    """Pure function. Slides an odd-sized kernel over a list of rows. Edge pixels repeat the nearest border pixel."""
    h = len(grid)
    if h == 0 or len(grid[0]) == 0:
        raise ValueError("the grid must have at least one row and one column")
    w = len(grid[0])
    kh, kw = len(kernel), len(kernel[0])
    if kh % 2 == 0 or kw % 2 == 0:
        raise ValueError("the kernel must have an odd number of rows and columns")
    oy, ox = kh // 2, kw // 2
    out = []
    for y in range(h):
        row = []
        for x in range(w):
            acc = 0.0
            for j in range(kh):
                yy = min(h - 1, max(0, y + j - oy))
                for i in range(kw):
                    xx = min(w - 1, max(0, x + i - ox))
                    acc += kernel[j][i] * grid[yy][xx]
            row.append(acc)
        out.append(row)
    return out


def edge_value(method, gx, gy, strength, invert):
    """Pure function. One finished edge value 0..1. For laplacian only gx is used (the Laplacian response)."""
    if method == "sobel":
        v = (gx * gx + gy * gy) ** 0.5 / 4.0
    elif method == "laplacian":
        v = abs(gx) / 4.0
    else:
        raise ValueError("method must be one of: %s" % ", ".join(METHODS))
    v = clamp01(v * strength)
    return 1.0 - v if invert else v


def check_settings(method, strength):
    if method not in METHODS:
        raise ValueError("method must be one of: %s, got %r" % (", ".join(METHODS), method))
    if not 0.1 <= strength <= 10.0:
        raise ValueError("strength must be between 0.1 and 10, got %s" % strength)


def edge_map(grid, method, strength, invert):
    """Pure function. Grey grid (list of rows, values 0..1) in, finished edge grid out."""
    check_settings(method, strength)
    if method == "sobel":
        gx = convolve_2d(grid, SOBEL_X)
        gy = convolve_2d(grid, SOBEL_Y)
    else:
        gx = convolve_2d(grid, LAPLACE)
        gy = gx
    return [[edge_value(method, gx[y][x], gy[y][x], strength, invert) for x in range(len(grid[0]))] for y in range(len(grid))]


class SYEdgeDetect:
    DESCRIPTION = "Finds the outlines in a picture and draws them as a grey edge map. Strong edges are bright, flat areas are dark."
    CATEGORY = category("Image")
    FUNCTION = "run"
    RETURN_TYPES = ("IMAGE", "MASK")
    RETURN_NAMES = ("image", "mask")

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "image": ("IMAGE", {"tooltip": "The picture or batch of pictures to find edges in."}),
                "method": (list(METHODS), {"default": "sobel", "tooltip": "Sobel gives smooth thick edges. Laplacian gives thin sharp lines."}),
                "strength": ("FLOAT", {"default": 1.0, "min": 0.1, "max": 10.0, "step": 0.1, "tooltip": "Brightness boost for the edges. Raise it to see faint edges."}),
                "invert": ("BOOLEAN", {"default": False, "tooltip": "Turn on for dark lines on a white background."}),
            }
        }

    def run(self, image, method, strength, invert):
        import torch
        import torch.nn.functional as F

        need_image(image)
        check_settings(method, strength)
        rgb = image[..., :3].to(torch.float32)
        grey = (0.2126 * rgb[..., 0] + 0.7152 * rgb[..., 1] + 0.0722 * rgb[..., 2]).unsqueeze(1)
        x = F.pad(grey, (1, 1, 1, 1), mode="replicate")

        def conv(k):
            kt = torch.tensor(k, dtype=torch.float32, device=x.device).view(1, 1, 3, 3)
            # conv2d is a correlation, which matches the plain sliding sum used by convolve_2d
            return F.conv2d(x, kt)

        if method == "sobel":
            gx, gy = conv(SOBEL_X), conv(SOBEL_Y)
            v = torch.sqrt(gx * gx + gy * gy) / 4.0
        else:
            v = conv(LAPLACE).abs() / 4.0
        v = (v * float(strength)).clamp(0.0, 1.0)
        if invert:
            v = 1.0 - v
        mask = v[:, 0].contiguous()
        out = mask.unsqueeze(-1).repeat(1, 1, 1, 3).to(image.dtype)
        return (out, mask.to(image.dtype))


NODE_CLASS_MAPPINGS = {}
NODE_DISPLAY_NAME_MAPPINGS = {}
register(NODE_CLASS_MAPPINGS, NODE_DISPLAY_NAME_MAPPINGS, "EdgeDetect", SYEdgeDetect)
NODE_DISPLAY_NAME_MAPPINGS["SYEdgeDetect"] = "Edge Detect SY"
