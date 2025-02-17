#include "ipset_c.h"

static PyTypeObject IPSetType;
static NetRangeObject* getNetRangeFromPy(PyObject* cidr);


#define IPSET_TYPE_CHECK(ipset) \
do { \
    if (!PyType_IsSubtype(Py_TYPE(ipset), &IPSetType)) {\
        PyErr_Format(PyExc_TypeError, "arg must be an IPSet type");\
        return NULL;\
    }\
} while(0)


static void
IPSet_dealloc(IPSet *self)
{
    NetRangeContainer_destroy(self->netsContainer);
    Py_TYPE(self)->tp_free((PyObject *) self);
}


static PyObject*
IPSet_new(PyTypeObject* type, PyObject* args, PyObject* kw)
{
    IPSet* self = (IPSet*)type->tp_alloc(type, 0);
    if (self != NULL) {
        self->netsContainer = NULL;
    }
    return (PyObject*)self;
}


static int
IPSet_init(IPSet *self, PyObject *args)
{
    PyObject *nets = NULL;
    if (!PyArg_ParseTuple(args, "O", &nets)) {
        return -1;
    }

    static char errMes[] = "cidrs must be a list or tuple";
    PyObject *it = PySequence_Fast(nets, errMes);
    // string also valid
    if (it == NULL){
        return -1;
    }

    PyObject *prefix = NULL;
    const Py_ssize_t len = PySequence_Fast_GET_SIZE(it);
    self->netsContainer = NetRangeContainer_create(len);
    if (self->netsContainer == NULL) {
        goto error;
    }
    for (Py_ssize_t i = 0; i < len; i++) {
        prefix = PySequence_Fast_GET_ITEM(it, i);
        NetRangeObject* netRange = getNetRangeFromPy(prefix);
        if (netRange == NULL) {
            goto error;
        }
        self->netsContainer->array[i] = netRange;
        self->netsContainer->len++;
    }
    Py_DECREF(it);
    NetRangeContainer_merge(self->netsContainer);
    return 0;
error:
    Py_DECREF(it);
    NetRangeContainer_destroy(self->netsContainer);
    self->netsContainer = NULL;
    return -1;
}


static NetRangeObject*
getNetRangeFromPy(PyObject* cidr) {
    if (!PyUnicode_Check(cidr)) {
        PyErr_Format(PyExc_TypeError, "cidr must be a string");
        return NULL;
    }
    const char* cidrUtf8 = PyUnicode_AsUTF8(cidr);
    if (cidrUtf8 == NULL) {
        return NULL;
    }
    NetRangeObject* netRange = NetRangeObject_create();
    if (netRange == NULL) {
        return NULL;
    }
    int code = NetRangeObject_parseCidr(netRange, cidrUtf8);
    if (code) {
        PyErr_Format(PyExc_ValueError, "%s is not a valid cidr", cidrUtf8);
        goto error;
    }
    return netRange;
error:
    NetRangeObject_destroy(netRange);
    return NULL;
}


static PyObject*
IPSet_getCidrs(IPSet *self) {
    PyObject* resList = PyList_New(self->netsContainer->len);
    char const prefix[IPV6_MAX_STRING_LEN] = "";
    const NetRangeObject** const netsArray = self->netsContainer->array;
    for (Py_ssize_t i = 0; i < self->netsContainer->len; i++) {
        NetRangeObject_asUtf8CharCidr((NetRangeObject*)netsArray[i], prefix, IPV6_MAX_STRING_LEN);
        PyList_SetItem(resList, i, PyUnicode_FromString(prefix));
    }
    return resList;
}


static PyObject*
IPSet_isContainsCidr(IPSet *self, PyObject* cidr) {
    NetRangeObject* netRange = getNetRangeFromPy(cidr);
    if (netRange == NULL) {
        return NULL;
    }
    const Py_ssize_t res = NetRangeContainer_findNetRangeContainsIndex(self->netsContainer, netRange);
    NetRangeObject_destroy(netRange);
    return PyBool_FromLong(res >= 0);
}

static PyObject*
IPSet_isIntersectsCidr(IPSet* self, PyObject* cidr) {
    NetRangeObject* netRange = getNetRangeFromPy(cidr);
    if (netRange == NULL) {
        return NULL;
    }
    const Py_ssize_t res = NetRangeContainer_findNetRangeIntersectsIndex(self->netsContainer, netRange);
    NetRangeObject_destroy(netRange);
    return PyBool_FromLong(res >= 0);
}


static PyObject*
IPSet_isSuperset(IPSet *self, IPSet *other) {
    IPSET_TYPE_CHECK(other);
    if (NetRangeContainer_isSuperset(self->netsContainer, other->netsContainer)) {
        Py_RETURN_TRUE;
    }
    Py_RETURN_FALSE;
}


static PyObject*
IPSet_isSubset(IPSet* self, IPSet* other) {
    IPSET_TYPE_CHECK(other);
    if (NetRangeContainer_isSuperset(other->netsContainer, self->netsContainer)) {
        Py_RETURN_TRUE;
    }
    Py_RETURN_FALSE;
}


static PyObject*
IPSet_addCidr(IPSet* self, PyObject* cidr) {
    NetRangeObject* netRange = getNetRangeFromPy(cidr);
    if (netRange == NULL) {
        return NULL;
    }
    NetRangeContainer_addNetRange(self->netsContainer, netRange);
    Py_RETURN_NONE;
}


static PyObject*
IPSet_removeCidr(IPSet* self, PyObject* cidr) {
    NetRangeObject* netRange = getNetRangeFromPy(cidr);
    if (netRange == NULL) {
        return NULL;
    }
    NetRangeContainer_removeNetRange(self->netsContainer, netRange);
    NetRangeObject_destroy(netRange);
    Py_RETURN_NONE;
}


static IPSet*
createIPSet() {
    PyObject* args = PyTuple_New(1);
    PyTuple_SET_ITEM(args, 0, PyTuple_New(0));
    IPSet* res = (IPSet*)PyObject_CallObject((PyObject*)&IPSetType, args);
    Py_DECREF(args);
    return res;
}


static IPSet*
IPSet_copy(IPSet* self) {
    IPSet* res = createIPSet();
    if (res == NULL) {
        goto exit;
    }
    NetRangeContainer_destroy(res->netsContainer);
    res->netsContainer = NetRangeContainer_copy(self->netsContainer);
    if (res->netsContainer == NULL) {
        Py_XDECREF(res);
        goto exit;
    }
exit:
    return res;
}


static IPSet*
IPSet__or__(IPSet* self, IPSet* other) {
    IPSET_TYPE_CHECK(other);
    if (self->netsContainer->len < other->netsContainer->len) {
        IPSet* tmp = self;
        self = other;
        self = tmp;
    }
    IPSet* res = IPSet_copy(self);
    if (res == NULL) {
        return res;
    }
    for (Py_ssize_t i = 0; i < other->netsContainer->len; i++) {
        NetRangeContainer_addNetRange(res->netsContainer, NetRangeObject_copy(other->netsContainer->array[i]));
    }
    return res;
}


static IPSet*
IPSet__subtract__(IPSet* self, IPSet* other) {
    IPSET_TYPE_CHECK(other);
    IPSet* res = IPSet_copy(self);
    if (res == NULL) {
        goto exit;
    }
    for (Py_ssize_t i = 0; i < other->netsContainer->len; i++) {
        NetRangeContainer_removeNetRange(res->netsContainer, other->netsContainer->array[i]);
    }
exit:
    return res;
}


static IPSet*
IPSet__and__(IPSet* self, IPSet* other) {
    IPSET_TYPE_CHECK(other);
    NetRangeContainer* cont = NetRangeContainer_intersection(self->netsContainer, other->netsContainer);
    IPSet* res = createIPSet();
    if (res == NULL) {
        return NULL;
    }
    NetRangeContainer_destroy(res->netsContainer);
    res->netsContainer = cont;
    return res;
}


static PyObject*
IPSet__eq__(IPSet* self, IPSet* other) {
    IPSET_TYPE_CHECK(other);
    if (self->netsContainer->len != other->netsContainer->len) {
        Py_RETURN_FALSE;
    }
    for (Py_ssize_t i = 0; i < self->netsContainer->len; i++) {
        NetRangeObject* a = self->netsContainer->array[i], *b = other->netsContainer->array[i];
        if (!EQ128(a->first, b->first) || a->len != b->len) {
            Py_RETURN_FALSE;
        }
    }
    Py_RETURN_TRUE;
}


static PyObject*
IPSet__neq__(IPSet* self, IPSet* other) {
    PyObject* res = IPSet__eq__(self, other);
    if (Py_IsTrue(res)) {
        Py_DECREF(res);
        Py_RETURN_FALSE;
    }
    Py_DECREF(res);
    Py_RETURN_TRUE;
}


static PyObject* 
IPSet_tp_richcompare(IPSet* self, IPSet* other, int op) {
    switch (op) {
    case(Py_GE):
        return IPSet_isSuperset(self, other);
    case(Py_LE):
        return IPSet_isSubset(self, other);
    case(Py_EQ):
        return IPSet__eq__(self, other);
    case(Py_NE):
        return IPSet__neq__(self, other);
    default:
        Py_RETURN_NOTIMPLEMENTED;
    }
}


static int
IPSet__bool__(IPSet* self) {
    return self->netsContainer->len > 0;
}


static PyObject*
IPSet_size(IPSet* self) {
    NetRangeObject** array = self->netsContainer->array;
    if (self->netsContainer->len == 1 && array[0]->len == 0 && array[0]->isIPv6) {
        PyObject* one = PyLong_FromLong(1L);
        PyObject* shift128 = PyLong_FromLong(128L);
        PyObject* resObj = PyNumber_Lshift(one, shift128);
        Py_DECREF(shift128);
        Py_DECREF(one);
        return resObj;
    }
    uint128c res = {.hi=0, .lo=0};
    for (Py_ssize_t i = 0; i < self->netsContainer->len; i++) {
        PY_UINT32_T lenShift = ((array[i]->isIPv6 ? 128:32) - array[i]->len);
        uint128c localLen = {.hi=0, .lo=0};
        if (lenShift >= 64) {
            localLen.hi = (PY_UINT64_T)0b1 << (lenShift - 64);
        } else {
            localLen.lo = (PY_UINT64_T)0b1 << lenShift;
        }
        res = ADD128(res, localLen);
    }
    return PyLong_FromUnsignedNativeBytes((const unsigned char *)&res, 16, -1);
}


// static PyMemberDef IPSet_members[] = {
//     {NULL}
// };


static PyNumberMethods IPSet_tp_as_number = {
    .nb_or = (binaryfunc)IPSet__or__,
    .nb_add = (binaryfunc)IPSet__or__,
    .nb_subtract = (binaryfunc)IPSet__subtract__,
    .nb_and = (binaryfunc)IPSet__and__,
    .nb_bool = (inquiry)IPSet__bool__,
};


// static PySequenceMethods IPSet_tp_as_sequence = {
// };


static PyMethodDef IPSet_tp_methods[] = {
    { "getCidrs", (PyCFunction)IPSet_getCidrs, METH_NOARGS, NULL },
    { "isContainsCidr", (PyCFunction)IPSet_isContainsCidr, METH_O, NULL },
    { "isIntersectsCidr", (PyCFunction)IPSet_isIntersectsCidr, METH_O, NULL },
    { "isSuperset", (PyCFunction)IPSet_isSuperset, METH_O, NULL },
    { "isSubset", (PyCFunction)IPSet_isSubset, METH_O, NULL },
    { "addCidr", (PyCFunction)IPSet_addCidr, METH_O, NULL },
    { "removeCidr", (PyCFunction)IPSet_removeCidr, METH_O, NULL },
    { "copy", (PyCFunction)IPSet_copy, METH_NOARGS, NULL },
    {NULL}
};


static PyGetSetDef IPSet_tp_descr_getset[] = {
    { "size", (getter)IPSet_size, NULL, NULL},
    {NULL}
};


static PyTypeObject IPSetType = {
    PyVarObject_HEAD_INIT(NULL, 0)
    .tp_name = "ipset_c_ext.IPSet",
    .tp_doc = "IPSet objects",
    .tp_basicsize = sizeof(IPSet),
    .tp_itemsize = 0,
    .tp_flags = Py_TPFLAGS_DEFAULT | Py_TPFLAGS_BASETYPE,
    .tp_new = (newfunc)IPSet_new,
    .tp_init = (initproc)IPSet_init,
    .tp_dealloc = (destructor)IPSet_dealloc,
    .tp_as_number = &IPSet_tp_as_number,
    //.tp_as_sequence = &IPSet_tp_as_sequence,
    //.tp_members = IPSet_members,
    .tp_methods = IPSet_tp_methods,
    .tp_richcompare = (richcmpfunc)IPSet_tp_richcompare,
    .tp_getset = IPSet_tp_descr_getset,
};


static PyModuleDef IPSet_module = {
    .m_base = PyModuleDef_HEAD_INIT,
    .m_name = "ipset_c_ext",
    .m_doc = "ipset_c",
    .m_size = -1,
};


PyMODINIT_FUNC
PyInit_ipset_c_ext(void)
{
    PyObject *m = NULL;
    if (PyType_Ready(&IPSetType) < 0){
        return NULL;
    }
    if ((m = PyModule_Create(&IPSet_module)) == NULL) {
        return NULL;
    }

    Py_INCREF(&IPSetType);
    if (PyModule_AddObject(m, "IPSet", &IPSetType) < 0) {
        Py_DECREF(m);
        return NULL;
    }
    #ifdef Py_GIL_DISABLED
        PyUnstable_Module_SetGIL(m, Py_MOD_GIL_NOT_USED);
    #endif
    return m;
}
