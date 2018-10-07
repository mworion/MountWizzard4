# from distutils.core import setup
from setuptools import setup
import mw4_global
import platform

setup(
    name='mountwizzard4',
    version=mw4_global.BUILD,
    packages=[
        'mountwizzard4',
        'mountwizzard4.base',
        'mountwizzard4.gui',
        'mountwizzard4.media',
        'mountwizzard3.test',
    ],
    python_requires='~=3.6.5',
    install_requires=[
        'PyQt5==5.11.2',
        'matplotlib==2.2.2',
        'wakeonlan>=1.0.0',
        'requests==2.18.4',
        'astropy==3.0.3',
        'numpy==1.15.2',
        'requests_toolbelt==0.8.0',
        'skyfield==1.9',
    ]
    # + (['pypiwin32==220'] if "Windows" == platform.system() else [])
    # + (['pywinauto==0.6.4'] if "Windows" == platform.system() else [])
    # + (['comtypes==1.1.1'] if "Windows" == platform.system() else [])
    ,
    url='https://github.com/mworion/MountWizzard3-DIST',
    license='APL 2.0',
    author='mw',
    author_email='michael@wuertenberger.org',
    description='tooling for a 10micron mount',
)

if platform.system() == 'Linux':
    print('#############################################')
    print('### Important hint:                       ###')
    print('### There might be the need to install    ###')
    print('### libfreetype6-dev manually as well     ###')
    print('### sudo apt-get install libfreetype6-dev ###')
    print('#############################################')

