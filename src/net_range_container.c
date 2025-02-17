#include "net_range_container.h"


static Py_ssize_t
ensureSpareSize(NetRangeContainer* const self, Py_ssize_t nelems) {
    if (self->len + nelems < self->allocatedLen) {
        return 0;
    }
    const Py_ssize_t newAllocSize = self->len + nelems*4;
    NetRangeObject** newCont = PyMem_Realloc(self->array, newAllocSize * sizeof(NetRangeObject*));
    if (newCont == NULL) {
        PyErr_NoMemory();
        return -1;
    }
    self->array = newCont;
    self->allocatedLen = newAllocSize;
    return newAllocSize - self->len;
}


inline static Py_ssize_t
mergeNetRangesArray(NetRangeObject** array, const Py_ssize_t size) {
    Py_ssize_t base = 0, next = 0, changeCounter = 0;
    uint128c mask;

    NetRangeObject* baseNode, * nextNode;
    while (next < size) {
        while (base < size && array[base] == NULL) {
            base++;
        }
        if (base > next) {
            next = base;
        }
        do {
            next++;
        } while (next < size && array[next] == NULL);
        if (next >= size) {
            break;
        }
        baseNode = array[base];
        nextNode = array[next];
        if (baseNode->len == nextNode->len && GT128(nextNode->first, baseNode->last)) {
            mask = MASK_MAP[baseNode->len - 1 + (baseNode->isIPv6 ? 0:96)];
            const uint128c a = BAND128(baseNode->first, mask);
            const uint128c b = BAND128(nextNode->first, mask);
            if (EQ128(a, b)) {
                baseNode->last = nextNode->last;
                baseNode->len--;
                NetRangeObject_destroy(nextNode);
                array[next] = NULL;
                changeCounter++;
                while (base > 0) {
                    base--;
                    if (array[base] != NULL) {
                        break;
                    }
                }
                next = base;
            }
            else {
                base++;
            }
        }
        else {
            mask = MASK_MAP[baseNode->len + (baseNode->isIPv6 ? 0:96)];
            const uint128c a = BAND128(baseNode->first, mask);
            const uint128c b = BAND128(nextNode->first, mask);
            if (EQ128(a, b)) {
                NetRangeObject_destroy(nextNode);
                array[next] = NULL;
                changeCounter++;
            }
            else {
                base++;
            }
        }
    }
    return changeCounter;
}


static void
removeGapsFromNetRanges(NetRangeContainer *const self, Py_ssize_t start) {
    Py_ssize_t base = start, next = start;
    NetRangeObject** array = self->array;
    while (base < self->len) {
        while (base < self->len && array[base] != NULL) {
            base++;
        }

        next = max(base, next) + 1;
        while (next < self->len && array[next] == NULL) {
            next++;
        }
        if (next < self->len) {
            array[base] = array[next];
            array[next] = NULL;
        }
        else {
            break;
        }
    }
    self->len = base;
}


static int
comparatorWithLen(const NetRangeObject **const elem1, const NetRangeObject **const elem2) {
    if (GT128((*elem1)->first, (*elem2)->first)) {
        return 1;
    } 
    if (GT128((*elem2)->first, (*elem1)->first)) {
        return -1;
    } 
    if ((*elem1)->len > (*elem2)->len) {
        return 1;
    } 
    if ((*elem1)->len < (*elem2)->len) {
        return -1;
    } 
    return 0;
}


static void
mergeNetRanges(NetRangeContainer *const  self) {
    if (self->len < 2) {
        return;
    }
    qsort(self->array, self->len, sizeof(self->array[0]), (int (*)(void const*, void const*))comparatorWithLen);
    Py_ssize_t changesNum = 0;
    changesNum = mergeNetRangesArray(self->array, self->len);
    if (changesNum) {
        removeGapsFromNetRanges(self, 0);
    }
}


void
NetRangeContainer_merge(NetRangeContainer *const self) {
    mergeNetRanges(self);
}


NetRangeContainer*
NetRangeContainer_create(Py_ssize_t nelem) {
    NetRangeContainer *c = PyMem_Malloc(sizeof(*c));
    if (c == NULL) {
        return (NetRangeContainer*)PyErr_NoMemory();
    }
    nelem = max(nelem, 1);
    c->array = PyMem_Calloc(nelem, sizeof(*c->array));
    if (c->array == NULL) {
        NetRangeContainer_destroy(c);
        return (NetRangeContainer*)PyErr_NoMemory();
    }
    c->len = 0;
    c->allocatedLen = nelem;
    return c;
}


NetRangeContainer*
NetRangeContainer_copy(NetRangeContainer* self) {
    NetRangeContainer* res = NetRangeContainer_create(self->allocatedLen);
    if (res == NULL) {
        return res;
    }
    for (Py_ssize_t i = 0; i < self->len; i++) {
        res->array[i] = NetRangeObject_copy(self->array[i]);
    }
    res->len = self->len;
    return res;
}


void
NetRangeContainer_destroy(NetRangeContainer* self) {
    if (self == NULL) {
        return;
    }
    for(Py_ssize_t i = 0; i < self->len; i++) {
        NetRangeObject_destroy(self->array[i]);
    }
    PyMem_Free(self->array);
    PyMem_Free(self);
}


static inline int
bsearchComparator (const NetRangeObject **const a, const NetRangeObject **const b) {
    if (GT128((*a)->last, (*b)->last)) {
        return 1;
    }
    if (GT128((*b)->first, (*a)->first)) {
        return -1;
    }
    return 0;
}


static inline int
bsearchComparatorIntersects(const NetRangeObject **const a, const NetRangeObject **const b) {
    if ((*a)->len >= (*b)->len) {
        return bsearchComparator(a, b);
    }
    else {
        return -bsearchComparator(b, a);
    }
}


Py_ssize_t
NetRangeContainer_findNetRangeContainsIndex(const NetRangeContainer *const self, const NetRangeObject *const item) {
    NetRangeObject **pItem = (NetRangeObject**)bsearch(
        &item, self->array, self->len, sizeof(NetRangeObject*), (int (*)(void const*, void const*))bsearchComparator
    );
    if (pItem) {
        return (pItem - self->array);
    }
    return -1;
}


Py_ssize_t
NetRangeContainer_findNetRangeIntersectsIndex(const NetRangeContainer *const self, const NetRangeObject *const item) {
    NetRangeObject **pItem = (NetRangeObject**)bsearch(
        &item, self->array, self->len, sizeof(NetRangeObject*), (int (*)(void const*, void const*))bsearchComparatorIntersects
    );
    if (pItem) {
        return (pItem - self->array);
    }
    return -1;
}


int
NetRangeContainer_isSuperset(const NetRangeContainer *const self, const NetRangeContainer *const other) {
    Py_ssize_t newStart = 0;
    NetRangeObject **const selfArray = self->array, **const otherArray = other->array;
    for (Py_ssize_t i = 0; i < other->len; i++) {
        NetRangeObject **pItem = (NetRangeObject**)bsearch(
            &otherArray[i], &selfArray[newStart], self->len - newStart, sizeof(NetRangeObject*), (int (*)(void const*, void const*))bsearchComparator
        );
        if (pItem) {
            newStart = (pItem - &selfArray[newStart]);
        } 
        else {
            return 0;
        }
    }
    return 1;
}


static Py_ssize_t
findInsertIndexLoop(const NetRangeObject** const array, Py_ssize_t len, const NetRangeObject* const item, Py_ssize_t* shiftPos) {
    Py_ssize_t start = 0, end = len - 1;
    Py_ssize_t i = 0;
    Py_ssize_t compRes = -1;
    while (start <= end) {
        i = (end + start) / 2;
        compRes = bsearchComparatorIntersects((const NetRangeObject** const)&item, (const NetRangeObject** const)&array[i]);
        if (compRes > 0) {
            start = i + 1;
        }
        else if (compRes < 0) {
            end = i - 1;
        }
        else {
            if (i - start > 0) {
                end = i;
            } else {
                break;
            }
        }
    }
    *shiftPos = compRes;
    return i;
}


static Py_ssize_t
findInsertIndex(const NetRangeContainer* const self, const NetRangeObject* const item, Py_ssize_t *shiftPos) {
    return findInsertIndexLoop(self->array, self->len, item, shiftPos);
}


int
NetRangeContainer_addNetRange (NetRangeContainer *const self, NetRangeObject* item) {
    Py_ssize_t posShift = 0;
    Py_ssize_t i = findInsertIndex(self, item, &posShift);
    if (posShift != 0 || item->len < self->array[i]->len) {
        if (ensureSpareSize(self, 1) == -1) {
            return -1;
        }
        if (posShift == 1) {
            i++;
        }
        memmove(self->array + i + 1, self->array + i, (self->len - i) * sizeof(NetRangeObject*));
        self->array[i] = item;
        self->len++;
        Py_ssize_t startIdx = max(i - item->len, 0);
        Py_ssize_t changesNum = mergeNetRangesArray(&self->array[startIdx], self->len - startIdx);
        if (changesNum) {
            removeGapsFromNetRanges(self, startIdx);
        }
        return 1;
    }
    else {
        NetRangeObject_destroy(item);
    }
    return 0;
}


static void
spliceNetRangeObject(NetRangeObject** cont, const NetRangeObject *const sub) {
    NetRangeObject* base = cont[0];
    NetRangeObject* upperPart = NULL;
    Py_ssize_t r = sub->len;
    r -= base->len;
    r--;
    PY_UINT32_T prefIdx = base->len + 1, l = 0;
    for (; prefIdx <= sub->len; prefIdx++) {
        if ((upperPart = NetRangeObject_create()) == NULL) {
            return;
        }
        upperPart->len = prefIdx;
        upperPart->isIPv6 = base->isIPv6;
        const uint128c mask = MASK_MAP[prefIdx + (base->isIPv6 ? 0:96)];
        upperPart->first = BAND128(base->last, mask);
        upperPart->last = base->last;
        base->len = prefIdx;
        base->last = SUBLONG128(upperPart->first, 1);
        if (GT128(sub->first, base->last)) {
            cont[l] = base;
            base = upperPart;
            l++;
        }
        else {
            cont[r] = upperPart;
            upperPart = NULL;
            r--;
        }
    }
    if (NULL != upperPart) {
        NetRangeObject_destroy(upperPart);
    }
    if (base != upperPart && cont[0] != base) {
        NetRangeObject_destroy(base);
    }
}


int
NetRangeContainer_removeNetRange(NetRangeContainer* const self, const NetRangeObject *const item) {
    Py_ssize_t posShift = 0;
    while (1) {
        Py_ssize_t i = findInsertIndex(self, item, &posShift);
        if (posShift == 0) {
            Py_ssize_t growNum = 0;
            growNum = item->len;
            growNum -= self->array[i]->len;
            growNum--;
            if (growNum >= 0) {
                if (ensureSpareSize(self, growNum) == -1) {
                    return -1;
                }
                memmove(self->array + i + growNum + 1, self->array + i + 1, (self->len - i - 1) * sizeof(NetRangeObject*));
                spliceNetRangeObject(&self->array[i], item);
                self->len += growNum;
            }
            else {
                NetRangeObject_destroy(self->array[i]);
                self->array[i] = NULL;
                removeGapsFromNetRanges(self, i);
            }
        }
        else {
            break;
        }
    }
    return 0;
}


NetRangeContainer* 
NetRangeContainer_intersection(const NetRangeContainer* self, const NetRangeContainer* other) {
    NetRangeContainer* res = NetRangeContainer_create(self->len + other->len);
    if (res == NULL) {
        return res;
    }
    if (self->len < other->len) {
        const NetRangeContainer* tmp = self;
        self = other;
        other = tmp;
    }
    Py_ssize_t insertPos = 0, shiftPos = 0, i = 0, startSearchPos = 0, resI = 0;
    while (i < other->len && startSearchPos < self->len) {
        insertPos = findInsertIndexLoop(self->array+startSearchPos, self->len-startSearchPos, other->array[i], &shiftPos);
        if (shiftPos == 0) {
            startSearchPos = startSearchPos + insertPos;
            if (other->array[i]->len > self->array[startSearchPos]->len) {
                res->array[resI] = other->array[i];
            }
            else {
                res->array[resI] = self->array[startSearchPos];
            }
            resI++;
            startSearchPos++;
            if (startSearchPos != self->len) {
                continue;
            }
        }
        startSearchPos = 0;
        i++;
    }
    res->len = resI;
    for (i = 0; i < res->len; i++) {
        res->array[i] = NetRangeObject_copy(res->array[i]);
    }
    return res;
}
