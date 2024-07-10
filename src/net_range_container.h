#pragma once
#include <Python.h>
#include "net_range.h"

#if !(defined(_WIN32) || defined(__CYGWIN__))
    #include <sys/param.h>
    #define max MAX
    #define min MIN
#endif


typedef struct {
    NetRangeObject **array;
    Py_ssize_t allocatedLen;
    Py_ssize_t len;
} NetRangeContainer;

NetRangeContainer* NetRangeContainer_create(const Py_ssize_t nelem);

void NetRangeContainer_destroy(NetRangeContainer *const self);

void NetRangeContainer_merge(NetRangeContainer *const self);

Py_ssize_t NetRangeContainer_findNetRangeContainsIndex(const NetRangeContainer *const self, const NetRangeObject *const item);

Py_ssize_t NetRangeContainer_findNetRangeIntersectsIndex(const NetRangeContainer *const self, const NetRangeObject *const item);

int NetRangeContainer_isSuperset(const NetRangeContainer *const self, const NetRangeContainer *const other);

int NetRangeContainer_addNetRange(NetRangeContainer* const self, NetRangeObject* item);

int NetRangeContainer_removeNetRange(NetRangeContainer* const self, const NetRangeObject* item);

NetRangeContainer* NetRangeContainer_copy(NetRangeContainer* self);

NetRangeContainer* NetRangeContainer_intersection(const NetRangeContainer* self, const NetRangeContainer* other);
