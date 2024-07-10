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
    (['5.5.5.4/30', '5.5.5.12/30', '5.5.5.28/30'], ['5.5.5.20/30', '7.7.7.7'], ['5.5.5.4/30', '5.5.5.12/30', '5.5.5.20/30', '5.5.5.28/30', '7.7.7.7/32']),
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
    (['8.8.0.0/31', '10.8.0.0/31', '30.0.0.0/8'], ['8.8.0.0/32', '10.8.0.0/32', '30.0.0.0/9'], ['8.8.0.1/32', '10.8.0.1/32', '30.128.0.0/9']),
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
    (['6.6.6.0/32', '6.6.6.6/32', '6.6.6.255/32'], ['6.6.6.0/24', '7.6.6.0/24', '8.6.6.0/24', '9.6.6.0/24'], ['6.6.6.0/32', '6.6.6.6/32', '6.6.6.255/32']),
    (['6.6.6.0/24', '7.6.6.0/24', '8.6.6.0/24', '9.6.6.0/24'], ['6.6.6.0/32', '6.6.6.6/32', '6.6.6.255/32'], ['6.6.6.0/32', '6.6.6.6/32', '6.6.6.255/32']),
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
])
def testIPSetLen(data, expected):
    import ipset_c
    ipset = ipset_c.IPSet(data)
    assert len(ipset) == expected


@pytest.mark.parametrize('data,sec', [
    ([], None),
    ([], '32.42.43.43'),
    (['32.32.32.32'], {}),
    ([], "200.2005.77.77/32"),
    ([], 8),
    ([], ["200.200.77.77/32"]),
])
def testIPSetGenericError(data, sec):
    import ipset_c
    ipset = ipset_c.IPSet(data)
    with pytest.raises(ValueError):
        v = ipset - sec
    with pytest.raises(ValueError):
        v = ipset + sec
    with pytest.raises(ValueError):
        v = ipset | sec
    with pytest.raises(ValueError):
        v = ipset & sec
    with pytest.raises(ValueError):
        ipset_c.IPSet(data).isSubset(sec)
    with pytest.raises(ValueError):
        ipset_c.IPSet(data).isSuperset(sec)
    with pytest.raises(ValueError):
        v = ipset_c.IPSet(data) >= sec
    with pytest.raises(ValueError):
        v = ipset_c.IPSet(data) <= sec
    with pytest.raises(ValueError):
        ipset_c.IPSet(data).isSubset(sec)
    with pytest.raises(ValueError):
        v = ipset == sec
