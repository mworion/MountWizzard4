// This is the definition of the QPyQuickView classes.
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


#ifndef _QPYQUICKVIEW_H
#define _QPYQUICKVIEW_H


#include <Python.h>

#include <qqmlprivate.h>
#include <QByteArray>
#include <QMetaObject>
#include <QQuickView>

#include "sipAPIQtQuick.h"


class QPyQuickView : public sipQQuickView
{
public:
    QPyQuickView(QWindow *parent = 0);

    virtual int typeNr() const = 0;

    static QQmlPrivate::RegisterType *addType(PyTypeObject *type,
            const QMetaObject *mo, const QByteArray &ptr_name,
            const QByteArray &list_name);
    void createPyObject(QWindow *parent);

private:
    QPyQuickView(const QPyQuickView &);
};


// The canned type declarations.
#define QPYQUICKVIEW_DECL(n) \
class QPyQuickView##n : public QPyQuickView \
{ \
public: \
    QPyQuickView##n(QWindow *parent = 0); \
    static QMetaObject staticMetaObject; \
    virtual const QMetaObject *metaObject() const; \
    virtual int typeNr() const {return n##U;} \
private: \
    QPyQuickView##n(const QPyQuickView##n &); \
}


QPYQUICKVIEW_DECL(0);
QPYQUICKVIEW_DECL(1);
QPYQUICKVIEW_DECL(2);
QPYQUICKVIEW_DECL(3);
QPYQUICKVIEW_DECL(4);
QPYQUICKVIEW_DECL(5);
QPYQUICKVIEW_DECL(6);
QPYQUICKVIEW_DECL(7);
QPYQUICKVIEW_DECL(8);
QPYQUICKVIEW_DECL(9);
QPYQUICKVIEW_DECL(10);
QPYQUICKVIEW_DECL(11);
QPYQUICKVIEW_DECL(12);
QPYQUICKVIEW_DECL(13);
QPYQUICKVIEW_DECL(14);
QPYQUICKVIEW_DECL(15);
QPYQUICKVIEW_DECL(16);
QPYQUICKVIEW_DECL(17);
QPYQUICKVIEW_DECL(18);
QPYQUICKVIEW_DECL(19);


#endif
