import io
import sys


class capture_stdout:
    r"""Class allowing to capture stdout.

    Example:
        >>> from pettingzoo.utils.capture_stdout import capture_stdout
        >>> with capture_stdout() as var:
        ...     print("test")
        ...     data = var.getvalue()
        ...
        >>> data
        'test\n'

    """

    def __init__(self):
        self.old_stdout = None

    def __enter__(self) -> io.StringIO:
        self.old_stdout = sys.stdout
        self.buff = io.StringIO()
        sys.stdout = self.buff
        return self.buff

    def __exit__(self, type, value, traceback):
        sys.stdout = self.old_stdout
        self.buff.close()
