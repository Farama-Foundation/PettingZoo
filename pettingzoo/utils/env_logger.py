import logging


class EnvLogger:
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
        # needed to get the pytest runner to work correctly, and doesn't seem to have serious issues
        EnvLogger.mqueue.append(msg)

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
    def error_possible_agents_attribute_missing(name):
        raise AttributeError(
            f"[ERROR]: This environment does not support {name}. This means that either the environment has procedurally generated agents such that this property cannot be well defined (which requires special learning code to handle) or the environment was improperly configured by the developer."
        )

    @staticmethod
    def warn_action_out_of_bound(action, action_space, backup_policy):
        EnvLogger._generic_warning(
            f"[WARNING]: Received an action {action} that was outside action space {action_space}. Environment is {backup_policy}"
        )

    @staticmethod
    def warn_close_unrendered_env():
        EnvLogger._generic_warning(
            "[WARNING]: Called close on an unrendered environment."
        )

    @staticmethod
    def warn_close_before_reset():
        EnvLogger._generic_warning(
            "[WARNING]: reset() needs to be called before close."
        )

    @staticmethod
    def warn_on_illegal_move():
        EnvLogger._generic_warning(
            "[WARNING]: Illegal move made, game terminating with current player losing. \nobs['action_mask'] contains a mask of all legal moves that can be chosen."
        )

    @staticmethod
    def error_observe_before_reset():
        assert False, "reset() needs to be called before observe"

    @staticmethod
    def error_step_before_reset():
        assert False, "reset() needs to be called before step"

    @staticmethod
    def warn_step_after_terminated_truncated():
        EnvLogger._generic_warning(
            "[WARNING]: step() called after all agents are terminated or truncated. Should reset() first."
        )

    @staticmethod
    def error_render_before_reset():
        assert False, "reset() needs to be called before render"

    @staticmethod
    def error_agent_iter_before_reset():
        assert False, "reset() needs to be called before agent_iter"

    @staticmethod
    def error_nan_action():
        assert False, "step() cannot take in a nan action"

    @staticmethod
    def error_state_before_reset():
        assert False, "reset() needs to be called before state"


class EnvWarningHandler(logging.Handler):
    def __init__(self, *args, mqueue, **kwargs):
        logging.Handler.__init__(self, *args, **kwargs)
        self.mqueue = mqueue

    def emit(self, record):
        m = self.format(record).rstrip("\n")
        self.mqueue.append(m)
        if EnvLogger._output:
            print(m)
