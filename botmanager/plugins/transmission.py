def get_instance(config=None):
    return PluginTransmission(config)


class PluginTransmission(object):
    def __init__(self,config=None):
        pass
    def get_commands(self):
        print("PluginTransmission get_commands")

    def process_command(self, args):
        print("PluginTransmission process_command")