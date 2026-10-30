"""GGUF reading, quantised layers and the LoRA-aware model patcher for the SY GGUF loaders.

Ported from ComfyUI-GGUF (Apache-2.0, city96). Changed for the SY pack by Stable Yogi.
Original copyright: (c) City96. Licence copy: third_party/ComfyUI-GGUF/LICENSE.

Changes: ComfyUI modules (comfy, folder_paths) are imported inside functions; the classes that
sit on top of ComfyUI classes are built on first use (get_ops, get_patcher); pure logic moved to
_sy_gguf_names.py; the architecture guess for files from other tools uses a small table instead of
the converter script; the byte table for the tekken tokenizer is our own function.
This helper needs torch and gguf. It is imported only when a GGUF file is really loaded.
"""
import collections
import inspect
import logging
import os
import warnings

import gguf
import torch

try:
    from . import _sy_gguf_names as N
    from . import _sy_gguf_dequant as D
except ImportError:  # run as a plain file by a test script
    import _sy_gguf_names as N
    import _sy_gguf_dequant as D

is_quantized = D.is_quantized
is_torch_compatible = D.is_torch_compatible
dequantize_tensor = D.dequantize_tensor


def chained_hasattr(obj, chained_attr):
    probe = obj
    for attr in chained_attr.split('.'):
        if hasattr(probe, attr):
            probe = getattr(probe, attr)
        else:
            return False
    return True


# A backward and forward compatible way to get `torch.compiler.disable`.
def get_torch_compiler_disable_decorator():
    def dummy_decorator(*args, **kwargs):
        def noop(x):
            return x
        return noop

    from packaging import version

    if not chained_hasattr(torch, "compiler.disable"):
        return dummy_decorator  # torch too old
    elif version.parse(torch.__version__) >= version.parse("2.8"):
        return dummy_decorator  # torch compile works
    if chained_hasattr(torch, "_dynamo.config.nontraceable_tensor_subclasses"):
        return dummy_decorator  # torch compile works, nightly before 2.8 release
    else:
        return torch.compiler.disable


torch_compiler_disable = get_torch_compiler_disable_decorator()


def move_patch_to_device(item, device):
    if isinstance(item, torch.Tensor):
        return item.to(device, non_blocking=True)
    elif isinstance(item, tuple):
        return tuple(move_patch_to_device(x, device) for x in item)
    elif isinstance(item, list):
        return [move_patch_to_device(x, device) for x in item]
    else:
        return item


class GGMLTensor(torch.Tensor):
    """Main tensor-like class for storing quantised weights."""

    def __init__(self, *args, tensor_type, tensor_shape, patches=[], **kwargs):
        super().__init__()
        self.tensor_type = tensor_type
        self.tensor_shape = tensor_shape
        self.patches = patches

    def __new__(cls, *args, tensor_type, tensor_shape, patches=[], **kwargs):
        return super().__new__(cls, *args, **kwargs)

    def to(self, *args, **kwargs):
        new = super().to(*args, **kwargs)
        new.tensor_type = getattr(self, "tensor_type", None)
        new.tensor_shape = getattr(self, "tensor_shape", new.data.shape)
        new.patches = getattr(self, "patches", []).copy()
        return new

    def clone(self, *args, **kwargs):
        return self

    def detach(self, *args, **kwargs):
        return self

    def copy_(self, *args, **kwargs):
        # fixes .weight.copy_ in comfy/clip_model/CLIPTextModel
        try:
            return super().copy_(*args, **kwargs)
        except Exception as e:
            logging.warning("SY GGUF: ignoring 'copy_' on tensor: %s", e)

    def new_empty(self, size, *args, **kwargs):
        new_tensor = super().new_empty(size, *args, **kwargs)
        return GGMLTensor(
            new_tensor,
            tensor_type=getattr(self, "tensor_type", None),
            tensor_shape=size,
            patches=getattr(self, "patches", []).copy(),
        )

    @property
    def shape(self):
        if not hasattr(self, "tensor_shape"):
            self.tensor_shape = self.size()
        return self.tensor_shape


class GGMLLayer(torch.nn.Module):
    """Dequantises on the fly (mixin for the layer classes built in get_ops)."""
    comfy_cast_weights = True
    dequant_dtype = None
    patch_dtype = None
    largest_layer = False
    torch_compatible_tensor_types = {None, gguf.GGMLQuantizationType.F32, gguf.GGMLQuantizationType.F16}

    def is_ggml_quantized(self, *, weight=None, bias=None):
        if weight is None:
            weight = self.weight
        if bias is None:
            bias = self.bias
        return is_quantized(weight) or is_quantized(bias)

    def _load_from_state_dict(self, state_dict, prefix, *args, **kwargs):
        weight, bias = state_dict.get(f"{prefix}weight"), state_dict.get(f"{prefix}bias")
        # NOTE: using modified load for linear due to not initializing on creation, see GGMLOps todo
        if self.is_ggml_quantized(weight=weight, bias=bias) or isinstance(self, torch.nn.Linear):
            return self.ggml_load_from_state_dict(state_dict, prefix, *args, **kwargs)
        # Not strictly required, but fixes embedding shape mismatch.
        if isinstance(self, torch.nn.Embedding) and self.weight.shape[0] >= (64 * 1024):
            return self.ggml_load_from_state_dict(state_dict, prefix, *args, **kwargs)
        return super()._load_from_state_dict(state_dict, prefix, *args, **kwargs)

    def ggml_load_from_state_dict(self, state_dict, prefix, local_metadata, strict, missing_keys, unexpected_keys, error_msgs):
        prefix_len = len(prefix)
        for k, v in state_dict.items():
            if k[prefix_len:] == "weight":
                self.weight = torch.nn.Parameter(v, requires_grad=False)
            elif k[prefix_len:] == "bias" and v is not None:
                self.bias = torch.nn.Parameter(v, requires_grad=False)
            else:
                unexpected_keys.append(k)

        # For Linear layer with missing weight
        if self.weight is None and isinstance(self, torch.nn.Linear):
            v = torch.zeros(self.in_features, self.out_features)
            self.weight = torch.nn.Parameter(v, requires_grad=False)
            missing_keys.append(prefix + "weight")

        # for vram estimation
        if getattr(self.weight, "is_largest_weight", False):
            self.largest_layer = True

    def _save_to_state_dict(self, *args, **kwargs):
        if self.is_ggml_quantized():
            return self.ggml_save_to_state_dict(*args, **kwargs)
        return super()._save_to_state_dict(*args, **kwargs)

    def ggml_save_to_state_dict(self, destination, prefix, keep_vars):
        # This is a fake state dict for vram estimation
        weight = torch.zeros_like(self.weight, device=torch.device("meta"))
        destination[prefix + "weight"] = weight
        if self.bias is not None:
            bias = torch.zeros_like(self.bias, device=torch.device("meta"))
            destination[prefix + "bias"] = bias

        # Take into account space required for dequantizing the largest tensor
        if self.largest_layer:
            shape = getattr(self.weight, "tensor_shape", self.weight.shape)
            dtype = self.dequant_dtype if self.dequant_dtype and self.dequant_dtype != "target" else torch.float16
            temp = torch.empty(*shape, device=torch.device("meta"), dtype=dtype)
            destination[prefix + "temp.weight"] = temp

    def get_weight(self, tensor, dtype):
        if tensor is None:
            return
        import comfy.lora

        # consolidate and load patches to GPU in async
        patch_list = []
        device = tensor.device
        for patches, key in getattr(tensor, "patches", []):
            patch_list += move_patch_to_device(patches, device)

        # dequantize tensor while patches load
        weight = dequantize_tensor(tensor, dtype, self.dequant_dtype)

        # prevent propagating custom tensor class
        if isinstance(weight, GGMLTensor):
            weight = torch.Tensor(weight)

        # apply patches (this is how a LoRA works on a GGUF model)
        if len(patch_list) > 0:
            if self.patch_dtype is None:
                weight = comfy.lora.calculate_weight(patch_list, weight, key)
            else:
                # for testing, may degrade image quality
                patch_dtype = dtype if self.patch_dtype == "target" else self.patch_dtype
                weight = comfy.lora.calculate_weight(patch_list, weight, key, patch_dtype)
        return weight

    @torch_compiler_disable()
    def cast_bias_weight(s, input=None, dtype=None, device=None, bias_dtype=None):
        import comfy.model_management
        import comfy.ops
        if input is not None:
            if dtype is None:
                dtype = getattr(input, "dtype", torch.float32)
            if bias_dtype is None:
                bias_dtype = dtype
            if device is None:
                device = input.device

        bias = None
        non_blocking = comfy.model_management.device_supports_non_blocking(device)
        if s.bias is not None:
            bias = s.get_weight(s.bias.to(device), dtype)
            bias = comfy.ops.cast_to(bias, bias_dtype, device, non_blocking=non_blocking, copy=False)

        weight = s.get_weight(s.weight.to(device), dtype)
        weight = comfy.ops.cast_to(weight, dtype, device, non_blocking=non_blocking, copy=False)
        return weight, bias

    def forward_comfy_cast_weights(self, input, *args, **kwargs):
        if self.is_ggml_quantized():
            out = self.forward_ggml_cast_weights(input, *args, **kwargs)
        else:
            out = super().forward_comfy_cast_weights(input, *args, **kwargs)

        # non-ggml forward might still propagate custom tensor class
        if isinstance(out, GGMLTensor):
            out = torch.Tensor(out)
        return out

    def forward_ggml_cast_weights(self, input):
        raise NotImplementedError


_OPS = None
_PATCHER = None


def get_ops():
    """The custom-operations class (built once, needs ComfyUI)."""
    global _OPS
    if _OPS is not None:
        return _OPS
    import comfy.ops

    class GGMLOps(comfy.ops.manual_cast):
        """Dequantize weights on the fly before doing the compute."""
        class Linear(GGMLLayer, comfy.ops.manual_cast.Linear):
            def __init__(self, in_features, out_features, bias=True, device=None, dtype=None):
                torch.nn.Module.__init__(self)
                # Not allocated on creation: avoids a big memory spike on Windows.
                self.in_features = in_features
                self.out_features = out_features
                self.weight = None
                self.bias = None

            def forward_ggml_cast_weights(self, input):
                weight, bias = self.cast_bias_weight(input)
                return torch.nn.functional.linear(input, weight, bias)

        class Conv2d(GGMLLayer, comfy.ops.manual_cast.Conv2d):
            def forward_ggml_cast_weights(self, input):
                weight, bias = self.cast_bias_weight(input)
                return self._conv_forward(input, weight, bias)

        class Embedding(GGMLLayer, comfy.ops.manual_cast.Embedding):
            def forward_ggml_cast_weights(self, input, out_dtype=None):
                output_dtype = out_dtype
                if self.weight.dtype == torch.float16 or self.weight.dtype == torch.bfloat16:
                    out_dtype = None
                weight, _bias = self.cast_bias_weight(self, device=input.device, dtype=out_dtype)
                return torch.nn.functional.embedding(
                    input, weight, self.padding_idx, self.max_norm, self.norm_type, self.scale_grad_by_freq, self.sparse
                ).to(dtype=output_dtype)

        class LayerNorm(GGMLLayer, comfy.ops.manual_cast.LayerNorm):
            def forward_ggml_cast_weights(self, input):
                if self.weight is None:
                    return super().forward_comfy_cast_weights(input)
                weight, bias = self.cast_bias_weight(input)
                return torch.nn.functional.layer_norm(input, self.normalized_shape, weight, bias, self.eps)

        class GroupNorm(GGMLLayer, comfy.ops.manual_cast.GroupNorm):
            def forward_ggml_cast_weights(self, input):
                weight, bias = self.cast_bias_weight(input)
                return torch.nn.functional.group_norm(input, self.num_groups, weight, bias, self.eps)

    _OPS = GGMLOps
    return _OPS


def get_patcher():
    """The model patcher class that keeps LoRA patches on quantised weights (built once, needs ComfyUI)."""
    global _PATCHER
    if _PATCHER is not None:
        return _PATCHER
    import comfy.float
    import comfy.lora
    import comfy.model_management
    import comfy.model_patcher
    import comfy.utils

    class GGUFModelPatcher(comfy.model_patcher.ModelPatcher):
        patch_on_device = False

        def patch_weight_to_device(self, key, device_to=None, inplace_update=False):
            if key not in self.patches:
                return
            weight = comfy.utils.get_attr(self.model, key)

            patches = self.patches[key]
            if is_quantized(weight):
                out_weight = weight.to(device_to)
                patches = move_patch_to_device(patches, self.load_device if self.patch_on_device else self.offload_device)
                out_weight.patches = [(patches, key)]
            else:
                inplace_update = self.weight_inplace_update or inplace_update
                if key not in self.backup:
                    self.backup[key] = collections.namedtuple('Dimension', ['weight', 'inplace_update'])(
                        weight.to(device=self.offload_device, copy=inplace_update), inplace_update
                    )

                if device_to is not None:
                    temp_weight = comfy.model_management.cast_to_device(weight, device_to, torch.float32, copy=True)
                else:
                    temp_weight = weight.to(torch.float32, copy=True)

                out_weight = comfy.lora.calculate_weight(patches, temp_weight, key)
                out_weight = comfy.float.stochastic_rounding(out_weight, weight.dtype)

            if inplace_update:
                comfy.utils.copy_to_param(self.model, key, out_weight)
            else:
                comfy.utils.set_attr_param(self.model, key, out_weight)

        def unpatch_model(self, device_to=None, unpatch_weights=True):
            if unpatch_weights:
                for p in self.model.parameters():
                    if is_torch_compatible(p):
                        continue
                    patches = getattr(p, "patches", [])
                    if len(patches) > 0:
                        p.patches = []
            return super().unpatch_model(device_to=device_to, unpatch_weights=unpatch_weights)

        def pin_weight_to_device(self, key):
            op_key = key.rsplit('.', 1)[0]
            if not self.mmap_released and op_key in self.named_modules_to_munmap:
                self.named_modules_to_munmap[op_key].to(self.load_device).to(self.offload_device)
                del self.named_modules_to_munmap[op_key]
            super().pin_weight_to_device(key)

        mmap_released = False
        named_modules_to_munmap = {}

        def load(self, *args, force_patch_weights=False, **kwargs):
            if not self.mmap_released:
                self.named_modules_to_munmap = dict(self.model.named_modules())

            # always call `patch_weight_to_device` even for lowvram
            super().load(*args, force_patch_weights=True, **kwargs)

            # make sure nothing stays linked to mmap after first load
            if not self.mmap_released:
                linked = []
                if kwargs.get("lowvram_model_memory", 0) > 0:
                    for n, m in self.named_modules_to_munmap.items():
                        if hasattr(m, "weight"):
                            device = getattr(m.weight, "device", None)
                            if device == self.offload_device:
                                linked.append((n, m))
                                continue
                        if hasattr(m, "bias"):
                            device = getattr(m.bias, "device", None)
                            if device == self.offload_device:
                                linked.append((n, m))
                                continue
                if linked and self.load_device != self.offload_device:
                    logging.info("SY GGUF: attempting to release mmap (%d)", len(linked))
                    for n, m in linked:
                        m.to(self.load_device).to(self.offload_device)
                self.mmap_released = True
                self.named_modules_to_munmap = {}

        def clone(self, *args, **kwargs):
            src_cls = self.__class__
            self.__class__ = GGUFModelPatcher
            n = super().clone(*args, **kwargs)
            n.__class__ = GGUFModelPatcher
            self.__class__ = src_cls
            # GGUF specific clone values below
            n.patch_on_device = getattr(self, "patch_on_device", False)
            n.mmap_released = getattr(self, "mmap_released", False)
            if src_cls != GGUFModelPatcher:
                n.size = 0  # force recalc
            return n

    _PATCHER = GGUFModelPatcher
    return _PATCHER


# ---------------------------------------------------------------- reading a .gguf file

def get_orig_shape(reader, tensor_name):
    field_key = f"comfy.gguf.orig_shape.{tensor_name}"
    field = reader.get_field(field_key)
    if field is None:
        return None
    # Has original shape metadata, so we try to decode it.
    if len(field.types) != 2 or field.types[0] != gguf.GGUFValueType.ARRAY or field.types[1] != gguf.GGUFValueType.INT32:
        raise TypeError(f"Bad original shape metadata for {field_key}: Expected ARRAY of INT32, got {field.types}")
    return torch.Size(tuple(int(field.parts[part_idx][0]) for part_idx in field.data))


def get_field(reader, field_name, field_type):
    field = reader.get_field(field_name)
    if field is None:
        return None
    elif field_type == str:
        # extra check here as this is used for checking arch string
        if len(field.types) != 1 or field.types[0] != gguf.GGUFValueType.STRING:
            raise TypeError(f"Bad type for GGUF {field_name} key: expected string, got {field.types!r}")
        return str(field.parts[field.data[-1]], encoding="utf-8")
    elif field_type in [int, float, bool]:
        return field_type(field.parts[field.data[-1]].item())
    else:
        raise TypeError(f"Unknown field type {field_type}")


def get_list_field(reader, field_name, field_type):
    field = reader.get_field(field_name)
    if field is None:
        return None
    elif field_type == str:
        return tuple(str(field.parts[part_idx], encoding="utf-8") for part_idx in field.data)
    elif field_type in [int, float, bool]:
        return tuple(field_type(field.parts[part_idx][0]) for part_idx in field.data)
    else:
        raise TypeError(f"Unknown field type {field_type}")


def get_gguf_metadata(reader):
    """Extract all simple metadata fields like safetensors."""
    metadata = {}
    for field_name in reader.fields:
        try:
            field = reader.get_field(field_name)
            if len(field.types) == 1:  # Simple scalar fields only
                if field.types[0] == gguf.GGUFValueType.STRING:
                    metadata[field_name] = str(field.parts[field.data[-1]], "utf-8")
                elif field.types[0] == gguf.GGUFValueType.INT32:
                    metadata[field_name] = int(field.parts[field.data[-1]])
                elif field.types[0] == gguf.GGUFValueType.F32:
                    metadata[field_name] = float(field.parts[field.data[-1]])
                elif field.types[0] == gguf.GGUFValueType.BOOL:
                    metadata[field_name] = bool(field.parts[field.data[-1]])
        except Exception:
            continue
    return metadata


def gguf_sd_loader(path, handle_prefix="model.diffusion_model.", is_text_model=False):
    """Read the file as a state dict of quantised tensors (memory mapped, nothing unpacked yet)."""
    reader = gguf.GGUFReader(path)

    # filter and strip prefix
    has_prefix = False
    if handle_prefix is not None:
        prefix_len = len(handle_prefix)
        tensor_names = set(tensor.name for tensor in reader.tensors)
        has_prefix = any(s.startswith(handle_prefix) for s in tensor_names)

    tensors = []
    for tensor in reader.tensors:
        sd_key = tensor_name = tensor.name
        if has_prefix:
            if not tensor_name.startswith(handle_prefix):
                continue
            sd_key = tensor_name[prefix_len:]
        tensors.append((sd_key, tensor))

    # detect and verify architecture
    compat = None
    arch_str = get_field(reader, "general.architecture", str)
    type_str = get_field(reader, "general.type", str)
    if arch_str in [None, "pig", "cow"]:
        if is_text_model:
            raise ValueError(f"This gguf file is incompatible with llama.cpp. Use a safetensors file or a compatible gguf file ({path})")
        compat = "sd.cpp" if arch_str is None else arch_str
        try:
            arch_str = N.detect_arch(set(val[0] for val in tensors))
        except Exception as e:
            raise ValueError(f"This model is not currently supported - ({e})")
    elif arch_str not in N.TXT_ARCH_LIST and is_text_model:
        if type_str not in N.VIS_TYPE_LIST:
            raise ValueError(f"Unexpected text model architecture type in GGUF file: {arch_str!r}")
    elif arch_str not in N.IMG_ARCH_LIST and not is_text_model:
        raise ValueError(f"Unexpected architecture type in GGUF file: {arch_str!r}")

    if compat:
        logging.warning(f"SY GGUF: this model file is loaded in compatibility mode '{compat}' [arch:{arch_str}]")

    # main loading loop
    state_dict = {}
    qtype_dict = {}
    for sd_key, tensor in tensors:
        tensor_name = tensor.name

        with warnings.catch_warnings():
            warnings.filterwarnings("ignore", message="The given NumPy array is not writable")
            torch_tensor = torch.from_numpy(tensor.data)  # mmap

        shape = get_orig_shape(reader, tensor_name)
        if shape is None:
            shape = torch.Size(tuple(int(v) for v in reversed(tensor.shape)))
            # Workaround for stable-diffusion.cpp SDXL detection.
            if compat == "sd.cpp" and arch_str == "sdxl":
                if any([tensor_name.endswith(x) for x in (".proj_in.weight", ".proj_out.weight")]):
                    while len(shape) > 2 and shape[-1] == 1:
                        shape = shape[:-1]

        # add to state dict
        if tensor.tensor_type in {gguf.GGMLQuantizationType.F32, gguf.GGMLQuantizationType.F16}:
            torch_tensor = torch_tensor.view(*shape)
        state_dict[sd_key] = GGMLTensor(torch_tensor, tensor_type=tensor.tensor_type, tensor_shape=shape)

        # 1D tensors shouldn't be quantized, this is a fix for BF16
        if len(shape) <= 1 and tensor.tensor_type == gguf.GGMLQuantizationType.BF16:
            state_dict[sd_key] = dequantize_tensor(state_dict[sd_key], dtype=torch.float32)

        # keep track of loaded tensor types
        tensor_type_str = getattr(tensor.tensor_type, "name", repr(tensor.tensor_type))
        qtype_dict[tensor_type_str] = qtype_dict.get(tensor_type_str, 0) + 1

    logging.info("SY GGUF qtypes: " + ", ".join(f"{k} ({v})" for k, v in qtype_dict.items()))

    # mark largest tensor for vram estimation
    qsd = {k: v for k, v in state_dict.items() if is_quantized(v)}
    if len(qsd) > 0:
        max_key = max(qsd.keys(), key=lambda k: qsd[k].numel())
        state_dict[max_key].is_largest_weight = True

    extra = {
        "arch_str": arch_str,
        "metadata": get_gguf_metadata(reader),
    }
    return (state_dict, extra)


# ---------------------------------------------------------------- text encoders

def llama_permute(raw_sd, n_head, n_head_kv):
    # Reverse version of LlamaModel.permute in the llama.cpp convert script
    sd = {}
    permute = lambda x, h: x.reshape(h, x.shape[0] // h // 2, 2, *x.shape[1:]).swapaxes(1, 2).reshape(x.shape)
    for k, v in raw_sd.items():
        if k.endswith(("q_proj.weight", "q_proj.bias")):
            v.data = permute(v.data, n_head)
        if k.endswith(("k_proj.weight", "k_proj.bias")):
            v.data = permute(v.data, n_head_kv)
        sd[k] = v
    return sd


def gemma3_norm_corrections(sd):
    # Reverse change from Gemma3Model modify_tensors in the llama.cpp convert script
    for key in list(sd.keys()):
        if N.is_gemma3_norm_key(key):
            if is_quantized(sd[key]):
                sd[key] = dequantize_tensor(sd[key], dtype=torch.float32) - 1.0
            else:
                sd[key] = sd[key].float() - 1.0
    return sd


def gguf_mmproj_loader(path):
    # Reverse version of Qwen2VLVisionModel.modify_tensors
    logging.info("SY GGUF: looking for the mmproj file of the text encoder...")

    tenc_fname = os.path.basename(path)
    tenc = N.strip_quant_suffix(os.path.splitext(tenc_fname)[0].lower())

    root = os.path.dirname(path)
    target = [f for f in os.listdir(root) if N.is_mmproj_for(tenc, f)]

    if len(target) == 0:
        logging.error(f"SY GGUF: no mmproj file found for '{tenc_fname}' (matching '{tenc}'). Image edit models will not work.")
        return {}
    if len(target) > 1:
        logging.error(f"SY GGUF: more than one mmproj file for '{tenc_fname}', using the first.")

    logging.info(f"SY GGUF: using mmproj '{target[0]}' for text encoder '{tenc_fname}'.")
    target = os.path.join(root, target[0])
    vsd, _ = gguf_sd_loader(target, is_text_model=True)

    # concat 4D to 5D
    if "v.patch_embd.weight.1" in vsd:
        w1 = dequantize_tensor(vsd.pop("v.patch_embd.weight"), dtype=torch.float32)
        w2 = dequantize_tensor(vsd.pop("v.patch_embd.weight.1"), dtype=torch.float32)
        vsd["v.patch_embd.weight"] = torch.stack([w1, w2], dim=2)

    vsd = N.sd_map_replace(vsd, N.CLIP_VISION_SD_MAP)

    # handle split Q/K/V
    if "visual.blocks.0.attn_q.weight" in vsd:
        attns = {}
        for k, v in vsd.items():
            if any(x in k for x in ["attn_q", "attn_k", "attn_v"]):
                k_attn, k_name = k.rsplit(".attn_", 1)
                k_attn += ".attn.qkv." + k_name.split(".")[-1]
                if k_attn not in attns:
                    attns[k_attn] = {}
                attns[k_attn][k_name] = dequantize_tensor(
                    v, dtype=(torch.bfloat16 if is_quantized(v) else torch.float16)
                )

        for k, v in attns.items():
            suffix = k.split(".")[-1]
            vsd[k] = torch.cat([
                v[f"q.{suffix}"],
                v[f"k.{suffix}"],
                v[f"v.{suffix}"],
            ], dim=0)
        del attns

    return vsd


def gguf_tokenizer_loader(path, temb_shape):
    # convert gguf tokenizer to spiece
    logging.info("SY GGUF: recreating the sentencepiece tokenizer from the file metadata...")
    try:
        from sentencepiece import sentencepiece_model_pb2 as model
    except ImportError:
        raise ValueError("This text encoder needs the Python packages sentencepiece and protobuf. "
                         "Install them with: python -m pip install sentencepiece protobuf (use the python of your ComfyUI).")
    spm = model.ModelProto()

    reader = gguf.GGUFReader(path)

    if get_field(reader, "tokenizer.ggml.model", str) == "t5":
        if temb_shape == (256384, 4096):  # probably UMT5
            spm.trainer_spec.model_type == 1  # Unigram
        else:
            raise ValueError("Unknown text encoder model, cannot set the tokenizer.")
    else:
        raise ValueError("Unknown text encoder model, cannot set the tokenizer.")

    spm.normalizer_spec.add_dummy_prefix = get_field(reader, "tokenizer.ggml.add_space_prefix", bool)
    spm.normalizer_spec.remove_extra_whitespaces = get_field(reader, "tokenizer.ggml.remove_extra_whitespaces", bool)

    tokens = get_list_field(reader, "tokenizer.ggml.tokens", str)
    scores = get_list_field(reader, "tokenizer.ggml.scores", float)
    toktypes = get_list_field(reader, "tokenizer.ggml.token_type", int)

    for idx, (token, score, toktype) in enumerate(zip(tokens, scores, toktypes)):
        piece = spm.SentencePiece()
        piece.piece = token
        piece.score = score
        piece.type = toktype
        spm.pieces.append(piece)

    spm.trainer_spec.byte_fallback = True
    spm.trainer_spec.vocab_size = len(tokens)
    spm.trainer_spec.max_sentence_length = 4096
    spm.trainer_spec.eos_id = get_field(reader, "tokenizer.ggml.eos_token_id", int)
    spm.trainer_spec.pad_id = get_field(reader, "tokenizer.ggml.padding_token_id", int)

    logging.info(f"SY GGUF: created tokenizer with vocab size {len(spm.pieces)}")
    del reader
    return torch.ByteTensor(list(spm.SerializeToString()))


def gguf_tekken_tokenizer_loader(path, temb_shape):
    # convert ggml (hf) tokenizer metadata to tekken/comfy data
    logging.info("SY GGUF: recreating the tekken tokenizer from the file metadata...")
    import json
    import base64

    reader = gguf.GGUFReader(path)

    model_str = get_field(reader, "tokenizer.ggml.model", str)
    if model_str == "gpt2":
        if temb_shape == (131072, 5120):  # probably Mistral
            data = {
                "config": {"num_vocab_tokens": 150000, "default_vocab_size": 131072},
                "vocab": [],
                "special_tokens": [],
            }
        else:
            raise ValueError("Unknown text encoder model, cannot set the tokenizer.")
    else:
        raise ValueError("Unknown text encoder model, cannot set the tokenizer.")

    tokens = get_list_field(reader, "tokenizer.ggml.tokens", str)
    toktypes = get_list_field(reader, "tokenizer.ggml.token_type", int)

    decoder = {v: k for k, v in N.bytes_to_unicode().items()}
    for idx, (token, toktype) in enumerate(zip(tokens, toktypes)):
        if toktype == 3:
            data["special_tokens"].append(
                {'rank': idx, 'token_str': token, 'is_control': True}
            )
        else:
            tok = bytes([decoder[char] for char in token])
            data["vocab"].append({
                "rank": len(data["vocab"]),
                "token_bytes": base64.b64encode(tok).decode("ascii"),
                "token_str": tok.decode("utf-8", errors="replace"),
            })

    logging.info(f"SY GGUF: created tekken tokenizer with vocab size {len(data['vocab'])} (+{len(data['special_tokens'])})")
    del reader
    return torch.ByteTensor(list(json.dumps(data).encode('utf-8')))


def gguf_gemma3_tokenizer_loader(path):
    logging.info("SY GGUF: recreating the sentencepiece tokenizer from the file metadata...")
    try:
        from sentencepiece import sentencepiece_model_pb2 as model
    except ImportError:
        raise ValueError("This text encoder needs the Python packages sentencepiece and protobuf. "
                         "Install them with: python -m pip install sentencepiece protobuf (use the python of your ComfyUI).")
    spm = model.ModelProto()
    reader = gguf.GGUFReader(path)

    spm.normalizer_spec.name = "identity"
    spm.normalizer_spec.add_dummy_prefix = False
    spm.trainer_spec.model_type = 2
    spm.trainer_spec.input_format = "tsv"
    spm.trainer_spec.byte_fallback = True
    spm.trainer_spec.max_sentence_length = 4192
    spm.trainer_spec.bos_piece = "<bos>"

    tokens = get_list_field(reader, "tokenizer.ggml.tokens", str)
    scores = get_list_field(reader, "tokenizer.ggml.scores", float)
    toktype = get_list_field(reader, "tokenizer.ggml.token_type", int)

    if not tokens or not scores or not toktype:
        raise ValueError("The GGUF file has no tokenizer data (missing metadata).")

    for idx in range(len(tokens)):
        piece = spm.SentencePiece()
        piece.piece = tokens[idx]
        if idx == 3:  # UNK position
            piece.type = 2  # UNK Token
            piece.score = 0.0  # UNK Score
        else:
            piece.type = toktype[idx]
            piece.score = scores[idx]
        spm.pieces.append(piece)

    spm.trainer_spec.vocab_size = len(spm.pieces)
    logging.info(f"SY GGUF: created tokenizer with vocab size {len(spm.pieces)}")

    del reader
    return torch.ByteTensor(list(spm.SerializeToString()))


def gguf_clip_loader(path):
    sd, extra = gguf_sd_loader(path, is_text_model=True)
    arch = extra.get("arch_str", None)
    if arch in {"t5", "t5encoder"}:
        temb_key = "token_embd.weight"
        if temb_key in sd and sd[temb_key].shape == (256384, 4096):
            # non-standard Comfy-Org tokenizer
            sd["spiece_model"] = gguf_tokenizer_loader(path, sd[temb_key].shape)
            # Dequantizing the token embedding here avoids running out of memory later.
            logging.warning(f"SY GGUF: dequantizing {temb_key} to prevent runtime OOM.")
            sd[temb_key] = dequantize_tensor(sd[temb_key], dtype=torch.float16)
        sd = N.sd_map_replace(sd, N.T5_SD_MAP)
    elif arch in {"llama", "qwen2vl", "qwen3", "qwen3vl", "gemma3"}:
        temb_key = "token_embd.weight"
        if temb_key in sd and sd[temb_key].shape[0] >= (64 * 1024):
            if arch == "llama" and sd[temb_key].shape == (131072, 5120):
                # non-standard Comfy-Org tokenizer
                sd["tekken_model"] = gguf_tekken_tokenizer_loader(path, sd[temb_key].shape)
            elif arch == "gemma3":
                sd["spiece_model"] = gguf_gemma3_tokenizer_loader(path)
            logging.warning(f"SY GGUF: dequantizing {temb_key} to prevent runtime OOM.")
            sd[temb_key] = dequantize_tensor(sd[temb_key], dtype=torch.float16)
        if arch == "gemma3":
            sd = N.sd_map_replace(sd, N.GEMMA3_SD_MAP)
            sd = gemma3_norm_corrections(sd)
        else:
            sd = N.sd_map_replace(sd, N.LLAMA_SD_MAP)
        if arch == "llama":
            sd = llama_permute(sd, 32, 8)  # L3 / Mistral
        if arch == "qwen2vl":
            vsd = gguf_mmproj_loader(path)
            sd.update(vsd)
    return sd


# ---------------------------------------------------------------- the three entry points the nodes call

def load_unet(unet_path, dequant_dtype=None, patch_dtype=None, patch_on_device=False):
    """Load a GGUF diffusion model into a ModelPatcher that supports LoRA."""
    import comfy.sd
    ops_cls = get_ops()
    ops = ops_cls()

    # reset the shared class settings on every load, so an earlier load cannot leak in
    for attr, value in (("dequant_dtype", dequant_dtype), ("patch_dtype", patch_dtype)):
        if value in ("default", None):
            setattr(ops.Linear, attr, None)
        elif value == "target":
            setattr(ops.Linear, attr, value)
        else:
            setattr(ops.Linear, attr, getattr(torch, value))

    sd, extra = gguf_sd_loader(unet_path)

    kwargs = {}
    valid_params = inspect.signature(comfy.sd.load_diffusion_model_state_dict).parameters
    if "metadata" in valid_params:
        kwargs["metadata"] = extra.get("metadata", {})

    model = comfy.sd.load_diffusion_model_state_dict(
        sd, model_options={"custom_operations": ops}, **kwargs,
    )
    if model is None:
        logging.error("SY GGUF: unsupported model %s", unet_path)
        raise ValueError("Could not detect the model type of %s. This GGUF file is not a supported diffusion model." % unet_path)
    model = get_patcher().clone(model)
    model.patch_on_device = patch_on_device
    return model


def load_clip(clip_paths, clip_type_name):
    """Load one or two text encoder files (.gguf or normal) into a CLIP object."""
    import comfy.model_management
    import comfy.sd
    import comfy.utils
    import folder_paths

    clip_data = []
    for p in clip_paths:
        if p.lower().endswith(".gguf"):
            sd = gguf_clip_loader(p)
        else:
            sd = comfy.utils.load_torch_file(p, safe_load=True)
            if "scaled_fp8" in sd:  # Scaled FP8 needs different custom ops, but only one can be active
                raise ValueError("Mixing scaled FP8 with GGUF is not supported. Use the normal CLIP loader, or pick other files (%s)" % p)
        clip_data.append(sd)

    clip_type = getattr(comfy.sd.CLIPType, clip_type_name.upper(), comfy.sd.CLIPType.STABLE_DIFFUSION)
    clip = comfy.sd.load_text_encoder_state_dicts(
        clip_type=clip_type,
        state_dicts=clip_data,
        model_options={
            "custom_operations": get_ops(),
            "initial_device": comfy.model_management.text_encoder_offload_device(),
        },
        embedding_directory=folder_paths.get_folder_paths("embeddings"),
    )
    clip.patcher = get_patcher().clone(clip.patcher)
    return clip
