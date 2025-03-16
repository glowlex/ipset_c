from ipset_c_ext import IPSet as _IPSet


class IPSet(_IPSet):
    def __len__(self) -> int:
        return self.size

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}({self.getCidrs()})"
