import logging


class EnvLogger():
    mqueue = []
    _output = True

    @staticmethod
    def get_logger():
        logger = logging.getLogger(__name__)
        return logger

    @staticmethod
    def _generic_warning(msg):
        logger = EnvLogger.get_logger()
        if not logger.hasHandlers():
            handler = EnvWarningHandler(mqueue=EnvLogger.mqueue)
            logger.addHandler(handler)
        logger.warning(msg)

    @staticmethod
    def flush():
        EnvLogger.mqueue.clear()

    @staticmethod
    def suppress_output():
        EnvLogger._output = False

    @staticmethod
    def unsuppress_output():
        EnvLogger._output = True

    @staticmethod
    def warn_action_out_of_bound(msg=""):
        EnvLogger._generic_warning("[WARNING]: Received an action that was outside action space {}".format(msg))

    @staticmethod
    def warn_action_is_NaN(msg=""):
        EnvLogger._generic_warning("[WARNING]: Received an NaN action {}".format(msg))

    @staticmethod
    def warn_close_unrendered_env(msg=""):
        EnvLogger._generic_warning("[WARNING]: Called close on an unrendered environment {}".format(msg))

    @staticmethod
    def error_observe_before_reset():
        assert False, "reset() needs to be called before observe"

    @staticmethod
    def error_step_before_reset():
        assert False, "reset() needs to be called before step"


class EnvWarningHandler(logging.Handler):
    def __init__(self, *args, mqueue, **kwargs):
        logging.Handler.__init__(self, *args, **kwargs)
        self.mqueue = mqueue

    def emit(self, record):
        m = self.format(record).rstrip("\n")
        self.mqueue.append(m)
        if EnvLogger._output:
            print(m)
