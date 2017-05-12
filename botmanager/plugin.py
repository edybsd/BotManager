import logging

log = logging.getLogger('plugin')

class PluginError(Exception):
    def __init__(self, value, logger=log, **kwargs):
        super(PluginError, self).__init__()
        # Value is expected to be a string
        if not isinstance(value, str):
            value = str(value)
        self.value = value
        self.log = logger
        self.kwargs = kwargs

    def __str__(self):
        return self.value