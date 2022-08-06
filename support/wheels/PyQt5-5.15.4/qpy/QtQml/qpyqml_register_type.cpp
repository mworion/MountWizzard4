// This contains the main implementation of qmlRegisterType.
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

#include <qqmlprivate.h>
#include <QByteArray>
#include <QString>
#include <QQmlListProperty>
#include <QQmlParserStatus>
#include <QQmlPropertyValueSource>

#include "qpyqml_api.h"
#include "qpyqmlobject.h"
#include "qpyqmlvalidator.h"

#include "sipAPIQtQml.h"


class QQmlPropertyValueInterceptor;


// Forward declarations.
static QQmlPrivate::RegisterType *init_type(PyTypeObject *py_type, bool ctor,
        int revision, PyTypeObject *attached);
static void complete_init(QQmlPrivate::RegisterType *rt, int revision);
static int register_type(QQmlPrivate::RegisterType *rt);


// The registration data for the QValidator proxy types.
const int NrOfQValidatorTypes = 10;
static QQmlPrivate::RegisterType validator_proxy_types[NrOfQValidatorTypes];

// The registration data for the QObject/QAbstractItemModel proxy types.
const int NrOfQObjectTypes = 60;
static QQmlPrivate::RegisterType object_proxy_types[NrOfQObjectTypes];


// Register a Python type.
int qpyqml_register_type(PyTypeObject *py_type, PyTypeObject *attached)
{
    // Initialise the registration data structure.
    QQmlPrivate::RegisterType *rt = init_type(py_type, false, -1, attached);

    if (!rt)
        return -1;

    return register_type(rt);
}


// Register a library Python type.
int qpyqml_register_library_type(PyTypeObject *py_type, const char *uri,
        int major, int minor, const char *qml_name, int revision,
        PyTypeObject *attached)
{
    // Initialise the registration data structure.
    QQmlPrivate::RegisterType *rt = init_type(py_type, true, revision,
            attached);

    if (!rt)
        return -1;

    rt->uri = uri;
    rt->versionMajor = major;
    rt->versionMinor = minor;
    rt->elementName = qml_name;

    return register_type(rt);
}


// Register an uncreatable library Python type.
int qpyqml_register_uncreatable_type(PyTypeObject *py_type, const char *uri,
        int major, int minor, const char *qml_name, const QString &reason,
        int revision)
{
    // Initialise the registration data structure.
    QQmlPrivate::RegisterType *rt = init_type(py_type, false, revision, 0);

    if (!rt)
        return -1;

    rt->noCreationReason = reason;
    rt->uri = uri;
    rt->versionMajor = major;
    rt->versionMinor = minor;
    rt->elementName = qml_name;

    return register_type(rt);
}


// Register the proxy type with QML.
static int register_type(QQmlPrivate::RegisterType *rt)
{
    int type_id = QQmlPrivate::qmlregister(QQmlPrivate::TypeRegistration, rt);

    if (type_id < 0)
    {
        PyErr_SetString(PyExc_RuntimeError,
                "unable to register type with QML");
        return -1;
    }

    return type_id;
}


#define QPYQML_TYPE_INIT(t, n) \
    case n##U: \
        QPyQml##t##n::staticMetaObject = *mo; \
        QPyQml##t##n::attachedPyType = attached; \
        rt->typeId = qRegisterNormalizedMetaType<QPyQml##t##n *>(ptr_name); \
        rt->listId = qRegisterNormalizedMetaType<QQmlListProperty<QPyQml##t##n> >(list_name); \
        rt->objectSize = ctor ? sizeof(QPyQml##t##n) : 0; \
        if (ctor) rt->create = QQmlPrivate::createInto<QPyQml##t##n>; else rt->create = 0; \
        rt->attachedPropertiesFunction = attached_mo ? QPyQml##t##n::attachedProperties : 0; \
        rt->parserStatusCast = is_parser_status ? QQmlPrivate::StaticCastSelector<QPyQml##t##n,QQmlParserStatus>::cast() : -1; \
        rt->valueSourceCast = is_value_source ? QQmlPrivate::StaticCastSelector<QPyQml##t##n,QQmlPropertyValueSource>::cast() : -1; \
        rt->valueInterceptorCast = QQmlPrivate::StaticCastSelector<QPyQml##t##n,QQmlPropertyValueInterceptor>::cast(); \
        break


// This is needed for GCC v4.6 and earlier.
#define QPYQML_TYPE_IMPL(t, n) \
    template void QQmlPrivate::createInto<QPyQml##t##n>(void *)


QPYQML_TYPE_IMPL(Validator, 0);
QPYQML_TYPE_IMPL(Validator, 1);
QPYQML_TYPE_IMPL(Validator, 2);
QPYQML_TYPE_IMPL(Validator, 3);
QPYQML_TYPE_IMPL(Validator, 4);
QPYQML_TYPE_IMPL(Validator, 5);
QPYQML_TYPE_IMPL(Validator, 6);
QPYQML_TYPE_IMPL(Validator, 7);
QPYQML_TYPE_IMPL(Validator, 8);
QPYQML_TYPE_IMPL(Validator, 9);

QPYQML_TYPE_IMPL(Object, 0);
QPYQML_TYPE_IMPL(Object, 1);
QPYQML_TYPE_IMPL(Object, 2);
QPYQML_TYPE_IMPL(Object, 3);
QPYQML_TYPE_IMPL(Object, 4);
QPYQML_TYPE_IMPL(Object, 5);
QPYQML_TYPE_IMPL(Object, 6);
QPYQML_TYPE_IMPL(Object, 7);
QPYQML_TYPE_IMPL(Object, 8);
QPYQML_TYPE_IMPL(Object, 9);
QPYQML_TYPE_IMPL(Object, 10);
QPYQML_TYPE_IMPL(Object, 11);
QPYQML_TYPE_IMPL(Object, 12);
QPYQML_TYPE_IMPL(Object, 13);
QPYQML_TYPE_IMPL(Object, 14);
QPYQML_TYPE_IMPL(Object, 15);
QPYQML_TYPE_IMPL(Object, 16);
QPYQML_TYPE_IMPL(Object, 17);
QPYQML_TYPE_IMPL(Object, 18);
QPYQML_TYPE_IMPL(Object, 19);
QPYQML_TYPE_IMPL(Object, 20);
QPYQML_TYPE_IMPL(Object, 21);
QPYQML_TYPE_IMPL(Object, 22);
QPYQML_TYPE_IMPL(Object, 23);
QPYQML_TYPE_IMPL(Object, 24);
QPYQML_TYPE_IMPL(Object, 25);
QPYQML_TYPE_IMPL(Object, 26);
QPYQML_TYPE_IMPL(Object, 27);
QPYQML_TYPE_IMPL(Object, 28);
QPYQML_TYPE_IMPL(Object, 29);
QPYQML_TYPE_IMPL(Object, 30);
QPYQML_TYPE_IMPL(Object, 31);
QPYQML_TYPE_IMPL(Object, 32);
QPYQML_TYPE_IMPL(Object, 33);
QPYQML_TYPE_IMPL(Object, 34);
QPYQML_TYPE_IMPL(Object, 35);
QPYQML_TYPE_IMPL(Object, 36);
QPYQML_TYPE_IMPL(Object, 37);
QPYQML_TYPE_IMPL(Object, 38);
QPYQML_TYPE_IMPL(Object, 39);
QPYQML_TYPE_IMPL(Object, 40);
QPYQML_TYPE_IMPL(Object, 41);
QPYQML_TYPE_IMPL(Object, 42);
QPYQML_TYPE_IMPL(Object, 43);
QPYQML_TYPE_IMPL(Object, 44);
QPYQML_TYPE_IMPL(Object, 45);
QPYQML_TYPE_IMPL(Object, 46);
QPYQML_TYPE_IMPL(Object, 47);
QPYQML_TYPE_IMPL(Object, 48);
QPYQML_TYPE_IMPL(Object, 49);
QPYQML_TYPE_IMPL(Object, 50);
QPYQML_TYPE_IMPL(Object, 51);
QPYQML_TYPE_IMPL(Object, 52);
QPYQML_TYPE_IMPL(Object, 53);
QPYQML_TYPE_IMPL(Object, 54);
QPYQML_TYPE_IMPL(Object, 55);
QPYQML_TYPE_IMPL(Object, 56);
QPYQML_TYPE_IMPL(Object, 57);
QPYQML_TYPE_IMPL(Object, 58);
QPYQML_TYPE_IMPL(Object, 59);


// Return a pointer to the initialised registration structure for a type.
static QQmlPrivate::RegisterType *init_type(PyTypeObject *py_type, bool ctor,
        int revision, PyTypeObject *attached)
{
    PyTypeObject *qobject_type = sipTypeAsPyTypeObject(sipType_QObject);

    // Check the type is derived from QObject and get its meta-object.
    if (!PyType_IsSubtype(py_type, qobject_type))
    {
        PyErr_SetString(PyExc_TypeError,
                "type being registered must be a sub-type of QObject");
        return 0;
    }

    const QMetaObject *mo = pyqt5_qtqml_get_qmetaobject(py_type);

    // See if the type is a parser status.
    bool is_parser_status = PyType_IsSubtype(py_type,
            sipTypeAsPyTypeObject(sipType_QQmlParserStatus));

    // See if the type is a property value source.
    bool is_value_source = PyType_IsSubtype(py_type,
            sipTypeAsPyTypeObject(sipType_QQmlPropertyValueSource));

    // Check any attached type is derived from QObject and get its meta-object.
    const QMetaObject *attached_mo;

    if (attached)
    {
        if (!PyType_IsSubtype(attached, qobject_type))
        {
            PyErr_SetString(PyExc_TypeError,
                    "attached properties type must be a sub-type of QObject");
            return 0;
        }

        attached_mo = pyqt5_qtqml_get_qmetaobject(attached);

        Py_INCREF((PyObject *)attached);
    }
    else
    {
        attached_mo = 0;
    }

    QByteArray ptr_name(sipPyTypeName(py_type));
    ptr_name.append('*');

    QByteArray list_name(sipPyTypeName(py_type));
    list_name.prepend("QQmlListProperty<");
    list_name.append('>');

    QQmlPrivate::RegisterType *rt;

    // See if we have the QQuickItem registation helper from the QtQuick
    // module.  Check each time because it could be imported at any point.

    typedef sipErrorState (*QQuickItemRegisterFn)(PyTypeObject *, const QMetaObject *, const QByteArray &, const QByteArray &, QQmlPrivate::RegisterType **);

    static QQuickItemRegisterFn qquickitem_register = 0;

    if (!qquickitem_register)
        qquickitem_register = (QQuickItemRegisterFn)sipImportSymbol(
                "qtquick_register_item");

    if (qquickitem_register)
    {
        sipErrorState estate = qquickitem_register(py_type, mo, ptr_name,
                list_name, &rt);

        if (estate == sipErrorFail)
            return 0;

        if (estate == sipErrorNone)
        {
            complete_init(rt, revision);
            return rt;
        }
    }

    // Initialise the specific type.

    static const sipTypeDef *qvalidator_td = 0;

    if (!qvalidator_td)
        qvalidator_td = sipFindType("QValidator");

    if (qvalidator_td && PyType_IsSubtype(py_type, sipTypeAsPyTypeObject(qvalidator_td)))
    {
        int type_nr = QPyQmlValidatorProxy::addType(py_type);

        if (type_nr >= NrOfQValidatorTypes)
        {
            PyErr_Format(PyExc_TypeError,
                    "a maximum of %d QValidator types may be registered with QML",
                    NrOfQValidatorTypes);
            return 0;
        }

        rt = &validator_proxy_types[type_nr];

        // Initialise those members that depend on the C++ type.
        switch (type_nr)
        {
            QPYQML_TYPE_INIT(Validator, 0);
            QPYQML_TYPE_INIT(Validator, 1);
            QPYQML_TYPE_INIT(Validator, 2);
            QPYQML_TYPE_INIT(Validator, 3);
            QPYQML_TYPE_INIT(Validator, 4);
            QPYQML_TYPE_INIT(Validator, 5);
            QPYQML_TYPE_INIT(Validator, 6);
            QPYQML_TYPE_INIT(Validator, 7);
            QPYQML_TYPE_INIT(Validator, 8);
            QPYQML_TYPE_INIT(Validator, 9);
        }
    }
    else
    {
        int type_nr = QPyQmlObjectProxy::addType(py_type);

        if (type_nr >= NrOfQObjectTypes)
        {
            PyErr_Format(PyExc_TypeError,
                    "a maximum of %d types may be registered with QML",
                    NrOfQObjectTypes);
            return 0;
        }

        rt = &object_proxy_types[type_nr];

        // Initialise those members that depend on the C++ type.
        switch (type_nr)
        {
            QPYQML_TYPE_INIT(Object, 0);
            QPYQML_TYPE_INIT(Object, 1);
            QPYQML_TYPE_INIT(Object, 2);
            QPYQML_TYPE_INIT(Object, 3);
            QPYQML_TYPE_INIT(Object, 4);
            QPYQML_TYPE_INIT(Object, 5);
            QPYQML_TYPE_INIT(Object, 6);
            QPYQML_TYPE_INIT(Object, 7);
            QPYQML_TYPE_INIT(Object, 8);
            QPYQML_TYPE_INIT(Object, 9);
            QPYQML_TYPE_INIT(Object, 10);
            QPYQML_TYPE_INIT(Object, 11);
            QPYQML_TYPE_INIT(Object, 12);
            QPYQML_TYPE_INIT(Object, 13);
            QPYQML_TYPE_INIT(Object, 14);
            QPYQML_TYPE_INIT(Object, 15);
            QPYQML_TYPE_INIT(Object, 16);
            QPYQML_TYPE_INIT(Object, 17);
            QPYQML_TYPE_INIT(Object, 18);
            QPYQML_TYPE_INIT(Object, 19);
            QPYQML_TYPE_INIT(Object, 20);
            QPYQML_TYPE_INIT(Object, 21);
            QPYQML_TYPE_INIT(Object, 22);
            QPYQML_TYPE_INIT(Object, 23);
            QPYQML_TYPE_INIT(Object, 24);
            QPYQML_TYPE_INIT(Object, 25);
            QPYQML_TYPE_INIT(Object, 26);
            QPYQML_TYPE_INIT(Object, 27);
            QPYQML_TYPE_INIT(Object, 28);
            QPYQML_TYPE_INIT(Object, 29);
            QPYQML_TYPE_INIT(Object, 30);
            QPYQML_TYPE_INIT(Object, 31);
            QPYQML_TYPE_INIT(Object, 32);
            QPYQML_TYPE_INIT(Object, 33);
            QPYQML_TYPE_INIT(Object, 34);
            QPYQML_TYPE_INIT(Object, 35);
            QPYQML_TYPE_INIT(Object, 36);
            QPYQML_TYPE_INIT(Object, 37);
            QPYQML_TYPE_INIT(Object, 38);
            QPYQML_TYPE_INIT(Object, 39);
            QPYQML_TYPE_INIT(Object, 40);
            QPYQML_TYPE_INIT(Object, 41);
            QPYQML_TYPE_INIT(Object, 42);
            QPYQML_TYPE_INIT(Object, 43);
            QPYQML_TYPE_INIT(Object, 44);
            QPYQML_TYPE_INIT(Object, 45);
            QPYQML_TYPE_INIT(Object, 46);
            QPYQML_TYPE_INIT(Object, 47);
            QPYQML_TYPE_INIT(Object, 48);
            QPYQML_TYPE_INIT(Object, 49);
            QPYQML_TYPE_INIT(Object, 50);
            QPYQML_TYPE_INIT(Object, 51);
            QPYQML_TYPE_INIT(Object, 52);
            QPYQML_TYPE_INIT(Object, 53);
            QPYQML_TYPE_INIT(Object, 54);
            QPYQML_TYPE_INIT(Object, 55);
            QPYQML_TYPE_INIT(Object, 56);
            QPYQML_TYPE_INIT(Object, 57);
            QPYQML_TYPE_INIT(Object, 58);
            QPYQML_TYPE_INIT(Object, 59);
        }
    }

    rt->metaObject = mo;
    rt->attachedPropertiesMetaObject = attached_mo;

    complete_init(rt, revision);

    return rt;
}


// Complete the initialisation of a type registration structure.
static void complete_init(QQmlPrivate::RegisterType *rt, int revision)
{
    if (revision < 0)
    {
        rt->version = 0;
        rt->revision = 0;
    }
    else
    {
        rt->version = 1;
        rt->revision = revision;
    }

    rt->uri = 0;
    rt->versionMajor = 0;
    rt->versionMinor = 0;
    rt->elementName = 0;
    rt->extensionObjectCreate = 0;
    rt->extensionMetaObject = 0;
    rt->customParser = 0;
}


// Return the proxy that created an object.  This is called with the GIL.
QObject *qpyqml_find_proxy_for(QObject *proxied)
{
    QSetIterator<QObject *> oit(QPyQmlObjectProxy::proxies);

    while (oit.hasNext())
    {
        QPyQmlObjectProxy *proxy = static_cast<QPyQmlObjectProxy *>(oit.next());

        if (proxy->proxied.data() == proxied)
            return proxy;
    }

    QSetIterator<QObject *> vit(QPyQmlValidatorProxy::proxies);

    while (vit.hasNext())
    {
        QPyQmlValidatorProxy *proxy = static_cast<QPyQmlValidatorProxy *>(vit.next());

        if (proxy->proxied.data() == proxied)
            return proxy;
    }

    PyErr_Format(PyExc_TypeError,
            "QObject instance at %p was not created from QML", proxied);

    return 0;
}
