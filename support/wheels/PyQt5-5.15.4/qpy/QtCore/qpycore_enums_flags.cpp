// This contains the implementation of the Q_ENUM, Q_ENUMS, Q_FLAG and Q_FLAGS
// support.
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

#include <QMultiHash>

#include "qpycore_chimera.h"
#include "qpycore_enums_flags.h"

#include "sipAPIQtCore.h"


// Forward declarations.
static bool add_enum_flag(PyObject *arg, bool flag, const char *context,
        struct _frame *frame);
static void add_key_value(EnumFlag &enum_flag, PyObject *key, PyObject *value);
static struct _frame *get_calling_frame();
static bool objectify(const char *s, PyObject **objp);
static PyObject *parse_enum_flag(PyObject *arg, bool flag,
        const char *context);
static PyObject *parse_enums_flags(PyObject *args, bool flags,
        const char *context);
static bool trawl_members(PyObject *members, EnumFlag &enum_flag);
static void trawl_type_dict(PyObject *arg, EnumFlag &enum_flag);


// The enums and flags defined in each frame.
static QMultiHash<const struct _frame *, EnumFlag> enums_flags_hash;


// Add the given Q_ENUM() argument to the current enums/flags hash.
PyObject *qpycore_Enum(PyObject *arg)
{
    return parse_enum_flag(arg, false, "Q_ENUM");
}


// Add the given Q_ENUMS() arguments to the current enums/flags hash.
PyObject *qpycore_Enums(PyObject *args)
{
    return parse_enums_flags(args, false, "Q_ENUMS");
}


// Add the given Q_FLAG() arguments to the current enums/flags hash.
PyObject *qpycore_Flag(PyObject *arg)
{
    return parse_enum_flag(arg, true, "Q_FLAG");
}


// Add the given Q_FLAGS() arguments to the current enums/flags hash.
PyObject *qpycore_Flags(PyObject *args)
{
    return parse_enums_flags(args, true, "Q_FLAGS");
}


// Return the calling frame.
static struct _frame *get_calling_frame()
{
    struct _frame *frame = sipGetFrame(1);

    if (!frame)
    {
        PyErr_SetString(PyExc_RuntimeError, "no previous frame");
        return 0;
    }

    return frame;
}


// Add the given Q_ENUM() or Q_FLAG() argument to the current enums/flags hash.
static PyObject *parse_enum_flag(PyObject *arg, bool flag, const char *context)
{
#if defined(PYPY_VERSION)
    PyErr_Format(PyExc_AttributeError, "%s is not supported on PyPy", context);
    return 0;
#else
    struct _frame *frame = get_calling_frame();

    if (!frame)
        return 0;

    if (!add_enum_flag(arg, flag, context, frame))
        return 0;

    Py_INCREF(Py_None);
    return Py_None;
#endif
}


// Add the given Q_ENUMS() or Q_FLAGS() arguments to the current enums/flags
// hash.
static PyObject *parse_enums_flags(PyObject *args, bool flags,
        const char *context)
{
#if defined(PYPY_VERSION)
    PyErr_Format(PyExc_AttributeError, "%s is not supported on PyPy", context);
    return 0;
#else
    struct _frame *frame = get_calling_frame();

    if (!frame)
        return 0;

    // Each argument is a separate enum/flag.
    for (Py_ssize_t i = 0; i < PyTuple_Size(args); ++i)
    {
        PyObject *arg = PyTuple_GetItem(args, i);

        if (!add_enum_flag(arg, flags, context, frame))
            return 0;
    }

    Py_INCREF(Py_None);
    return Py_None;
#endif
}


// Add the given enum/flag to the current hash.  Return true if successfull.
static bool add_enum_flag(PyObject *arg, bool flag, const char *context,
        struct _frame *frame)
{
    // Check the argument's type is type.  This will also pass Enums.
    if (!PyType_Check(arg))
    {
        PyErr_Format(PyExc_TypeError,
                "arguments to %s() must be type or enum.Enum objects",
                context);

        return false;
    }

    // Create the basic enum/flag.
    EnumFlag enum_flag(sipPyTypeName((PyTypeObject *)arg), flag);

    // See if it an Enum.  We assume it is if it has a __members__ attribute.
    static PyObject *members_s = 0;

    if (!objectify("__members__", &members_s))
        return false;

    PyObject *members = PyObject_GetAttr(arg, members_s);

    if (members)
    {
        bool ok = trawl_members(members, enum_flag);

        Py_DECREF(members);

        if (!ok)
            return false;

        enum_flag.isScoped = true;
    }
    else
    {
        trawl_type_dict(arg, enum_flag);
    }

    enums_flags_hash.insert(frame, enum_flag);

    Chimera::registerPyEnum(arg);

    // Make sure there are no exceptions left after failed value conversions.
    PyErr_Clear();

    return true;
}


// Trawl a __members__ mapping for int keys.
static bool trawl_members(PyObject *members, EnumFlag &enum_flag)
{
    static PyObject *value_s = 0;

    if (!objectify("value", &value_s))
        return false;

    PyObject *items;
    Py_ssize_t nr_items;

    // Get the contents of __members__.
#if PY_MAJOR_VERSION >= 3
    items = PyMapping_Items(members);
#else
    // Python v2 implements PyMapping_Items() as a macro that expands to the
    // following - but without the const_cast.  It isn't a problem for the
    // version of MSVC supported by Python v2 but the const_cast is needed by
    // later versions of MSVC and people will want to use them even though they
    // are not supported.
    items = PyObject_CallMethod(members, const_cast<char *>("items"), NULL);
#endif

    if (!items)
        goto return_error;

    nr_items = PySequence_Length(items);
    if (nr_items < 0)
        goto release_items;

    for (Py_ssize_t i = 0; i < nr_items; ++i)
    {
        PyObject *item, *key, *member, *value;

        item = PySequence_GetItem(items, i);
        if (!item)
            goto release_items;

        // The item should be a 2-element sequence of the key name and an
        // object containing the value.
        key = PySequence_GetItem(item, 0);
        member = PySequence_GetItem(item, 1);

        Py_DECREF(item);

        if (!key || !member)
        {
            Py_XDECREF(key);
            Py_XDECREF(member);

            goto release_items;
        }

        // Get the value.
        value = PyObject_GetAttr(member, value_s);

        Py_DECREF(member);

        if (!value)
        {
            Py_DECREF(key);

            goto release_items;
        }

        add_key_value(enum_flag, key, value);

        Py_DECREF(key);
        Py_DECREF(value);
    }

    Py_DECREF(items);

    return true;

release_items:
    Py_DECREF(items);

return_error:
    return false;
}


// Trawl the dictionary of a type looking for int attributes.
static void trawl_type_dict(PyObject *arg, EnumFlag &enum_flag)
{
    Py_ssize_t pos = 0;
    PyObject *key, *value, *dict;

    dict = sipPyTypeDict((PyTypeObject *)arg);

    while (PyDict_Next(dict, &pos, &key, &value))
        add_key_value(enum_flag, key, value);
}


// Add a key/value to an enum/flag.
static void add_key_value(EnumFlag &enum_flag, PyObject *key, PyObject *value)
{
    PyErr_Clear();

    int i_value = sipLong_AsInt(value);

    if (!PyErr_Occurred())
    {
        const char *s_key = sipString_AsASCIIString(&key);

        if (s_key)
        {
            enum_flag.keys.insert(s_key, i_value);
            Py_DECREF(key);
        }
    }
}


// Convert an ASCII string to a Python object if it hasn't already been done.
static bool objectify(const char *s, PyObject **objp)
{
    if (*objp == NULL)
    {
#if PY_MAJOR_VERSION >= 3
        *objp = PyUnicode_FromString(s);
#else
        *objp = PyString_FromString(s);
#endif

        if (*objp == NULL)
            return false;
    }

    return true;
}


// Return the current enums/flags list.
QList<EnumFlag> qpycore_get_enums_flags_list()
{
    QList<EnumFlag> enums_flags_list;

#if !defined(PYPY_VERSION)
    struct _frame *frame = sipGetFrame(0);

    enums_flags_list = enums_flags_hash.values(frame);
    enums_flags_hash.remove(frame);
#endif

    return enums_flags_list;
}
