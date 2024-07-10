#pragma once
#include <Python.h>
#include <math.h>
#include "net_range_container.h"

#if PY_VERSION_HEX < 0x03100000
    #define PyModule_AddObjectRef PyModule_AddObject
    #define Py_Is(x, y) ((x) == (y))
    #define Py_IsTrue(x) Py_Is((x), Py_True)
    static inline PyObject* __Py_NewRef(PyObject* obj) {
        Py_INCREF(obj);
        return obj;
    }
    #define Py_NewRef(obj) __Py_NewRef(_PyObject_CAST(obj))
#endif


typedef struct {
    PyObject_HEAD
    NetRangeContainer *netsContainer;
} IPSet;

PyMODINIT_FUNC PyInit_ipset_c_ext(void);
