from typing import List, Sequence


class IPSet:
    def __init__(self, cidrs: Sequence[str], /) -> None:
        '''
        >>> a = IPSet(["1.1.1.1", "5.5.5.4/30", "1.1.1.0"])
        >>> a.getCidrs()
        ['1.1.1.0/31', '5.5.5.4/30']
        '''

    def __gt__(self, other: "IPSet", /) -> bool: ...

    def __ge__(self, other: "IPSet", /) -> bool: ...

    def __lt__(self, other: "IPSet", /) -> bool: ...

    def __le__(self, other: "IPSet", /) -> bool: ...

    def __eq__(self, other: "IPSet", /) -> bool: ...

    def __ne__(self, other: "IPSet", /) -> bool: ...

    def __and__(self, other: "IPSet", /) -> "IPSet": ...

    def __or__(self, other: "IPSet", /) -> "IPSet": ...

    def __sub__(self, other: "IPSet", /) -> "IPSet": ...

    def __add__(self, other: "IPSet", /) -> "IPSet": ...

    def __bool__(self) -> bool: ...

    def __len__(self) -> int: ...

    def __repr__(self) -> str: ...

    def __contains__(self, cidr: str) -> bool: ...

    @property
    def size(self) -> int: ...

    def isContainsCidr(self, cidr: str, /) -> bool: ...

    def isIntersectsCidr(self, cidr: str, /) -> bool: ...

    def isSubset(self, other: "IPSet", /) -> bool: ...

    def isSuperset(self, other: "IPSet", /) -> bool: ...

    def getCidrs(self) -> List[str]: ...

    def addCidr(self, cidr: str, /) -> None: ...

    def removeCidr(self, cidr: str, /) -> None: ...

    def copy(self) -> "IPSet": ...
