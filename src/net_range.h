#pragma once
#include <Python.h>

#if !(defined(_WIN32) || defined(__CYGWIN__))
    #include <arpa/inet.h>
    #include <sys/socket.h>
#else
    #include <WS2tcpip.h>
    #include <winsock2.h>
    #pragma comment(lib, "Ws2_32.lib")
#endif

#ifdef _MSC_VER
    #include <stdlib.h>
    #define bswap_64(x) _byteswap_uint64(x)
#elif defined(__APPLE__)
    #include <libkern/OSByteOrder.h>
    #define bswap_64(x) OSSwapInt64(x)
#elif defined(__sun) || defined(sun)
    #include <sys/byteorder.h>
    #define bswap_64(x) BSWAP_64(x)
#elif defined(__FreeBSD__)
    #include <sys/endian.h>
    #define bswap_64(x) bswap64(x)
#elif defined(__OpenBSD__)
    #include <sys/types.h>
    #define bswap_64(x) swap64(x)
#elif defined(__NetBSD__)
    #include <sys/types.h>
    #include <machine/bswap.h>
    #if defined(__BSWAP_RENAME) && !defined(__bswap_32)
    #define bswap_64(x) bswap64(x)
    #endif
#else
    #include <byteswap.h>
#endif


typedef struct {
#if PY_BIG_ENDIAN
    PY_UINT64_T hi;
    PY_UINT64_T lo;
#else
    PY_UINT64_T lo;
    PY_UINT64_T hi;
#endif
} uint128c;


typedef struct {
    uint128c first;
    uint128c last;
    PY_UINT32_T len;
    PY_UINT32_T isIPv6;
} NetRangeObject;


#define GT128(a, b) ((a).hi > (b).hi || ((a).hi == (b).hi && (a).lo > (b).lo))

#define GTE128(a, b) ((a).hi > (b).hi || ((a).hi == (b).hi && (a).lo >= (b).lo))

#define EQ128(a, b) ((a).hi == (b).hi && (a).lo == (b).lo)

#define BAND128(a, b) ((uint128c){.hi=((a).hi & (b).hi), .lo=((a).lo & (b).lo)})

#define SUBLONG128(a, blong) ((uint128c){.hi=((a).hi - ((a).lo < (blong))), .lo=((a).lo - (blong))})

#define SUB128(a, b) ((uint128c){.hi=((a).hi - (b).hi - ((a).lo < (b).lo)), .lo=((a).lo - (b).lo)})

#define ADD128(a, b) ((uint128c){.hi=((a).hi + (b).hi + ((a).lo + (b).lo < (b).lo)), .lo=((a).lo + (b).lo)})


NetRangeObject* NetRangeObject_create(void);

void NetRangeObject_destroy(NetRangeObject* const self);

int NetRangeObject_parseCidr(NetRangeObject* const self, const char* const cidr);

int NetRangeObject_asUtf8CharCidr(const NetRangeObject* const self, char* const str, const Py_ssize_t size);

NetRangeObject* NetRangeObject_copy(const NetRangeObject* const self);









#define IPV6_MAX_STRING_LEN 50

static const uint128c MASK_MAP[] = {
{.hi=(PY_UINT64_T)0b0000000000000000000000000000000000000000000000000000000000000000, .lo=(PY_UINT64_T)0b0000000000000000000000000000000000000000000000000000000000000000},
{.hi=(PY_UINT64_T)0b1000000000000000000000000000000000000000000000000000000000000000, .lo=(PY_UINT64_T)0b0000000000000000000000000000000000000000000000000000000000000000},
{.hi=(PY_UINT64_T)0b1100000000000000000000000000000000000000000000000000000000000000, .lo=(PY_UINT64_T)0b0000000000000000000000000000000000000000000000000000000000000000},
{.hi=(PY_UINT64_T)0b1110000000000000000000000000000000000000000000000000000000000000, .lo=(PY_UINT64_T)0b0000000000000000000000000000000000000000000000000000000000000000},
{.hi=(PY_UINT64_T)0b1111000000000000000000000000000000000000000000000000000000000000, .lo=(PY_UINT64_T)0b0000000000000000000000000000000000000000000000000000000000000000},
{.hi=(PY_UINT64_T)0b1111100000000000000000000000000000000000000000000000000000000000, .lo=(PY_UINT64_T)0b0000000000000000000000000000000000000000000000000000000000000000},
{.hi=(PY_UINT64_T)0b1111110000000000000000000000000000000000000000000000000000000000, .lo=(PY_UINT64_T)0b0000000000000000000000000000000000000000000000000000000000000000},
{.hi=(PY_UINT64_T)0b1111111000000000000000000000000000000000000000000000000000000000, .lo=(PY_UINT64_T)0b0000000000000000000000000000000000000000000000000000000000000000},
{.hi=(PY_UINT64_T)0b1111111100000000000000000000000000000000000000000000000000000000, .lo=(PY_UINT64_T)0b0000000000000000000000000000000000000000000000000000000000000000},
{.hi=(PY_UINT64_T)0b1111111110000000000000000000000000000000000000000000000000000000, .lo=(PY_UINT64_T)0b0000000000000000000000000000000000000000000000000000000000000000},
{.hi=(PY_UINT64_T)0b1111111111000000000000000000000000000000000000000000000000000000, .lo=(PY_UINT64_T)0b0000000000000000000000000000000000000000000000000000000000000000},
{.hi=(PY_UINT64_T)0b1111111111100000000000000000000000000000000000000000000000000000, .lo=(PY_UINT64_T)0b0000000000000000000000000000000000000000000000000000000000000000},
{.hi=(PY_UINT64_T)0b1111111111110000000000000000000000000000000000000000000000000000, .lo=(PY_UINT64_T)0b0000000000000000000000000000000000000000000000000000000000000000},
{.hi=(PY_UINT64_T)0b1111111111111000000000000000000000000000000000000000000000000000, .lo=(PY_UINT64_T)0b0000000000000000000000000000000000000000000000000000000000000000},
{.hi=(PY_UINT64_T)0b1111111111111100000000000000000000000000000000000000000000000000, .lo=(PY_UINT64_T)0b0000000000000000000000000000000000000000000000000000000000000000},
{.hi=(PY_UINT64_T)0b1111111111111110000000000000000000000000000000000000000000000000, .lo=(PY_UINT64_T)0b0000000000000000000000000000000000000000000000000000000000000000},
{.hi=(PY_UINT64_T)0b1111111111111111000000000000000000000000000000000000000000000000, .lo=(PY_UINT64_T)0b0000000000000000000000000000000000000000000000000000000000000000},
{.hi=(PY_UINT64_T)0b1111111111111111100000000000000000000000000000000000000000000000, .lo=(PY_UINT64_T)0b0000000000000000000000000000000000000000000000000000000000000000},
{.hi=(PY_UINT64_T)0b1111111111111111110000000000000000000000000000000000000000000000, .lo=(PY_UINT64_T)0b0000000000000000000000000000000000000000000000000000000000000000},
{.hi=(PY_UINT64_T)0b1111111111111111111000000000000000000000000000000000000000000000, .lo=(PY_UINT64_T)0b0000000000000000000000000000000000000000000000000000000000000000},
{.hi=(PY_UINT64_T)0b1111111111111111111100000000000000000000000000000000000000000000, .lo=(PY_UINT64_T)0b0000000000000000000000000000000000000000000000000000000000000000},
{.hi=(PY_UINT64_T)0b1111111111111111111110000000000000000000000000000000000000000000, .lo=(PY_UINT64_T)0b0000000000000000000000000000000000000000000000000000000000000000},
{.hi=(PY_UINT64_T)0b1111111111111111111111000000000000000000000000000000000000000000, .lo=(PY_UINT64_T)0b0000000000000000000000000000000000000000000000000000000000000000},
{.hi=(PY_UINT64_T)0b1111111111111111111111100000000000000000000000000000000000000000, .lo=(PY_UINT64_T)0b0000000000000000000000000000000000000000000000000000000000000000},
{.hi=(PY_UINT64_T)0b1111111111111111111111110000000000000000000000000000000000000000, .lo=(PY_UINT64_T)0b0000000000000000000000000000000000000000000000000000000000000000},
{.hi=(PY_UINT64_T)0b1111111111111111111111111000000000000000000000000000000000000000, .lo=(PY_UINT64_T)0b0000000000000000000000000000000000000000000000000000000000000000},
{.hi=(PY_UINT64_T)0b1111111111111111111111111100000000000000000000000000000000000000, .lo=(PY_UINT64_T)0b0000000000000000000000000000000000000000000000000000000000000000},
{.hi=(PY_UINT64_T)0b1111111111111111111111111110000000000000000000000000000000000000, .lo=(PY_UINT64_T)0b0000000000000000000000000000000000000000000000000000000000000000},
{.hi=(PY_UINT64_T)0b1111111111111111111111111111000000000000000000000000000000000000, .lo=(PY_UINT64_T)0b0000000000000000000000000000000000000000000000000000000000000000},
{.hi=(PY_UINT64_T)0b1111111111111111111111111111100000000000000000000000000000000000, .lo=(PY_UINT64_T)0b0000000000000000000000000000000000000000000000000000000000000000},
{.hi=(PY_UINT64_T)0b1111111111111111111111111111110000000000000000000000000000000000, .lo=(PY_UINT64_T)0b0000000000000000000000000000000000000000000000000000000000000000},
{.hi=(PY_UINT64_T)0b1111111111111111111111111111111000000000000000000000000000000000, .lo=(PY_UINT64_T)0b0000000000000000000000000000000000000000000000000000000000000000},
{.hi=(PY_UINT64_T)0b1111111111111111111111111111111100000000000000000000000000000000, .lo=(PY_UINT64_T)0b0000000000000000000000000000000000000000000000000000000000000000},
{.hi=(PY_UINT64_T)0b1111111111111111111111111111111110000000000000000000000000000000, .lo=(PY_UINT64_T)0b0000000000000000000000000000000000000000000000000000000000000000},
{.hi=(PY_UINT64_T)0b1111111111111111111111111111111111000000000000000000000000000000, .lo=(PY_UINT64_T)0b0000000000000000000000000000000000000000000000000000000000000000},
{.hi=(PY_UINT64_T)0b1111111111111111111111111111111111100000000000000000000000000000, .lo=(PY_UINT64_T)0b0000000000000000000000000000000000000000000000000000000000000000},
{.hi=(PY_UINT64_T)0b1111111111111111111111111111111111110000000000000000000000000000, .lo=(PY_UINT64_T)0b0000000000000000000000000000000000000000000000000000000000000000},
{.hi=(PY_UINT64_T)0b1111111111111111111111111111111111111000000000000000000000000000, .lo=(PY_UINT64_T)0b0000000000000000000000000000000000000000000000000000000000000000},
{.hi=(PY_UINT64_T)0b1111111111111111111111111111111111111100000000000000000000000000, .lo=(PY_UINT64_T)0b0000000000000000000000000000000000000000000000000000000000000000},
{.hi=(PY_UINT64_T)0b1111111111111111111111111111111111111110000000000000000000000000, .lo=(PY_UINT64_T)0b0000000000000000000000000000000000000000000000000000000000000000},
{.hi=(PY_UINT64_T)0b1111111111111111111111111111111111111111000000000000000000000000, .lo=(PY_UINT64_T)0b0000000000000000000000000000000000000000000000000000000000000000},
{.hi=(PY_UINT64_T)0b1111111111111111111111111111111111111111100000000000000000000000, .lo=(PY_UINT64_T)0b0000000000000000000000000000000000000000000000000000000000000000},
{.hi=(PY_UINT64_T)0b1111111111111111111111111111111111111111110000000000000000000000, .lo=(PY_UINT64_T)0b0000000000000000000000000000000000000000000000000000000000000000},
{.hi=(PY_UINT64_T)0b1111111111111111111111111111111111111111111000000000000000000000, .lo=(PY_UINT64_T)0b0000000000000000000000000000000000000000000000000000000000000000},
{.hi=(PY_UINT64_T)0b1111111111111111111111111111111111111111111100000000000000000000, .lo=(PY_UINT64_T)0b0000000000000000000000000000000000000000000000000000000000000000},
{.hi=(PY_UINT64_T)0b1111111111111111111111111111111111111111111110000000000000000000, .lo=(PY_UINT64_T)0b0000000000000000000000000000000000000000000000000000000000000000},
{.hi=(PY_UINT64_T)0b1111111111111111111111111111111111111111111111000000000000000000, .lo=(PY_UINT64_T)0b0000000000000000000000000000000000000000000000000000000000000000},
{.hi=(PY_UINT64_T)0b1111111111111111111111111111111111111111111111100000000000000000, .lo=(PY_UINT64_T)0b0000000000000000000000000000000000000000000000000000000000000000},
{.hi=(PY_UINT64_T)0b1111111111111111111111111111111111111111111111110000000000000000, .lo=(PY_UINT64_T)0b0000000000000000000000000000000000000000000000000000000000000000},
{.hi=(PY_UINT64_T)0b1111111111111111111111111111111111111111111111111000000000000000, .lo=(PY_UINT64_T)0b0000000000000000000000000000000000000000000000000000000000000000},
{.hi=(PY_UINT64_T)0b1111111111111111111111111111111111111111111111111100000000000000, .lo=(PY_UINT64_T)0b0000000000000000000000000000000000000000000000000000000000000000},
{.hi=(PY_UINT64_T)0b1111111111111111111111111111111111111111111111111110000000000000, .lo=(PY_UINT64_T)0b0000000000000000000000000000000000000000000000000000000000000000},
{.hi=(PY_UINT64_T)0b1111111111111111111111111111111111111111111111111111000000000000, .lo=(PY_UINT64_T)0b0000000000000000000000000000000000000000000000000000000000000000},
{.hi=(PY_UINT64_T)0b1111111111111111111111111111111111111111111111111111100000000000, .lo=(PY_UINT64_T)0b0000000000000000000000000000000000000000000000000000000000000000},
{.hi=(PY_UINT64_T)0b1111111111111111111111111111111111111111111111111111110000000000, .lo=(PY_UINT64_T)0b0000000000000000000000000000000000000000000000000000000000000000},
{.hi=(PY_UINT64_T)0b1111111111111111111111111111111111111111111111111111111000000000, .lo=(PY_UINT64_T)0b0000000000000000000000000000000000000000000000000000000000000000},
{.hi=(PY_UINT64_T)0b1111111111111111111111111111111111111111111111111111111100000000, .lo=(PY_UINT64_T)0b0000000000000000000000000000000000000000000000000000000000000000},
{.hi=(PY_UINT64_T)0b1111111111111111111111111111111111111111111111111111111110000000, .lo=(PY_UINT64_T)0b0000000000000000000000000000000000000000000000000000000000000000},
{.hi=(PY_UINT64_T)0b1111111111111111111111111111111111111111111111111111111111000000, .lo=(PY_UINT64_T)0b0000000000000000000000000000000000000000000000000000000000000000},
{.hi=(PY_UINT64_T)0b1111111111111111111111111111111111111111111111111111111111100000, .lo=(PY_UINT64_T)0b0000000000000000000000000000000000000000000000000000000000000000},
{.hi=(PY_UINT64_T)0b1111111111111111111111111111111111111111111111111111111111110000, .lo=(PY_UINT64_T)0b0000000000000000000000000000000000000000000000000000000000000000},
{.hi=(PY_UINT64_T)0b1111111111111111111111111111111111111111111111111111111111111000, .lo=(PY_UINT64_T)0b0000000000000000000000000000000000000000000000000000000000000000},
{.hi=(PY_UINT64_T)0b1111111111111111111111111111111111111111111111111111111111111100, .lo=(PY_UINT64_T)0b0000000000000000000000000000000000000000000000000000000000000000},
{.hi=(PY_UINT64_T)0b1111111111111111111111111111111111111111111111111111111111111110, .lo=(PY_UINT64_T)0b0000000000000000000000000000000000000000000000000000000000000000},
{.hi=(PY_UINT64_T)0b1111111111111111111111111111111111111111111111111111111111111111, .lo=(PY_UINT64_T)0b0000000000000000000000000000000000000000000000000000000000000000},
{.hi=(PY_UINT64_T)0b1111111111111111111111111111111111111111111111111111111111111111, .lo=(PY_UINT64_T)0b1000000000000000000000000000000000000000000000000000000000000000},
{.hi=(PY_UINT64_T)0b1111111111111111111111111111111111111111111111111111111111111111, .lo=(PY_UINT64_T)0b1100000000000000000000000000000000000000000000000000000000000000},
{.hi=(PY_UINT64_T)0b1111111111111111111111111111111111111111111111111111111111111111, .lo=(PY_UINT64_T)0b1110000000000000000000000000000000000000000000000000000000000000},
{.hi=(PY_UINT64_T)0b1111111111111111111111111111111111111111111111111111111111111111, .lo=(PY_UINT64_T)0b1111000000000000000000000000000000000000000000000000000000000000},
{.hi=(PY_UINT64_T)0b1111111111111111111111111111111111111111111111111111111111111111, .lo=(PY_UINT64_T)0b1111100000000000000000000000000000000000000000000000000000000000},
{.hi=(PY_UINT64_T)0b1111111111111111111111111111111111111111111111111111111111111111, .lo=(PY_UINT64_T)0b1111110000000000000000000000000000000000000000000000000000000000},
{.hi=(PY_UINT64_T)0b1111111111111111111111111111111111111111111111111111111111111111, .lo=(PY_UINT64_T)0b1111111000000000000000000000000000000000000000000000000000000000},
{.hi=(PY_UINT64_T)0b1111111111111111111111111111111111111111111111111111111111111111, .lo=(PY_UINT64_T)0b1111111100000000000000000000000000000000000000000000000000000000},
{.hi=(PY_UINT64_T)0b1111111111111111111111111111111111111111111111111111111111111111, .lo=(PY_UINT64_T)0b1111111110000000000000000000000000000000000000000000000000000000},
{.hi=(PY_UINT64_T)0b1111111111111111111111111111111111111111111111111111111111111111, .lo=(PY_UINT64_T)0b1111111111000000000000000000000000000000000000000000000000000000},
{.hi=(PY_UINT64_T)0b1111111111111111111111111111111111111111111111111111111111111111, .lo=(PY_UINT64_T)0b1111111111100000000000000000000000000000000000000000000000000000},
{.hi=(PY_UINT64_T)0b1111111111111111111111111111111111111111111111111111111111111111, .lo=(PY_UINT64_T)0b1111111111110000000000000000000000000000000000000000000000000000},
{.hi=(PY_UINT64_T)0b1111111111111111111111111111111111111111111111111111111111111111, .lo=(PY_UINT64_T)0b1111111111111000000000000000000000000000000000000000000000000000},
{.hi=(PY_UINT64_T)0b1111111111111111111111111111111111111111111111111111111111111111, .lo=(PY_UINT64_T)0b1111111111111100000000000000000000000000000000000000000000000000},
{.hi=(PY_UINT64_T)0b1111111111111111111111111111111111111111111111111111111111111111, .lo=(PY_UINT64_T)0b1111111111111110000000000000000000000000000000000000000000000000},
{.hi=(PY_UINT64_T)0b1111111111111111111111111111111111111111111111111111111111111111, .lo=(PY_UINT64_T)0b1111111111111111000000000000000000000000000000000000000000000000},
{.hi=(PY_UINT64_T)0b1111111111111111111111111111111111111111111111111111111111111111, .lo=(PY_UINT64_T)0b1111111111111111100000000000000000000000000000000000000000000000},
{.hi=(PY_UINT64_T)0b1111111111111111111111111111111111111111111111111111111111111111, .lo=(PY_UINT64_T)0b1111111111111111110000000000000000000000000000000000000000000000},
{.hi=(PY_UINT64_T)0b1111111111111111111111111111111111111111111111111111111111111111, .lo=(PY_UINT64_T)0b1111111111111111111000000000000000000000000000000000000000000000},
{.hi=(PY_UINT64_T)0b1111111111111111111111111111111111111111111111111111111111111111, .lo=(PY_UINT64_T)0b1111111111111111111100000000000000000000000000000000000000000000},
{.hi=(PY_UINT64_T)0b1111111111111111111111111111111111111111111111111111111111111111, .lo=(PY_UINT64_T)0b1111111111111111111110000000000000000000000000000000000000000000},
{.hi=(PY_UINT64_T)0b1111111111111111111111111111111111111111111111111111111111111111, .lo=(PY_UINT64_T)0b1111111111111111111111000000000000000000000000000000000000000000},
{.hi=(PY_UINT64_T)0b1111111111111111111111111111111111111111111111111111111111111111, .lo=(PY_UINT64_T)0b1111111111111111111111100000000000000000000000000000000000000000},
{.hi=(PY_UINT64_T)0b1111111111111111111111111111111111111111111111111111111111111111, .lo=(PY_UINT64_T)0b1111111111111111111111110000000000000000000000000000000000000000},
{.hi=(PY_UINT64_T)0b1111111111111111111111111111111111111111111111111111111111111111, .lo=(PY_UINT64_T)0b1111111111111111111111111000000000000000000000000000000000000000},
{.hi=(PY_UINT64_T)0b1111111111111111111111111111111111111111111111111111111111111111, .lo=(PY_UINT64_T)0b1111111111111111111111111100000000000000000000000000000000000000},
{.hi=(PY_UINT64_T)0b1111111111111111111111111111111111111111111111111111111111111111, .lo=(PY_UINT64_T)0b1111111111111111111111111110000000000000000000000000000000000000},
{.hi=(PY_UINT64_T)0b1111111111111111111111111111111111111111111111111111111111111111, .lo=(PY_UINT64_T)0b1111111111111111111111111111000000000000000000000000000000000000},
{.hi=(PY_UINT64_T)0b1111111111111111111111111111111111111111111111111111111111111111, .lo=(PY_UINT64_T)0b1111111111111111111111111111100000000000000000000000000000000000},
{.hi=(PY_UINT64_T)0b1111111111111111111111111111111111111111111111111111111111111111, .lo=(PY_UINT64_T)0b1111111111111111111111111111110000000000000000000000000000000000},
{.hi=(PY_UINT64_T)0b1111111111111111111111111111111111111111111111111111111111111111, .lo=(PY_UINT64_T)0b1111111111111111111111111111111000000000000000000000000000000000},
{.hi=(PY_UINT64_T)0b1111111111111111111111111111111111111111111111111111111111111111, .lo=(PY_UINT64_T)0b1111111111111111111111111111111100000000000000000000000000000000},
{.hi=(PY_UINT64_T)0b1111111111111111111111111111111111111111111111111111111111111111, .lo=(PY_UINT64_T)0b1111111111111111111111111111111110000000000000000000000000000000},
{.hi=(PY_UINT64_T)0b1111111111111111111111111111111111111111111111111111111111111111, .lo=(PY_UINT64_T)0b1111111111111111111111111111111111000000000000000000000000000000},
{.hi=(PY_UINT64_T)0b1111111111111111111111111111111111111111111111111111111111111111, .lo=(PY_UINT64_T)0b1111111111111111111111111111111111100000000000000000000000000000},
{.hi=(PY_UINT64_T)0b1111111111111111111111111111111111111111111111111111111111111111, .lo=(PY_UINT64_T)0b1111111111111111111111111111111111110000000000000000000000000000},
{.hi=(PY_UINT64_T)0b1111111111111111111111111111111111111111111111111111111111111111, .lo=(PY_UINT64_T)0b1111111111111111111111111111111111111000000000000000000000000000},
{.hi=(PY_UINT64_T)0b1111111111111111111111111111111111111111111111111111111111111111, .lo=(PY_UINT64_T)0b1111111111111111111111111111111111111100000000000000000000000000},
{.hi=(PY_UINT64_T)0b1111111111111111111111111111111111111111111111111111111111111111, .lo=(PY_UINT64_T)0b1111111111111111111111111111111111111110000000000000000000000000},
{.hi=(PY_UINT64_T)0b1111111111111111111111111111111111111111111111111111111111111111, .lo=(PY_UINT64_T)0b1111111111111111111111111111111111111111000000000000000000000000},
{.hi=(PY_UINT64_T)0b1111111111111111111111111111111111111111111111111111111111111111, .lo=(PY_UINT64_T)0b1111111111111111111111111111111111111111100000000000000000000000},
{.hi=(PY_UINT64_T)0b1111111111111111111111111111111111111111111111111111111111111111, .lo=(PY_UINT64_T)0b1111111111111111111111111111111111111111110000000000000000000000},
{.hi=(PY_UINT64_T)0b1111111111111111111111111111111111111111111111111111111111111111, .lo=(PY_UINT64_T)0b1111111111111111111111111111111111111111111000000000000000000000},
{.hi=(PY_UINT64_T)0b1111111111111111111111111111111111111111111111111111111111111111, .lo=(PY_UINT64_T)0b1111111111111111111111111111111111111111111100000000000000000000},
{.hi=(PY_UINT64_T)0b1111111111111111111111111111111111111111111111111111111111111111, .lo=(PY_UINT64_T)0b1111111111111111111111111111111111111111111110000000000000000000},
{.hi=(PY_UINT64_T)0b1111111111111111111111111111111111111111111111111111111111111111, .lo=(PY_UINT64_T)0b1111111111111111111111111111111111111111111111000000000000000000},
{.hi=(PY_UINT64_T)0b1111111111111111111111111111111111111111111111111111111111111111, .lo=(PY_UINT64_T)0b1111111111111111111111111111111111111111111111100000000000000000},
{.hi=(PY_UINT64_T)0b1111111111111111111111111111111111111111111111111111111111111111, .lo=(PY_UINT64_T)0b1111111111111111111111111111111111111111111111110000000000000000},
{.hi=(PY_UINT64_T)0b1111111111111111111111111111111111111111111111111111111111111111, .lo=(PY_UINT64_T)0b1111111111111111111111111111111111111111111111111000000000000000},
{.hi=(PY_UINT64_T)0b1111111111111111111111111111111111111111111111111111111111111111, .lo=(PY_UINT64_T)0b1111111111111111111111111111111111111111111111111100000000000000},
{.hi=(PY_UINT64_T)0b1111111111111111111111111111111111111111111111111111111111111111, .lo=(PY_UINT64_T)0b1111111111111111111111111111111111111111111111111110000000000000},
{.hi=(PY_UINT64_T)0b1111111111111111111111111111111111111111111111111111111111111111, .lo=(PY_UINT64_T)0b1111111111111111111111111111111111111111111111111111000000000000},
{.hi=(PY_UINT64_T)0b1111111111111111111111111111111111111111111111111111111111111111, .lo=(PY_UINT64_T)0b1111111111111111111111111111111111111111111111111111100000000000},
{.hi=(PY_UINT64_T)0b1111111111111111111111111111111111111111111111111111111111111111, .lo=(PY_UINT64_T)0b1111111111111111111111111111111111111111111111111111110000000000},
{.hi=(PY_UINT64_T)0b1111111111111111111111111111111111111111111111111111111111111111, .lo=(PY_UINT64_T)0b1111111111111111111111111111111111111111111111111111111000000000},
{.hi=(PY_UINT64_T)0b1111111111111111111111111111111111111111111111111111111111111111, .lo=(PY_UINT64_T)0b1111111111111111111111111111111111111111111111111111111100000000},
{.hi=(PY_UINT64_T)0b1111111111111111111111111111111111111111111111111111111111111111, .lo=(PY_UINT64_T)0b1111111111111111111111111111111111111111111111111111111110000000},
{.hi=(PY_UINT64_T)0b1111111111111111111111111111111111111111111111111111111111111111, .lo=(PY_UINT64_T)0b1111111111111111111111111111111111111111111111111111111111000000},
{.hi=(PY_UINT64_T)0b1111111111111111111111111111111111111111111111111111111111111111, .lo=(PY_UINT64_T)0b1111111111111111111111111111111111111111111111111111111111100000},
{.hi=(PY_UINT64_T)0b1111111111111111111111111111111111111111111111111111111111111111, .lo=(PY_UINT64_T)0b1111111111111111111111111111111111111111111111111111111111110000},
{.hi=(PY_UINT64_T)0b1111111111111111111111111111111111111111111111111111111111111111, .lo=(PY_UINT64_T)0b1111111111111111111111111111111111111111111111111111111111111000},
{.hi=(PY_UINT64_T)0b1111111111111111111111111111111111111111111111111111111111111111, .lo=(PY_UINT64_T)0b1111111111111111111111111111111111111111111111111111111111111100},
{.hi=(PY_UINT64_T)0b1111111111111111111111111111111111111111111111111111111111111111, .lo=(PY_UINT64_T)0b1111111111111111111111111111111111111111111111111111111111111110},
{.hi=(PY_UINT64_T)0b1111111111111111111111111111111111111111111111111111111111111111, .lo=(PY_UINT64_T)0b1111111111111111111111111111111111111111111111111111111111111111}
};
