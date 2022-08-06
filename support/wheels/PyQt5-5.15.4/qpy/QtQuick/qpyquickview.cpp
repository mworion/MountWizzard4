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

#include "qpyquickview.h"

#include "sipAPIQtQuick.h"


// The maximum number of Python QQuickView types.
const int NrOfQuickViewTypes = 20;

// The list of registered Python types.
static QList<PyTypeObject *> pyqt_types;

// The registration data for the canned types.
static QQmlPrivate::RegisterType canned_types[NrOfQuickViewTypes];

// External declarations.
extern const QMetaObject *qpyquick_pick_metaobject(const QMetaObject *super_mo,
        const QMetaObject *static_mo);


#define QPYQUICKVIEW_INIT(n) \
    case n##U: \
        QPyQuickView##n::staticMetaObject = *mo; \
        rt->typeId = qRegisterNormalizedMetaType<QPyQuickView##n *>(ptr_name); \
        rt->listId = qRegisterNormalizedMetaType<QQmlListProperty<QPyQuickView##n> >(list_name); \
        rt->objectSize = sizeof(QPyQuickView##n); \
        rt->create = QQmlPrivate::createInto<QPyQuickView##n>; \
        rt->metaObject = mo; \
        rt->attachedPropertiesFunction = QQmlPrivate::attachedPropertiesFunc<QPyQuickView##n>(); \
        rt->attachedPropertiesMetaObject = QQmlPrivate::attachedPropertiesMetaObject<QPyQuickView##n>(); \
        rt->parserStatusCast = QQmlPrivate::StaticCastSelector<QPyQuickView##n,QQmlParserStatus>::cast(); \
        rt->valueSourceCast = QQmlPrivate::StaticCastSelector<QPyQuickView##n,QQmlPropertyValueSource>::cast(); \
        rt->valueInterceptorCast = QQmlPrivate::StaticCastSelector<QPyQuickView##n,QQmlPropertyValueInterceptor>::cast(); \
        break


// The ctor.
QPyQuickView::QPyQuickView(QWindow *parent) : sipQQuickView(parent)
{
}


// Add a new Python type and return its number.
QQmlPrivate::RegisterType *QPyQuickView::addType(PyTypeObject *type,
        const QMetaObject *mo, const QByteArray &ptr_name,
        const QByteArray &list_name)
{
    int type_nr = pyqt_types.size();

    // Check we have a spare canned type.
    if (type_nr >= NrOfQuickViewTypes)
    {
        PyErr_Format(PyExc_TypeError,
                "a maximum of %d QQuickView types may be registered with QML",
                NrOfQuickViewTypes);
        return 0;
    }

    pyqt_types.append(type);

    QQmlPrivate::RegisterType *rt = &canned_types[type_nr];

    // Initialise those members that depend on the C++ type.
    switch (type_nr)
    {
        QPYQUICKVIEW_INIT(0);
        QPYQUICKVIEW_INIT(1);
        QPYQUICKVIEW_INIT(2);
        QPYQUICKVIEW_INIT(3);
        QPYQUICKVIEW_INIT(4);
        QPYQUICKVIEW_INIT(5);
        QPYQUICKVIEW_INIT(6);
        QPYQUICKVIEW_INIT(7);
        QPYQUICKVIEW_INIT(8);
        QPYQUICKVIEW_INIT(9);
        QPYQUICKVIEW_INIT(10);
        QPYQUICKVIEW_INIT(11);
        QPYQUICKVIEW_INIT(12);
        QPYQUICKVIEW_INIT(13);
        QPYQUICKVIEW_INIT(14);
        QPYQUICKVIEW_INIT(15);
        QPYQUICKVIEW_INIT(16);
        QPYQUICKVIEW_INIT(17);
        QPYQUICKVIEW_INIT(18);
        QPYQUICKVIEW_INIT(19);
    }

    return rt;
}


// Create the Python instance.
void QPyQuickView::createPyObject(QWindow *parent)
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
#define QPYQUICKVIEW_IMPL(n) \
QPyQuickView##n::QPyQuickView##n(QWindow *parent) : QPyQuickView(parent) \
{ \
    createPyObject(parent); \
} \
const QMetaObject *QPyQuickView##n::metaObject() const \
{ \
    return qpyquick_pick_metaobject(QPyQuickView::metaObject(), &staticMetaObject); \
} \
QMetaObject QPyQuickView##n::staticMetaObject


QPYQUICKVIEW_IMPL(0);
QPYQUICKVIEW_IMPL(1);
QPYQUICKVIEW_IMPL(2);
QPYQUICKVIEW_IMPL(3);
QPYQUICKVIEW_IMPL(4);
QPYQUICKVIEW_IMPL(5);
QPYQUICKVIEW_IMPL(6);
QPYQUICKVIEW_IMPL(7);
QPYQUICKVIEW_IMPL(8);
QPYQUICKVIEW_IMPL(9);
QPYQUICKVIEW_IMPL(10);
QPYQUICKVIEW_IMPL(11);
QPYQUICKVIEW_IMPL(12);
QPYQUICKVIEW_IMPL(13);
QPYQUICKVIEW_IMPL(14);
QPYQUICKVIEW_IMPL(15);
QPYQUICKVIEW_IMPL(16);
QPYQUICKVIEW_IMPL(17);
QPYQUICKVIEW_IMPL(18);
QPYQUICKVIEW_IMPL(19);
