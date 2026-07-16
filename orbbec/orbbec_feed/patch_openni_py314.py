"""
Re-apply the Python 3.13+/3.14 compatibility fix to the installed `openni`
package. Run this once after (re)installing `openni` in an environment:

    python patch_openni_py314.py

The stock `openni` (2.3.0) defines its C enums through a custom ctypes
metaclass that instantiates enum members during class creation. On Python
3.13+ that raises "TypeError: abstract class". This rewrites CEnum to subclass
ctypes.c_int directly, which works on all Python versions. Idempotent.
"""
import io
import os
import openni.utils as u

path = u.__file__
src = io.open(path, encoding="utf-8").read()

if "Python 3.13+/3.14 compatibility patch" in src:
    print("Already patched:", path)
    raise SystemExit(0)

marker = "class CEnumMeta(type(ctypes.c_int)):"
if marker not in src:
    print("Could not find CEnumMeta in", path, "- openni version may differ; not patched.")
    raise SystemExit(1)

old = '''class CEnumMeta(type(ctypes.c_int)):
    def __new__(cls, name, bases, namespace):
        cls2 = type(ctypes.c_int).__new__(cls, name, bases, namespace)
        if namespace.get("__module__") != __name__:
            namespace["_values_"].clear()
            for name in namespace["_names_"].keys():
                if name.startswith("_"):
                    continue
                setattr(cls2, name, cls2(namespace[name]))
                namespace["_names_"][name] = namespace[name]
                namespace["_values_"][namespace[name]] = name
        return cls2


def with_meta(meta, base=object):
    return meta("NewBase", (base,), {"__module__": __name__})


class CEnum(with_meta(CEnumMeta, ctypes.c_int)):
    _names_ = {}
    _values_ = {}
    __slots__ = []'''

new = '''# --- Python 3.13+/3.14 compatibility patch ---------------------------------
# The original code instantiated each enum member while the class was still
# being created, which raises "TypeError: abstract class" on Python 3.13+.
# CEnum now subclasses c_int directly (normal ctypes metaclass); values
# returned from C via `restype` still construct correctly, and enum members
# remain the plain ints declared in _openni2.py (they compare through int()).
class CEnum(ctypes.c_int):
    _names_ = {}
    _values_ = {}
    __slots__ = []'''

if old not in src:
    print("CEnumMeta present but does not match the expected text; not patched.")
    raise SystemExit(1)

io.open(path, "w", encoding="utf-8").write(src.replace(old, new))
# drop stale bytecode
cache = os.path.join(os.path.dirname(path), "__pycache__")
if os.path.isdir(cache):
    for f in os.listdir(cache):
        if f.startswith("utils."):
            os.remove(os.path.join(cache, f))
print("Patched:", path)
