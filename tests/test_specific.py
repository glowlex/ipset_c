import pytest


def testAddRemove():
    import ipset_c
    ipset = ipset_c.IPSet([])
    ipset.addCidr("1.1.1.1")
    ipset.removeCidr("1.1.1.1")
    ipset.addCidr("1.1.1.3")
    ipset.removeCidr("1.1.1.3")
    assert ipset.size == 0


def testRepr():
    import ipset_c
    ipset = ipset_c.IPSet(["9.9.9.9"])
    assert repr(ipset) == "IPSet(['9.9.9.9/32'])"


def testPickleTypeError():
    import ipset_c
    with pytest.raises(TypeError):
        ipset_c.IPSet([]).__setstate__(5)


def testPickleValueError():
    import ipset_c
    with pytest.raises(ValueError):
        ipset_c.IPSet([]).__setstate__(b"5")
    with pytest.raises(ValueError):
        ipset_c.IPSet([]).__setstate__(b"\0"*1024)


def testIPSetWOargs():
    import ipset_c
    with pytest.raises(TypeError):
        ipset_c.IPSet()
