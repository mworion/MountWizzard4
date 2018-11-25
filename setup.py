# from distutils.core import setup
from setuptools import setup
import mw4_glob
import platform

setup(
    name='mw4',
    version=mw4_glob.BUILD,
    packages=[
        'mw4',
        'mw4.base',
        'mw4.build',
        'mw4.environ',
        'mw4.gui',
        'mw4.gui.media',
        'mw4.gui.widgets',
        'mw4.relay',
        'mw4.test',
    ],
    python_requires='~=3.6.5',
    install_requires=[
        'PyQt5==5.11.3',
        'matplotlib==3.0.1',
        'requests==2.20.0',
        'numpy==1.15.3',
        'requests_toolbelt==0.8.0',
        'skyfield==1.9',
    ]
    ,
    url='https://github.com/mworion/MountWizzard4',
    license='APL 2.0',
    author='mw',
    author_email='michael@wuertenberger.org',
    description='tooling for a 10micron mount',
)
