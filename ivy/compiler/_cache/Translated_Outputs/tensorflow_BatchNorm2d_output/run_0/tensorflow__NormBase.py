import tensorflow
import tensorflow as tf
from collections import OrderedDict
import threading

import typing

from .tensorflow__stateful import Layer as tensorflow_keras_Layer
from .tensorflow__helpers import tensorflow__is_variable
from .tensorflow__helpers import tensorflow_add
from .tensorflow__helpers import tensorflow_default
from .tensorflow__helpers import tensorflow_device
from .tensorflow__helpers import tensorflow_empty
from .tensorflow__helpers import tensorflow_fill_
from .tensorflow__helpers import tensorflow_ones
from .tensorflow__helpers import tensorflow_ones_
from .tensorflow__helpers import tensorflow_set_item
from .tensorflow__helpers import tensorflow_split_2
from .tensorflow__helpers import tensorflow_store_config_info
from .tensorflow__helpers import tensorflow_tensor
from .tensorflow__helpers import tensorflow_zero_
from .tensorflow__helpers import tensorflow_zeros
from .tensorflow__helpers import tensorflow_zeros_


class tensorflow__NormBase(tensorflow_keras_Layer):
    _version = 2
    __constants__ = ["track_running_stats", "momentum", "eps", "num_features", "affine"]
    num_features: typing.Any
    eps: typing.Any
    momentum: typing.Any
    affine: typing.Any
    track_running_stats: typing.Any

    @tensorflow_store_config_info
    def __init__(
        self,
        num_features,
        eps=1e-05,
        momentum=0.1,
        affine=True,
        track_running_stats=True,
        device=None,
        dtype=None,
    ):
        factory_kwargs = {"device": device, "dtype": dtype}
        self.super___init__(
            num_features,
            eps=eps,
            momentum=momentum,
            affine=affine,
            track_running_stats=track_running_stats,
            device=device,
            dtype=dtype,
            v=getattr(self, "_v", None),
            buffers=getattr(self, "_buffers", None),
            module_dict=getattr(self, "_module_dict", None),
        )
        self.num_features = num_features
        self.eps = eps
        self.momentum = momentum
        self.affine = affine
        self.track_running_stats = track_running_stats
        if self.affine:
            self.weight = tensorflow.Variable(
                tensorflow_empty(num_features, **factory_kwargs), name="weight"
            )
            self.bias = tensorflow.Variable(
                tensorflow_empty(num_features, **factory_kwargs), name="bias"
            )
        else:
            self.register_parameter("weight", None)
            self.register_parameter("bias", None)
        if self.track_running_stats:
            self.register_buffer(
                "running_mean", tensorflow_zeros(num_features, **factory_kwargs)
            )
            self.register_buffer(
                "running_var", tensorflow_ones(num_features, **factory_kwargs)
            )
            self.running_mean: typing.Any
            self.running_var: typing.Any
            self.register_buffer(
                "num_batches_tracked",
                tensorflow_tensor(
                    0,
                    dtype=tf.int64,
                    **{k: v for k, v in factory_kwargs.items() if k != "dtype"},
                ),
            )
            self.num_batches_tracked: typing.Any
        else:
            self.register_buffer("running_mean", None)
            self.register_buffer("running_var", None)
            self.register_buffer("num_batches_tracked", None)
        self.reset_parameters()

    def reset_running_stats(self):
        if self.track_running_stats:
            tensorflow_zero_(self.running_mean)
            tensorflow_fill_(self.running_var, 1)
            tensorflow_zero_(self.num_batches_tracked)

    def reset_parameters(self):
        self.reset_running_stats()
        if self.affine:
            tensorflow_ones_(self.weight)
            tensorflow_zeros_(self.bias)

    def _check_input_dim(self, input):
        raise NotImplementedError

    def extra_repr(self):
        return "{num_features}, eps={eps}, momentum={momentum}, affine={affine}, track_running_stats={track_running_stats}".format(
            **self.__dict__
        )

    def _load_from_state_dict(
        self,
        state_dict,
        prefix,
        local_metadata,
        strict,
        missing_keys,
        unexpected_keys,
        error_msgs,
    ):
        version = local_metadata.get("version", None)
        if (version is None or version < 2) and self.track_running_stats:
            num_batches_tracked_key = prefix + "num_batches_tracked"
            if num_batches_tracked_key not in state_dict:
                with tensorflow.name_scope("state_dict"):
                    state_dict = tensorflow_set_item(
                        state_dict,
                        num_batches_tracked_key,
                        self.num_batches_tracked
                        if self.num_batches_tracked is not None
                        and self.num_batches_tracked.device != tensorflow_device("meta")
                        else tensorflow_tensor(0, dtype=tf.int64),
                    )
        super()._load_from_state_dict(
            state_dict,
            prefix,
            local_metadata,
            strict,
            missing_keys,
            unexpected_keys,
            error_msgs,
        )

    def super___init__(self, *args, device=None, devices=None, **kwargs):
        super().__init__(
            self,
            *args,
            device=device,
            devices=devices,
            training=True,
            build_mode="explicit",
            dynamic_backend=True,
            **kwargs,
        )
        super().__setattr__("_frontend_module", True)
        super().__setattr__(
            "_attr_mapping", {"_parameters": "v", "_modules": "module_dict"}
        )

    def __dir__(self):
        module_attrs = dir(self.__class__)
        attrs = list(self.__dict__.keys())
        parameters = list(self._v.keys())
        modules = list(self._module_dict.keys())
        buffers = list(self._buffers.keys())
        keys = module_attrs + attrs + parameters + modules + buffers
        ag__result_list_0 = []
        for key in keys:
            if not key[0].isdigit():
                res = key
                ag__result_list_0.append(res)
        keys = ag__result_list_0
        return sorted(keys)

    def __getattribute__(self, name):
        if name == "__dict__":
            return super().__getattribute__(name)
        if "_module_dict" in self.__dict__:
            modules = self.__dict__["_module_dict"]
            if name in modules:
                return modules[name]
        if "_buffers" in self.__dict__:
            buffers = self.__dict__["_buffers"]
            if name in buffers:
                return buffers[name]
        if "_v" in self.__dict__:
            v = self.__dict__["_v"]
            if name in v:
                return v[name]
        if "_attr_mapping" in self.__dict__:
            mapping = self.__dict__["_attr_mapping"]
            if name in mapping:
                return super().__getattribute__(mapping[name])
        return super().__getattribute__(name)

    def __getstate__(self):
        state = self.__dict__.copy()
        state.pop("_compiled_call_impl", None)
        state.pop("_thread_local", None)
        state.pop("_metrics_lock", None)
        return state

    def __repr__(self):
        extra_lines = []
        extra_repr = self._extra_repr()
        if extra_repr:
            with tensorflow.name_scope("extra_lines"):
                extra_lines = tensorflow_split_2(extra_repr, "\n")
        child_lines = []
        for key, module in self._module_dict.items():
            mod_str = repr(module)
            mod_str = self._addindent(mod_str, 2)
            child_lines.append("(" + key + "): " + mod_str)
        lines = extra_lines + child_lines
        main_str = self._get_name() + "("
        if lines:
            if len(extra_lines) == 1 and not child_lines:
                main_str += extra_lines[0]
            else:
                main_str += "\n  " + "\n  ".join(lines) + "\n"
        main_str += ")"
        return main_str

    def __setattr__(self, name, value):
        def remove_from(*dicts_or_sets):
            for d in dicts_or_sets:
                if name in d:
                    if isinstance(d, dict):
                        del d[name]
                    else:
                        d.discard(name)

        params = self.__dict__.get("_v")
        if (
            params is not None
            and name in params
            and isinstance(value, tensorflow.Variable)
        ):
            remove_from(self.__dict__, self._buffers, self._module_dict)
            self.register_parameter(name, value)
            super().__setattr__(name, value)
        else:
            super().__setattr__(name, value)

    def __setstate__(self, state):
        state["_thread_local"] = threading.local()
        state["_metrics_lock"] = threading.Lock()
        self.__dict__.update(state)

    def _build(self, *args, **kwargs):
        for module in self.__dict__.values():
            if isinstance(module, tensorflow_keras_Layer) and module is not self:
                if not module._built:
                    module.build(
                        *module._args,
                        dynamic_backend=module._dynamic_backend,
                        **module._kwargs,
                    )
        return True

    def _call_impl(self, *args, **kwargs):
        return self.call(*args, **kwargs)

    def _create_variables(self, device=None, dtype=None):
        with tensorflow.name_scope("v"):
            v = dict(
                OrderedDict(
                    [
                        (k.replace(".", "/"), v)
                        for k, v in self.__dict__.items()
                        if isinstance(v, tensorflow.Variable) and not k.startswith("_")
                    ]
                )
            )
        v = (
            dict(
                OrderedDict(
                    {
                        _k.replace(".", "/"): _v
                        for _k, _v in self._v.items()
                        if _k.replace(".", "/") not in v and not isinstance(_v, dict)
                    },
                    **v,
                )
            )
            if self._v
            else v
        )
        return v

    def _extra_repr(self):
        return ""

    def _forward(self, *a, **kw):
        ret = self._call_impl(*a, **kw)
        return ret

    def _get_name(self):
        return self.__class__.__name__

    def _named_members(
        self, get_members_fn, prefix="", recurse=True, remove_duplicate=True
    ):
        memo = set()
        modules = (
            self.named_modules(prefix=prefix, remove_duplicate=remove_duplicate)
            if recurse
            else [(prefix, self)]
        )
        for module_prefix, module in modules:
            members = get_members_fn(module)
            for k, v in members:
                if v is None or id(v) in memo:
                    continue
                if remove_duplicate:
                    tensorflow_add(memo, id(v))
                name = module_prefix + ("." if module_prefix else "") + k
                yield name, v

    def _replace_update_v(self, new_v, native=None):
        with tensorflow.name_scope("native"):
            native = tensorflow_default(native, self)
        for k, v in new_v.items():
            if isinstance(v, dict):
                native.module_dict[k] = self._replace_update_v(v, native.module_dict[k])
            elif isinstance(v, tensorflow.Variable):
                native.__setattr__(k, v)
            elif tensorflow__is_variable(v):
                native.__setattr__(k, tensorflow.Variable(v))
            elif isinstance(v, tensorflow.Variable):
                native.__setattr__(k, tensorflow.Variable(v))
            else:
                raise Exception(
                    f"found item in variable container {v} which was neither a sub ivy.Container nor a variable."
                )
        return native

    def _update_v(self, new_v, native=None):
        with tensorflow.name_scope("native"):
            native = tensorflow_default(native, self)
        for k, v in new_v.items():
            if isinstance(v, dict):
                native.module_dict[k] = self._replace_update_v(v, native.module_dict[k])
            elif isinstance(v, tensorflow.Variable):
                native.__setattr__(k, v)
            elif tensorflow__is_variable(v):
                native.__setattr__(k, tensorflow.Variable(v))
            elif isinstance(v, tensorflow.Variable):
                native.__setattr__(k, tensorflow.Variable(v))
            else:
                raise Exception(
                    f"found item in variable container {v} which was neither a sub ivy.Container nor a variable."
                )
        return native

    def add_module(self, name, module):
        if (
            not isinstance(
                module, (tensorflow_keras_Layer, tensorflow.keras.layers.Layer)
            )
            and module is not None
        ):
            raise TypeError(f"{type(module)} is not a Module subclass")
        elif not isinstance(name, str):
            raise TypeError(f"module name should be a string. Got {type(name)}")
        elif hasattr(self, name) and name not in self._modules:
            raise KeyError(f"attribute '{name}' already exists")
        elif "." in name:
            raise KeyError(f'module name can\'t contain ".", got: {name}')
        elif name == "":
            raise KeyError('module name can\'t be empty string ""')
        self._modules[name] = module
        super().__setattr__(name, module)

    def apply(self, fn):
        for module in self.children():
            if hasattr(module, "apply"):
                module.apply(fn)
            else:
                fn(module)
        fn(self)
        return self

    def children(self):
        for _, module in self.named_children():
            yield module

    def call(self, *input):
        raise NotImplementedError(
            f'Module [{type(self).__name__}] is missing the required "forward" function'
        )

    def get_parameter(self, target):
        target = target.replace(".", "/")
        return self.pt_v[target]

    def get_submodule(self, target):
        if target == "":
            return self
        atoms: typing.Any = tensorflow_split_2(target, ".")
        mod: typing.Any = self
        for item in atoms:
            if not hasattr(mod, item):
                raise AttributeError(
                    mod._get_name() + " has no attribute `" + item + "`"
                )
            mod = getattr(mod, item)
            if not isinstance(mod, tensorflow_keras_Layer):
                raise TypeError("`" + item + "` is not an nn.Module")
        return mod

    def modules(self):
        for _, module in self.named_modules():
            yield module

    def named_buffers(self, prefix="", recurse=True, remove_duplicate=True):
        if not getattr(self, "_built", False):
            self.build(
                *self._args, dynamic_backend=self._dynamic_backend, **self._kwargs
            )
        gen = self._named_members(
            lambda module: module.buffers.items(),
            prefix=prefix,
            recurse=recurse,
            remove_duplicate=remove_duplicate,
        )
        yield from gen

    def named_children(self):
        if not getattr(self, "_built", False):
            self.build(
                *self._args, dynamic_backend=self._dynamic_backend, **self._kwargs
            )
        memo = set()
        for name, module in self._module_dict.items():
            if module is not None and id(module) not in memo:
                tensorflow_add(memo, id(module))
                yield name, module

    def named_modules(self, memo=None, prefix="", remove_duplicate=True):
        if not getattr(self, "_built", False):
            self.build(
                *self._args, dynamic_backend=self._dynamic_backend, **self._kwargs
            )
        if memo is None:
            memo = set()
        if id(self) not in memo:
            if remove_duplicate:
                tensorflow_add(memo, id(self))
            yield prefix, self
            for name, module in self._module_dict.items():
                if module is None:
                    continue
                submodule_prefix = prefix + ("." if prefix else "") + name
                if not hasattr(module, "named_modules"):
                    yield submodule_prefix, self
                else:
                    yield from module.named_modules(
                        memo, submodule_prefix, remove_duplicate
                    )

    def named_parameters(self, prefix="", recurse=True, remove_duplicate=True):
        if not getattr(self, "_built", False):
            self.build(
                *self._args, dynamic_backend=self._dynamic_backend, **self._kwargs
            )
        gen = self._named_members(
            lambda module: module.v.items(),
            prefix=prefix,
            recurse=recurse,
            remove_duplicate=remove_duplicate,
        )
        yield from gen

    def parameters(self, recurse=True):
        for _, param in self.named_parameters(recurse=recurse):
            yield param

    def register_buffer(self, name, value, persistent=False):
        super().register_buffer(name, value)

    def register_module(self, name, module):
        self.add_module(name, module)

    def register_parameter(self, name, value):
        super().register_parameter(name, value)

    def requires_grad_(self, requires_grad=True):
        for p in self.parameters():
            p.requires_grad_(requires_grad)
        return self
