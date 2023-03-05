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
# written in python3, (c) 2019-2023 by mworion
# Licence APL2.0
#
###########################################################
import os
import sys
import pathlib
import subprocess
import venv
import glob
import platform
import logging
from logging.handlers import RotatingFileHandler
import time
import datetime
import argparse
import tarfile

log = logging.getLogger()
version = '3.1b0'
sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')
if platform.system() == 'Windows':
    py = 'python'
else:
    py = 'python3'


def prt(*args):
    """
    :param args:
    :return:
    """
    print('    ', *args)


def run(command):
    """
    :param command:
    :return:
    """
    try:
        process = subprocess.Popen(args=command,
                                   stdout=subprocess.PIPE,
                                   stderr=subprocess.STDOUT,
                                   text=True)
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
        retCode = process.returncode

    success = (process.returncode == 0)
    log.debug(f'Exit code:[{retCode}], message:[{output}], success:[{success}]')
    return success


def installBasicPackages():
    """
    :return:
    """
    prt('...adding basic packages')
    command = [py, '-m', 'pip', 'install', 'pip', '-U']
    run(command)
    command = [py, '-m', 'pip', 'install', 'requests', '-U']
    run(command)
    command = [py, '-m', 'pip', 'install', 'wheel', '-U']
    run(command)
    command = [py, '-m', 'pip', 'install', 'packaging', '-U']
    run(command)


try:
    import requests
except ImportError:
    installBasicPackages()
    import requests

try:
    from packaging.utils import Version
except ImportError:
    installBasicPackages()
    from packaging.utils import Version


def findfile(startDir, pattern):
    for root, dirs, files in os.walk(startDir):
        for name in files:
            if name.find(pattern) >= 0:
                return root + os.sep + name

    return None


class EnvBuilder(venv.EnvBuilder):
    """
    """
    def __init__(self, *args, **kwargs):
        """
        :param args:
        :param kwargs:
        """
        self.context = None
        super().__init__(*args, **kwargs)

    def post_setup(self, context):
        """
        :param context:
        :return:
        """
        self.context = context
        binPath = os.path.dirname(findfile(os.getcwd(), 'activate')) + os.pathsep
        os.environ['PATH'] = binPath + os.environ['PATH']


class LoggerWriter:
    """
    """
    def __init__(self, level, mode, std):
        """
        :param level:
        :param mode:
        :param std:
        """
        self.level = level
        self.mode = mode
        self.standard = std

    def write(self, message):
        """
        :param message:
        :return:
        """
        first = True
        for line in message.rstrip().splitlines():
            if first:
                self.level(f'[{self.mode}] ' + line.strip())
                first = False
            else:
                self.level(' ' * 9 + line.strip())

    def flush(self):
        pass


def addLoggingLevel(levelName, levelNum, methodName=None):
    """    
    :param levelName: 
    :param levelNum: 
    :param methodName: 
    :return: 
    """
    if not methodName:
        methodName = levelName.lower()
    if hasattr(logging, levelName):
        return
    if hasattr(logging, methodName):
        return
    if hasattr(logging.getLoggerClass(), methodName):
        return

    def logForLevel(self, message, *args, **kwargs):
        if self.isEnabledFor(levelNum):
            self._log(levelNum, message, args, **kwargs)

    logging.addLevelName(levelNum, levelName)
    setattr(logging, levelName, levelNum)
    setattr(logging.getLoggerClass(), methodName, logForLevel)


def setupLogging():
    """
    setupLogging defines the logger and formats and disables unnecessary
    library logging

    :return: true for test purpose
    """
    if not os.path.isdir('./log'):
        os.mkdir('./log')

    logging.Formatter.converter = time.gmtime
    timeTag = datetime.datetime.utcnow().strftime('%Y-%m-%d')
    logFile = f'./log/mw4-{timeTag}.log'
    logHandler = RotatingFileHandler(logFile, mode='a', maxBytes=100 * 1024 * 1024,
                                     backupCount=100, encoding=None, delay=False)
    logging.basicConfig(level=logging.DEBUG,
                        format='[%(asctime)s.%(msecs)03d]'
                               '[%(levelname)1.1s]'
                               '[%(filename)15.15s]'
                               '[%(lineno)4s]'
                               ' %(message)s',
                        handlers=[logHandler],
                        datefmt='%Y-%m-%d %H:%M:%S',
                        )
    logging.getLogger('requests').setLevel(logging.WARNING)
    logging.getLogger('urllib3').setLevel(logging.WARNING)
    # transfer all sys outputs to logging
    sys.stderr = LoggerWriter(logging.getLogger().error, 'STDERR', sys.stderr)
    return True


def cleanSystem():
    """
    :return:
    """
    prt('Clean system site-packages')
    prt('...takes some time')
    ret = os.popen(f'{py} -m pip freeze > clean.txt').read()
    prt(ret)
    ret = os.popen(f'{py} -m pip uninstall -y -r clean.txt').read()
    prt(ret)
    prt('Clean finished')


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


def venvCreate(venvPath, upgrade=False):
    """
    :param venvPath:
    :param upgrade:
    :return:
    """
    prt()
    prt('-' * 45)
    prt('MountWizzard4')
    prt('-' * 45)
    prt(f'script version   : {version}')
    prt(f'platform         : {platform.system()}')
    prt(f'machine          : {platform.machine()}')
    prt(f'python           : {platform.python_version()}')
    prt('-' * 45)

    log.header('-' * 100)
    log.header(f'script version   : {version}')
    log.header(f'platform         : {platform.system()}')
    log.header(f'sys.executable   : {sys.executable}')
    log.header(f'actual workdir   : {os.getcwd()}')
    log.header(f'machine          : {platform.machine()}')
    log.header(f'cpu              : {platform.processor()}')
    log.header(f'release          : {platform.release()}')
    log.header(f'python           : {platform.python_version()}')
    log.header(f'python runtime   : {platform.architecture()[0]}')
    log.header(f'upgrade venv     : {upgrade}')
    log.header('-' * 100)

    if upgrade:
        prt('Update virtual environment')
        EnvBuilder(with_pip=True, upgrade=upgrade)

    existInstall = os.path.isdir('venv')
    if existInstall:
        prt('Activate virtual environment')
    else:
        prt('Install and activate virtual environment')

    venvBuilder = EnvBuilder(with_pip=True)
    venvBuilder.create(venvPath)
    return venvBuilder.context


def downloadAndInstallWheels(venvContext, version=None):
    """
    :param venvContext:
    :param version:
    :return:
    """
    preRepo = 'https://github.com/mworion/MountWizzard4'
    preSource = '/blob/master/support/wheels/'
    postRepo = '?raw=true'
    wheels = {
        '2.0.0': {
            '3.8': [
                'sep-1.2.0-cp38-cp38-linux_aarch64.whl',
                'sgp4-2.20-cp38-cp38-linux_aarch64.whl',
                'pyerfa-2.0.0-cp38-cp38-linux_aarch64.whl',
                'astropy-4.3.1-cp38-cp38-linux_aarch64.whl',
                'PyQt5_sip-12.8.1-cp38-cp38-linux_aarch64.whl',
                'PyQt5-5.15.4-cp36.cp37.cp38.cp39-abi3-manylinux2014_aarch64.whl',
            ],
            '3.9': [
                'sep-1.2.0-cp39-cp39-linux_aarch64.whl',
                'sgp4-2.20-cp39-cp39-linux_aarch64.whl',
                'pyerfa-2.0.0-cp39-cp39-linux_aarch64.whl',
                'astropy-4.3.1-cp39-cp39-linux_aarch64.whl',
                'PyQt5_sip-12.8.1-cp39-cp39-linux_aarch64.whl',
                'PyQt5-5.15.4-cp36.cp37.cp38.cp39-abi3-manylinux2014_aarch64.whl',
            ],
            '3.10': [
                'sep-1.2.0-cp310-cp310-linux_aarch64.whl',
                'sgp4-2.20-cp310-cp310-linux_aarch64.whl',
                'pyerfa-2.0.0-cp310-cp310-linux_aarch64.whl',
                'astropy-4.3.1-cp310-cp310-linux_aarch64.whl',
                'PyQt5_sip-12.8.1-cp310-cp310-linux_aarch64.whl',
                'PyQt5-5.15.4-cp36.cp37.cp38.cp39-abi3-manylinux2014_aarch64.whl',
            ],
        },
        '3.1.0': {
            '3.8': [
                'PyQt5_sip-12.11.1-cp38-cp38-linux_aarch64.whl',
                'PyQt5-5.15.9-cp37-abi3-manylinux_2_17_aarch64.whl',
            ],
            '3.9': [
                'PyQt5_sip-12.11.1-cp39-cp39-linux_aarch64.whl',
                'PyQt5-5.15.9-cp37-abi3-manylinux_2_17_aarch64.whl',
            ],
            '3.10': [
                'PyQt5_sip-12.11.1-cp310-cp310-linux_aarch64.whl',
                'PyQt5-5.15.9-cp37-abi3-manylinux_2_17_aarch64.whl',
            ],
        },
    }
    log.info(f'Got version {version}')
    prt(f'Install precompiled packages for {version}')
    if version > Version('3.0.99'):
        versionKey = '3.1.0'
        log.info('Path version 3.x.y')
    elif version >= Version('2'):
        versionKey = '2.0.0'
        log.info('Path version 2.x.y')
    else:
        log.info('No actual supported version')
        prt('...no supported version')
        return False

    ver = f'{sys.version_info[0]}.{sys.version_info[1]}'
    for item in wheels[versionKey][ver]:
        prt(f'...{item.split("-")[0]}-{item.split("-")[1]}')
        command = ['-m', 'pip', 'install', preRepo + preSource + item + postRepo]
        suc = runPythonInVenv(venvContext, command)
        if not suc:
            prt('...error install precompiled packages')
            return False
    prt('Precompiled packages ready')
    return True


def versionOnline(updateBeta):
    """
    :param updateBeta:
    :return:
    """
    url = f'https://pypi.python.org/pypi/mountwizzard4/json'
    try:
        response = requests.get(url).json()
    except Exception as e:
        log.critical(f'Cannot determine package version: {e}')
        return Version('0.0.0')

    vPackage = list(response['releases'].keys())
    vPackage.sort(key=Version, reverse=True)
    verBeta = [x for x in vPackage if 'b' in x]
    verRelease = [x for x in vPackage if 'b' not in x and 'a' not in x]
    log.info(f'Package Beta:   {verBeta[:10]}')
    log.info(f'Package Release:{verRelease[:10]}')

    if updateBeta:
        version = Version(verBeta[0])
    else:
        version = Version(verRelease[0])

    return version


def versionLocal():
    """
    :return:
    """
    with tarfile.open('mountwizzard4.tar.gz', 'r') as f:
        for member in f.getmembers():
            if "PKG-INFO" in member.name:
                pkg = f.extractfile(member.name)
                with open('PKG_INFO', 'wb') as o:
                    o.write(pkg.read())
    ver = ''
    with open('PKG_INFO', 'r') as f:
        for line in f.readlines():
            if line.startswith('Version:'):
                ver = line.split(':')[1]
    os.remove('PKG_INFO')
    return Version(ver)


def getVersion(isTest, updateBeta, version):
    """
    :param isTest:
    :param updateBeta:
    :param version:
    :return:
    """
    if version:
        version = Version(version)
    elif isTest:
        version = versionLocal()
    elif updateBeta:
        version = versionOnline(True)
    else:
        version = versionOnline(False)
    return version


def install(venvContext, version='', isTest=False):
    """
    :param venvContext:
    :param version:
    :param isTest:
    :return:
    """
    command = ['-m', 'pip', 'install', 'wheel']
    runPythonInVenv(venvContext, command)
    command = ['-m', 'pip', 'install', 'pip', '-U']
    runPythonInVenv(venvContext, command)

    if isTest:
        prt('Install local package mountwizzard4.tar.gz')
        command = ['-m', 'pip', 'install', 'mountwizzard4.tar.gz']
    else:
        prt(f'Install version {version}')
        command = ['-m', 'pip', 'install', f'mountwizzard4=={version}']

    prt('...this will take some time')
    suc = runPythonInVenv(venvContext, command)
    return suc


def checkIfInstalled(venvContext):
    """
    :param venvContext:
    :return:
    """
    solutions = glob.glob(venvContext.env_dir + '/lib/**/mw4/loader.py',
                          recursive=True)
    isInstalled = len(solutions) == 1
    if isInstalled:
        prt('MountWizzard4 installed')
        loaderPath = [solutions[0]]
    else:
        prt('MountWizzard4 not installed')
        loaderPath = ''
    return isInstalled, loaderPath


def prepareInstall(venvContext, update=False, updateBeta=False, version=''):
    """
    :param venvContext:
    :param update:
    :param updateBeta:
    :param version:
    :return:
    """
    isInstalled, loaderPath = checkIfInstalled(venvContext)
    if isInstalled and not (update or updateBeta or version):
        return loaderPath

    isTest = os.path.isfile('mountwizzard4.tar.gz') and not version
    version = getVersion(isTest, updateBeta, version)
    isV2 = version < Version('2.100')
    compatibleV2 = Version(platform.python_version()) < Version('3.10')

    if isV2 and not compatibleV2:
        prt('MountWizzard4 v2.x needs python 3.7-3.9')
        return ''

    if platform.machine() == 'aarch64':
        suc = downloadAndInstallWheels(venvContext, version=version)
        if not suc:
            return ''
    elif platform.machine() == 'armv7':
        return ''

    suc = install(venvContext, version=version, isTest=isTest)
    if not suc:
        return ''

    _, loaderPath = checkIfInstalled(venvContext)
    return loaderPath


def checkBaseCompatibility():
    """
    :return:
    """
    compatible = True
    if sys.version_info < (3, 8) or sys.version_info >= (3, 11):
        compatible = False
    elif not hasattr(sys, 'base_prefix'):
        compatible = False
    if platform.machine() in ['armv7l']:
        compatible = False
    return compatible


def main(options):
    """
    :param options:
    :return:
    """
    setupLogging()
    addLoggingLevel('HEADER', 55)
    compatible = checkBaseCompatibility()
    if not compatible:
        prt()
        prt('-' * 45)
        prt('MountWizzard4 startup - no compatible environment')
        prt('needs python 3.7-3.9 for version 2.x')
        prt('needs python 3.8-3.10 for version 3.x')
        prt('no support for ARM7')
        prt(f'you are running {platform.python_version()}')
        prt('Closing application')
        prt('-' * 45)
        return False

    if platform.system() == 'Windows':
        os.environ['QT_SCALE_FACTOR'] = f'{options.scale:2.1f}'
        os.environ['QT_FONT_DPI'] = f'{options.dpi:2.0f}'
    venvPath = pathlib.Path.cwd().joinpath('venv')
    venvContext = venvCreate(venvPath, upgrade=options.venv)

    if options.basic:
        installBasicPackages()
    if options.clean:
        cleanSystem()

    loaderPath = prepareInstall(
        venvContext,
        update=options.update,
        updateBeta=options.updateBeta,
        version=options.version)

    if not options.noStart and loaderPath:
        prt('MountWizzard4 starting')
        suc = runPythonInVenv(venvContext, loaderPath)
        if not suc:
            prt('...failed to start MountWizzard4')
    elif not loaderPath:
        prt('Install failed')


def readOptions():
    """
    :return:
    """
    parser = argparse.ArgumentParser(
        prog=__name__, description='Installs MountWizzard4 in Python virtual '
                                   'environment in local workdir')
    parser.add_argument(
        '-c', '--clean', default=False, action='store_true', dest='clean',
        help='Cleaning system packages from faulty installs')
    parser.add_argument(
        '-d', '--dpi', default=96, type=float, dest='dpi',
        help='Setting QT font DPI (+dpi = -fontsize, default=96)')
    parser.add_argument(
        '-n', '--no-start', default=False, action='store_true', dest='noStart',
        help='Running script without starting MountWizzard4')
    parser.add_argument(
        '-s', '--scale', default=1, type=float, dest='scale',
        help='Setting Qt DPI scale factor (+scale = +size, default=1)')
    parser.add_argument(
        '-u', '--update', default=False, action='store_true', dest='update',
        help='Update MountWizzard4 to the actual release version')
    parser.add_argument(
        '--update-basic', default=False, action='store_true', dest='basic',
        help='Update basic install packages')
    parser.add_argument(
        '--update-beta', default=False, action='store_true', dest='updateBeta',
        help='Update MountWizzard4 to the actual beta version')
    parser.add_argument(
        '--update-venv', default=False, action='store_true', dest='venv',
        help='Update the virtual environment directory to use this version of '
             'Python, assuming Python has been upgraded in-place.')
    parser.add_argument(
        '-v', '--version', default='', type=str, dest='version',
        help='Update MountWizzard4 to the named version')

    options = parser.parse_args()
    return options


if __name__ == '__main__':
    options = readOptions()
    main(options)
    prt('-' * 45)
    prt('Closing application')
    prt('-' * 45)
    prt()
