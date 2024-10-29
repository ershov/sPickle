import io
import pickle
import enum, dataclasses
from collections import namedtuple

VERSION = "0.1.0"

safe_classes = {
    ("builtins", "NoneType"),
    ("builtins", "bool"),
    ("builtins", "str"),
    ("builtins", "bytes"),
    ("builtins", "bytearray"),
    ("builtins", "int"),
    ("builtins", "float"),
    ("builtins", "list"),
    ("builtins", "dict"),
    ("builtins", "tuple"),
    ("builtins", "set"),
    ("builtins", "frozenset"),
}

PickleError = pickle.PickleError
PicklingError = pickle.PicklingError
UnpicklingError = pickle.UnpicklingError

# This doesn't really work. TODO: fix it.
class RestrictedPicklerClassic(pickle.Pickler):
    def save(self, obj, *args, **kwargs):
        objtype = type(obj)
        if (objtype.__module__, objtype.__name__) not in safe_classes:
            raise PicklingError(f"Attempting to pickle unsafe class {objtype.__module__}.{objtype.__name__}")

        return super().save(obj, *args, **kwargs)

class RestrictedUnpicklerClassic(pickle.Unpickler):
    def find_class(self, module, name):
        if (module, name) not in safe_classes:
            raise UnpicklingError(f"Attempting to unpickle unsafe class {module}.{name}")

        return super().find_class(module, name)

def dump(obj, *args, **kwargs):
    return RestrictedPicklerClassic(*args, **kwargs).dump(obj)

def dumps(obj, *args, **kwargs):
    f = io.BytesIO()
    RestrictedPicklerClassic(f, *args, **kwargs).dump(obj)
    return f.getvalue()

def load(*args, **kwargs):
    return RestrictedUnpicklerClassic(*args, **kwargs).load()

def loads(s, *args, **kwargs):
    if isinstance(s, str):
        raise TypeError("Can't load pickle from unicode string")
    f = io.BytesIO(s)
    return RestrictedUnpicklerClassic(f, *args, **kwargs).load()
