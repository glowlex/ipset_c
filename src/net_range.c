#include "net_range.h"


NetRangeObject*
NetRangeObject_create(void) {
    return PyMem_Malloc(sizeof(NetRangeObject));
}


NetRangeObject*
NetRangeObject_copy(NetRangeObject* self) {
    NetRangeObject *newItem = NetRangeObject_create();
    memcpy(newItem, self, sizeof(*newItem));
    return newItem;
}


int
NetRangeObject_parseCidr(const wchar_t *cidr, NetRangeObject *netObj) {
    PY_UINT32_T buf[4] = {0}, len=32;
    if (swscanf_s(cidr, L"%u.%u.%u.%u/%u", &buf[0], &buf[1], &buf[2], &buf[3], &len) < 4) {
        return -1;
    }
    if (len > 32) {
        return -1;
    }
    for (Py_ssize_t i = 0; i < 4; i++) {
        if (buf[i] > 255) {
            return -1;
        }
    }
    netObj->first =
        (buf[0] << 24) |
        (buf[1] << 16) |
        (buf[2] << 8) |
        (buf[3]);
    netObj->len = len;
    PY_UINT32_T mask = MASK_MAP[len];
    netObj->first &= mask;
    netObj->last = netObj->first | ~mask;
    return 0;
}


void
NetRangeObject_destroy(NetRangeObject* self) {
    PyMem_Free(self);
}


int
NetRangeObject_comparator(const NetRangeObject** const elem1, const NetRangeObject** const elem2) {
    if ((*elem1)->first > (*elem2)->first) {
        return 1;
    } 
    if ((*elem1)->first < (*elem2)->first) {
        return -1;
    } 
    return 0;
}


int
NetRangeObject_asWideCharCidr(NetRangeObject* const self, wchar_t* const str, const Py_ssize_t size) {
    PY_UINT32_T buf[4];
    PY_UINT32_T addr = self->first;
    for(Py_ssize_t i=3; i >= 0; i--) {
        buf[i] = addr & UINT8_MAX;
        addr >>= 8;
    }
    return swprintf_s(str, size, L"%u.%u.%u.%u/%u", buf[0], buf[1], buf[2], buf[3], self->len);
}
