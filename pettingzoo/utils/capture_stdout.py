import numpy as np
import io
import sys


class capture_stdout:
    '''
    usage:

    with capture_stdout() as var:
        print("hithere")

        # value of var will be "hithere"
        data = var.getvalue()
    '''
    def __init__(self):
        self.old_stdout = None

    def __enter__(self):
        self.old_stdout = sys.stdout
        self.buff = io.StringIO()
        sys.stdout = self.buff
        return self.buff

    def __exit__(self, type, value, traceback):
        sys.stdout = self.old_stdout
        self.buff.close()
