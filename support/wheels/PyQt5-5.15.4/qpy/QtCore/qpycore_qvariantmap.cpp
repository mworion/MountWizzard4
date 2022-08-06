// This is the implementation of the QVariantMap convertors.
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

#include <QString>
#include <QVariant>

#include "qpycore_api.h"
#include "qpycore_chimera.h"

#include "sipAPIQtCore.h"


// Convert a Python object to a QVariantMap and return false if there was an
// error.
bool qpycore_toQVariantMap(PyObject *py, QVariantMap &cpp)
{
    Q_ASSERT(PyDict_Check(py));

    PyObject *key_obj, *val_obj;
    Py_ssize_t i;

    i = 0;
    while (PyDict_Next(py, &i, &key_obj, &val_obj))
    {
        int key_state, val_state, iserr = 0;

        QString *key = reinterpret_cast<QString *>(sipForceConvertToType(
                key_obj, sipType_QString, NULL, SIP_NOT_NONE, &key_state,
                &iserr));

        QVariant *val = reinterpret_cast<QVariant *>(sipForceConvertToType(
                val_obj, sipType_QVariant, NULL, SIP_NOT_NONE, &val_state,
                &iserr));

        if (iserr)
            return false;

        cpp.insert(*key, *val);

        sipReleaseType(key, sipType_QString, key_state);
        sipReleaseType(val, sipType_QVariant, val_state);
    }

    return true;
}


// Convert a QVariantMap to a Python object and return 0 if there was an error.
PyObject *qpycore_fromQVariantMap(const QVariantMap &qm)
{
    PyObject *py = PyDict_New();

    if (!py)
        return 0;

    for (QVariantMap::const_iterator it = qm.constBegin(); it != qm.constEnd(); ++it)
        if (!Chimera::addVariantToDict(py, it.key(), it.value()))
        {
            Py_DECREF(py);
            return 0;
        }

    return py;
}
