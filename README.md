# ipset_c

IPSet is written in C.
It is designed to fast calculating ip/subnet/prefixes intersection, inclusion, joining, subtracting and other operations on IP sets. If you use pytricia or py-radix over netaddr.IPSet because of performance reasons, you should try this library.
Runs on Windows, Linux, macOS. Wheels are available for supported versions.
Tens of times faster than pure Python netaddr IPSet.
Supports both IPv4 and IPv6. Picklable. Can be compiled for free-threading usage.

> [!IMPORTANT]
> Due to the max sequence size in python(sys.maxsize), using len() with a large IPv6 IPSet raising an error. Use the IPSet([]).size attribute instead.

> [!IMPORTANT]
> Do not mix IPv4 and IPv6 in one IPSet without converting to IPv4-mapped IPv6. For example, instead of "0.0.0.0/32" pass "::ffff:0.0.0.0/128".

## Installation

```
pip install ipset_c
```

## Usage

```
from ipset_c import IPSet
a = IPSet(['12.12.12.0/25', '12.12.12.128/25'])
a.getCidrs()  # ['12.12.12.0/24']
a.addCidr('8.8.8.8/30')
a.getCidrs()  # ['8.8.8.8/30', '12.12.12.0/24']
b = IPSet(['12.12.12.0/25'])
a.isSubset(b)  # False
a.isSuperset(b)  # True
a == b  # False
a < b  # False
a <= b  # False
a > b  # True
a >= b  # True
a.isContainsCidr("12.12.0.0/16")  # False
a.isIntersectsCidr("12.12.0.0/16")  # True
b.addCidr('4.4.4.4/32')
a.getCidrs()  # ['8.8.8.8/30', '12.12.12.0/24']
b.getCidrs()  # ['4.4.4.4/32', '12.12.12.0/25']
c = a & b
c.getCidrs()  # ['12.12.12.0/25']
c = a | b
c.getCidrs()  # ['4.4.4.4/32', '8.8.8.8/30', '12.12.12.0/24']
c = a ^ b
c.getCidrs()  # ['4.4.4.4/32', '8.8.8.8/30', '12.12.12.128/25']
c = a - b
c.getCidrs()  # ['8.8.8.8/30', '12.12.12.128/25']
a.removeCidr('8.8.8.8/30')
a.getCidrs()  # ['12.12.12.0/24']
len(a)  # 256
a.size  # 256
c = a.copy()
bool(IPSet([]))  # False
str(IPSet(['8.8.8.8/30']))  # "IPSet(['8.8.8.8/30'])"
```
