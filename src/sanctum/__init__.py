
from .exception_handler import SecretError
from importlib.abc import MetaPathFinder
from typing import Iterable, TypeVar, List
from pathlib import Path
from abc import ABCMeta
from functools import wraps
import inspect
import sys

M = TypeVar('METHOD')

class LibSpec(MetaPathFinder):
    def __init__(
            self,
            restricted: Iterable[str],
            allowed: Iterable[str],
    ) -> None:
        super().__init__()
        # normalize allowed: from . to /
        if (not isinstance(restricted, Iterable) or not all(isinstance(t, str) for t in restricted)) or (not isinstance(allowed, Iterable) or not all(isinstance(t, str) for t in allowed)):
            return SecretError(TypeError, "paramets must be Iterable[str] for LibSpec.")
        for idx, _ in enumerate(allowed):
            parts = _.split('.')
            append = Path(parts[0])
            for part in parts[1:]:
                append /= part
            allowed[idx] = append
        setattr(self, '!restricted', restricted)
        setattr(self, '!allowed', list(map(str, allowed)))
    
    def find_spec(self, fullname, path, target):
        for restrictee in getattr(self, '!restricted'):
            if fullname == restrictee:
                setattr(self, '!caller[]', [])
                stack = inspect.stack()
                for frame in stack:
                    getattr(self, '!caller[]').append(frame.filename)
                for caller in getattr(self, '!caller[]'):
                    # print("caller", caller, "fullname", fullname)
                    for allowed in getattr(self, '!allowed'):
                        if allowed in caller:
                            # print("check passed:", fullname, caller)
                            # print(caller)
                            setattr(self, '!caller[]', [])
                            return None
                # print("not passed:", fullname, getattr(self, '!caller[]'))
                setattr(self, '!caller[]', [])
                return SecretError(ImportError, f"{fullname} cannot be imported. This module path is restricted to user.")
        return None

LIBSpec: LibSpec = None

def libspec(spec: LibSpec) -> None:
    global LIBSpec
    LIBSpec = spec

class Sanctum:
    def __init__(self) -> None:
        spec = LIBSpec
        if spec is None:
            return SecretError(RuntimeError, "use 'sanctum.libspec' method to set the library specifications!")
        if not isinstance(spec, LibSpec):
            return SecretError(TypeError, "'spec' must be of type <class 'sanctum.sanctum.LibSpec'>")
        if not isinstance(sys.meta_path[0], LibSpec):
            sys.meta_path.insert(0, spec)
        setattr(self, '!spec', spec)
    
    def reset(self) -> None:
        if isinstance(sys.meta_path[0], LibSpec):
            sys.meta_path.pop(0)
        return None
    
    def __call__(self, func: M) -> M:
        @wraps(func)
        def wrapper(*args, **kwargs):
            self.clear()
            return func(*args, **kwargs)
        return wrapper
    
    def clear(self) -> None:
        restricted: List[str] = getattr(getattr(self, '!spec'), '!restricted')
        for rest in restricted:
            if rest in sys.modules:
                del sys.modules[rest]
    
    @staticmethod
    def clear_cache_with_name(_: str) -> None:
        if _ in sys.modules:
            del sys.modules[_]

class SanctumMeta(ABCMeta):
    def __init__(cls, name, bases, dct, /, **kwds):
        super().__init__(name, bases, dct)
        Sanctum().clear()

__all__ = [
    "LibSpec",
    "Sanctum",
    "libspec",
]