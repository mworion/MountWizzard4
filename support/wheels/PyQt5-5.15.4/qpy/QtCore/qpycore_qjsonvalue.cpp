// This is the support for QJsonValue.
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

#include "qpycore_api.h"

#include "sipAPIQtCore.h"


// See if a Python object can be converted to a QJsonValue.
int qpycore_canConvertTo_QJsonValue(PyObject *py)
{
    // Note that the API doesn't provide a test for constrained named enums.
    if (PyObject_TypeCheck(py, sipTypeAsPyTypeObject(sipType_QJsonValue_Type)))
        return 1;

    if (PyBool_Check(py))
        return 1;

    if (PyLong_Check(py))
        return 1;

#if PY_MAJOR_VERSION < 3
    if (PyInt_Check(py))
        return 1;
#endif

    if (PyFloat_Check(py))
        return 1;

    if (sipCanConvertToType(py, sipType_QString, 0))
        return 1;

    // We must check for QJsonObject before QJsonArray.
    if (sipCanConvertToType(py, sipType_QJsonObject, 0))
        return 1;

    // We must check for QJsonValue before QJsonArray.
    if (sipCanConvertToType(py, sipType_QJsonValue, SIP_NO_CONVERTORS))
        return 1;

    return sipCanConvertToType(py, sipType_QJsonArray, 0);
}


// Convert a Python object to a QJsonValue.
int qpycore_convertTo_QJsonValue(PyObject *py, PyObject *transferObj,
        QJsonValue **cpp, int *isErr)
{
    if (py == Py_None)
    {
        *cpp = new QJsonValue();

        return sipGetState(transferObj);
    }

    if (PyObject_TypeCheck(py, sipTypeAsPyTypeObject(sipType_QJsonValue_Type)))
    {
        int v = sipConvertToEnum(py, sipType_QJsonValue_Type);

        if (PyErr_Occurred())
        {
            *isErr = 1;
            return 0;
        }

        *cpp = new QJsonValue(static_cast<QJsonValue::Type>(v));

        return sipGetState(transferObj);
    }

    if (PyBool_Check(py))
    {
        *cpp = new QJsonValue(py == Py_True);

        return sipGetState(transferObj);
    }

    if (PyLong_Check(py))
    {
        *cpp = new QJsonValue((qint64)PyLong_AsLong(py));

        return sipGetState(transferObj);
    }

#if PY_MAJOR_VERSION < 3
    if (PyInt_Check(py))
    {
        *cpp = new QJsonValue((int)PyInt_AS_LONG(py));

        return sipGetState(transferObj);
    }
#endif

    if (PyFloat_Check(py))
    {
        *cpp = new QJsonValue((double)PyFloat_AsDouble(py));

        return sipGetState(transferObj);
    }

    if (sipCanConvertToType(py, sipType_QString, 0))
    {
        int state;
        QString *q = reinterpret_cast<QString *>(sipConvertToType(py,
                sipType_QString, 0, 0, &state, isErr));

        if (*isErr)
            return 0;

        *cpp = new QJsonValue(*q);

        sipReleaseType(q, sipType_QString, state);

        return sipGetState(transferObj);
    }

    // We must check for QJsonObject before QJsonArray.
    if (sipCanConvertToType(py, sipType_QJsonObject, 0))
    {
        int state;
        QJsonObject *q = reinterpret_cast<QJsonObject *>(sipConvertToType(py,
                sipType_QJsonObject, 0, 0, &state, isErr));

        if (*isErr)
            return 0;

        *cpp = new QJsonValue(*q);

        sipReleaseType(q, sipType_QJsonObject, state);

        return sipGetState(transferObj);
    }

    // We must check for QJsonValue before QJsonArray.
    if (sipCanConvertToType(py, sipType_QJsonValue, SIP_NO_CONVERTORS))
    {
        *cpp = reinterpret_cast<QJsonValue *>(sipConvertToType(py,
                sipType_QJsonValue, transferObj, SIP_NO_CONVERTORS, 0, isErr));

        return 0;
    }

    // Now it is safe to convert to QJsonArray.
    {
        int state;
        QJsonArray *q = reinterpret_cast<QJsonArray *>(sipConvertToType(py,
                sipType_QJsonArray, 0, 0, &state, isErr));

        if (*isErr)
            return 0;

        *cpp = new QJsonValue(*q);

        sipReleaseType(q, sipType_QJsonArray, state);

        return sipGetState(transferObj);
    }
}
