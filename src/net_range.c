#include "net_range.h"


NetRangeObject*
NetRangeObject_create(void) {
    NetRangeObject* self = PyMem_Malloc(sizeof(NetRangeObject));
    if (self == NULL) {
        return (NetRangeObject*)PyErr_NoMemory();
    }
    self->isIPv6 = 0;
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
NetRangeObject_parseCidr(NetRangeObject* const self, const char* const cidr) {
    char tmpcidr[IPV6_MAX_STRING_LEN];
    strncpy(tmpcidr, cidr, IPV6_MAX_STRING_LEN);
    tmpcidr[IPV6_MAX_STRING_LEN - 1] = '\0';
    PY_UINT32_T len = 32;
    if (strchr(tmpcidr, ':')){
        self->isIPv6 = 1;
        len = 128;
    } else {
        self->isIPv6 = 0;
    }
    char* sep = strchr(tmpcidr, '/');
    if (sep != NULL) {
        *sep = '\0';
        sep++;
        if (strlen(sep) == 0) {
            return -1;
        }
        if (sscanf(sep, "%d", &len) == 0) {  // strtoul on linux moves end_ptr on error
            return -1;
        }
        if (self->isIPv6){
            if (len > 128) {
                return -1;
            }
        } else {
            if (len > 32) {
                return -1;
            }
        }
    }
    Py_UCS1 buf[16] = { 0 };

    if (self->isIPv6){
        if (inet_pton(AF_INET6, tmpcidr, buf) != 1) {
            return -1;
        } 
        #if PY_LITTLE_ENDIAN
            *(PY_UINT64_T*)buf = bswap_64(*(PY_UINT64_T*)buf);
            *(PY_UINT64_T*)(buf + 8) = bswap_64(*(PY_UINT64_T*)(buf + 8));
        #endif
        self->first = (uint128c){
            .hi = *(PY_UINT64_T*)buf,
            .lo = *(PY_UINT64_T*)(buf + 8),
        };
    } else {
    if (inet_pton(AF_INET, tmpcidr, buf) != 1) {
        return -1;
    }
        self->first = (uint128c){
            .hi=0,
            .lo=(PY_UINT32_T)(
                buf[0] << 24 |
                buf[1] << 16 |
                buf[2] << 8 |
                buf[3]
            )
        };
    }
    self->len = len;
    uint128c mask = MASK_MAP[len + (self->isIPv6 ? 0:96)];
    self->first = BAND128(self->first, mask);
    self->last.hi = self->first.hi | ~mask.hi;
    self->last.lo = self->first.lo | ~mask.lo;
    return 0;
}


void
NetRangeObject_destroy(NetRangeObject* const self) {
    PyMem_Free(self);
}


int
NetRangeObject_asUtf8CharCidr(const NetRangeObject* const self, char* const str, const Py_ssize_t size) {
    Py_UCS1 buf[16];
    *(uint128c*)buf = self->first;
    if (self->isIPv6) {
        #if PY_LITTLE_ENDIAN
            *(PY_UINT64_T*)buf = bswap_64(self->first.hi);
            *(PY_UINT64_T*)(buf + 8) = bswap_64(self->first.lo);
        #endif
        inet_ntop(AF_INET6, buf, str, size);
        return snprintf(strchr(str, '\0'), 5, "/%u", self->len);
    }
    return snprintf(str, size, "%u.%u.%u.%u/%u", buf[3], buf[2], buf[1], buf[0], self->len);
}
