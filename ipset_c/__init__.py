from ipset_c_ext import IPSet as _IPSet


class IPSet(_IPSet):

    def __len__(self) -> int:
        return self.size
