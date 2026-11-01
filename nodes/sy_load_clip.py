"""Load Clip SY: loads a video or a sound file, trims it to the part you want and tells you its length, frames and fps."""
import os

try:
    from ._sy_common import category, register
    from ._sy_core_call import core
except ImportError:  # run as a plain file by the selftest
    from _sy_common import category, register
    from _sy_core_call import core

NONE = "(none)"
VIDEO_EXT = (".mp4", ".mov", ".webm", ".mkv", ".avi", ".m4v", ".gif")
AUDIO_EXT = (".wav", ".mp3", ".flac", ".ogg", ".m4a", ".aac", ".opus")


def pick_files(names, exts):
    """Pure function. Keeps the file names with one of the given extensions, sorted, with (none) first."""
    keep = sorted(n for n in names if os.path.splitext(n)[1].lower() in exts)
    return [NONE] + keep


def plan_trim(total_frames, fps, start_seconds, length_seconds, max_frames):
    """Pure function. Returns (first_frame, frame_count). length 0 = to the end. max_frames 0 = no limit."""
    total_frames = int(total_frames)
    fps = float(fps)
    if fps <= 0:
        raise ValueError("the clip has no frame rate (fps = %s)" % fps)
    if start_seconds < 0 or length_seconds < 0 or max_frames < 0:
        raise ValueError("start, length and max frames cannot be negative")
    first = int(round(start_seconds * fps))
    if first >= total_frames:
        raise ValueError("start (%.2f s) is after the end of the clip (%.2f s)" % (start_seconds, total_frames / fps))
    count = total_frames - first
    if length_seconds > 0:
        count = min(count, max(1, int(round(length_seconds * fps))))
    if max_frames > 0:
        count = min(count, max_frames)
    return first, count


def audio_range(sample_count, sample_rate, first_frame, frame_count, fps):
    """Pure function. The sound samples that belong to the kept frames: (from, to), clamped to the sound length."""
    start = int(round(first_frame / float(fps) * sample_rate))
    end = int(round((first_frame + frame_count) / float(fps) * sample_rate))
    return min(start, sample_count), min(end, sample_count)


def audio_trim_range(sample_count, sample_rate, start_seconds, length_seconds):
    """Pure function. Sample range for a sound-only file. length 0 = to the end."""
    if start_seconds < 0 or length_seconds < 0:
        raise ValueError("start and length cannot be negative")
    start = int(round(start_seconds * sample_rate))
    if start >= sample_count:
        raise ValueError("start (%.2f s) is after the end of the sound (%.2f s)" % (start_seconds, sample_count / float(sample_rate)))
    end = sample_count if length_seconds <= 0 else min(sample_count, start + int(round(length_seconds * sample_rate)))
    return start, end


def info_text(kind, frames, fps, seconds, width=0, height=0, trimmed=False):
    """Pure function. One line about what was loaded."""
    cut = " (trimmed)" if trimmed else ""
    if kind == "video":
        return "Video: %d frame(s) at %.3f fps = %.2f s, %dx%d%s" % (frames, fps, seconds, width, height, cut)
    return "Sound: %.2f s%s" % (seconds, cut)


def _input_names():
    try:
        import folder_paths
        return os.listdir(folder_paths.get_input_directory())
    except Exception:
        return []


def _blank_image():
    import torch
    return torch.zeros((1, 64, 64, 3), dtype=torch.float32)


def _silent_audio():
    import torch
    return {"waveform": torch.zeros((1, 2, 1), dtype=torch.float32), "sample_rate": 44100}


class SYLoadClip:
    DESCRIPTION = ("Loads a video or a sound file from the input folder and trims it: start time, length and a frame limit. "
                   "It shows the frame count, fps and length so you do not have to guess, and cuts the sound to match the frames.")
    CATEGORY = category("Image")
    FUNCTION = "run"
    RETURN_TYPES = ("IMAGE", "AUDIO", "FLOAT", "INT", "FLOAT", "STRING")
    RETURN_NAMES = ("images", "audio", "fps", "frame_count", "seconds", "info")

    @classmethod
    def INPUT_TYPES(cls):
        names = _input_names()
        return {
            "required": {
                "video": (pick_files(names, VIDEO_EXT), {"video_upload": True, "tooltip": "A video from the input folder. You can also upload one. (none) = load only a sound."}),
                "sound": (pick_files(names, AUDIO_EXT), {"tooltip": "A sound file from the input folder. Only used when video is (none)."}),
                "start_seconds": ("FLOAT", {"default": 0.0, "min": 0.0, "max": 100000.0, "step": 0.1, "tooltip": "Where to start, in seconds from the beginning."}),
                "length_seconds": ("FLOAT", {"default": 0.0, "min": 0.0, "max": 100000.0, "step": 0.1, "tooltip": "How many seconds to keep. 0 = to the end."}),
                "max_frames": ("INT", {"default": 0, "min": 0, "max": 100000, "tooltip": "Frame limit after trimming. 0 = no limit."}),
            }
        }

    def run(self, video, sound, start_seconds, length_seconds, max_frames):
        if video != NONE:
            return self._load_video(video, start_seconds, length_seconds, max_frames)
        if sound != NONE:
            return self._load_sound(sound, start_seconds, length_seconds)
        raise ValueError("pick a video or a sound file first")

    def _load_video(self, name, start_seconds, length_seconds, max_frames):
        import folder_paths
        from comfy_api.latest import InputImpl
        path = folder_paths.get_annotated_filepath(name)
        if not os.path.isfile(path):
            raise ValueError("video not found in the input folder: %s" % name)
        comps = InputImpl.VideoFromFile(path).get_components()
        images, audio, fps = comps.images, comps.audio, float(comps.frame_rate)
        total = int(images.shape[0])
        first, count = plan_trim(total, fps, start_seconds, length_seconds, max_frames)
        trimmed = (first, count) != (0, total)
        images = images[first:first + count]
        if audio is not None:
            wave = audio["waveform"]
            a, b = audio_range(wave.shape[-1], audio["sample_rate"], first, count, fps)
            audio = {"waveform": wave[..., a:b], "sample_rate": audio["sample_rate"]}
        else:
            audio = _silent_audio()
        seconds = count / fps
        info = info_text("video", count, fps, seconds, images.shape[2], images.shape[1], trimmed)
        return (images, audio, fps, count, seconds, info)

    def _load_sound(self, name, start_seconds, length_seconds):
        audio = core("LoadAudio", "Load Clip SY", audio=name)[0]
        wave, rate = audio["waveform"], int(audio["sample_rate"])
        a, b = audio_trim_range(wave.shape[-1], rate, start_seconds, length_seconds)
        trimmed = (a, b) != (0, wave.shape[-1])
        audio = {"waveform": wave[..., a:b], "sample_rate": rate}
        seconds = (b - a) / float(rate)
        return (_blank_image(), audio, 0.0, 0, seconds, info_text("sound", 0, 0.0, seconds, trimmed=trimmed))


NODE_CLASS_MAPPINGS = {}
NODE_DISPLAY_NAME_MAPPINGS = {}
register(NODE_CLASS_MAPPINGS, NODE_DISPLAY_NAME_MAPPINGS, "LoadClip", SYLoadClip)
NODE_DISPLAY_NAME_MAPPINGS["SYLoadClip"] = "Load Clip SY"
