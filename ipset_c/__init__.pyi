from typing import List, Iterable
import sys


if sys.version_info >= (3, 11):
    from typing import Self
else:
    from typing_extensions import Self


class IPSet:
    def __init__(self: Self, cidrs: Iterable[str], /) -> None:
        """
        Do not mix IPv4 and IPv6 in one IPSet without converting to IPv4-mapped IPv6.
        For example, instead of "0.0.0.0/32" pass "::ffff:0.0.0.0/128".
        >>> a = IPSet(["1.1.1.1", "5.5.5.4/30", "1.1.1.0"])
        >>> a.getCidrs()
        ['1.1.1.0/31', '5.5.5.4/30']
        """

    def __gt__(self: Self, other: "IPSet", /) -> bool: ...
    def __ge__(self: Self, other: "IPSet", /) -> bool: ...
    def __lt__(self: Self, other: "IPSet", /) -> bool: ...
    def __le__(self: Self, other: "IPSet", /) -> bool: ...
    def __eq__(self: Self, other: "IPSet", /) -> bool: ...
    def __ne__(self: Self, other: "IPSet", /) -> bool: ...
    def __and__(self: Self, other: "IPSet", /) -> Self: ...
    def __or__(self: Self, other: "IPSet", /) -> Self: ...
    def __xor__(self: Self, other: "IPSet", /) -> Self: ...
    def __sub__(self: Self, other: "IPSet", /) -> Self: ...
    def __add__(self: Self, other: "IPSet", /) -> Self: ...
    def __bool__(self: Self) -> bool: ...

    def __len__(self: Self) -> int:
        """
        Due to the max sequence size in python(sys.maxsize), using len() with a large IPv6 IPSet raising an error.
        Use the IPSet([]).size attribute instead.
        """

    def __repr__(self: Self) -> str:
        """
        Returns a string representation of the IPSet object.
        >>> str(IPSet(["5.5.5.4/30"]))
        "IPSet(['5.5.5.4/30'])"
        """

    def __getstate__(self: Self) -> bytes: ...
    def __setstate__(self: Self, state: bytes) -> None: ...
    def __contains__(self: Self, cidr: str) -> bool: ...

    @property
    def size(self: Self) -> int:
        """
        Returns the number of IPs in the IPSet.
        >>> IPSet(["5.5.5.4/30"]).size
        4
        """

    def isContainsCidr(self: Self, cidr: str, /) -> bool:
        """
        Returns True if the IPSet contains the given CIDR.
        >>> IPSet(["5.5.5.4/30"]).isContainsCidr("5.5.5.4/32")
        True
        """

    def isIntersectsCidr(self: Self, cidr: str, /) -> bool:
        """
        Returns True if the IPSet intersects with the given CIDR.
        >>> IPSet(["5.5.5.4/30"]).isIntersectsCidr("5.5.5.0/24")
        True
        """

    def isSubset(self: Self, other: "IPSet", /) -> bool:
        """
        Returns True if the IPSet is a subset of the given IPSet.
        >>> IPSet(["5.5.5.4/30"]).isSubset(IPSet(["5.5.5.4/28"]))
        True
        """

    def isSuperset(self: Self, other: "IPSet", /) -> bool:
        """
        Returns True if the IPSet is a superset of the given IPSet.
        >>> IPSet(["5.5.5.4/28"]).isSuperset(IPSet(["5.5.5.4/30"]))
        True
        """

    def isIntersects(self: Self, other: "IPSet", /) -> bool:
        """
        Returns True if the IPSet intersects with the given IPSet.
        >>> IPSet(["5.5.5.4/30"]).isIntersects(IPSet(["5.5.5.7/32"]))
        True
        """

    def getCidrs(self: Self) -> List[str]:
        """
        Returns a list of CIDRs that the IPSet contains.
        >>> IPSet(["5.5.5.4/30"]).getCidrs()
        ['5.5.5.4/30']
        """

    def addCidr(self: Self, cidr: str, /) -> None:
        """
        Adds a CIDR to the IPSet.
        >>> ipset = IPSet(["5.5.5.4/30"])
        >>> ipset.addCidr("5.5.5.8/32")
        >>> ipset.getCidrs()
        ['5.5.5.4/30', '5.5.5.8/32']
        """

    def removeCidr(self: Self, cidr: str, /) -> None:
        """
        Removes a CIDR from the IPSet.
        >>> ipset = IPSet(["5.5.5.4/30", "5.5.5.8/32"])
        >>> ipset.removeCidr("5.5.5.8/32")
        >>> ipset.getCidrs()
        ['5.5.5.4/30']
        """

    def copy(self: Self) -> Self:
        """
        Returns a new IPSet with the same CIDRs as this one.
        >>> ipset = IPSet(["5.5.5.4/30", "5.5.5.8/32"])
        >>> ipsetCopy = ipset.copy()
        >>> ipsetCopy.getCidrs()
        ['5.5.5.4/30', '5.5.5.8/32']
        """
