import pytest


def testNotImplemented():
    import ipset_c
    with pytest.raises(TypeError):
        r = ipset_c.IPSet(['1.1.1.1']) > ipset_c.IPSet(['1.1.1.1'])
