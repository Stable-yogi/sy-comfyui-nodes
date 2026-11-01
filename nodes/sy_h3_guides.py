"""H3 Guides SY: pins a start picture, an end picture and a voice file, and follows a layout video, in one box."""
try:
    from ._sy_common import category, register
    from ._sy_core_call import core
    from ._sy_model_files import list_names, NONE_NAME
except ImportError:  # run as a plain file by the selftest
    from _sy_common import category, register
    from _sy_core_call import core
    from _sy_model_files import list_names, NONE_NAME


def plan_guides(has_start, has_end, has_voice, has_layout, layout_model, vae_present, audio_vae_present):
    """Pure function. Returns the steps in order as a list of (kind, frame_idx). Raises ValueError for a missing partner input."""
    steps = []
    if (has_start or has_end) and not vae_present:
        raise ValueError("a start or end picture needs the vae input connected")
    if has_voice and not audio_vae_present:
        raise ValueError("a voice file needs the audio_vae input connected")
    if has_start:
        steps.append(("start", 0))
    if has_end:
        steps.append(("end", -1))
    if has_voice:
        steps.append(("voice", 0))
    if has_layout:
        if not layout_model or layout_model == NONE_NAME:
            raise ValueError("a layout video needs a layout model picked")
        if not vae_present:
            raise ValueError("a layout video needs the vae input connected")
        steps.append(("layout", None))
    return steps


def info_text(steps, layout_model, layout_strength):
    """Pure function. Shows which guides were applied."""
    if not steps:
        return "No guides applied (everything left empty)."
    words = {"start": "start picture at the first frame", "end": "end picture at the last frame",
             "voice": "voice file from the first frame"}
    lines = []
    for kind, _idx in steps:
        if kind == "layout":
            lines.append("layout video (%s, strength %g)" % (layout_model, layout_strength))
        else:
            lines.append(words[kind])
    return "Applied: " + "; ".join(lines)


class SYH3Guides:
    DESCRIPTION = ("Puts the optional guides for an H3 video into one box: a start picture, an end picture, a voice file and a "
                   "layout video that the new clip follows. Leave a guide empty and it is skipped, so you never bypass nodes.")
    CATEGORY = category("Utility")
    FUNCTION = "run"
    RETURN_TYPES = ("MODEL", "CONDITIONING", "STRING")
    RETURN_NAMES = ("model", "positive", "info")

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "model": ("MODEL", {"tooltip": "The video model. Only changed when a layout video is used."}),
                "positive": ("CONDITIONING", {"tooltip": "The positive prompt conditioning to add the pins to."}),
                "latent": ("LATENT", {"tooltip": "The empty video latent the pins are placed into."}),
                "layout_model": ([NONE_NAME] + list_names("model_patches"), {"tooltip": "The layout (control) model file. Only needed with a layout video."}),
                "layout_strength": ("FLOAT", {"default": 1.0, "min": 0.0, "max": 10.0, "step": 0.05, "tooltip": "How strongly the clip follows the layout video."}),
            },
            "optional": {
                "vae": ("VAE", {"tooltip": "The video VAE. Needed for pictures and a layout video."}),
                "audio_vae": ("VAE", {"tooltip": "The audio VAE. Needed for a voice file."}),
                "start_image": ("IMAGE", {"tooltip": "Picture the clip starts with."}),
                "end_image": ("IMAGE", {"tooltip": "Picture the clip ends with."}),
                "voice": ("AUDIO", {"tooltip": "A voice file the clip follows, from the first frame."}),
                "layout_video": ("IMAGE", {"tooltip": "Frames of a depth, line or 3D layout video the new clip follows."}),
            },
        }

    def run(self, model, positive, latent, layout_model, layout_strength, vae=None, audio_vae=None,
            start_image=None, end_image=None, voice=None, layout_video=None):
        steps = plan_guides(start_image is not None, end_image is not None, voice is not None, layout_video is not None,
                            layout_model, vae is not None, audio_vae is not None)
        for kind, idx in steps:
            if kind == "layout":
                patch = core("ModelPatchLoader", "H3 Guides SY", name=layout_model)[0]
                model = core("MiniMaxH3FunControlNetApply", "H3 Guides SY", model=model, model_patch=patch, vae=vae,
                             strength=float(layout_strength), start_percent=0.0, end_percent=1.0, control_video=layout_video)[0]
                continue
            extra = {"image": start_image if kind == "start" else end_image} if kind in ("start", "end") else {"audio": voice}
            positive = core("MiniMaxH3AddGuide", "H3 Guides SY", positive=positive, latent=latent, frame_idx=idx,
                            vae=vae, audio_vae=audio_vae, **extra)[0]
        return (model, positive, info_text(steps, layout_model, layout_strength))


NODE_CLASS_MAPPINGS = {}
NODE_DISPLAY_NAME_MAPPINGS = {}
register(NODE_CLASS_MAPPINGS, NODE_DISPLAY_NAME_MAPPINGS, "H3Guides", SYH3Guides)
NODE_DISPLAY_NAME_MAPPINGS["SYH3Guides"] = "H3 Guides SY"
