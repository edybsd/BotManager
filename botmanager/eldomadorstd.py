#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Simple Bot to reply to Telegram messages
# This program is dedicated to the public domain under the CC0 license.
"""
This Bot uses the Updater class to handle the bot.
First, a few handler functions are defined. Then, those functions are passed to
the Dispatcher and registered at their respective places.
Then, the bot is started and runs until we press Ctrl-C on the command line.
Usage:
Basic Echobot example, repeats messages.
Press Ctrl-C on the command line or send a signal to the process to stop the
bot.
"""
import logging
import sys
import yaml  # noqa
import os  # noqa
import io  # noqa

from botmanager.manager import Manager
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
from botmanager.utils import restricted

# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

logger = logging.getLogger(__name__)


# Define a few command handlers. These usually take the two arguments bot and
# update. Error handlers also receive the raised TelegramError object in error.
def start(bot, update):
    update.message.reply_text('¿Sí, maestro? ')


def help(bot, update):
    update.message.reply_text('Help!')


@restricted
def my_handler(bot, update):
    pass  # only accessible if `user_id` is in `LIST_OF_ADMINS`.


def torrent(bot, update, args):
    text_caps = ' '.join(args).upper()
    update.message.reply_text(text_caps)


def echo(bot, update):
    update.message.reply_text(update.message.text)


def error(bot, update, error):
    logger.warning('Update "%s" caused error "%s"' % (update, error))

def load_config(output_to_console=True):
    """
    Loads the config file from disk, validates and activates it.

    :raises: `ValueError` if there is a problem loading the config file
    """
    config_path=find_config()
    with io.open(config_path, 'r', encoding='utf-8') as f:
        try:
            raw_config = f.read()
        except UnicodeDecodeError:
            logger.critical('Config file must be UTF-8 encoded.')
            raise ValueError('Config file is not UTF-8 encoded')
    try:
        config = yaml.safe_load(raw_config) or {}
    except Exception as e:
        msg = str(e).replace('\n', ' ')
        msg = ' '.join(msg.split())
        logger.critical(msg, exc_info=False)
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
    logger.debug('config: %s' % config)

    return config

def find_config(self):
    """
    Find the configuration file.

    :raises: `IOError` when no config file could be found.
    """
    config_name="config.yml"
    home_path = os.path.join(os.path.expanduser('~'), '.'+config_name)
    options_config = os.path.expanduser(self.args.config)

    possible = []
    if os.path.isabs(options_config):
        # explicit path given, don't try anything
        config = options_config
        possible = [config]
    else:
        logger.debug('Figuring out config load paths')
        try:
            possible.append(os.getcwd())
        except OSError:
            logger.debug('current directory invalid, not searching for config there')
        # for virtualenv / dev sandbox
        if hasattr(sys, 'real_prefix'):
            logger.debug('Adding virtualenv path')
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
                logger.debug('Found config: %s' % config)
                break
        else:
            config = None

    if not config:
        logger.critical('Failed to find configuration file %s' % options_config)
        logger.info('Tried to read from: %s' % ', '.join(possible))
        raise IOError('No configuration file found.')
    if not os.path.isfile(config):
        raise IOError('Config `%s` does not appear to be a file.' % config)

    logger.debug('Config file %s selected' % config)

    #self.config_path = config
    #self.config_name = os.path.basename(config)
    #self.config_base = os.path.normpath(os.path.dirname(config))
    #self.lockfile = os.path.join(self.config_base, '.%s-lock' % self.config_name)
    #self.db_filename = os.path.join(self.config_base, 'db-%s.sqlite' % self.config_name)
    return config  # complete path to config

def main():

    eldomadorbot = Manager(sys.argv)

    # Create the EventHandler and pass it your bot's token.
    updater = Updater("366425107:AAFtJ-ufw7XDzTcNN2QoJvLC-aE5wb4on18")

    # Get the dispatcher to register handlers
    dp = updater.dispatcher

    # on different commands - answer in Telegram
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("help", help))

    dp.add_handler(CommandHandler("torrent", torrent, pass_args=True))

    # on noncommand i.e message - echo the message on Telegram
    dp.add_handler(MessageHandler(Filters.all, echo))

    # log all errors
    dp.add_error_handler(error)

    # Start the Bot
    updater.start_polling()
    updater.start_webhook(listen='0.0.0.0',
                          port=8443,
                          url_path='TOKEN',
                          key='private.key',
                          cert='cert.pem',
                          webhook_url='https://example.com:8443/TOKEN')

    # Run the bot until you press Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT. This should be used most of the time, since
    # start_polling() is non-blocking and will stop the bot gracefully.
    updater.idle()


if __name__ == '__main__':
    main()
