#pragma once
#include <Python.h>
#include <math.h>
#include "net_range.h"
#include "net_range_container.h"


#if PY_VERSION_HEX < 0x03100000
    #define Py_Is(x, y) ((x) == (y))
    #define Py_IsTrue(x) Py_Is((x), Py_True)
#endif

#if PY_VERSION_HEX < 0x03130000
    #define PyLong_FromUnsignedNativeBytes(buffer, n_bytes, flags) (_PyLong_FromByteArray(buffer, n_bytes, PY_LITTLE_ENDIAN, 0))
#endif


typedef struct {
    PyObject_HEAD
    NetRangeContainer *netsContainer;
} IPSet;


typedef struct {
    long version;
    Py_ssize_t len;
    NetRangeObject data[];
} IPSetPickle;


PyMODINIT_FUNC PyInit_ipset_c_ext(void);
