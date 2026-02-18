import pytest


def testAddRemove():
    import ipset_c

    ipset = ipset_c.IPSet([])
    ipset.addCidr("1.1.1.1")
    ipset.removeCidr("1.1.1.1")
    ipset.addCidr("1.1.1.3")
    ipset.removeCidr("1.1.1.3")
    assert ipset.size == 0


def testAddRemoveBig():
    import ipset_c

    ipset = ipset_c.IPSet(["0.0.0.0/0"])
    ipset.removeCidr("0.0.0.0")
    assert len(ipset.getCidrs()) == 32
    ipset.addCidr("0.0.0.0")
    assert ipset.getCidrs() == ["0.0.0.0/0"]
    ipset = ipset_c.IPSet(["::/0"])
    ipset.removeCidr("::")
    assert len(ipset.getCidrs()) == 128
    ipset.addCidr("::")
    assert ipset.getCidrs() == ["::/0"]


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
        ipset_c.IPSet([]).__setstate__(b"\0" * 1024)


def testIPSetWOargs():
    import ipset_c

    with pytest.raises(TypeError):
        ipset_c.IPSet()


def testInheritance():
    import ipset_c

    class TestA(ipset_c.IPSet):
        test = "test"

    class TestB(ipset_c.IPSet):
        test = "other"

    a = TestA(["1.1.1.0/31", "5.5.5.4/30"])
    b = TestB(["1.1.1.1/32"])
    b.test = "other1"
    assert a.copy().test == "test"
    assert (a | b).test == "test"
    assert (a ^ b).test == "test"
    assert (a & b).test == "test"
    assert (a - b).test == "test"
    assert (a + b).test == "test"
    assert b.copy().test == "other"
    assert (b | a).test == "other"
    assert (b ^ a).test == "other"
    assert (b & a).test == "other"
    assert (b - a).test == "other"
    assert (b + a).test == "other"
