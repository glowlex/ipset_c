import concurrent.futures.thread
import pickle
import time

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


def testAddRemoveBig2():
    import ipset_c

    ipset = ipset_c.IPSet(["1.0.0.0/8", "6.6.0.0/16"])
    ipset.removeCidr("6.6.6.6")
    ipset.removeCidr("1.6.6.6")
    ipset.addCidr("6.6.6.6")
    ipset.addCidr("1.6.6.6")
    assert len(ipset.getCidrs()) == 2


def testAddRemoveBig3():
    import ipset_c

    ipset = ipset_c.IPSet(["1.0.0.0/8", "2.255.0.0/16"])
    ipset.removeCidr("2.255.240.6")
    ipset.removeCidr("1.6.6.6")
    ipset.addCidr("2.255.240.6")
    ipset.addCidr("1.6.6.6")
    assert len(ipset.getCidrs()) == 2


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


def testThreading():
    import ipset_c

    data = ipset_c.IPSet(["6.6.0.0/16", "1.0.0.0/8"])
    data2 = ipset_c.IPSet(["1.1.1.1", "6.6.6.6"])
    valid = [
        data.getCidrs(),
        (data - ipset_c.IPSet(["6.6.6.6"])).getCidrs(),
        (data - ipset_c.IPSet(["1.6.6.6"])).getCidrs(),
        (data - ipset_c.IPSet(["1.6.6.6", "6.6.6.6"])).getCidrs(),
    ]

    def worker(*a):
        tm = time.monotonic()
        while time.monotonic() - tm < 5:
            data.removeCidr("6.6.6.6")
            assert data.getCidrs() in valid
            data.removeCidr("1.6.6.6")
            assert data.getCidrs() in valid
            data.addCidr("6.6.6.6")
            assert data.getCidrs() in valid
            data.addCidr("1.6.6.6")
            assert data.getCidrs() in valid
            assert data.isContainsCidr("1.1.1.1")
            assert "1.1.1.1" in data
            assert data.isIntersectsCidr("1.1.1.1")
            assert data.isIntersects(ipset_c.IPSet(["1.1.1.1"]))
            assert data.size
            assert data.isSuperset(ipset_c.IPSet(["1.1.1.1"]))
            assert data > ipset_c.IPSet(["1.1.1.1"])
            assert ipset_c.IPSet(["1.1.1.1"]).isSubset(data)
            assert ipset_c.IPSet(["1.1.1.1"]) < data
            r = data.copy()
            r = data | data2
            r = data ^ data2
            r = data - data2
            r = data & data2
            r = data == data2
            r = data != data2
            r = bool(data)
            v = pickle.dumps(data)
            pickle.loads(v)

    with concurrent.futures.thread.ThreadPoolExecutor(4) as thPool:
        list(thPool.map(worker, range(7)))
