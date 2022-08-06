# This is the PyQt5 build script.
#
# Copyright (c) 2021 Riverbank Computing Limited <info@riverbankcomputing.com>
# 
# This file is part of PyQt5.
# 
# This file may be used under the terms of the GNU General Public License
# version 3.0 as published by the Free Software Foundation and appearing in
# the file LICENSE included in the packaging of this file.  Please review the
# following information to ensure the GNU General Public License version 3.0
# requirements will be met: http://www.gnu.org/copyleft/gpl.html.
# 
# If you do not wish to use this file under the terms of the GPL version 3.0
# then you may purchase a commercial license.  For more information contact
# info@riverbankcomputing.com.
# 
# This file is provided AS IS with NO WARRANTY OF ANY KIND, INCLUDING THE
# WARRANTY OF DESIGN, MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE.


import glob
import os
import sys

from pyqtbuild import PyQtBindings, PyQtProject, QmakeTargetInstallable
from sipbuild import (Buildable, BuildableModule, Installable, Option,
        UserException)


class PyQt(PyQtProject):
    """ The PyQt5 project. """

    def __init__(self):
        """ Initialise the project. """

        super().__init__(dunder_init=True, tag_prefix='Qt',
                console_scripts=[
                    'pylupdate5 = PyQt5.pylupdate_main:main',
                    'pyrcc5 = PyQt5.pyrcc_main:main',
                    'pyuic5 = PyQt5.uic.pyuic:main'])

        # Each set of bindings must appear after any set they depend on.
        self.bindings_factories = [Qt, QtCore, QtNetwork, QtGui, QtWidgets,
            QtQml, QAxContainer, QtAndroidExtras, QtBluetooth, QtDBus,
            QtDesigner, Enginio, QtHelp, QtMacExtras, QtMultimedia,
            QtMultimediaWidgets, QtNfc, QtOpenGL, QtPositioning, QtLocation,
            QtPrintSupport, QtQuick, QtQuick3D, QtQuickWidgets,
            QtRemoteObjects, QtSensors, QtSerialPort, QtSql, QtSvg, QtTest,
            QtTextToSpeech, QtWebChannel, QtWebKit, QtWebKitWidgets,
            QtWebSockets, QtWinExtras, QtX11Extras, QtXml, QtXmlPatterns,
            _QOpenGLFunctions_2_0, _QOpenGLFunctions_2_1,
            _QOpenGLFunctions_4_1_Core, _QOpenGLFunctions_ES2, pylupdate,
            pyrcc]

    def apply_user_defaults(self, tool):
        """ Set default values where needed. """

        if self.license_dir is None:
            self.license_dir = os.path.join(self.root_dir, 'sip')
        else:
            self.license_dir = os.path.abspath(self.license_dir)

        super().apply_user_defaults(tool)

        if not self.tools:
            self.console_scripts = []

    def get_dunder_init(self):
        """ Return the contents of the __init__.py file to install. """

        with open(os.path.join(self.root_dir, '__init__.py')) as f:
            dunder_init = f.read()

        if self.py_platform == 'win32':
            dunder_init += """

def find_qt():
    import os, sys

    qtcore_dll = '\\\\Qt5Core.dll'

    dll_dir = os.path.dirname(sys.executable)
    if not os.path.isfile(dll_dir + qtcore_dll):
        path = os.environ['PATH']

        dll_dir = os.path.dirname(__file__) + '\\\\Qt5\\\\bin'
        if os.path.isfile(dll_dir + qtcore_dll):
            path = dll_dir + ';' + path
            os.environ['PATH'] = path
        else:
            for dll_dir in path.split(';'):
                if os.path.isfile(dll_dir + qtcore_dll):
                    break
            else:
                return

    try:
        os.add_dll_directory(dll_dir)
    except AttributeError:
        pass


find_qt()
del find_qt
"""

        return dunder_init

    def get_options(self):
        """ Return the sequence of configurable options. """

        # Get the standard options.
        options = super().get_options()

        # Add our new options.
        options.append(
                Option('confirm_license', option_type=bool,
                        help="confirm acceptance of the license"))

        options.append(
                Option('license_dir', option_type=str,
                        help="the license file can be found in DIR",
                        metavar="DIR"))

        options.append(
                Option('qt_shared', option_type=bool,
                        help="assume Qt has been built as shared libraries"))

        options.append(
                Option('designer_plugin', option_type=bool, inverted=True,
                        help="disable the building of the Python plugin for Qt Designer"))

        options.append(
                Option('qml_plugin', option_type=bool, inverted=True,
                        help="disable the building of the Python plugin for qmlscene"))

        options.append(
                Option('dbus', option_type=str,
                        help="the directory containing the dbus/dbus-python.h file",
                        metavar="DIR"))

        options.append(
                Option('dbus_python', option_type=bool, inverted=True,
                        help="disable the Qt support for the dbus-python package"))

        options.append(
                Option('tools', option_type=bool, inverted=True,
                        help="disable the building of pyuic5, pyrcc5 and pylupdate5"))

        return options

    def update(self, tool):
        """ Update the configuration. """

        if tool not in Option.BUILD_TOOLS:
            return

        # Check we support the version of Qt.
        if self.builder.qt_version >> 16 != 5:
            raise UserException(
                    "Qt v5 is required, not v{0}".format(
                            self.builder.qt_version_str))

        # Automatically confirm the license if there might not be a command
        # line option to do so.
        if tool == 'pep517':
            self.confirm_license = True

        self._check_license()

        # Handle the platform tag (allowing for win32-g++).
        if self.py_platform.startswith('win32'):
            plattag = 'WS_WIN'
        elif self.py_platform == 'darwin':
            plattag = 'WS_MACX'
        else:
            plattag = 'WS_X11'

        self.bindings['QtCore'].tags.append(plattag)

        # Make sure the bindings are buildable.
        super().update(tool)

        # PyQtWebEngine needs to know if QtWebChannel is available.
        if 'QtWebChannel' not in self.bindings:
            qtcore = self.bindings.get('QtCore')
            if qtcore is not None:
                qtcore.disabled_features.append('PyQt_WebChannel')

        # Add the composite module.
        if 'Qt' in self.bindings:
            self._add_composite_module(tool)

        # Always install the uic module.
        installable = Installable('uic', target_subdir='PyQt5')
        installable.files.append(os.path.join(self.root_dir, 'pyuic', 'uic'))
        self.installables.append(installable)

        # If any set of bindings is being built as a debug version then assume
        # the plugins and DBus support should as well.
        for bindings in self.bindings.values():
            if bindings.debug:
                others_debug = True
                break
        else:
            others_debug = self.py_debug

        # Add the plugins.  For the moment we don't include them in wheels.
        # This may change when we improve the bundling of Qt.
        if tool in ('build', 'install'):
            if self.designer_plugin and 'QtDesigner' in self.bindings:
                self._add_plugin('designer', "Qt Designer", 'pyqt5',
                        'designer', others_debug)

            if self.qml_plugin and 'QtQml' in self.bindings:
                self._add_plugin('qmlscene', "qmlscene", 'pyqt5qmlplugin',
                        'PyQt5', others_debug)

        # Add the dbus-python support.
        if self.dbus_python:
            self._add_dbus(others_debug)

    def _add_composite_module(self, tool):
        """ Add the bindings for the composite module. """

        sip_file = os.path.join(self.build_dir, 'Qt.sip')
        sip_f = self.open_for_writing(sip_file)

        sip_f.write('''%CompositeModule PyQt5.Qt

''')

        for bindings in self.bindings.values():
            if not bindings.internal:
                sip_f.write(
                        '%Include {}\n'.format(
                                bindings.sip_file.replace('\\', '/')))

        sip_f.close()

        self.bindings['Qt'].sip_file = sip_file

    def _add_dbus(self, debug):
        """ Add the dbus-python support. """

        self.progress(
                "Checking to see if the dbus-python support should be built")

        # See if dbus-python is installed.
        try:
            import dbus.mainloop
        except ImportError:
            self.progress(
                    "The dbus-python package does not seem to be installed.")
            return

        dbus_module_dir = dbus.mainloop.__path__[0]

        # Get the flags for the DBus library.
        dbus_inc_dirs = []
        dbus_lib_dirs = []
        dbus_libs = []

        args = ['pkg-config', '--cflags-only-I', '--libs dbus-1']

        for line in self.read_command_pipe(args, fatal=False):
            for flag in line.strip().split():
                if flag.startswith('-I'):
                    dbus_inc_dirs.append(flag[2:])
                elif flag.startswith('-L'):
                    dbus_lib_dirs.append(flag[2:])
                elif flag.startswith('-l'):
                    dbus_libs.append(flag[2:])

        if not any([dbus_inc_dirs, dbus_lib_dirs, dbus_libs]):
            self.progress("DBus v1 does not seem to be installed.")

        # Try and find dbus-python.h.  The current PyPI package doesn't install
        # it.  We look where DBus itself is installed.
        if self.dbus:
            dbus_inc_dirs.append(self.dbus)

        for d in dbus_inc_dirs:
            if os.path.isfile(os.path.join(d, 'dbus', 'dbus-python.h')):
                break
        else:
            self.progress(
                    "dbus/dbus-python.h could not be found and so the "
                    "dbus-python support module will be disabled. If "
                    "dbus-python is installed then use the --dbus argument to "
                    "explicitly specify the directory containing "
                    "dbus/dbus-python.h.")
            return

        # Create the buildable.
        sources_dir = os.path.join(self.root_dir, 'dbus')

        buildable = BuildableModule(self, 'dbus', 'dbus.mainloop.pyqt5',
                uses_limited_api=True)
        buildable.builder_settings.append('QT -= gui')
        buildable.sources.extend(glob.glob(os.path.join(sources_dir, '*.cpp')))
        buildable.headers.extend(glob.glob(os.path.join(sources_dir, '*.h')))
        buildable.include_dirs.extend(dbus_inc_dirs)
        buildable.library_dirs.extend(dbus_lib_dirs)
        buildable.libraries.extend(dbus_libs)
        buildable.debug = debug

        self.buildables.append(buildable)

    def _add_plugin(self, name, user_name, target_name, target_subdir, debug):
        """ Add a plugin to the project buildables. """

        builder = self.builder

        # Check we have a shared interpreter library.
        if not self.py_pylib_shlib:
            self.progress("The {0} plugin was disabled because a shared Python library couldn't be found.".format(user_name))
            return

        # Where the plugin will (eventually) be installed.
        target_plugin_dir = os.path.join(
                builder.qt_configuration['QT_INSTALL_PLUGINS'], target_subdir)

        # Create the buildable and add it to the builder.
        buildable = Buildable(self, name)
        self.buildables.append(buildable)

        # The platform-specific name of the plugin file.
        if self.py_platform == 'win32':
            target_name = target_name + '.dll'
        elif self.py_platform == 'darwin':
            target_name = 'lib' + target_name + '.dylib'
        else:
            target_name = 'lib' + target_name + '.so'

        # Create the corresponding installable.
        installable = QmakeTargetInstallable(target_name, target_plugin_dir)
        buildable.installables.append(installable)

        # Create the .pro file.
        self.progress(
                "Generating the {0} plugin .pro file".format(user_name))

        root_plugin_dir = os.path.join(self.root_dir, name)

        with open(os.path.join(root_plugin_dir, name + '.pro-in')) as f:
            prj = f.read()

        prj = prj.replace('@QTCONFIG@', 'debug' if debug else 'release')
        prj = prj.replace('@PYINCDIR@',
                builder.qmake_quote(self.py_include_dir))
        prj = prj.replace('@SIPINCDIR@', builder.qmake_quote(self.build_dir))
        prj = prj.replace('@PYLINK@',
                '-L{} -l{}'.format(self.py_pylib_dir, self.py_pylib_lib))
        prj = prj.replace('@PYSHLIB@', self.py_pylib_shlib)
        prj = prj.replace('@QTPLUGINDIR@',
                builder.qmake_quote(target_plugin_dir))

        # Write the .pro file.
        pro_path = os.path.join(buildable.build_dir, name + '.pro')
        pro_f = self.open_for_writing(pro_path)

        pro_f.write(prj)

        pro_f.write('''
INCLUDEPATH += {}
VPATH = {}
'''.format(builder.qmake_quote(root_plugin_dir), builder.qmake_quote(root_plugin_dir)))

        pro_f.write('\n'.join(builder.qmake_settings) + '\n')

        pro_f.close()

    def _check_license(self):
        """ Handle the validation of the PyQt5 license. """

        # We read the license.py file as data.
        license_py = os.path.join(self.root_dir, 'license.py')

        if os.path.isfile(license_py):
            ltype = lname = lfile = None

            with open(license_py) as lf:
                for line in lf:
                    parts = line.split('=')
                    if len(parts) == 2:
                        name, value = parts

                        name = name.strip()
                        value = value.strip()[1:-1]

                        if name == 'LicenseType':
                            ltype = value
                        elif name == 'LicenseName':
                            lname = value
                        elif name == 'LicenseFile':
                            lfile = value

            if lname is None or lfile is None:
                ltype = None
        else:
            ltype = None

        # Default to the GPL.
        if ltype is None:
            ltype = 'GPL'
            lname = "GNU General Public License"
            lfile = 'pyqt-gpl.sip'

        self.progress(
                "This is the {0} version of PyQt {1} (licensed under the {2}) "
                        "for Python {3} on {4}.".format(
                                ltype, self.version_str, lname,
                                sys.version.split()[0], sys.platform))

        # Confirm the license if not already done.
        if not self.confirm_license:
            loptions = """
Type 'L' to view the license.
"""

            sys.stdout.write(loptions)
            sys.stdout.write("""Type 'yes' to accept the terms of the license.
Type 'no' to decline the terms of the license.

""")

            while True:
                sys.stdout.write("Do you accept the terms of the license? ")
                sys.stdout.flush()

                try:
                    resp = sys.stdin.readline()
                except KeyboardInterrupt:
                    raise SystemExit
                except:
                    resp = ""

                resp = resp.strip().lower()

                if resp == "yes":
                    break

                if resp == "no":
                    sys.exit()

                if resp == 'l':
                    os.system('more LICENSE')

        # Check that the license file exists and fix its syntax.
        src_lfile = os.path.join(self.license_dir, lfile)

        if os.path.isfile(src_lfile):
            self.progress("Found the license file '{0}'.".format(lfile))
            self._fix_license(src_lfile,
                    os.path.join(self.build_dir, lfile + '5'))

            # Make sure sip can find the license file.
            self.sip_include_dirs.append(self.build_dir)
        else:
            raise UserException(
                    "Please copy the license file '{0}' to '{1}'".format(lfile,
                            self.license_dir))

    def _fix_license(self, src_lfile, dst_lfile):
        """ Copy the license file and fix it so that it conforms to the SIP v5
        syntax.
        """

        with open(src_lfile) as f:
            f5 = self.open_for_writing(dst_lfile)

            for line in f:
                if line.startswith('%License'):
                    anno_start = line.find('/')
                    anno_end = line.rfind('/')

                    if anno_start < 0 or anno_end < 0 or anno_start == anno_end:
                        f5.close()

                        raise UserException(
                                "'{0}' has missing annotations".format(name))

                    annos = line[anno_start + 1:anno_end].split(', ')
                    annos5 = [anno[0].lower() + anno[1:] for anno in annos]

                    f5.write('%License(')
                    f5.write(', '.join(annos5))
                    f5.write(')\n')
                else:
                    f5.write(line)

            f5.close()


class OpenGLBindings(PyQtBindings):
    """ Encapsulate internal OpenGL functions bindings. """

    def __init__(self, project, version):
        """ Initialise the bindings. """

        super().__init__(project, '_QOpenGLFunctions_' + version,
                test_headers=['qopenglfunctions_{}.h'.format(version.lower())],
                test_statement='new QOpenGLFunctions_{}()'.format(version),
                internal=True)

    def is_buildable(self):
        """ Return True if the bindings are buildable. """

        # Check that the QtGui bindings are being built.
        qtgui = self.project.bindings.get('QtGui')
        if qtgui is None:
            return False

        # Check if all OpenGL support is disabled.
        if 'PyQt_OpenGL' in qtgui.disabled_features:
            return False

        # Check if OpenGL desktop support has been disabled.
        if 'PyQt_Desktop_OpenGL' in qtgui.disabled_features:
            if self.is_desktop_opengl():
                return False
        else:
            if not self.is_desktop_opengl():
                return False

        # Run the standard configuration checks.
        return super().is_buildable()

    def is_desktop_opengl(self):
        """ Return True if the bindings are for desktop OpenGL. """

        return True


class Qt(PyQtBindings):
    """ The Qt composite module. """

    def __init__(self, project):
        """ Initialise the bindings. """

        # We specify 'internal' to avoid the generation of .api and .pyi files
        # and the installation of the .sip files.
        super().__init__(project, 'Qt', qmake_QT=['-core', '-gui'],
                internal=True)


class QAxContainer(PyQtBindings):
    """ The QAxContainer bindings. """

    def __init__(self, project):
        """ Initialise the bindings. """

        super().__init__(project, 'QAxContainer', qmake_QT=['axcontainer'],
                test_headers=['qaxobject.h'], test_statement='new QAxObject()')


class QtAndroidExtras(PyQtBindings):
    """ The QtAndroidExtras bindings. """

    def __init__(self, project):
        """ Initialise the bindings. """

        super().__init__(project, 'QtAndroidExtras',
                qmake_QT=['androidextras'], test_headers=['QtAndroid'],
                test_statement='QtAndroid::androidSdkVersion()')


class QtBluetooth(PyQtBindings):
    """ The QtBluetooth bindings. """

    def __init__(self, project):
        """ Initialise the bindings. """

        super().__init__(project, 'QtBluetooth', qmake_QT=['bluetooth'],
                test_headers=['qbluetoothaddress.h'],
                test_statement='new QBluetoothAddress()')


class QtCore(PyQtBindings):
    """ The QtCore bindings. """

    def __init__(self, project):
        """ Initialise the bindings. """

        super().__init__(project, 'QtCore', qmake_QT=['-gui'])

    def generate(self):
        """ Generate the bindings source code and return the corresponding
        buildable.
        """

        # This is re-implemented so that we can update the buildable to include
        # the embedded sip flags.  Note that this support is deprecated and can
        # be removed once support for sip4 has been dropped.

        project = self.project

        # The embedded flags.
        sip_flags = ['-n', project.sip_module]

        if project.py_debug:
            sip_flags.append('-D')

        for tag in self.tags:
            sip_flags.append('-t')
            sip_flags.append(tag)

        for bindings in project.bindings.values():
            for feature in bindings.disabled_features:
                sip_flags.append('-x')
                sip_flags.append(feature)

        buildable = super().generate()

        cpp = 'qpycore_post_init.cpp'
        in_path = os.path.join(project.root_dir, 'qpy', 'QtCore', cpp + '.in')
        out_path = os.path.join(buildable.build_dir, cpp)

        out_f = project.open_for_writing(out_path)

        with open(in_path) as in_f:
            code = in_f.read()
            code = code.replace('@@PYQT_SIP_FLAGS@@', ' '.join(sip_flags))
            out_f.write(code)

        out_f.close()

        buildable.sources.append(cpp)

        return buildable

    def handle_test_output(self, test_output):
        """ Handle the output from the external test program and return True if
        the bindings are buildable.
        """

        project = self.project

        if not project.qt_shared and test_output[0] == 'shared':
            project.qt_shared = True

        return super().handle_test_output(test_output[1:])


class QtDBus(PyQtBindings):
    """ The QtDBus bindings. """

    def __init__(self, project):
        """ Initialise the bindings. """

        super().__init__(project, 'QtDBus', qmake_QT=['dbus', '-gui'],
                test_headers=['qdbusconnection.h'],
                test_statement='QDBusConnection::systemBus()')


class QtDesigner(PyQtBindings):
    """ The QtDesigner bindings. """

    def __init__(self, project):
        """ Initialise the bindings. """

        super().__init__(project, 'QtDesigner', qmake_QT=['designer'],
                test_headers=['QExtensionFactory', 'customwidget.h'],
                test_statement='new QExtensionFactory()')

    def is_buildable(self):
        """ Return True if the bindings are buildable. """

        project = self.project

        if not project.qt_shared:
            project.progress(
                    "The QtDesigner bindings are disabled with a static Qt "
                    "installation")
            return False

        return super().is_buildable()


class Enginio(PyQtBindings):
    """ The Enginio bindings. """

    def __init__(self, project):
        """ Initialise the bindings. """

        super().__init__(project, 'Enginio', qmake_QT=['enginio'],
                test_headers=['enginioclient.h'],
                test_statement='new EnginioClient()')


class QtGui(PyQtBindings):
    """ The QtGui bindings. """

    def __init__(self, project):
        """ Initialise the bindings. """

        super().__init__(project, 'QtGui')


class QtHelp(PyQtBindings):
    """ The QtHelp bindings. """

    def __init__(self, project):
        """ Initialise the bindings. """

        super().__init__(project, 'QtHelp', qmake_QT=['help'],
                test_headers=['qhelpengine.h'],
                test_statement='new QHelpEngine("foo")')


class QtLocation(PyQtBindings):
    """ The QtLocation bindings. """

    def __init__(self, project):
        """ Initialise the bindings. """

        super().__init__(project, 'QtLocation', qmake_QT=['location'],
                test_headers=['qplace.h'], test_statement='new QPlace()')


class QtMacExtras(PyQtBindings):
    """ The QtMacExtras bindings. """

    def __init__(self, project):
        """ Initialise the bindings. """

        super().__init__(project, 'QtMacExtras', qmake_QT=['macextras'],
                test_headers=['qmacpasteboardmime.h'],
                test_statement='class Foo : public QMacPasteboardMime {}')


class QtMultimedia(PyQtBindings):
    """ The QtMultimedia bindings. """

    def __init__(self, project):
        """ Initialise the bindings. """

        super().__init__(project, 'QtMultimedia', qmake_QT=['multimedia'],
                test_headers=['QAudioDeviceInfo'],
                test_statement='new QAudioDeviceInfo()')


class QtMultimediaWidgets(PyQtBindings):
    """ The QtMultimediaWidgets bindings. """

    def __init__(self, project):
        """ Initialise the bindings. """

        super().__init__(project, 'QtMultimediaWidgets',
                qmake_QT=['multimediawidgets', 'multimedia'],
                test_headers=['QVideoWidget'],
                test_statement='new QVideoWidget()')


class QtNetwork(PyQtBindings):
    """ The QtNetwork bindings. """

    def __init__(self, project):
        """ Initialise the bindings. """

        super().__init__(project, 'QtNetwork', qmake_QT=['network', '-gui'])


class QtNfc(PyQtBindings):
    """ The QtNfc bindings. """

    def __init__(self, project):
        """ Initialise the bindings. """

        super().__init__(project, 'QtNfc', qmake_QT=['nfc', '-gui'],
                test_headers=['qnearfieldmanager.h'],
                test_statement='new QNearFieldManager()')


class QtOpenGL(PyQtBindings):
    """ The QtOpenGL bindings. """

    def __init__(self, project):
        """ Initialise the bindings. """

        super().__init__(project, 'QtOpenGL', qmake_QT=['opengl'],
                test_headers=['qgl.h'], test_statement='new QGLWidget()')


class QtPositioning(PyQtBindings):
    """ The QtPositioning bindings. """

    def __init__(self, project):
        """ Initialise the bindings. """

        super().__init__(project, 'QtPositioning', qmake_QT=['positioning'],
                test_headers=['qgeoaddress.h'],
                test_statement='new QGeoAddress()')


class QtPrintSupport(PyQtBindings):
    """ The QtPrintSupport bindings. """

    def __init__(self, project):
        """ Initialise the bindings. """

        super().__init__(project, 'QtPrintSupport', qmake_QT=['printsupport'])


class QtQml(PyQtBindings):
    """ The QtQml bindings. """

    def __init__(self, project):
        """ Initialise the bindings. """

        super().__init__(project, 'QtQml', qmake_QT=['qml'],
                test_headers=['qjsengine.h'], test_statement='new QJSEngine()')


class QtQuick(PyQtBindings):
    """ The QtQuick bindings. """

    def __init__(self, project):
        """ Initialise the bindings. """

        super().__init__(project, 'QtQuick', qmake_QT=['quick'],
                test_headers=['qquickwindow.h'],
                test_statement='new QQuickWindow()')


class QtQuick3D(PyQtBindings):
    """ The QtQuick3D bindings. """

    def __init__(self, project):
        """ Initialise the bindings. """

        super().__init__(project, 'QtQuick3D', qmake_QT=['quick3d'],
                test_headers=['qquick3d.h'],
                test_statement='QQuick3D::idealSurfaceFormat()')


class QtQuickWidgets(PyQtBindings):
    """ The QtQuickWidgets bindings. """

    def __init__(self, project):
        """ Initialise the bindings. """

        super().__init__(project, 'QtQuickWidgets', qmake_QT=['quickwidgets'],
                test_headers=['qquickwidget.h'],
                test_statement='new QQuickWidget()')


class QtRemoteObjects(PyQtBindings):
    """ The QtRemoteObjects bindings. """

    def __init__(self, project):
        """ Initialise the bindings. """

        super().__init__(project, 'QtRemoteObjects',
                qmake_QT=['remoteobjects', '-gui'],
                test_headers=['qtremoteobjectsversion.h'],
                test_statement='const char *v = QTREMOTEOBJECTS_VERSION_STR')


class QtSensors(PyQtBindings):
    """ The QtSensors bindings. """

    def __init__(self, project):
        """ Initialise the bindings. """

        super().__init__(project, 'QtSensors', qmake_QT=['sensors'],
                test_headers=['qsensor.h'],
                test_statement='new QSensor(QByteArray())')


class QtSerialPort(PyQtBindings):
    """ The QtSerialPort bindings. """

    def __init__(self, project):
        """ Initialise the bindings. """

        super().__init__(project, 'QtSerialPort', qmake_QT=['serialport'],
                test_headers=['qserialport.h'],
                test_statement='new QSerialPort()')


class QtSql(PyQtBindings):
    """ The QtSql bindings. """

    def __init__(self, project):
        """ Initialise the bindings. """

        super().__init__(project, 'QtSql', qmake_QT=['sql', 'widgets'],
                test_headers=['qsqldatabase.h'],
                test_statement='new QSqlDatabase()')


class QtSvg(PyQtBindings):
    """ The QtSvg bindings. """

    def __init__(self, project):
        """ Initialise the bindings. """

        super().__init__(project, 'QtSvg', qmake_QT=['svg'],
                test_headers=['qsvgwidget.h'],
                test_statement='new QSvgWidget()')


class QtTest(PyQtBindings):
    """ The QtTest bindings. """

    def __init__(self, project):
        """ Initialise the bindings. """

        super().__init__(project, 'QtTest', qmake_QT=['testlib', 'widgets'],
                test_headers=['QtTest'], test_statement='QTest::qSleep(0)')


class QtTextToSpeech(PyQtBindings):
    """ The QtTextToSpeech bindings. """

    def __init__(self, project):
        """ Initialise the bindings. """

        super().__init__(project, 'QtTextToSpeech',
                qmake_QT=['texttospeech', '-gui'],
                test_headers=['QTextToSpeech'],
                test_statement='new QTextToSpeech()')


class QtWebChannel(PyQtBindings):
    """ The QtWebChannel bindings. """

    def __init__(self, project):
        """ Initialise the bindings. """

        super().__init__(project, 'QtWebChannel',
                qmake_QT=['webchannel', 'network', '-gui'],
                test_headers=['qwebchannel.h'],
                test_statement='new QWebChannel()')


class QtWebKit(PyQtBindings):
    """ The QtWebKit bindings. """

    def __init__(self, project):
        """ Initialise the bindings. """

        super().__init__(project, 'QtWebKit', qmake_QT=['webkit', 'network'],
                test_headers=['qwebkitglobal.h'],
                test_statement='qWebKitVersion()')


class QtWebKitWidgets(PyQtBindings):
    """ The QtWebKitWidgets bindings. """

    def __init__(self, project):
        """ Initialise the bindings. """

        super().__init__(project, 'QtWebKitWidgets',
                qmake_QT=['webkitwidgets', 'printsupport'],
                test_headers=['qwebpage.h'], test_statement='new QWebPage()')


class QtWebSockets(PyQtBindings):
    """ The QtWebSockets bindings. """

    def __init__(self, project):
        """ Initialise the bindings. """

        super().__init__(project, 'QtWebSockets',
                qmake_QT=['websockets', '-gui'], test_headers=['qwebsocket.h'],
                test_statement='new QWebSocket()')


class QtWidgets(PyQtBindings):
    """ The QtWidgets bindings. """

    def __init__(self, project):
        """ Initialise the bindings. """

        super().__init__(project, 'QtWidgets', qmake_QT=['widgets'],
                test_headers=['qwidget.h'], test_statement='new QWidget()')


class QtWinExtras(PyQtBindings):
    """ The QtWinExtras bindings. """

    def __init__(self, project):
        """ Initialise the bindings. """

        super().__init__(project, 'QtWinExtras',
                qmake_QT=['winextras', 'widgets'], test_headers=['QtWin'],
                test_statement='QtWin::isCompositionEnabled()')


class QtX11Extras(PyQtBindings):
    """ The QtX11Extras bindings. """

    def __init__(self, project):
        """ Initialise the bindings. """

        super().__init__(project, 'QtX11Extras', qmake_QT=['x11extras'],
                test_headers=['QX11Info'],
                test_statement='QX11Info::display()')


class QtXml(PyQtBindings):
    """ The QtXml bindings. """

    def __init__(self, project):
        """ Initialise the bindings. """

        super().__init__(project, 'QtXml', qmake_QT=['xml', '-gui'],
                test_headers=['qdom.h'], test_statement='new QDomDocument()')


class QtXmlPatterns(PyQtBindings):
    """ The QtXmlPatterns bindings. """

    def __init__(self, project):
        """ Initialise the bindings. """

        super().__init__(project, 'QtXmlPatterns',
                qmake_QT=['xmlpatterns', '-gui', 'network'],
                test_headers=['qxmlname.h'], test_statement='new QXmlName()')


class _QOpenGLFunctions_2_0(OpenGLBindings):
    """ The _QOpenGLFunctions_2_0 bindings. """

    def __init__(self, project):
        """ Initialise the bindings. """

        super().__init__(project, '2_0')


class _QOpenGLFunctions_2_1(OpenGLBindings):
    """ The _QOpenGLFunctions_2_1 bindings. """

    def __init__(self, project):
        """ Initialise the bindings. """

        super().__init__(project, '2_1')


class _QOpenGLFunctions_4_1_Core(OpenGLBindings):
    """ The _QOpenGLFunctions_4_1_Core bindings. """

    def __init__(self, project):
        """ Initialise the bindings. """

        super().__init__(project, '4_1_Core')


class _QOpenGLFunctions_ES2(OpenGLBindings):
    """ The _QOpenGLFunctions_ES2 bindings. """

    def __init__(self, project):
        """ Initialise the bindings. """

        super().__init__(project, 'ES2')

    def is_desktop_opengl(self):
        """ Return True if the bindings are for desktop OpenGL. """

        return False


class pylupdate(PyQtBindings):
    """ The pylupdate bindings. """

    def __init__(self, project):
        """ Initialise the bindings. """

        super().__init__(project, 'pylupdate', qmake_QT=['xml', '-gui'],
                internal=True)

    def generate(self):
        """ Generate the bindings source code and return the corresponding
        buildable.
        """

        # This is re-implemented so that we can update the buildable to include
        # pylupdate_main.py.

        project = self.project

        buildable = super().generate()

        installable = Installable('pylupdate_main', target_subdir='PyQt5')
        installable.files.append(
                os.path.join(project.root_dir, 'pylupdate',
                        'pylupdate_main.py'))
        buildable.installables.append(installable)

        return buildable

    def is_buildable(self):
        """ Return True if the bindings are buildable. """

        return self.project.tools


class pyrcc(PyQtBindings):
    """ The pyrcc bindings. """

    def __init__(self, project):
        """ Initialise the bindings. """

        super().__init__(project, 'pyrcc', qmake_QT=['xml', '-gui'],
                internal=True)

    def generate(self):
        """ Generate the bindings source code and return the corresponding
        buildable.
        """

        # This is re-implemented so that we can update the buildable to include
        # pyrcc_main.py.

        project = self.project

        buildable = super().generate()

        installable = Installable('pyrcc_main', target_subdir='PyQt5')
        installable.files.append(
                os.path.join(project.root_dir, 'pyrcc', 'pyrcc_main.py'))
        buildable.installables.append(installable)

        return buildable

    def is_buildable(self):
        """ Return True if the bindings are buildable. """

        return self.project.tools
