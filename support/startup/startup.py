############################################################
# -*- coding: utf-8 -*-
#
#       #   #  #   #   #    #
#      ##  ##  #  ##  #    #
#     # # # #  # # # #    #  #
#    #  ##  #  ##  ##    ######
#   #   #   #  #   #       #
#
# Python-based Tool for interaction with the 10micron mounts
# GUI with PyQT5 for python3
#
# written in python3, (c) 2019-2022 by mworion
# Licence APL2.0
#
###########################################################
import os
import sys
import site
import pathlib
import subprocess
import venv
import glob
import platform
import logging
import datetime
from logging.handlers import RotatingFileHandler
import argparse

log = logging.getLogger()
version = '3.0'


class EnvBuilder(venv.EnvBuilder):

    def __init__(self, *args, **kwargs):
        self.context = None
        super().__init__(*args, **kwargs)

    def post_setup(self, context):
        self.context = context


class LoggerWriter:
    # taken from:
    # https://stackoverflow.com/questions/19425736/
    # how-to-redirect-stdout-and-stderr-to-logger-in-python
    def __init__(self, level, mode, std):
        self.level = level
        self.mode = mode
        self.standard = std

    def write(self, message):
        self.standard.write(message)
        first = True
        for line in message.rstrip().splitlines():
            if first:
                self.level(f'[{self.mode}] ' + line.strip())
                first = False
            else:
                self.level(' ' * 9 + line.strip())

    def flush(self):
        pass


def setupLogging():
    """
    setupLogging defines the logger and formats and disables unnecessary
    library logging

    :return: true for test purpose
    """
    timeTag = datetime.datetime.now(datetime.timezone.utc).strftime('%Y-%m-%d')
    logFile = f'./startup-{timeTag}.log'
    logging.basicConfig(level=logging.DEBUG,
                        format='[%(asctime)s.%(msecs)03d]'
                               '[%(levelname)1.1s]'
                               '[%(filename)15.15s]'
                               '[%(lineno)4s]'
                               ' %(message)s',
                        datefmt='%Y-%m-%d %H:%M:%S',
                        filename=logFile)
    # transfer all sys outputs to logging
    sys.stderr = LoggerWriter(logging.getLogger().error, 'STDERR', sys.stderr)
    sys.stdout = LoggerWriter(logging.getLogger().info, 'STDOUT', sys.stdout)
    return True


def run(command):
    """
    :param command:
    :return:
    """
    try:
        process = subprocess.Popen(args=command,
                                   stdout=subprocess.PIPE,
                                   stderr=subprocess.STDOUT,
                                   text=True,
                                   )
        for stdout_line in iter(process.stdout.readline, ""):
            if stdout_line:
                log.info(stdout_line.strip('\n'))
        output = process.communicate(timeout=60)[0]

    except subprocess.TimeoutExpired as e:
        log.error(e)
        return False

    except Exception as e:
        log.error(f'Error: {e} happened')
        return False

    else:
        retCode = str(process.returncode)
        log.debug(f'run: [{retCode}] [{output}]')

    success = (process.returncode == 0)
    return success


def venvCreate(venvPath, upgrade=False):
    """
    :param venvPath:
    :param upgrade:
    :return:
    """
    print()
    print()
    print()
    print('-' * 40)
    print('MountWizzard4')
    print('-' * 40)
    print(f'scrip version    : {version}')
    print(f'platform         : {platform.system()}')
    print(f'machine          : {platform.machine()}')
    print(f'python           : {platform.python_version()}')
    print('-' * 40)
    print()

    log.info('-' * 100)
    log.info(f'scrip version    : {version}')
    log.info(f'platform         : {platform.system()}')
    log.info(f'sys.executable   : {sys.executable}')
    log.info(f'actual workdir   : {os.getcwd()}')
    log.info(f'machine          : {platform.machine()}')
    log.info(f'cpu              : {platform.processor()}')
    log.info(f'release          : {platform.release()}')
    log.info(f'python           : {platform.python_version()}')
    log.info(f'python runtime   : {platform.architecture()[0]}')
    log.info(f'upgrade venv     : {upgrade}')
    log.info('-' * 100)

    if upgrade:
        print('Prepare environment present')
        print('...upgrading to actual python version')
        EnvBuilder(with_pip=True, upgrade=upgrade)
        print()

    print('Activate virtual environment')
    venvBuilder = EnvBuilder(with_pip=True)
    venvBuilder.create(venvPath)
    print()
    return venvBuilder.context


def runPythonInVenv(venvContext, command):
    """
    :param venvContext:
    :param command:
    :return:
    """
    command = [venvContext.env_exe] + command
    return run(command)


def runBinInVenv(venvContext, command):
    """
    :param venvContext:
    :param command:
    :return:
    """
    command[0] = str(pathlib.Path(venvContext.bin_path).joinpath(command[0]))
    return run(command)


def installMW4(venvContext, upgrade=False):
    """
    :param venvContext:
    :param upgrade:
    :return:
    """
    command = glob.glob(venvContext.env_dir + '/lib/**/mw4/loader.py',
                        recursive=True)

    hasInstall = len(command) == 1
    if hasInstall and not upgrade:
        print('MountWizzard4 present')
        print('...starting')
        return command

    isTest = os.path.isfile('test.package')
    if isTest:
        package = 'mountwizzard4.tar.gz'
        print()
        print('Test setup')
        print()
    else:
        package = 'mountwizzard4'

    if upgrade:
        print('MountWizzard4 present')
        print('...upgrading to latest release')
        print('...this will take some time')
        command = ['-m', 'pip', 'install', '-U', package]
    else:
        print('MountWizzard4 not present')
        print('...installing latest release')
        print('...this will take some time')
        command = ['-m', 'pip', 'install', package]

    runPythonInVenv(venvContext, command)
    if upgrade:
        print('Upgrade finished')
    else:
        print('Install finished')

    command = glob.glob(venvContext.env_dir + '/lib/**/mw4/loader.py',
                        recursive=True)
    return command


def main(args=None):
    """
    :return:
    """
    setupLogging()
    compatible = True
    if sys.version_info < (3, 7) or sys.version_info >= (3, 11):
        compatible = False
    elif not hasattr(sys, 'base_prefix'):
        compatible = False
    if not compatible:
        print()
        print()
        print()
        print('-' * 40)
        print('MountWizzard4 startup')
        print('needs python3.7 .. 3.10')
        print('...closing application')
        print()
        print('-' * 40)
        print()
        return

    parser = argparse.ArgumentParser(
        prog=__name__, description='Installs MountWizzard4 in Python virtual '
                                   'environment in local workdir')
    parser.add_argument(
        '--upgrade-venv', default=False, action='store_true', dest='upgrade',
        help='Upgrade the virtual environment directory to use this version of '
             'Python, assuming Python has been upgraded in-place.')
    parser.add_argument(
        '--upgrade-mw4', default=False, action='store_true', dest='upgradeMW4',
        help='Upgrade MountWizzard4 to the actual release version')
    parser.add_argument(
        '--no-start', default=False, action='store_true', dest='noStart',
        help='Running script without starting MountWizzard4')

    options = parser.parse_args(args)
    venvPath = pathlib.Path.cwd().joinpath('venv')
    venvContext = venvCreate(venvPath, upgrade=options.upgrade)
    command = installMW4(venvContext, upgrade=options.upgradeMW4)
    if not options.noStart:
        runPythonInVenv(venvContext, command)

    print()
    print('Closing application')
    print('-' * 40)
    print()


if __name__ == '__main__':
    main()