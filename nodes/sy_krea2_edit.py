"""Krea2 Edit SY: two nodes for Krea 2 edit models (source patch and grounded encode).

Ported from: comfyui-krea2edit (Krea2EditModelPatch, Krea2EditGroundedEncode)
Original author: lbouaraba (repository owner; the source files name no other author). Licence: Apache-2.0
(copy in third_party/comfyui-krea2edit/LICENSE).
Changed by Stable Yogi (renamed, SY standard; the pure geometry and prompt logic moved into plain functions).

Krea2EditModelPatch wraps the model's forward pass. The sequence becomes [text | source(frame=1) | target(frame=0)]:
the clean source picture is prepended as tokens, told apart from the noisy target only by the frame index in the
3-axis position code, and only the target tokens come out.

Krea2EditGroundedEncode encodes the edit instruction together with the source picture through the vision text
encoder, so the instruction can say "the man on the left".

Wiring: LoadImage -> VAEEncode -> Krea2EditModelPatch(model, source_latent) -> KSampler.
"""
from __future__ import annotations

import math

try:
    from ._sy_common import category, register
except ImportError:  # run as a plain file by the selftest
    from _sy_common import category, register


FIT_CROP_TOL = 0.08
VISION_BLOCK = "<|vision_start|><|image_pad|><|vision_end|>"
DEFAULT_SYSTEM = (
    "Describe the image by detailing the color, shape, size, "
    "texture, quantity, text, spatial relationships of the objects and background:"
)


# ---------------------------------------------------------------- pure logic (plain Python values)

def center_crop_box(sh, sw, H, W):
    """Pure function. Centered crop of an (sh x sw) picture to the aspect ratio of (H x W). Returns (y0, x0, ch, cw)."""
    s = max(H / sh, W / sw)
    ch, cw = min(sh, int(round(H / s))), min(sw, int(round(W / s)))
    y0, x0 = (sh - ch) // 2, (sw - cw) // 2
    return y0, x0, ch, cw


def plan_pixel_fit(ih, iw, px_h, px_w, fit_mode="crop"):
    """Pure function. How a source picture of ih x iw is prepared for a target of px_h x px_w pixels.

    Returns {"box": (y0, x0, ch, cw) or None, "size": (new_h, new_w)}: crop to the box (if any), then resize to size.
    """
    if fit_mode == "fit":
        sc = min(px_h / ih, px_w / iw)
        # near-matched aspect ratio: fill the target grid exactly with a minimal centered crop
        if ih * sc >= px_h * (1 - FIT_CROP_TOL) and iw * sc >= px_w * (1 - FIT_CROP_TOL):
            return {"box": center_crop_box(ih, iw, px_h, px_w), "size": (px_h, px_w)}
        # real aspect mismatch: /16 floor snap, capped at the target's /16 floor
        nh = min(max(16, int(ih * sc) // 16 * 16), max(16, px_h // 16 * 16))
        nw = min(max(16, int(iw * sc) // 16 * 16), max(16, px_w // 16 * 16))
        return {"box": None, "size": (nh, nw)}
    return {"box": center_crop_box(ih, iw, px_h, px_w), "size": (px_h, px_w)}


def centered_offset(gh, gw, th, tw):
    """Pure function. Integer (row, column) offset that centers a gh x gw grid inside a th x tw grid."""
    return max(0, (th - gh) // 2), max(0, (tw - gw) // 2)


def ref_boost_list(ref_boost, ref_boost_a, n_refs):
    """Pure function. One boost factor per reference: earlier refs get ref_boost_a, the last ref gets ref_boost."""
    return [ref_boost_a] * (n_refs - 1) + [ref_boost]


def ref_block_offsets(txtlen, slens):
    """Pure function. Start column of each reference block in [text | refs... | target], plus the first target row."""
    offs = [txtlen]
    for sl in slens:
        offs.append(offs[-1] + sl)
    return offs[:-1], offs[-1]


def boost_bias_value(b):
    """Pure function. The additive attention bias for a boost factor b (log of b, floored at 1e-4)."""
    return math.log(max(b, 1e-4))


def path_modes(fit_mode, has_vae, has_image):
    """Pure function. Returns (ref_native, pos_mode) for the forward pass."""
    return (fit_mode == "fit" and has_vae and has_image), ("stride1" if fit_mode == "fit" else "anchor")


def template_for(nimg, system_prompt=""):
    """Pure function. The text-encoder template with one vision block per reference picture."""
    sp = system_prompt.strip() or DEFAULT_SYSTEM
    vis = VISION_BLOCK * nimg
    return ("<|im_start|>system\n" + sp + "<|im_end|>\n<|im_start|>user\n"
            + vis + "{}<|im_end|>\n<|im_start|>assistant\n")


def future_inputs_warning(names, node_note):
    """Pure function. The console warning for workflow inputs this node version does not know."""
    return (f"[krea2edit] WARNING: workflow provides inputs this node version does not "
            f"know ({', '.join(sorted(names))}). {node_note}")


# ---------------------------------------------------------------- torch part (imports inside)

def _imgids(bs, frame, h_, w_, device):
    import torch

    ids = torch.zeros(h_, w_, 3, device=device, dtype=torch.float32)
    ids[..., 0] = frame
    ids[..., 1] = torch.arange(h_, device=device, dtype=torch.float32)[:, None]
    ids[..., 2] = torch.arange(w_, device=device, dtype=torch.float32)[None, :]
    return ids.reshape(1, h_ * w_, 3).repeat(bs, 1, 1)


def _imgids_offset(bs, frame, gh, gw, th, tw, device):
    """Stride-1 integer positions at a centered integer offset (for fit references)."""
    import torch

    off_h, off_w = centered_offset(gh, gw, th, tw)
    ids = torch.zeros(gh, gw, 3, device=device, dtype=torch.float32)
    ids[..., 0] = frame
    ids[..., 1] = (torch.arange(gh, device=device, dtype=torch.float32) + off_h)[:, None]
    ids[..., 2] = (torch.arange(gw, device=device, dtype=torch.float32) + off_w)[None, :]
    return ids.reshape(1, gh * gw, 3).repeat(bs, 1, 1)


def _to_4d(v):
    """(B,C,T,H,W) -> (B*T,C,H,W); pass 4D through. Images use T=1."""
    if v.ndim == 5:
        b, c, t, h, w = v.shape
        return v.reshape(b * t, c, h, w)
    return v


def _fit_src(src, H, W):
    """Fit a source latent to the target grid: center-crop to the target aspect ratio, then resize."""
    import torch.nn.functional as F

    sh, sw = src.shape[-2:]
    if (sh, sw) == (H, W):
        return src
    y0, x0, ch, cw = center_crop_box(sh, sw, H, W)
    src = src[..., y0:y0 + ch, x0:x0 + cw]
    return F.interpolate(src.float(), size=(H, W), mode="bilinear")


def _fit_encode_image(image, vae, H, W, cache, key, fit_mode="crop"):
    """Pixel-space source prep: crop and resize the IMAGE to the target pixel grid, then VAE-encode. Cached per size."""
    import torch.nn.functional as F

    key = key + (fit_mode,)
    if key in cache:
        return cache[key]
    print(f"[krea2edit] _fit_encode_image: mode={fit_mode} in={tuple(image.shape)} target_latent={H}x{W}", flush=True)
    px_h, px_w = H * 8, W * 8
    img = image.movedim(-1, 1)  # B,H,W,C -> B,C,H,W
    ih, iw = img.shape[-2:]
    plan = plan_pixel_fit(ih, iw, px_h, px_w, fit_mode)
    if plan["box"] is not None:
        y0, x0, ch, cw = plan["box"]
        img = img[..., y0:y0 + ch, x0:x0 + cw]
    nh, nw = plan["size"]
    img = F.interpolate(img.float(), size=(nh, nw), mode="bicubic", antialias=True)
    lat = vae.encode(img.movedim(1, -1)[..., :3].clamp(0, 1))
    cache[key] = lat
    return lat


def _ref_attn_bias(boosts, boost_mask, txtlen, slens, tgtlen, mask_hw, device, dtype):
    """Additive attention-logit bias on the [text | refs... | target] sequence."""
    import torch
    import torch.nn.functional as F

    nsrc = len(slens)
    offs, rows0 = ref_block_offsets(txtlen, slens)
    L = rows0 + tgtlen
    bias = torch.zeros(1, 1, L, L, device=device, dtype=dtype)
    for i, b in enumerate(boosts):
        if b == 1.0:
            continue
        off, sl = offs[i], slens[i]
        if boost_mask is not None and i == nsrc - 1 and mask_hw is not None:
            mask = boost_mask[:1]
            if mask.ndim == 2:
                mask = mask[None]
            mask = F.interpolate(mask[None].float(), size=mask_hw[i], mode="area")[0, 0]
            cols = off + torch.nonzero(mask.reshape(-1) > 0.5, as_tuple=True)[0].to(device)
        else:
            cols = torch.arange(off, off + sl, device=device)
        bias[:, :, rows0:, cols] = boost_bias_value(b)
    return bias


def krea2_edit_forward(m, x, timesteps, context, src_latent, transformer_options,
                       ref_boost=1.0, ref_boost_a=1.0, ref_boost_mask=None,
                       ref_native=False, pos_mode="anchor"):
    """The model's forward pass with source block(s) prepended: [text | refs... | target], target tokens out."""
    import torch
    from einops import rearrange

    import comfy.ldm.common_dit
    from comfy.ldm.flux.layers import timestep_embedding

    patch = m.patch

    temporal = x.ndim == 5
    if temporal:
        b5, c5, t5, h5, w5 = x.shape
    x = _to_4d(x)
    bs, c, H_orig, W_orig = x.shape

    x = comfy.ldm.common_dit.pad_to_patch_size(x, (patch, patch), padding_mode="replicate")
    H, W = x.shape[-2], x.shape[-1]
    h_, w_ = H // patch, W // patch

    src_list = src_latent if isinstance(src_latent, (list, tuple)) else [src_latent]
    srcs = []
    for sl in src_list:
        src = _to_4d(sl).to(x.device, x.dtype)
        if src.shape[0] != bs:
            src = src[:1].expand(bs, *src.shape[1:])
        if not ref_native and src.shape[-2:] != (H, W):
            print(f"[krea2edit] LATENT-PATH fit_src (crop): src={tuple(src.shape[-2:])} -> {H}x{W}", flush=True)
            src = _fit_src(src, H, W).to(x.dtype)
        srcs.append(comfy.ldm.common_dit.pad_to_patch_size(src, (patch, patch), padding_mode="replicate"))
    src_grids = [(s_.shape[-2] // patch, s_.shape[-1] // patch) for s_ in srcs]

    context = m._unpack_context(context)                       # (B, seq, 12, 2560)

    tgt_img = m.first(rearrange(x, "b c (h ph) (w pw) -> b (h w) (c ph pw)", ph=patch, pw=patch))
    src_imgs = [m.first(rearrange(s_, "b c (h ph) (w pw) -> b (h w) (c ph pw)", ph=patch, pw=patch))
                for s_ in srcs]

    t = m.tmlp(timestep_embedding(timesteps, m.tdim).unsqueeze(1).to(tgt_img.dtype))
    tvec = m.tproj(t)

    context = m.txtfusion(context, mask=None, transformer_options=transformer_options)
    context = m.txtmlp(context)

    txtlen, tgtlen = context.shape[1], tgt_img.shape[1]
    srclen = sum(si.shape[1] for si in src_imgs)
    combined = torch.cat([context] + src_imgs + [tgt_img], dim=1)  # [text | refs... | target]

    device = combined.device
    if pos_mode == "stride1" and ref_native:
        print(f"[krea2edit] STRIDE1-POS fit: ref grids {src_grids} centered in ({h_},{w_})", flush=True)
        ref_ids = [_imgids_offset(bs, i + 1, gh, gw, h_, w_, device)
                   for i, (gh, gw) in enumerate(src_grids)]
    else:
        ref_ids = [_imgids(bs, i + 1, gh, gw, device) for i, (gh, gw) in enumerate(src_grids)]
    pos = torch.cat([
        torch.zeros(bs, txtlen, 3, device=device, dtype=torch.float32)]   # text @ 0
        + ref_ids
        + [_imgids(bs, 0, h_, w_, device)],                                    # target frame=0
        dim=1)
    freqs = m.pe_embedder(pos)

    attn_bias = None
    if ref_boost != 1.0 or ref_boost_a != 1.0:
        boosts = ref_boost_list(ref_boost, ref_boost_a, len(src_imgs))
        attn_bias = _ref_attn_bias(boosts, ref_boost_mask, txtlen,
                                   [si.shape[1] for si in src_imgs], tgtlen,
                                   src_grids, combined.device, combined.dtype)

    for block in m.blocks:
        combined = block(combined, tvec, freqs, attn_bias, transformer_options=transformer_options)

    final = m.last(combined, t)
    out = final[:, txtlen + srclen: txtlen + srclen + tgtlen, :]         # target tokens only
    out = rearrange(out, "b (h w) (c ph pw) -> b c (h ph) (w pw)",
                    h=h_, w=w_, ph=patch, pw=patch, c=m.channels)
    out = out[:, :, :H_orig, :W_orig]
    if temporal:
        out = out.reshape(b5, t5, m.channels, H_orig, W_orig).movedim(1, 2)
    return out


# ---------------------------------------------------------------- nodes

class SYKrea2EditModelPatch:
    DESCRIPTION = "Adds the in-context source picture path to a Krea 2 edit model, so the edit keeps the look of the source."
    CATEGORY = category("Editors")
    FUNCTION = "patch"
    RETURN_TYPES = ("MODEL",)

    @classmethod
    def INPUT_TYPES(cls):
        return {"required": {
            "model": ("MODEL", {"tooltip": "The Krea 2 model, with the edit LoRA already applied. A patched copy is returned."}),
            "source_latent": ("LATENT", {"tooltip": "The source picture encoded by a VAE Encode node."}),
        }, "optional": {
            "source_latent_b": ("LATENT", {"tooltip": "Second reference (the subject) for two-reference edit LoRAs. Scene first, subject second."}),
            "ref_boost": ("FLOAT", {"default": 1.0, "min": 0.0, "max": 1000.0, "step": 0.01, "round": 0.001,
                                     "tooltip": "Pulls the result toward the last reference. 1 is off, above 1 pulls harder, below 1 loosens."}),
            "ref_boost_a": ("FLOAT", {"default": 1.0, "min": 0.0, "max": 1000.0, "step": 0.01, "round": 0.001,
                                       "tooltip": "Same pull for the first reference (the scene in two-reference edits). 1 is off."}),
            "fit_mode": (["fit", "crop (legacy)"], {"default": "fit",
                          "tooltip": "How a source image fits a different output shape. Use fit; crop (legacy) is only for older weights."}),
            "ref_boost_mask": ("MASK", {"tooltip": "Optional area of the last reference to boost, for example the face. Empty means all of it."}),
            "vae": ("VAE", {"tooltip": "Recommended with source_image: lets the node fit the picture in pixels before encoding."}),
            "source_image": ("IMAGE", {"tooltip": "The source as an image (needs vae). Replaces source_latent and avoids blur from size mismatch."}),
            "source_image_b": ("IMAGE", {"tooltip": "Second reference as an image (needs vae)."}),
        }}

    def patch(self, model, source_latent, source_latent_b=None, ref_boost=1.0, ref_boost_a=1.0,
              ref_boost_mask=None, vae=None, source_image=None,
              source_image_b=None, fit_mode="fit", **_future):
        import comfy.patcher_extension

        if _future:
            print(future_inputs_warning(
                _future, "The workflow is newer than this node. Update the SY nodes and restart ComfyUI. "
                         "Continuing without them."), flush=True)
        m = model.clone()
        # The target latent reaches the diffusion model already scaled (process_latent_in);
        # scale the source(s) the same way so all share one latent space.
        src_samples = model.model.process_latent_in(source_latent["samples"])
        if source_latent_b is not None:
            src_samples = [src_samples, model.model.process_latent_in(source_latent_b["samples"])]

        px_cache = {}   # pixel-path encoded sources, keyed per target resolution
        mm = model.model  # for process_latent_in on the pixel path

        if fit_mode == "fit" and (vae is None or source_image is None):
            print(f"[krea2edit] WARNING: fit_mode='fit' has NO EFFECT — it needs both "
                  f"'vae' and 'source_image' connected (the pixel path). Falling back to the "
                  f"latent crop path.", flush=True)

        def wrapper(executor, x, timesteps, context, *wargs, **kwargs):
            # Accept both call shapes: transformer_options is the trailing dict; any native
            # ref_latents are ignored (this patch supplies its own source path).
            transformer_options = kwargs.pop("transformer_options", None)
            if transformer_options is None:
                transformer_options = {}
                for a in reversed(wargs):
                    if isinstance(a, dict):
                        transformer_options = a
                        break
            dm = executor.class_obj  # the SingleStreamDiT instance
            src = src_samples
            if vae is not None and source_image is not None:
                if not px_cache:
                    print(f"[krea2edit] pixel path ACTIVE (fit_mode={fit_mode})", flush=True)
                xx = _to_4d(x)
                Hh, Ww = xx.shape[-2], xx.shape[-1]
                lat = mm.process_latent_in(_fit_encode_image(source_image, vae, Hh, Ww, px_cache, ("a", Hh, Ww), fit_mode))
                if source_image_b is not None:
                    lat = [lat, mm.process_latent_in(_fit_encode_image(source_image_b, vae, Hh, Ww, px_cache, ("b", Hh, Ww), fit_mode))]
                src = lat
            ref_native, pos_mode = path_modes(fit_mode, vae is not None, source_image is not None)
            v = krea2_edit_forward(dm, x, timesteps, context, src, transformer_options,
                                   ref_boost=ref_boost, ref_boost_a=ref_boost_a,
                                   ref_boost_mask=ref_boost_mask,
                                   ref_native=ref_native,
                                   pos_mode=pos_mode)
            return v

        to = m.model_options.setdefault("transformer_options", {})
        comfy.patcher_extension.add_wrapper_with_key(
            comfy.patcher_extension.WrappersMP.DIFFUSION_MODEL, "krea2_edit", wrapper, to
        )
        return (m,)


class SYKrea2EditGroundedEncode:
    DESCRIPTION = "Encodes the edit instruction together with the source picture, so words like 'the man on the left' work."
    CATEGORY = category("Editors")
    FUNCTION = "encode"
    RETURN_TYPES = ("CONDITIONING",)

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "clip": ("CLIP", {"tooltip": "The Krea 2 text encoder (Qwen3-VL with its vision part)."}),
                "prompt": ("STRING", {"multiline": True, "default": "",
                                      "tooltip": "The edit instruction. For the negative side, leave it empty and use the same image."}),
            },
            "optional": {
                "image": ("IMAGE", {"tooltip": "The source picture the instruction refers to. Without it the node encodes text only."}),
                "image_b": ("IMAGE", {"tooltip": "Second reference (the subject) for two-reference edit LoRAs. Scene first, subject second."}),
                "grounding_px": ("INT", {"default": 768, "min": 0, "max": 4096, "step": 64,
                                          "tooltip": "Longest side in pixels fed to the vision encoder. 0 keeps the native size."}),
                "system_prompt": ("STRING", {"multiline": True, "default": "",
                                              "tooltip": "Advanced: replaces the built-in system prompt. Empty uses the training default."}),
            },
        }

    def _prep(self, image, grounding_px):
        import comfy.utils

        samples = image.movedim(-1, 1)  # B,H,W,C -> B,C,H,W
        h, w = samples.shape[2], samples.shape[3]
        if grounding_px and max(h, w) > grounding_px:
            s = grounding_px / max(h, w)
            samples = comfy.utils.common_upscale(samples, round(w * s), round(h * s), "area", "disabled")
        return samples.movedim(1, -1)[:, :, :, :3]

    def encode(self, clip, prompt, image=None, image_b=None, grounding_px=768, system_prompt="", **_future):
        if _future:
            print(future_inputs_warning(
                _future, "Update the SY nodes and restart ComfyUI. Continuing without them."), flush=True)
        if image is None:  # text-only fallback
            tokens = clip.tokenize(prompt)
            return (clip.encode_from_tokens_scheduled(tokens),)
        imgs = [self._prep(image, grounding_px)]
        if image_b is not None:
            imgs.append(self._prep(image_b, grounding_px))
        template = template_for(len(imgs), system_prompt)
        tokens = clip.tokenize(prompt, images=imgs, llama_template=template)
        return (clip.encode_from_tokens_scheduled(tokens),)


NODE_CLASS_MAPPINGS = {}
NODE_DISPLAY_NAME_MAPPINGS = {}
register(NODE_CLASS_MAPPINGS, NODE_DISPLAY_NAME_MAPPINGS, "Krea2EditModelPatch", SYKrea2EditModelPatch)
register(NODE_CLASS_MAPPINGS, NODE_DISPLAY_NAME_MAPPINGS, "Krea2EditGroundedEncode", SYKrea2EditGroundedEncode)
