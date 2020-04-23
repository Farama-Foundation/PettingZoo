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
    def warn_action_out_of_bound(action, action_space, backup_policy):
        EnvLogger._generic_warning("[WARNING]: Received an action {} that was outside action space {}. Environment is {}".format(action, action_space, backup_policy))

    @staticmethod
    def warn_action_is_NaN(backup_policy):
        EnvLogger._generic_warning("[WARNING]: Received an NaN action. Environment is {}".format(backup_policy))

    @staticmethod
    def warn_close_unrendered_env():
        EnvLogger._generic_warning("[WARNING]: Called close on an unrendered environment.")

    @staticmethod
    def warn_on_illegal_move():
        EnvLogger._generic_warning("[WARNING]: Illegal move made, game terminating with current player losing. \nenv.infos[player]['legal_moves'] contains a list of all legal moves that can be chosen.")

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
