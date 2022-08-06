// This is the definition of the QPyQuickWindow classes.
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


#ifndef _QPYQUICKWINDOW_H
#define _QPYQUICKWINDOW_H


#include <Python.h>

#include <qqmlprivate.h>
#include <QByteArray>
#include <QMetaObject>
#include <QQuickWindow>

#include "sipAPIQtQuick.h"


class QPyQuickWindow : public sipQQuickWindow
{
public:
    QPyQuickWindow(QWindow *parent = 0);

    virtual int typeNr() const = 0;

    static QQmlPrivate::RegisterType *addType(PyTypeObject *type,
            const QMetaObject *mo, const QByteArray &ptr_name,
            const QByteArray &list_name);
    void createPyObject(QWindow *parent);

private:
    QPyQuickWindow(const QPyQuickWindow &);
};


// The canned type declarations.
#define QPYQUICKWINDOW_DECL(n) \
class QPyQuickWindow##n : public QPyQuickWindow \
{ \
public: \
    QPyQuickWindow##n(QWindow *parent = 0); \
    static QMetaObject staticMetaObject; \
    virtual const QMetaObject *metaObject() const; \
    virtual int typeNr() const {return n##U;} \
private: \
    QPyQuickWindow##n(const QPyQuickWindow##n &); \
}


QPYQUICKWINDOW_DECL(0);
QPYQUICKWINDOW_DECL(1);
QPYQUICKWINDOW_DECL(2);
QPYQUICKWINDOW_DECL(3);
QPYQUICKWINDOW_DECL(4);
QPYQUICKWINDOW_DECL(5);
QPYQUICKWINDOW_DECL(6);
QPYQUICKWINDOW_DECL(7);
QPYQUICKWINDOW_DECL(8);
QPYQUICKWINDOW_DECL(9);
QPYQUICKWINDOW_DECL(10);
QPYQUICKWINDOW_DECL(11);
QPYQUICKWINDOW_DECL(12);
QPYQUICKWINDOW_DECL(13);
QPYQUICKWINDOW_DECL(14);
QPYQUICKWINDOW_DECL(15);
QPYQUICKWINDOW_DECL(16);
QPYQUICKWINDOW_DECL(17);
QPYQUICKWINDOW_DECL(18);
QPYQUICKWINDOW_DECL(19);


#endif
