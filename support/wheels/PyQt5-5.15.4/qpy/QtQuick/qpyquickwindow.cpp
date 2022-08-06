// This is the implementation of the QPyQuickWindow classes.
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

#include <QQmlListProperty>

#include "qpyquickwindow.h"

#include "sipAPIQtQuick.h"


// The maximum number of Python QQuickWindow types.
const int NrOfQuickWindowTypes = 20;

// The list of registered Python types.
static QList<PyTypeObject *> pyqt_types;

// The registration data for the canned types.
static QQmlPrivate::RegisterType canned_types[NrOfQuickWindowTypes];

// External declarations.
extern const QMetaObject *qpyquick_pick_metaobject(const QMetaObject *super_mo,
        const QMetaObject *static_mo);


#define QPYQUICKWINDOW_INIT(n) \
    case n##U: \
        QPyQuickWindow##n::staticMetaObject = *mo; \
        rt->typeId = qRegisterNormalizedMetaType<QPyQuickWindow##n *>(ptr_name); \
        rt->listId = qRegisterNormalizedMetaType<QQmlListProperty<QPyQuickWindow##n> >(list_name); \
        rt->objectSize = sizeof(QPyQuickWindow##n); \
        rt->create = QQmlPrivate::createInto<QPyQuickWindow##n>; \
        rt->metaObject = mo; \
        rt->attachedPropertiesFunction = QQmlPrivate::attachedPropertiesFunc<QPyQuickWindow##n>(); \
        rt->attachedPropertiesMetaObject = QQmlPrivate::attachedPropertiesMetaObject<QPyQuickWindow##n>(); \
        rt->parserStatusCast = QQmlPrivate::StaticCastSelector<QPyQuickWindow##n,QQmlParserStatus>::cast(); \
        rt->valueSourceCast = QQmlPrivate::StaticCastSelector<QPyQuickWindow##n,QQmlPropertyValueSource>::cast(); \
        rt->valueInterceptorCast = QQmlPrivate::StaticCastSelector<QPyQuickWindow##n,QQmlPropertyValueInterceptor>::cast(); \
        break


// The ctor.
QPyQuickWindow::QPyQuickWindow(QWindow *parent) : sipQQuickWindow(parent)
{
}


// Add a new Python type and return its number.
QQmlPrivate::RegisterType *QPyQuickWindow::addType(PyTypeObject *type,
        const QMetaObject *mo, const QByteArray &ptr_name,
        const QByteArray &list_name)
{
    int type_nr = pyqt_types.size();

    // Check we have a spare canned type.
    if (type_nr >= NrOfQuickWindowTypes)
    {
        PyErr_Format(PyExc_TypeError,
                "a maximum of %d QQuickWindow types may be registered with QML",
                NrOfQuickWindowTypes);
        return 0;
    }

    pyqt_types.append(type);

    QQmlPrivate::RegisterType *rt = &canned_types[type_nr];

    // Initialise those members that depend on the C++ type.
    switch (type_nr)
    {
        QPYQUICKWINDOW_INIT(0);
        QPYQUICKWINDOW_INIT(1);
        QPYQUICKWINDOW_INIT(2);
        QPYQUICKWINDOW_INIT(3);
        QPYQUICKWINDOW_INIT(4);
        QPYQUICKWINDOW_INIT(5);
        QPYQUICKWINDOW_INIT(6);
        QPYQUICKWINDOW_INIT(7);
        QPYQUICKWINDOW_INIT(8);
        QPYQUICKWINDOW_INIT(9);
        QPYQUICKWINDOW_INIT(10);
        QPYQUICKWINDOW_INIT(11);
        QPYQUICKWINDOW_INIT(12);
        QPYQUICKWINDOW_INIT(13);
        QPYQUICKWINDOW_INIT(14);
        QPYQUICKWINDOW_INIT(15);
        QPYQUICKWINDOW_INIT(16);
        QPYQUICKWINDOW_INIT(17);
        QPYQUICKWINDOW_INIT(18);
        QPYQUICKWINDOW_INIT(19);
    }

    return rt;
}


// Create the Python instance.
void QPyQuickWindow::createPyObject(QWindow *parent)
{
    SIP_BLOCK_THREADS

    // Assume C++ owns everything.
    PyObject *obj = sipConvertFromNewPyType(this, pyqt_types.at(typeNr()),
            NULL, &sipPySelf, "D", parent, sipType_QWindow, NULL);

    if (!obj)
        pyqt5_qtquick_err_print();

    SIP_UNBLOCK_THREADS
}


// The canned type implementations.
#define QPYQUICKWINDOW_IMPL(n) \
QPyQuickWindow##n::QPyQuickWindow##n(QWindow *parent) : QPyQuickWindow(parent) \
{ \
    createPyObject(parent); \
} \
const QMetaObject *QPyQuickWindow##n::metaObject() const \
{ \
    return qpyquick_pick_metaobject(QPyQuickWindow::metaObject(), &staticMetaObject); \
} \
QMetaObject QPyQuickWindow##n::staticMetaObject


QPYQUICKWINDOW_IMPL(0);
QPYQUICKWINDOW_IMPL(1);
QPYQUICKWINDOW_IMPL(2);
QPYQUICKWINDOW_IMPL(3);
QPYQUICKWINDOW_IMPL(4);
QPYQUICKWINDOW_IMPL(5);
QPYQUICKWINDOW_IMPL(6);
QPYQUICKWINDOW_IMPL(7);
QPYQUICKWINDOW_IMPL(8);
QPYQUICKWINDOW_IMPL(9);
QPYQUICKWINDOW_IMPL(10);
QPYQUICKWINDOW_IMPL(11);
QPYQUICKWINDOW_IMPL(12);
QPYQUICKWINDOW_IMPL(13);
QPYQUICKWINDOW_IMPL(14);
QPYQUICKWINDOW_IMPL(15);
QPYQUICKWINDOW_IMPL(16);
QPYQUICKWINDOW_IMPL(17);
QPYQUICKWINDOW_IMPL(18);
QPYQUICKWINDOW_IMPL(19);
