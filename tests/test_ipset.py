import sys
import pytest


@pytest.mark.parametrize("data, other, expected", [
    ([], ["200.200.77.77/32"], False),
    ([], ["0.0.0.0/0"], False),
    (["1.0.0.0/24"], ["1.0.0.0/16"], False),
    ([], [], True),
    (["200.200.77.77/32"], [], True),
    (["200.200.77.77/32"], ["200.200.77.77/32"], True),
    (["200.200.77.0/24"], ["200.200.77.128/25"], True),
    (["200.200.77.0/24", "2.200.77.0/24"], ["2.200.77.128/25", "2.200.77.128/27"], True),
    (["2.200.77.0/24", "2.200.77.128/26", "2.200.77.128/29"], ["2.200.77.128/25"], True),
    (["0.0.0.0/0"], ["0.0.0.0/0"], True),
    (["151.206.175.38/32", "221.248.188.240/29"], ["221.248.188.240/29"], True),
    (["1.0.0.0/8", "5.0.0.0/8"], ["1.0.0.0/8", "5.0.0.0/8"], True),
    (["c7f7:d80f::/32"], ["c7f7:d80f:4048:7b1b::/64", "c7f7:d80f:1::/112"], True),
])
def testIsSuperset(data, other, expected):
    import ipset_c
    setD = ipset_c.IPSet(data)
    setO = ipset_c.IPSet(other)
    assert setD.isSuperset(setO) == expected
    assert (setD >= setO) == expected


@pytest.mark.parametrize("data, other, expected", [
    ([], [], True),
    ([], ["200.200.77.77/32"], True),
    ([], ["0.0.0.0/0"], True),
    (["1.0.0.0/24"], ["1.0.0.0/16"], True),
    (["0.0.0.0/0"], ["0.0.0.0/0"], True),
    (["1.0.0.0/8", "5.0.0.0/8"], ["1.0.0.0/8", "5.0.0.0/8"], True),
    (["2.200.77.128/25"], ["2.200.77.0/24", "2.200.77.128/26", "2.200.77.128/29"], True),
    (["200.200.77.77/32"], ["200.200.77.77/32"], True),
    (["200.200.77.77/32"], [], False),
    (["200.200.77.0/24"], ["200.200.77.128/25"], False),
    (["200.200.77.0/24", "2.200.77.0/24"], ["2.200.77.128/25", "2.200.77.128/27"], False),
    (["2.200.77.0/24", "2.200.77.128/26", "2.200.77.128/29"], ["2.200.77.128/25"], False),
    (["151.206.175.38/32", "221.248.188.240/29"], ["221.248.188.240/29"], False),
    (["c7f7:d80f:4048:7b1b::/64", "c7f7:d80f:1::/112"], ["c7f7:d80f::/32"], True),
])
def testIsSubset(data, other, expected):
    import ipset_c
    setD = ipset_c.IPSet(data)
    setO = ipset_c.IPSet(other)
    assert setD.isSubset(setO) == expected
    assert (setD <= setO) == expected


@pytest.mark.parametrize("data,cidrs,expected", [
    ([], [], []),
    (['5.5.5.5/32'], [], ['5.5.5.5/32']),
    ([], ['5.5.5.5/32'], ['5.5.5.5/32']),
    (['5.5.5.4/31'], ['5.5.5.6/31'], ['5.5.5.4/30']),
    (['5.5.5.4/31'], ['5.5.5.4/30'], ['5.5.5.4/30']),
    (
        ['5.5.5.4/30', '5.5.5.12/30', '5.5.5.28/30'],
        ['5.5.5.20/30', '7.7.7.7'],
        ['5.5.5.4/30', '5.5.5.12/30', '5.5.5.20/30', '5.5.5.28/30', '7.7.7.7/32']
    ),
])
def testIPSetCopyAdd(data, cidrs, expected):
    import ipset_c
    ipset = ipset_c.IPSet(data)
    ipsetCopy = ipset.copy()
    assert ipset.getCidrs() == ipsetCopy.getCidrs(), 'should be equal'
    for cidr in cidrs:
        ipsetCopy.addCidr(cidr)
    assert ipset.getCidrs() == data, "origin ipset shouldnt change"
    assert ipsetCopy.getCidrs() == expected


@pytest.mark.parametrize("data,cidrs,expected", [
    ([], [], []),
    (['5.5.5.5/32'], [], ['5.5.5.5/32']),
    ([], ['5.5.5.5/32'], []),
    (['5.5.5.4/30'], ['5.5.5.6/31'], ['5.5.5.4/31']),
    (['5.5.5.4/31'], ['5.5.5.4/30'], []),
    (['5.5.5.4/30', '5.5.5.12/30', '5.5.5.28/30'], ['5.5.5.12/30'], ['5.5.5.4/30', '5.5.5.28/30']),
    (['5.5.5.4/30', '5.5.5.12/30', '5.5.5.28/30'], ['5.5.5.12/31'], ['5.5.5.4/30', '5.5.5.14/31', '5.5.5.28/30']),
])
def testIPSetCopyAddRemove(data, cidrs, expected):
    import ipset_c
    ipset = ipset_c.IPSet(data)
    ipsetCopy = ipset.copy()
    assert ipset.getCidrs() == ipsetCopy.getCidrs(), 'should be equal'
    for cidr in cidrs:
        ipsetCopy.removeCidr(cidr)
    assert ipset.getCidrs() == data, "origin ipset shouldnt change"
    assert ipsetCopy.getCidrs() == expected


@pytest.mark.parametrize('data, add, expected', [
    ([], [], []),
    (['8.8.8.8/32'], [], ['8.8.8.8/32']),
    ([], ['8.8.8.8/32'], ['8.8.8.8/32']),
    (['8.8.8.8/32'], ['8.8.8.8/32'], ['8.8.8.8/32']),
    (['8.8.0.0/17', '8.24.0.0/17', '8.255.2.0/32'], ['8.0.0.0/8'], ['8.0.0.0/8']),
    (['12.22.0.0/16'], ['12.22.128.0/24'], ['12.22.0.0/16']),
    (['8.8.0.0/17'], ['8.8.128.0/17'], ['8.8.0.0/16']),
    (['8.8.0.0/32', '10.8.0.0/32'], ['9.8.128.0/32'], ['8.8.0.0/32', '9.8.128.0/32', '10.8.0.0/32']),
    (["4444::/16"], ["1111::/16"], ["1111::/16", "4444::/16"])
])
def testIPSetUnion(data, add, expected):
    import ipset_c
    ipset = ipset_c.IPSet(data)
    ipsetAdd = ipset_c.IPSet(add)
    ipsetFinal = ipset | ipsetAdd
    ipsetFinal2 = ipset + ipsetAdd
    for final in (ipsetFinal, ipsetFinal2):
        if data != expected:
            assert ipset.getCidrs() != final.getCidrs()
        else:
            assert ipset.getCidrs() == final.getCidrs()
        if add != expected:
            assert ipsetAdd.getCidrs() != final.getCidrs()
        else:
            assert ipsetAdd.getCidrs() == final.getCidrs()
        assert final.getCidrs() == expected


@pytest.mark.parametrize('data, sub, expected', [
    ([], [], []),
    (['8.8.8.8/32'], [], ['8.8.8.8/32']),
    ([], ['8.8.8.8/32'], []),
    (['1.1.1.1/32'], ['1.1.1.1/32'], []),
    (['8.8.0.0/17', '8.24.0.0/17', '8.255.2.0/32'], ['8.0.0.0/8'], []),
    (['8.8.0.0/16'], ['8.8.0.0/17'], ['8.8.128.0/17']),
    (['5.5.0.0/16'], ['19.8.0.0/17'], ['5.5.0.0/16']),
    (
        ['8.8.0.0/31', '10.8.0.0/31', '30.0.0.0/8'],
        ['8.8.0.0/32', '10.8.0.0/32', '30.0.0.0/9'],
        ['8.8.0.1/32', '10.8.0.1/32', '30.128.0.0/9']
    ),
    (["8dcf:dcd5::/31"], ["8dcf:dcd5::/32"], ["8dcf:dcd4::/32"]),
])
def testIPSetSubstruct(data, sub, expected):
    import ipset_c
    ipset = ipset_c.IPSet(data)
    ipsetSub = ipset_c.IPSet(sub)
    ipsetFinal = ipset - ipsetSub
    if data != expected:
        assert ipset.getCidrs() != ipsetFinal.getCidrs()
    else:
        assert ipset.getCidrs() == ipsetFinal.getCidrs()
    if sub != expected:
        assert ipsetSub.getCidrs() != ipsetFinal.getCidrs()
    else:
        assert ipsetSub.getCidrs() == ipsetFinal.getCidrs()
    assert ipsetFinal.getCidrs() == expected


@pytest.mark.parametrize('data, intersect, expected', [
    ([], [], []),
    (['6.6.6.0/24'], [], []),
    ([], ['6.6.6.0/24'], []),
    (['6.6.6.0/24'], ['6.6.6.0/24'], ['6.6.6.0/24']),
    (['6.6.6.0/24'], ['6.6.6.0/28'], ['6.6.6.0/28']),
    (['6.6.6.0/28'], ['6.6.6.0/24'], ['6.6.6.0/28']),
    (['17.1.0.0/16', '17.2.0.0/16'], ['0.0.0.0/32', '0.0.0.2/32', '17.0.0.0/8'], ['17.1.0.0/16', '17.2.0.0/16']),
    (['6.6.6.0/32', '6.6.6.6/32', '6.6.6.255/32'], ['6.6.6.0/24'], ['6.6.6.0/32', '6.6.6.6/32', '6.6.6.255/32']),
    (['6.6.6.0/24'], ['6.6.6.0/32', '6.6.6.6/32', '6.6.6.255/32'], ['6.6.6.0/32', '6.6.6.6/32', '6.6.6.255/32']),
    (
        ['6.6.6.0/32', '6.6.6.6/32', '6.6.6.255/32'],
        ['6.6.6.0/24', '7.6.6.0/24', '8.6.6.0/24', '9.6.6.0/24'],
        ['6.6.6.0/32', '6.6.6.6/32', '6.6.6.255/32']
    ),
    (
        ['6.6.6.0/24', '7.6.6.0/24', '8.6.6.0/24', '9.6.6.0/24'],
        ['6.6.6.0/32', '6.6.6.6/32', '6.6.6.255/32'],
        ['6.6.6.0/32', '6.6.6.6/32', '6.6.6.255/32']
    ),
    (
        ['0.0.0.0/24', '5.0.0.0/32', '5.0.0.64/32', '5.0.0.128/32'],
        ['0.0.0.0/32', '0.0.0.64/32', '0.0.0.128/32', '5.0.0.0/24'],
        ['0.0.0.0/32', '0.0.0.64/32', '0.0.0.128/32', '5.0.0.0/32', '5.0.0.64/32', '5.0.0.128/32'],
    ),
    (["8dcf:dcd4::/31"], ["8dcf:dcd5::/32"], ["8dcf:dcd5::/32"]),
    (
        ['1::/24', '5::/128', '5::128/128'],
        ['1::/128', '1::128/128', '5::/24'],
        ['1::/128', '1::128/128', '5::/128', '5::128/128'],
    ),
])
def testIPSetIntersection(data, intersect, expected):
    import ipset_c
    ipset = ipset_c.IPSet(data)
    ipsetIntersect = ipset_c.IPSet(intersect)
    ipsetFinal = ipset & ipsetIntersect
    assert ipset.getCidrs() == data
    assert ipsetIntersect.getCidrs() == intersect
    assert ipsetFinal.getCidrs() == expected


@pytest.mark.parametrize('data,equal,expected', [
    ([], [], True),
    (['222.222.222.222/32'], ['222.222.222.222/32'], True),
    (['222.222.222.222/32', '122.222.222.222/32'], ['222.222.222.222/32', '122.222.222.222/32'], True),
    (['222.222.222.220/32', '222.222.222.221/32'], ['222.222.222.220/31'], True),
    ([], ['222.222.222.222/32'], False),
    (['222.222.222.222/32'], [], False),
    (['222.222.222.222/32', '122.222.222.222/32'], ['222.222.222.222/32'], False),
    (['0.0.0.0/16'], ['0.0.0.0/24'], False),
    (['0.0.0.0/24'], ['0.0.0.0/16'], False),
    (['b4a0:310f:fc01:2732:b179:b518:01b1:04bd'], ['b4a0:310f:fc01:2732:b179:b518:01b1:04bd/128'], True),
    (['14a0:310f:fc01:2732:b179:b518:01b1:04bd/127'], ['b4a0:310f:fc01:2732:b179:b518:01b1:04bd/127'], False),
])
def testIPSetEqual(data, equal, expected):
    import ipset_c
    ipset = ipset_c.IPSet(data)
    ipsetEq = ipset_c.IPSet(equal)
    assert (ipset == ipsetEq) == expected
    assert (ipset != ipsetEq) != expected


@pytest.mark.parametrize('data, expected', [
    ([], False),
    (['20.19.18.1'], True),
])
def testIPSetBool(data, expected):
    import ipset_c
    ipset = ipset_c.IPSet(data)
    assert bool(ipset) == expected


@pytest.mark.parametrize('data, expected', [
    ([], 0),
    (['0.0.0.0/0'], 2**32),
    (['156.1.1.1/32'], 1),
    (['156.1.1.1/17'], 2**15),
    (['156.1.1.1/32', '67.9.8.8/30'], 5),
    (['1f5b:f7fe:1c8c:42b0:92ea:10bc:89c9:811a'], 1),
    (['1f5b:f7fe:1c8c:42b0:92ea:10bc:89c9:811a/100'], 2**28),
    (['1f5b:f7fe:1c8c:42b0:92ea:10bc:89c9:811a/0'], 2**128),
    (['1f5b:f7fe:1c8c:42b0:92ea:10bc:89c9:811a/3'], 2**125),
])
def testIPSetLenAndSize(data, expected):
    import ipset_c
    ipset = ipset_c.IPSet(data)
    if expected < sys.maxsize:
        assert len(ipset) == expected
    assert ipset.size == expected


@pytest.mark.parametrize('data,sec', [
    ([], None),
    ([], '32.42.43.43'),
    (['32.32.32.32'], {}),
    ([], "200.2005.77.77/32"),
    ([], 8),
    ([], ["200.200.77.77/32"]),
])
def testIPSetTypeError(data, sec):
    import ipset_c
    ipset = ipset_c.IPSet(data)
    with pytest.raises(TypeError):
        v = ipset - sec
    with pytest.raises(TypeError):
        v = ipset + sec
    with pytest.raises(TypeError):
        v = ipset | sec
    with pytest.raises(TypeError):
        v = ipset & sec
    with pytest.raises(TypeError):
        ipset_c.IPSet(data).isSubset(sec)
    with pytest.raises(TypeError):
        ipset_c.IPSet(data).isSuperset(sec)
    with pytest.raises(TypeError):
        v = ipset_c.IPSet(data) >= sec
    with pytest.raises(TypeError):
        v = ipset_c.IPSet(data) <= sec
    with pytest.raises(TypeError):
        ipset_c.IPSet(data).isSubset(sec)
    with pytest.raises(TypeError):
        v = ipset == sec
