import pytest


def testAddRemove():
    import ipset_c
    ipset = ipset_c.IPSet([])
    ipset.addCidr('1.1.1.1')
    ipset.removeCidr('1.1.1.1')
    ipset.addCidr('1.1.1.3')
    ipset.removeCidr('1.1.1.3')
    assert ipset.size == 0


def testNotImplemented():
    import ipset_c
    with pytest.raises(TypeError):
        r = ipset_c.IPSet(['1.1.1.1']) @ ipset_c.IPSet(['1.1.1.1'])


def testRepr():
    import ipset_c
    ipset = ipset_c.IPSet(["9.9.9.9"])
    assert repr(ipset) == "IPSet(['9.9.9.9/32'])"
