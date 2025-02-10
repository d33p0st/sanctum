
from os.path import basename
from typing import Type
import platform
import colorama

class SecretError:
    def __init__(self, exception: Type[BaseException], *args) -> None:
        colorama.init()
        print(
            ("" if platform.system() == "Windows" else colorama.Fore.RED) \
            + exception.__qualname__ \
            + ("" if platform.system() == "Windows" else colorama.Fore.RESET) + \
            ':',
            *args
        )
        colorama.deinit()
        exit(1)
