// This is the implementatation of an embedded qt.conf file.
//
// Copyright (c) 2021 Riverbank Computing Limited <info@riverbankcomputing.com>
// 
// This file is part of PyQt5.
// 
// This file may be used under the terms of the GNU General Public License
// version 3.0 as published by the Free Software Foundation and appearing in
// the file LICENSE included in the packaging of this file.  Please review the
// following information to ensure the GNU General Public License version 3.0
// requirements will be met: http://www.gnu.org/copyleft/gpl.html.
// 
// If you do not wish to use this file under the terms of the GPL version 3.0
// then you may purchase a commercial license.  For more information contact
// info@riverbankcomputing.com.
// 
// This file is provided AS IS with NO WARRANTY OF ANY KIND, INCLUDING THE
// WARRANTY OF DESIGN, MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE.


#include <Python.h>

#include <QByteArray>
#include <QDir>
#include <QFileInfo>
#include <QLatin1String>

#include "qpycore_api.h"


static const unsigned char qt_resource_name[] = {
  // qt
  0x0,0x2,
  0x0,0x0,0x7,0x84,
  0x0,0x71,
  0x0,0x74,
    // etc
  0x0,0x3,
  0x0,0x0,0x6c,0xa3,
  0x0,0x65,
  0x0,0x74,0x0,0x63,
    // qt.conf
  0x0,0x7,
  0x8,0x74,0xa6,0xa6,
  0x0,0x71,
  0x0,0x74,0x0,0x2e,0x0,0x63,0x0,0x6f,0x0,0x6e,0x0,0x66,

};

static const unsigned char qt_resource_struct[] = {
  // :
  0x0,0x0,0x0,0x0,0x0,0x2,0x0,0x0,0x0,0x1,0x0,0x0,0x0,0x1,
  // :/qt
  0x0,0x0,0x0,0x0,0x0,0x2,0x0,0x0,0x0,0x1,0x0,0x0,0x0,0x2,
  // :/qt/etc
  0x0,0x0,0x0,0xa,0x0,0x2,0x0,0x0,0x0,0x1,0x0,0x0,0x0,0x3,
  // :/qt/etc/qt.conf
  0x0,0x0,0x0,0x16,0x0,0x0,0x0,0x0,0x0,0x1,0x0,0x0,0x0,0x0,

};


QT_BEGIN_NAMESPACE
bool qRegisterResourceData(int, const unsigned char *, const unsigned char *,
        const unsigned char *);
QT_END_NAMESPACE


// Embed a qt.conf file.
bool qpycore_qt_conf()
{
    // Get PyQt5.__file__.
    PyObject *pyqt5 = PyImport_ImportModule("PyQt5");

    if (!pyqt5)
        return false;

    PyObject *init = PyObject_GetAttrString(pyqt5, "__file__");
    Py_DECREF(pyqt5);

    if (!init)
        return false;

    QString init_impl(qpycore_PyObject_AsQString(init));
    Py_DECREF(init);

    if (init_impl.isEmpty())
        return false;

    // Get the directory containing the PyQt5 extension modules.
    QDir pyqt5_dir = QFileInfo(QDir::fromNativeSeparators(init_impl)).absoluteDir();
    QString qt_dir_name = pyqt5_dir.absoluteFilePath(QLatin1String("Qt5"));

    // Check if there is a bundled copy of Qt.
    if (QFileInfo(qt_dir_name).exists())
    {
        // Get the prefix path with non-native separators.
        static QByteArray qt_conf = qt_dir_name.toLocal8Bit();

        qt_conf.prepend("[Paths]\nPrefix = ");
        qt_conf.append("\n");

        // Prepend the 4-byte size.
        int size = qt_conf.size();

        for (int i = 0; i < 4; ++i)
        {
            qt_conf.prepend(size & 0xff);
            size >>= 8;
        }

        // Register the structures.
        qRegisterResourceData(0x01, qt_resource_struct, qt_resource_name,
                (const unsigned char *)qt_conf.constData());
    }

    return true;
}
