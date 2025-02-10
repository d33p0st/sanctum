
class SecretError:
    """Secretive Error Exception Generator."""
    def __init__(self, exception: BaseException, *args: str):
        """Creates a suprressed secret error of the given type."""