"""`sanctum`, as the name suggests helps in creating private/protected
modules in python. It is capable of making certain modules restricted
to the user while maintaing usability withing the library.

Methodology:

1. Choosing the restricted paths: It is recommended to keep your private
modules in a separate folder. Suppose you want to restrict a module
whose path goes like `my_lib.private._bins`, you have to create a list
such that - `["my_lib.private", "my_lib.private._bins"]`.

2. Choosing the allowed paths: It is also recommended to not mix private
and public modules in the same folder. Just the folder path is sufficient
to recognize all sub-modules under it. If there is a folder named `public`
and the path goes like `my_lib.public` which contains one or more 
sub-modules, all of which uses the private module, you can create the list
as `["my_lib.public"]` which will whitelist all sub-modules under it. If
only few of the sub-modules are using the `private` module, you can mention
them individually.

3. Defining a global library specification. This has to be done inside the
root `__init__.py` file of your library.

    ```python
    from sanctum import libspec, LibSpec, Sanctum

    # create a library spec
    specs = LibSpec(
        restricted=["my_lib.private", "my_lib.private._bins"],
        allowed=["my_lib.public"], # includes all sub-modules by folder 
    )

    # set the libspec globally.
    libspec(specs)

    # Initialize Sanctum
    Sanctum()
    ```
4. For all classes defined in any of the whitelisted modules use the
`SanctumMeta` metaclass to clear caches of restricted modules upon
loading.

    ```python
    from sanctum import SanctumMeta

    # this file is a whitelisted file.
    class ExampleClass(metaclass=SanctumMeta):
        # class body here
        pass
    ```
5. For all methods defined in any of the whitelisted modules use the
`Sanctum` class itself as a decorator to clear caches of restricted
modules upon loading.

    ```python
    from sanctum import Sanctum

    @Sanctum()
    def example_function() -> None:
        # logic here
        ...
    ```
"""


from importlib.machinery import ModuleSpec
from types import ModuleType
from typing import Sequence, TypeVar, Iterable, Union
from typing import overload
from importlib.abc import MetaPathFinder

M = TypeVar('METHOD')

class LibSpec(MetaPathFinder):
    """LibSpec Class.

    This class acts as a specification manager as well as meta path
    resolver for differentiating restricted and allowed module paths.
    The module paths must use dot format (`"my_lib.module.module2"`).

    This class is responsible for changing the default behaviour of
    python for looking up modules and storing caches of it, to a custom
    behaviour where it restricts the specified module paths from being
    imported while allowing imports internally/externally in whitelisted
    (allowed) module paths.

    All the module paths that are whitelisted will be able to use the
    restricted module and after loading those whitelisted modules, the
    caches are cleared which makes python look for it again (which is 
    bound to raise restricted error if the module that tried to import
    it among the whitelisted modules).
    """
    def __init__(
            self,
            restricted: Iterable[str],
            allowed: Iterable[str],
    ) -> None:
        """Create a LibSpec with given iterable of restricted and allowed
        module paths.
        
        The module paths specified in the restricted iterable will be
        restricted to the user and therefore will raise a no-traceback
        `Import Error`. This is to ensure security and omit partial
        code printing in the traceback which might reveal unwanted hints
        towards the restricted modules.

        The module paths specified in the allowed iterable will be
        whitelisted from the restriction. This can be a list of module
        folders if all sub-modules are to be included (individual names
        are not needed). For example, if there is a module folder named
        `utils` and it has a lot of `py` files inside, mentioning the
        module name itself is enough to include all the sub-modules under
        it.

        All module paths follow the python dot format. For example,
        `my_lib.module` where module can be either a folder (which will
        include all sub-modules under it) or a py file.
        """
    
    def find_spec(self, fullname: str, path: Union[Sequence[str], None], target: Union[ModuleType, None] = ...) -> Union[ModuleSpec, None]: ...

def libspec(spec: LibSpec) -> None:
    """Sets the Library Specs globally."""

class Sanctum:
    """Sanctum class/decorator.
    
    In the root `__init__.py` file use it as a class. while it can be
    used as a decorator over functions (not methods in a class) to
    clear caches of restricted modules upon loading.

    This is to be used for all functions under the whitelisted modules.
    """
    def __init__(self) -> None:
        """Creates a Sanctum Object."""
    
    def reset(self) -> None:
        """Resets the default python behaviour for resolving module paths."""
    
    def __call__(self, func: M) -> M:
        """Decorator implementation to clear caches after loading
        functions. To be strictly used with functions."""
    
    def clear(self) -> None:
        """Clears caches manually."""
    
    @staticmethod
    def clear_cache_with_name(_: str) -> None: ...

class SanctumMeta(type):
    """Metaclass for classes to clear caches of restricted modules upon
    load.
    
    >>> class Example(metaclass=SanctumMeta):
    ...     pass

    This will remove any dangling caches after the class has been loaded.
    It is to be used for all classes that are defined under the whitelisted
    modules.
    """