"""H3 Latent Upscaler SY: makes a Minimax H3 video latent bigger with a trained 3D network, without a VAE round trip.

Ported from: Comfyui_Minimax_h3_latent_Upscaler (MinimaxH3LatentUpscaler3D)
Original author: LBH-123-AI. Licence: MIT (copy in third_party/Comfyui_Minimax_h3_latent_Upscaler/LICENSE).
Copyright (c) 2026 LBH-123-AI.
Changed by Stable Yogi (renamed, SY standard, size and chunk maths split into pure functions, no ComfyUI io schema).

Only the 3D variant is ported. The model file (Apache-2.0, by the same author) is NOT bundled: the user puts it in
ComfyUI/models/latent_upscale_models/. This saves time, not VRAM: the refine pass still runs at the target size.
"""
import gc
import re

try:
    from ._sy_common import category, register
    from ._sy_model_files import list_names, find_file
except ImportError:  # run as a plain file by the selftest
    from _sy_common import category, register
    from _sy_model_files import list_names, find_file

FOLDER = "latent_upscale_models"
VAE_DOWNSAMPLE = 16
CHUNK = 32
MODES = ("scale by multiplier", "target dimensions", "megapixels")
DEVICES = ("cuda", "rocm", "cpu")
PRECISIONS = ("fp16", "bf16", "fp32")
NO_MODEL = "(none: put a model file in models/latent_upscale_models)"

# Minimax H3 latent normalisation (24 channels).
LATENTS_MEAN = [
    0.858090341091156, -0.9606591463088989, 1.0661640167236328, -0.5090325474739075,
    -0.2727581858634949, -1.3675414323806763, -0.2553254961967468, -0.26907554268836975,
    -0.5376840829849243, -0.0464097298681736, 0.6657370328903198, 0.19690127670764923,
    -0.5460608005523682, -0.4035342037677765, -0.23683024942874908, 0.25928452610969543,
    -0.30133944749832153, 0.211341992020607, -1.1206848621368408, 0.3581933379173279,
    -0.04225143790245056, 0.2604829967021942, 0.22864092886447906, 0.7056031823158264,
]
LATENTS_STD = [
    1.2223774194717407, 1.2767263650894165, 1.6831774711608887, 1.7549455165863037,
    1.5636216402053833, 2.194143533706665, 0.9653137922286987, 1.0569885969161987,
    0.841948926448822, 0.7729952931404114, 1.8955937623977661, 0.946841835975647,
    0.7996809482574463, 0.44988900423049927, 0.7197399735450745, 0.6936293244361877,
    2.961095094680786, 2.7694199085235596, 3.0496184825897217, 2.1088054180145264,
    3.276226282119751, 3.1627357006073, 2.2816812992095947, 2.6127843856811523,
]


def plan_target(w_in, h_in, mode, scale=2.0, width=1280, height=704, megapixels=1.0, align=32):
    """Pure function. Latent size in, new latent size out. Returns (w_out, h_out, effective_scale).

    Sizes are latent cells; one cell is 16 pixels. The pixel target is rounded to `align`, then to the 16 pixel grid."""
    if mode not in MODES:
        raise ValueError("mode must be one of %s, got %r" % (", ".join(MODES), mode))
    if w_in < 1 or h_in < 1:
        raise ValueError("the latent has no size: %dx%d" % (w_in, h_in))
    if mode == MODES[0]:
        w_px, h_px, eff = w_in * VAE_DOWNSAMPLE * scale, h_in * VAE_DOWNSAMPLE * scale, float(scale)
    else:
        if mode == MODES[1]:
            w_px, h_px = float(width), float(height)
        else:
            aspect = w_in / h_in
            h_px = (megapixels * 1024 * 1024 / aspect) ** 0.5
            w_px = h_px * aspect
        eff = (w_px / (w_in * VAE_DOWNSAMPLE) + h_px / (h_in * VAE_DOWNSAMPLE)) / 2.0
    grid = max(1, int(align))
    w_al = round(w_px / grid) * grid
    h_al = round(h_px / grid) * grid
    w_out = max(1, int(round(w_al / VAE_DOWNSAMPLE) * VAE_DOWNSAMPLE) // VAE_DOWNSAMPLE)
    h_out = max(1, int(round(h_al / VAE_DOWNSAMPLE) * VAE_DOWNSAMPLE) // VAE_DOWNSAMPLE)
    if eff < 1.0 and (w_out < w_in or h_out < h_in):
        raise ValueError("this model only makes a latent bigger (scale 1.0 or more), got scale %.3f" % eff)
    return w_out, h_out, eff


def chunk_ranges(frames, overlap, chunk=CHUNK):
    """Pure function. Time chunks as tuples (seg_start, seg_end, out_start, out_end, lo, hi).

    lo..hi are positions in the replicate-padded input; out_start..out_end are the output frames the chunk fills."""
    out = []
    start = 0
    while start < frames:
        seg_end = min(frames, start + chunk)
        out_start = max(0, start - overlap)
        out_end = min(frames, seg_end + overlap)
        lo = max(0, out_start - overlap)
        hi = min(frames + 2 * overlap, out_end + overlap)
        out.append((start, seg_end, out_start, out_end, lo, hi))
        start += chunk
    return out


def blend_weights(n_valid, lead, tail):
    """Pure function. Weights of one chunk: a ramp up over `lead` frames, a ramp down over `tail` frames, 1 between."""
    w = [1.0] * n_valid
    for i in range(min(lead, n_valid)):
        w[i] = (i + 1) / (lead + 1)
    for i in range(min(tail, n_valid)):
        w[n_valid - 1 - i] = (i + 1) / (tail + 1)
    return w


def detect_arch(keys_shapes):
    """Pure function. Network settings from a {name: shape tuple} map of the checkpoint."""
    cfg = {"in_channels": 24, "in_blocks": 12, "out_blocks": 12, "channels": 512, "temporal_every": 2,
           "temporal_kernel": 5}
    if "conv_in.weight" in keys_shapes:
        cfg["channels"], cfg["in_channels"] = keys_shapes["conv_in.weight"][0], keys_shapes["conv_in.weight"][1]
    in_ids, out_ids, has_temporal = set(), set(), False
    for k, shape in keys_shapes.items():
        m = re.match(r"in_blocks\.(\d+)\.in_layers\.", k)
        if m:
            in_ids.add(int(m.group(1)))
        m = re.match(r"out_blocks\.(\d+)\.in_layers\.", k)
        if m:
            out_ids.add(int(m.group(1)))
        if re.match(r"(in|out)_blocks\.\d+\.dwconv\.weight$", k):
            has_temporal = True
            cfg["temporal_kernel"] = shape[2]
    if in_ids:
        cfg["in_blocks"] = len(in_ids)
    if out_ids:
        cfg["out_blocks"] = len(out_ids)
    if not has_temporal:
        cfg["temporal_every"] = 0
    return cfg


_NET_CLASS = None


def _net_class():
    """Build the network class on first use, so importing this file never needs torch."""
    global _NET_CLASS
    if _NET_CLASS is not None:
        return _NET_CLASS
    import torch
    import torch.nn as nn
    import torch.nn.functional as F

    def norm(channels):
        return nn.GroupNorm(32, channels)

    class ResBlock(nn.Module):
        def __init__(self, channels, emb_channels, dropout=0.0):
            super().__init__()
            self.in_layers = nn.Sequential(norm(channels), nn.SiLU(), nn.Conv3d(channels, channels, 3, padding=1))
            self.emb_layers = nn.Sequential(nn.SiLU(), nn.Linear(emb_channels, 2 * channels))
            self.out_norm = norm(channels)
            self.out_layers = nn.Sequential(nn.SiLU(), nn.Dropout(p=dropout), nn.Conv3d(channels, channels, 3, padding=1))
            self.skip = nn.Identity()

        def forward(self, x, emb):
            h = self.in_layers(x)
            e = self.emb_layers(emb).type(h.dtype)
            while e.dim() < h.dim():
                e = e[..., None]
            scale, shift = torch.chunk(e, 2, dim=1)
            h = self.out_norm(h) * (1 + scale) + shift
            return self.skip(x) + self.out_layers(h)

    class TemporalConv(nn.Module):
        def __init__(self, channels, kernel_size=5):
            super().__init__()
            self.norm = norm(channels)
            self.dwconv = nn.Conv3d(channels, channels, kernel_size=(kernel_size, 1, 1),
                                    padding=(kernel_size // 2, 0, 0), groups=channels)
            self.pwconv = nn.Conv3d(channels, channels, kernel_size=1)

        def forward(self, x):
            return x + self.pwconv(self.dwconv(F.silu(self.norm(x))))

    class Net(nn.Module):
        def __init__(self, in_channels=24, in_blocks=12, out_blocks=12, channels=512, temporal_every=2,
                     temporal_kernel=5):
            super().__init__()
            self.conv_in = nn.Conv3d(in_channels, channels, 3, padding=1)
            embed_dim = 64
            self.embed = nn.Sequential(nn.Linear(1, embed_dim), nn.SiLU(), nn.Linear(embed_dim, embed_dim))

            def stack(n):
                blocks = nn.ModuleList()
                for b in range(n):
                    blocks.append(ResBlock(channels, embed_dim))
                    if temporal_every > 0 and b % temporal_every == 0:
                        blocks.append(TemporalConv(channels, temporal_kernel))
                return blocks

            self.in_blocks = stack(in_blocks)
            self.out_blocks = stack(out_blocks)
            self.norm_out = norm(channels)
            self.conv_out = nn.Conv3d(channels, in_channels, 3, padding=1)

        def _segment(self, x, scale, size):
            emb = self.embed(torch.tensor([[scale - 1]], dtype=x.dtype, device=x.device))
            x = self.conv_in(x)
            for b in self.in_blocks:
                x = b(x, emb.expand(x.shape[0], -1)) if isinstance(b, ResBlock) else b(x)
            x = F.interpolate(x, size=size, mode="trilinear", align_corners=False)
            for b in self.out_blocks:
                x = b(x, emb.expand(x.shape[0], -1)) if isinstance(b, ResBlock) else b(x)
            return self.conv_out(F.silu(self.norm_out(x)))

        def forward(self, x, scale, target_size, chunking=True):
            if tuple(target_size) == tuple(x.shape[-3:]):
                return x
            bsz, ch, frames = x.shape[0], x.shape[1], x.shape[2]
            overlap = 0
            for b in self.in_blocks:
                if isinstance(b, TemporalConv):
                    overlap = b.dwconv.weight.shape[2]
                    break
            if not chunking or frames <= CHUNK:
                return self._segment(x, scale, tuple(target_size))
            padded = F.pad(x, (0, 0, 0, 0, overlap, overlap), mode="replicate")
            out_full = torch.zeros(bsz, ch, frames, target_size[-2], target_size[-1], device=x.device, dtype=x.dtype)
            weight_full = torch.zeros(1, 1, frames, 1, 1, device=x.device, dtype=x.dtype)
            for n, (s0, s1, o0, o1, lo, hi) in enumerate(chunk_ranges(frames, overlap)):
                seg = padded[:, :, lo:hi].contiguous()
                seg_out = self._segment(seg, scale, (hi - lo, target_size[-2], target_size[-1]))
                a = (o0 + overlap) - lo
                valid = seg_out[:, :, a:a + (o1 - o0)]
                w = torch.tensor(blend_weights(o1 - o0, s0 - o0, o1 - s1), device=x.device, dtype=x.dtype)
                out_full[:, :, o0:o1] += valid * w.view(1, 1, -1, 1, 1)
                weight_full[:, :, o0:o1] += w.view(1, 1, -1, 1, 1)
                del seg, seg_out, valid
                if (n + 1) % 4 == 0:
                    gc.collect()
            return out_full / weight_full.clamp(min=1e-8)

    _NET_CLASS = Net
    return Net


_MODEL_CACHE = {}


def _load_model(name, device, precision):
    import torch
    key = "%s::%s::%s" % (name, device.type, precision)
    if key in _MODEL_CACHE:
        return _MODEL_CACHE[key].to(device)
    path = find_file(FOLDER, name)
    if path.lower().endswith(".safetensors"):
        from safetensors.torch import load_file
        sd = load_file(path, device="cpu")
    else:
        sd = torch.load(path, map_location="cpu", weights_only=True)
    if isinstance(sd, dict) and "model" in sd:
        sd = sd["model"]
    if any(k.startswith("upscaler.") for k in sd):
        sd = {k[len("upscaler."):]: v for k, v in sd.items() if k.startswith("upscaler.")}
    sd = {k: (v.to(torch.float16) if v.dtype == torch.float8_e4m3fn else v) for k, v in sd.items()}
    cfg = detect_arch({k: tuple(v.shape) for k, v in sd.items()})
    net = _net_class()(**cfg)
    net.load_state_dict(sd, strict=True)
    dtype = {"fp32": torch.float32, "fp16": torch.float16, "bf16": torch.bfloat16}[precision]
    net = net.to(device).eval().requires_grad_(False).to(dtype)
    _MODEL_CACHE[key] = net
    return net


def _device(backend):
    import torch
    if backend == "cpu":
        return torch.device("cpu")
    if backend == "rocm" and getattr(torch.version, "hip", None) is None:
        raise ValueError("device rocm was picked, but this PyTorch build has no ROCm support")
    if backend in ("cuda", "rocm"):
        if not torch.cuda.is_available():
            raise ValueError("device %s was picked, but PyTorch sees no GPU. Pick cpu or fix the GPU setup." % backend)
        return torch.device("cuda")
    raise ValueError("device must be one of %s, got %r" % (", ".join(DEVICES), backend))


class SYH3LatentUpscaler:
    DESCRIPTION = ("Makes a Minimax H3 video latent bigger with a trained 3D network, without decoding it first. "
                   "Needs a model file in models/latent_upscale_models. Saves time, not VRAM. "
                   "Feed it the VIDEO latent only (split the sound latent off first).")
    CATEGORY = category("Resize")
    FUNCTION = "run"
    RETURN_TYPES = ("LATENT",)
    RETURN_NAMES = ("latent",)

    @classmethod
    def INPUT_TYPES(cls):
        names = [n for n in list_names(FOLDER) if n.lower().endswith((".safetensors", ".pth"))] or [NO_MODEL]
        return {"required": {
            "latent": ("LATENT", {"tooltip": "The video latent (24 channels). Not the joined video+sound latent."}),
            "model_name": (names, {"tooltip": "Upscaler file from models/latent_upscale_models."}),
            "mode": (list(MODES), {"default": MODES[0], "tooltip": "How the new size is chosen. Only the matching number is used."}),
            "scale": ("FLOAT", {"default": 2.0, "min": 1.0, "max": 4.0, "step": 0.05, "tooltip": "Used by 'scale by multiplier'."}),
            "width": ("INT", {"default": 1280, "min": 64, "max": 8192, "step": 8, "tooltip": "Used by 'target dimensions': new width in pixels."}),
            "height": ("INT", {"default": 704, "min": 64, "max": 8192, "step": 8, "tooltip": "Used by 'target dimensions': new height in pixels."}),
            "megapixels": ("FLOAT", {"default": 1.0, "min": 0.1, "max": 16.0, "step": 0.1, "tooltip": "Used by 'megapixels': new picture size, aspect kept."}),
            "align": ("INT", {"default": 32, "min": 1, "max": 512, "step": 1, "tooltip": "Round the pixel size to this grid. 32 is best."}),
            "enable_temporal_chunking": ("BOOLEAN", {"default": True, "tooltip": "Work on 32 frames at a time. Saves memory on long clips."}),
            "force_unload": ("BOOLEAN", {"default": True, "tooltip": "Move the model to the CPU when done, to free VRAM for the next node."}),
            "device": (list(DEVICES), {"default": "cuda", "tooltip": "cuda is the normal choice for an NVIDIA card."}),
            "precision": (list(PRECISIONS), {"default": "fp16", "tooltip": "fp16 matches the model file."}),
        }}

    def run(self, latent, model_name, mode, scale, width, height, megapixels, align, enable_temporal_chunking,
            force_unload, device, precision):
        import torch
        if model_name == NO_MODEL:
            raise ValueError("no upscaler model found: put a file in ComfyUI/models/latent_upscale_models and refresh")
        src = latent["samples"]
        if getattr(src, "is_nested", False) or src.dim() not in (4, 5):
            raise ValueError("this node needs the plain video latent (4 or 5 dimensions). "
                             "A joined video+sound latent must be split first (Separate AV Latent).")
        dev = _device(device)
        dtype = {"fp32": torch.float32, "fp16": torch.float16, "bf16": torch.bfloat16}[precision]
        was_4d = src.dim() == 4
        s = src.to(device=dev, dtype=dtype, copy=True)
        if was_4d:
            s = s.unsqueeze(2)
        if s.shape[1] != len(LATENTS_MEAN):
            raise ValueError("this upscaler needs an H3 video latent with %d channels, got %d"
                             % (len(LATENTS_MEAN), s.shape[1]))
        t, h_in, w_in = s.shape[2], s.shape[3], s.shape[4]
        w_out, h_out, eff = plan_target(w_in, h_in, mode, scale, width, height, megapixels, align)
        if (w_out, h_out) == (w_in, h_in):
            return (latent,)
        model = _load_model(model_name, dev, precision)
        mean = torch.tensor(LATENTS_MEAN, dtype=dtype, device=dev).view(1, -1, 1, 1, 1)
        std = torch.tensor(LATENTS_STD, dtype=dtype, device=dev).view(1, -1, 1, 1, 1)
        with torch.inference_mode():
            out = model((s - mean) / std, eff, (t, h_out, w_out), enable_temporal_chunking) * std + mean
        if was_4d:
            out = out.squeeze(2)
        result = dict(latent)
        result["samples"] = out.to(device="cpu", dtype=src.dtype)
        result.pop("noise_mask", None)  # the old mask no longer fits the new size
        if dev.type == "cuda":
            if force_unload:
                model.to("cpu")
            try:
                import comfy.model_management as mm
                mm.soft_empty_cache()
            except Exception:
                torch.cuda.empty_cache()
            gc.collect()
        return (result,)


NODE_CLASS_MAPPINGS = {}
NODE_DISPLAY_NAME_MAPPINGS = {}
register(NODE_CLASS_MAPPINGS, NODE_DISPLAY_NAME_MAPPINGS, "H3LatentUpscaler", SYH3LatentUpscaler)
