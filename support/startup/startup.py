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
import shutil
import sys
import pathlib
import subprocess
import venv
import glob
import platform
import logging
import datetime
import argparse
import tarfile

if platform.system() == 'Windows':
    py = 'python'
else:
    py = 'python3'

log = logging.getLogger()
version = '3.0beta1'


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
        log.debug(f'Run exit code: [{retCode}], message: [{output}]')

    success = (process.returncode == 0)
    return success


def installBasicPackages():
    """
    :return:
    """
    print('...adding basic packages')
    command = [py, '-m', 'pip', 'install', 'pip', '-U']
    run(command)
    command = [py, '-m', 'pip', 'install', 'requests', '-U']
    run(command)
    command = [py, '-m', 'pip', 'install', 'packaging', '-U']
    run(command)


try:
    import requests
    import packaging
except ImportError:
    installBasicPackages()
finally:
    import requests
    from packaging.utils import Version


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


def cleanSystem():
    print('Clean system site-packages')
    print('...takes some time')
    print()
    ret = os.popen(f'{py} -m pip freeze > clean.txt').read()
    print(ret)
    ret = os.popen(f'{py} -m pip uninstall -y -r clean.txt').read()
    print(ret)
    print()
    print('Clean finished')
    print()


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


def updateEnvironment(venvContext):
    """
    :param venvContext:
    :return:
    """
    command = ['-m', 'pip', 'install', 'wheel']
    runPythonInVenv(venvContext, command)


def venvCreate(venvPath, upgrade=False):
    """
    :param venvPath:
    :param upgrade:
    :return:
    """
    print()
    print('-' * 50)
    print(' ███    ███  ██     ██  ██   ██')
    print(' ████  ████  ██     ██  ██   ██')
    print(' ██ ████ ██  ██  █  ██  ███████')
    print(' ██  ██  ██  ██ ███ ██       ██')
    print(' ██      ██   ███ ███        ██')
    print('-' * 50)
    print('MountWizzard4')
    print(f'script version   : {version}')
    print(f'platform         : {platform.system()}')
    print(f'machine          : {platform.machine()}')
    print(f'python           : {platform.python_version()}')
    print('-' * 50)

    log.info('-' * 100)
    log.info(f'script version   : {version}')
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
        print('Upgrading virtual environment')
        print('...to actual python version')
        EnvBuilder(with_pip=True, upgrade=upgrade)
        print()

    existInstall = os.path.isdir('venv')
    if existInstall:
        print('Activate virtual environment')
    else:
        print('Install and activate virtual environment')

    venvBuilder = EnvBuilder(with_pip=True)
    venvBuilder.create(venvPath)
    return venvBuilder.context


def downloadAndInstallWheels(venvContext, verMW4=None):
    """
    :param venvContext:
    :param verMW4:
    :return:
    """
    preRepo = 'https://github.com/mworion/MountWizzard4'
    preSource = '/blob/master/support/wheels/'
    postRepo = '?raw=true'
    wheels = {
        '2.0.0': {
            '3.7': [
                'sep-1.2.0-cp37-cp37m-linux_aarch64.whl',
                'sgp4-2.20-cp37-cp37m-linux_aarch64.whl',
                'pyerfa-2.0.0-cp37-cp37m-linux_aarch64.whl',
                'astropy-4.3.1-cp37-cp37m-linux_aarch64.whl',
                'PyQt5_sip-12.8.1-cp37-cp37-linux_aarch64.whl',
                'PyQt5-5.15.4-cp36.cp37.cp38.cp39-abi3-manylinux2014_aarch64.whl',
            ],
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
        '3.0.0': {
            '3.7': [
                'PyQt5_sip-12.11.0-cp37-cp37-linux_aarch64.whl',
                'PyQt5-5.15.7-cp36.cp37.cp38.cp39-abi3-manylinux2014_aarch64.whl',
            ],
            '3.8': [
                'PyQt5_sip-12.11.0-cp38-cp38-linux_aarch64.whl',
                'PyQt5-5.15.7-cp36.cp37.cp38.cp39-abi3-manylinux2014_aarch64.whl',
            ],
            '3.9': [
                'PyQt5_sip-12.11.0-cp39-cp39-linux_aarch64.whl',
                'PyQt5-5.15.7-cp36.cp37.cp38.cp39-abi3-manylinux2014_aarch64.whl',
            ],
            '3.10': [
                'PyQt5_sip-12.11.0-cp310-cp310-linux_aarch64.whl',
                'PyQt5-5.15.7-cp36.cp37.cp38.cp39-abi3-manylinux2014_aarch64.whl',
            ],
        },
    }
    log.info(f'Got version {verMW4}')
    print('Installing precompiled packages')
    if not verMW4 < Version('3.0.0'):
        log.info('Path version 3.0.0 and above')
        print('...no precompiled packages available')
        print('Install aborted')
        print('')
        if not Version(platform.python_version()) < Version('3.10'):
            print('...no precompiled packages available')
            print('Install aborted')
            print('')
        verMW4 = '3.0.0'
        return False
    elif not verMW4 < Version('2.0.0'):
        log.info('Path version 2.0.0 and above')
        verMW4 = '2.0.0'
    else:
        log.info('Path default')
        print('...no precompiled packages available')
        print('Install aborted')
        print('')
        return False

    ver = f'{sys.version_info[0]}.{sys.version_info[1]}'
    for item in wheels[verMW4][ver]:
        print(f'...{item.split("-")[0]}-{item.split("-")[1]}')
        command = ['-m', 'pip', 'install', preRepo + preSource + item + postRepo]
        suc = runPythonInVenv(venvContext, command)
        if not suc:
            print('...error installing precompiled packages')
            print('Install aborted')
            print('')
            return False
    print('...finished')
    print('Precompiled packages ready')
    print('')
    return True


def addArmSpecials(venvContext, verMW4=''):
    """
    :param venvContext:
    :param verMW4:
    :return:
    """
    if platform.machine() == 'aarch64':
        return downloadAndInstallWheels(venvContext, verMW4=verMW4)

    return True


def versionOnline(upgradeBeta):
    """
    :param upgradeBeta:
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

    if upgradeBeta:
        verMW4 = Version(verBeta[0])
    else:
        verMW4 = Version(verRelease[0])
    return verMW4


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


def checkVersion(isTest, upgradeBeta):
    """
    :param isTest:
    :param upgradeBeta:
    :return:
    """
    if isTest:
        verMW4 = versionLocal()
    elif upgradeBeta:
        verMW4 = versionOnline(True)
    else:
        verMW4 = versionOnline(False)
    return verMW4


def installMW4(venvContext, upgrade=False, upgradeBeta=False, version=''):
    """
    :param venvContext:
    :param upgrade:
    :param upgradeBeta:
    :param version:
    :return:
    """
    command = glob.glob(venvContext.env_dir + '/lib/**/mw4/loader.py',
                        recursive=True)

    hasInstall = len(command) == 1
    if hasInstall:
        print('MountWizzard4 present')
    else:
        print('MountWizzard4 not present')
    print('')

    if hasInstall and not (upgrade or upgradeBeta or version):
        return command

    updateEnvironment(venvContext)

    isTest = os.path.isfile('mountwizzard4.tar.gz')
    if isTest:
        package = 'mountwizzard4.tar.gz'
    else:
        package = 'mountwizzard4'

    log.info(f'Package is test: {isTest}, {package}')
    verMW4 = checkVersion(isTest, upgradeBeta)
    suc = addArmSpecials(venvContext, verMW4=verMW4)
    if not suc:
        log.info('Add ARM specials failed')
        return ''

    if isTest:
        print('Installing local package mountwizzard4.tar.gz')
        command = ['-m', 'pip', 'install', package]
    elif version:
        print(f'Installing version {version}')
        command = ['-m', 'pip', 'install', f'{package}=={version}']
    elif upgrade:
        print('Upgrading to latest release')
        command = ['-m', 'pip', 'install', '-U', package]
    elif upgradeBeta:
        print('Upgrading to latest version including beta')
        command = ['-m', 'pip', 'install', '-U', package, '--pre']
    else:
        print('Installing latest release')
        command = ['-m', 'pip', 'install', package]

    print(f'...version is {verMW4}')
    print('...this will take some time')
    suc = runPythonInVenv(venvContext, command)
    print()
    if not suc:
        print('Install failed, abort')
        print()
        return ''

    if upgrade or upgradeBeta:
        print('Upgrade finished')
    else:
        print('Install finished')
    print()

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
    if platform.machine() in ['armv7l']:
        compatible = False
    elif platform.machine() in ['aarch64'] and sys.version_info >= (3, 10):
        compatible = False

    if not compatible:
        print()
        print('-' * 50)
        print('MountWizzard4 startup - no compatible environment')
        print('needs python 3.7 .. 3.9 for version 2.x')
        print('needs python 3.7 .. 3.10 for version 3.x')
        print('actually no support for ARM7')
        print('actually no support for AARCH64 for MW4 3.x')
        print('actually no support for AARCH64 for python 3.10')
        print(f'you are running {platform.python_version()}')
        print('Closing application')
        print('-' * 50)
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
        '--upgrade', default=False, action='store_true', dest='upgradeMW4',
        help='Upgrade MountWizzard4 to the actual release version')
    parser.add_argument(
        '--upgrade-beta', default=False, action='store_true', dest='upgradeMW4beta',
        help='Upgrade MountWizzard4 to the actual beta version')
    parser.add_argument(
        '--version', default='', type=str, dest='version',
        help='Upgrade MountWizzard4 to the named version')
    parser.add_argument(
        '--no-start', default=False, action='store_true', dest='noStart',
        help='Running script without starting MountWizzard4')
    parser.add_argument(
        '--clean_system', default=False, action='store_true', dest='clean',
        help='Cleaning system packages from faulty installs')
    parser.add_argument(
        '--scale', default=1, type=float, dest='scale',
        help='Setting Qt DPI scale factor for MountWizzard4')
    parser.add_argument(
        '--dpi', default=96, type=float, dest='dpi',
        help='Setting QT font DPI for MountWizzard4')
    parser.add_argument(
        '--basic', default=False, action='store_true', dest='basic',
        help='Upgrade basic install packages')

    options = parser.parse_args(args)
    venvPath = pathlib.Path.cwd().joinpath('venv')
    venvContext = venvCreate(venvPath, upgrade=options.upgrade)

    if options.clean:
        cleanSystem()
    if options.basic:
        installBasicPackages()
    print()

    command = installMW4(venvContext,
                         upgrade=options.upgradeMW4,
                         upgradeBeta=options.upgradeMW4beta,
                         version=options.version)

    os.environ['QT_SCALE_FACTOR'] = str(options.scale)
    os.environ['QT_FONT_DPI'] = str(options.dpi)

    if not options.noStart and command:
        print('MountWizzard4 is ready')
        print('...starting')
        print()
        suc = runPythonInVenv(venvContext, command)
        if not suc:
            print('...failed to start MW4')

    print('Closing application')
    print('-' * 50)
    print()


if __name__ == '__main__':
    main()
