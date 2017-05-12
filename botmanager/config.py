import argparse
import yaml  # noqa
import io  # noqa
import logging
import os
import sys

log = logging.getLogger(__name__)

class Config(object):
    """Config class
        Manages params and the config file
    """
    def __init__(self, args):
        self.arguments=self.parse_args(args)


    def parse_args(self, args):
            parser = argparse.ArgumentParser()
            parser.add_argument('-c', dest='config', default='config.yml',
                                help='Specify configuration file. Default: %(default)s')
            parser.add_argument('--logfile', '-l', default='botmanager.log',
                                help='Specify a custom logfile name/location. '
                                     'Default: %(default)s in the config directory.')
            parser.add_argument('--loglevel', '-L', metavar='LEVEL',
                                help='Set the verbosity of the logger. Levels: %(choices)s',
                                choices=['none', 'critical', 'error', 'warning', 'info', 'verbose', 'debug',
                                         'trace'])
            return parser.parse_args()

    def find_config(self):
        """
        Find the configuration file.

        :raises: `IOError` when no config file could be found.
        """
        config_name="config.yml"
        home_path = os.path.join(os.path.expanduser('~'), '.'+config_name)
        options_config = os.path.expanduser(self.arguments.config)

        possible = []
        if os.path.isabs(options_config):
            # explicit path given, don't try anything
            config = options_config
            possible = [config]
        else:
            log.debug('Figuring out config load paths')
            try:
                possible.append(os.getcwd())
            except OSError:
                log.debug('current directory invalid, not searching for config there')
            # for virtualenv / dev sandbox
            if hasattr(sys, 'real_prefix'):
                log.debug('Adding virtualenv path')
                possible.append(sys.prefix)
            # normal lookup locations
            possible.append(home_path)
            if sys.platform.startswith('win'):
                # On windows look in ~/flexget as well, as explorer does not let you create a folder starting with a dot
                home_path = os.path.join(os.path.expanduser('~'), config_name)
                possible.append(home_path)
            else:
                # The freedesktop.org standard config location
                xdg_config = os.environ.get('XDG_CONFIG_HOME', os.path.join(os.path.expanduser('~'), '.config'))
                possible.append(os.path.join(xdg_config, config_name))

            for path in possible:
                config = os.path.join(path, options_config)
                if os.path.exists(config):
                    log.debug('Found config: %s' % config)
                    break
            else:
                config = None

        if not config:
            log.critical('Failed to find configuration file %s' % options_config)
            log.info('Tried to read from: %s' % ', '.join(possible))
            raise IOError('No configuration file found.')
        if not os.path.isfile(config):
            raise IOError('Config `%s` does not appear to be a file.' % config)

        log.debug('Config file %s selected' % config)
        self.config_path = config
        #self.config_name = os.path.splitext(os.path.basename(config))[0]
        self.config_name = os.path.basename(config)
        self.config_base = os.path.normpath(os.path.dirname(config))
        #self.lockfile = os.path.join(self.config_base, '.%s-lock' % self.config_name)
        #self.db_filename = os.path.join(self.config_base, 'db-%s.sqlite' % self.config_name)

    def load_config(self, output_to_console=True):
        """
        Loads the config file from disk, validates and activates it.

        :raises: `ValueError` if there is a problem loading the config file
        """
        self.find_config()
        with io.open(self.config_path, 'r', encoding='utf-8') as f:
            try:
                raw_config = f.read()
            except UnicodeDecodeError:
                log.critical('Config file must be UTF-8 encoded.')
                raise ValueError('Config file is not UTF-8 encoded')
        try:
            config = yaml.safe_load(raw_config) or {}
        except Exception as e:
            msg = str(e).replace('\n', ' ')
            msg = ' '.join(msg.split())
            log.critical(msg, exc_info=False)
            if output_to_console:
                print('')
                print('-' * 79)
                print(' Malformed configuration file (check messages above). Common reasons:')
                print('-' * 79)
                print('')
                print(' o Indentation error')
                print(' o Missing : from end of the line')
                print(' o Non ASCII characters (use UTF8)')
                print(' o If text contains any of :[]{}% characters it must be single-quoted '
                      '(eg. value{1} should be \'value{1}\')\n')

                # Not very good practice but we get several kind of exceptions here, I'm not even sure all of them
                # At least: ReaderError, YmlScannerError (or something like that)
                if hasattr(e, 'problem') and hasattr(e, 'context_mark') and hasattr(e, 'problem_mark'):
                    lines = 0
                    if e.problem is not None:
                        print(' Reason: %s\n' % e.problem)
                        if e.problem == 'mapping values are not allowed here':
                            print(' ----> MOST LIKELY REASON: Missing : from end of the line!')
                            print('')
                    if e.context_mark is not None:
                        print(' Check configuration near line %s, column %s' % (
                            e.context_mark.line, e.context_mark.column))
                        lines += 1
                    if e.problem_mark is not None:
                        print(' Check configuration near line %s, column %s' % (
                            e.problem_mark.line, e.problem_mark.column))
                        lines += 1
                    if lines:
                        print('')
                    if lines == 1:
                        print(' Fault is almost always in this or previous line\n')
                    if lines == 2:
                        print(' Fault is almost always in one of these lines or previous ones\n')

            # When --debug escalate to full stacktrace
#            if self.options.debug or not output_to_console:
#                raise
            raise ValueError('Config file is not valid YAML')

        # config loaded successfully
        log.debug('config_name: %s' % self.config_name)
        log.debug('config_base: %s' % self.config_base)
        # Install the newly loaded config
        self.config = config