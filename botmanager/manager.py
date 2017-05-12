import argparse
import sys
import os
import logging
from functools import partial
from pluginbase import PluginBase
import yaml  # noqa
import io  # noqa

log = logging.getLogger(__name__)

# For easier usage calculate the path relative to here.
here = os.path.abspath(os.path.dirname(__file__))
get_path = partial(os.path.join, here)

class Manager(object):
    """Manager class for BotManager
    """

    def __init__(self, config):
        self.config = config




    def load_plugins(self):

        self.plugins = {}

        # Setup a plugin base for "example.modules" and make sure to load
        # all the default built-in plugins from the builtin_plugins folder.
        self.plugin_base = PluginBase(package='test.plugins')

        # and a source which loads the plugins from the "app_name/plugins"
        # folder.  We also pass the application name as identifier.  This
        # is optional but by doing this out plugins have consistent
        # internal module names which allows pickle to work.
        self.source = self.plugin_base.make_plugin_source(searchpath=[get_path('./plugins')])

        # Here we list all the plugins the source knows about, load them
        # and the use the "setup" function provided by the plugin to
        # initialize the plugin.
        for plugin_name in self.source.list_plugins():
            plugin = self.source.load_plugin(plugin_name)
            #self.plugins.add (plugin.get_instance())
            obj=plugin.get_instance(self.config)
            commands=obj.process_command('')



    def hola(self):
        print('Filename: ', self.config_name)