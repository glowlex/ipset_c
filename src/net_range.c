#include "net_range.h"


NetRangeObject*
NetRangeObject_create(void) {
    NetRangeObject* self = PyMem_Malloc(sizeof(NetRangeObject));
    if (self == NULL) {
        return (NetRangeObject*)PyErr_NoMemory();
    }
    return self;
}


NetRangeObject*
NetRangeObject_copy(const NetRangeObject* const self) {
    NetRangeObject *newItem = NetRangeObject_create();
    if (newItem == NULL) {
        return NULL;
    }
    memcpy(newItem, self, sizeof(*newItem));
    return newItem;
}


int
NetRangeObject_parseCidr(NetRangeObject * const self, const char * const cidr) {
    char tmpcidr[IPV4_MAX_STRING_LEN];
    strncpy(tmpcidr, cidr, IPV4_MAX_STRING_LEN);
    tmpcidr[IPV4_MAX_STRING_LEN - 1] = '\0';
    PY_UINT32_T len = 32;
    char *sep = strchr(tmpcidr, '/');
    if (sep != NULL) {
        *sep = '\0';
        sep++;
        if (strlen(sep) == 0) {
            return -1;
        }
        len = strtoul(sep, NULL, 10);
        if (len > 32) {
            return -1;
        }
    }
    Py_UCS1 buf[4] = {0};
    if (inet_pton(AF_INET, tmpcidr, buf) != 1) {
        return -1;
    }
    self->first =
        (buf[0] << 24) |
        (buf[1] << 16) |
        (buf[2] << 8) |
        (buf[3]);
    self->len = len;
    PY_UINT32_T mask = MASK_MAP[len];
    self->first &= mask;
    self->last = self->first | ~mask;
    return 0;
}


void
NetRangeObject_destroy(NetRangeObject* const self) {
    PyMem_Free(self);
}


int
NetRangeObject_asUtf8CharCidr(const NetRangeObject* const self, char* const str, const Py_ssize_t size) {
    Py_UCS1 buf[4];
    *(PY_UINT32_T*)&buf = self->first;
    return snprintf(str, size, "%u.%u.%u.%u/%u", buf[3], buf[2], buf[1], buf[0], self->len);
}
