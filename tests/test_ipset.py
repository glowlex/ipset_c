import pickle
import sys
from typing import List

import pytest


@pytest.mark.parametrize("data, expected", [
    ([], []),
    (["0.0.0.0/0"], ["0.0.0.0/0"]),
    (["9.9.9.9"], ["9.9.9.9/32"]),
    (["119.119.4.33/24"], ["119.119.4.0/24"]),
    (["119.119.4.0/24", "119.119.4.64/26"], ["119.119.4.0/24"]),
    (["119.119.4.30/32", "119.119.4.31/32"], ["119.119.4.30/31"]),
    (["0.1.0.0/16", "0.2.0.0/16"], ["0.1.0.0/16", "0.2.0.0/16"]),
    (
        [
            "119.119.4.36/30", "119.119.4.32/32", "119.119.4.33/32",
            "119.119.4.34/32", "119.119.4.35/32", "119.119.4.33/32"
        ],
        ["119.119.4.32/29"]
    ),
    (
        ["12.63.82.64/29", "151.224.192.0/22", "151.224.0.0/16", "46.49.213.136/29"],
        ["12.63.82.64/29", "46.49.213.136/29", "151.224.0.0/16"]
    ),
    (["75.154.88.15/17", "75.154.129.104/17"], ["75.154.0.0/16"]),
    (["62.2.183.127/16", "62.2.205.128/16"], ["62.2.0.0/16"]),
    (["229.126.135.46/16", "229.51.41.149/16", "229.127.63.104/16",], ["229.51.0.0/16", "229.126.0.0/15"]),
    (
        ["f3c9:8af5:873d:3e68:e840:0000::/75", "f546:1c5e:7d5e:ae9e:b2c0::/74", "f546:1c5e:7d5e:ae9e:b2c0::/74"],
        ["f3c9:8af5:873d:3e68:e840::/75", "f546:1c5e:7d5e:ae9e:b2c0::/74"]
    ),
    (
        ["0027:e670:478a:ab08:c845:1260:0f8e:ac25/128", "27:e670:478a:ab08:c845:1260:f8e:ac24/128"],
        ["27:e670:478a:ab08:c845:1260:f8e:ac24/127"]
    ),
    (
        ["0027:e670:478a:ab08:c845:1260:0f8e:ac25/32", "27:e671:478a:ab08:c845:1260:f8e:ac24/32"],
        ["27:e670::/31"]
    ),
    (["::ffff:75.154.88.15/113", "::ffff:75.154.129.104/113"], ["::ffff:75.154.0.0/112"]),
    (
        ["76aa:b7c4:07d3:a831:b5b4:8dab:38de:1300/127", "76aa:b7c4:07d3:a831:b5b4:8dab:38de:1300/120"],
        ["76aa:b7c4:7d3:a831:b5b4:8dab:38de:1300/120"]
    ),
])
def testIPSetCreate(data: List[str], expected):
    import ipset_c
    res = ipset_c.IPSet(data).getCidrs()
    assert res == expected


@pytest.mark.parametrize("data", [
    5,
    [{}],
    ["0.0.0.0/0", 5],
    [["1.1.1.1/33"]],
    None,
    # "9.9.9.9/32",  # PySequence_Fast
])
def testIPSetCreateTypeError(data):
    import ipset_c
    with pytest.raises(TypeError):
        ipset_c.IPSet(data)


@pytest.mark.parametrize("data", [
    ["1.1.1.1/33"],
    ["1.1.1.1/a"],
    ["1.1.1.1/😊"],
    ["1.1.1.1:"],
    ["333.1.1.1/32"],
    ["1.-1.1.1/32"],
    ["1.1.1.1/-32"],
    ["9.9.9.9/"],
    ["1.1.1/32"],
    ["111.111.111.😊"],
    ["test"],
    ["11111111111111111111111111111111111111111111111111111111111"],
    ["27:e670::/129"],
    ["::27:e670::/127"],
    ["27:e1670::/120"],
])
def testIPSetCreateValueError(data):
    import ipset_c
    with pytest.raises(ValueError):
        ipset_c.IPSet(data)


@pytest.mark.parametrize("data, other, expected, expectedGT", [
    ([], ["200.200.77.77/32"], False, False),
    ([], ["0.0.0.0/0"], False, False),
    (["1.0.0.0/24"], ["1.0.0.0/16"], False, False),
    ([], [], True, False),
    (["200.200.77.77/32"], [], True, True),
    (["200.200.77.77/32"], ["200.200.77.77/32"], True, False),
    (["200.200.77.0/24"], ["200.200.77.128/25"], True, True),
    (["200.200.77.0/24", "2.200.77.0/24"], ["2.200.77.128/25", "2.200.77.128/27"], True, True),
    (["2.200.77.0/24", "2.200.77.128/26", "2.200.77.128/29"], ["2.200.77.128/25"], True, True),
    (["0.0.0.0/0"], ["0.0.0.0/0"], True, False),
    (["151.206.175.38/32", "221.248.188.240/29"], ["221.248.188.240/29"], True, True),
    (["1.0.0.0/8", "5.0.0.0/8"], ["1.0.0.0/8", "5.0.0.0/8"], True, False),
    (["::0/0"], ["::0/0"], True, False),
    (["c7f7:d80f::/32"], ["c7f7:d80f:4048:7b1b::/64", "c7f7:d80f:1::/112"], True, True),
])
def testIsSupersetAndGT(data, other, expected, expectedGT):
    import ipset_c
    setD = ipset_c.IPSet(data)
    setO = ipset_c.IPSet(other)
    assert setD.isSuperset(setO) == expected
    assert (setD >= setO) == expected
    assert (setD > setO) == expectedGT


@pytest.mark.parametrize("data, other, expected, expectedLT", [
    ([], [], True, False),
    ([], ["200.200.77.77/32"], True, True),
    ([], ["0.0.0.0/0"], True, True),
    (["1.0.0.0/24"], ["1.0.0.0/16"], True, True),
    (["0.0.0.0/0"], ["0.0.0.0/0"], True, False),
    (["1.0.0.0/8", "5.0.0.0/8"], ["1.0.0.0/8", "5.0.0.0/8"], True, False),
    (["2.200.77.128/25"], ["2.200.77.0/24", "2.200.77.128/26", "2.200.77.128/29"], True, True),
    (["200.200.77.77/32"], ["200.200.77.77/32"], True, False),
    (["200.200.77.77/32"], [], False, False),
    (["200.200.77.0/24"], ["200.200.77.128/25"], False, False),
    (["200.200.77.0/24", "2.200.77.0/24"], ["2.200.77.128/25", "2.200.77.128/27"], False, False),
    (["2.200.77.0/24", "2.200.77.128/26", "2.200.77.128/29"], ["2.200.77.128/25"], False, False),
    (["151.206.175.38/32", "221.248.188.240/29"], ["221.248.188.240/29"], False, False),
    (["::0/0"], ["::0/0"], True, False),
    (["c7f7:d80f:4048:7b1b::/64", "c7f7:d80f:1::/112"], ["c7f7:d80f::/32"], True, True),
])
def testIsSubsetAndLT(data, other, expected, expectedLT):
    import ipset_c
    setD = ipset_c.IPSet(data)
    setO = ipset_c.IPSet(other)
    assert setD.isSubset(setO) == expected
    assert (setD <= setO) == expected
    assert (setD < setO) == expectedLT


@pytest.mark.parametrize("data,cidrs,expected", [
    ([], [], []),
    (["5.5.5.5/32"], [], ["5.5.5.5/32"]),
    ([], ["5.5.5.5/32"], ["5.5.5.5/32"]),
    (["5.5.5.4/31"], ["5.5.5.6/31"], ["5.5.5.4/30"]),
    (["5.5.5.4/31"], ["5.5.5.4/30"], ["5.5.5.4/30"]),
    (
        ["5.5.5.4/30", "5.5.5.12/30", "5.5.5.28/30"],
        ["5.5.5.20/30", "7.7.7.7"],
        ["5.5.5.4/30", "5.5.5.12/30", "5.5.5.20/30", "5.5.5.28/30", "7.7.7.7/32"]
    ),
])
def testIPSetCopyAdd(data, cidrs, expected):
    import ipset_c
    ipset = ipset_c.IPSet(data)
    ipsetCopy = ipset.copy()
    assert ipset.getCidrs() == ipsetCopy.getCidrs(), "should be equal"
    for cidr in cidrs:
        ipsetCopy.addCidr(cidr)
    assert ipset.getCidrs() == data, "origin ipset shouldnt change"
    assert ipsetCopy.getCidrs() == expected


@pytest.mark.parametrize("data,cidrs,expected", [
    ([], [], []),
    (["5.5.5.5/32"], [], ["5.5.5.5/32"]),
    ([], ["5.5.5.5/32"], []),
    (["5.5.5.4/30"], ["5.5.5.6/31"], ["5.5.5.4/31"]),
    (["5.5.5.4/31"], ["5.5.5.4/30"], []),
    (["5.5.5.4/30", "5.5.5.12/30", "5.5.5.28/30"], ["5.5.5.12/30"], ["5.5.5.4/30", "5.5.5.28/30"]),
    (["5.5.5.4/30", "5.5.5.12/30", "5.5.5.28/30"], ["5.5.5.12/31"], ["5.5.5.4/30", "5.5.5.14/31", "5.5.5.28/30"]),
])
def testIPSetCopyAddRemove(data, cidrs, expected):
    import ipset_c
    ipset = ipset_c.IPSet(data)
    ipsetCopy = ipset.copy()
    assert ipset.getCidrs() == ipsetCopy.getCidrs(), "should be equal"
    for cidr in cidrs:
        ipsetCopy.removeCidr(cidr)
    assert ipset.getCidrs() == data, "origin ipset shouldnt change"
    assert ipsetCopy.getCidrs() == expected


@pytest.mark.parametrize("data, add, expected", [
    ([], [], []),
    (["0.0.0.0/0"], ["0.0.0.0/0"], ["0.0.0.0/0"]),
    (["8.8.8.8/32"], [], ["8.8.8.8/32"]),
    ([], ["8.8.8.8/32"], ["8.8.8.8/32"]),
    (["8.8.8.8/32"], ["8.8.8.8/32"], ["8.8.8.8/32"]),
    (["8.8.0.0/17", "8.24.0.0/17", "8.255.2.0/32"], ["8.0.0.0/8"], ["8.0.0.0/8"]),
    (["12.22.0.0/16"], ["12.22.128.0/24"], ["12.22.0.0/16"]),
    (["8.8.0.0/17"], ["8.8.128.0/17"], ["8.8.0.0/16"]),
    (["8.8.0.0/32", "10.8.0.0/32"], ["9.8.128.0/32"], ["8.8.0.0/32", "9.8.128.0/32", "10.8.0.0/32"]),
    (["::/0"], ["::/0"], ["::/0"]),
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


@pytest.mark.parametrize("data, add, expected", [
    ([], [], []),
    (["8.8.8.8/32"], [], ["8.8.8.8/32"]),
    ([], ["8.8.8.8/32"], ["8.8.8.8/32"]),
    (["0.0.0.0/0"], ["0.0.0.0/0"], []),
    (["8.8.8.8/32"], ["8.8.8.8/32"], []),
    (["12.22.128.0/20"], ["12.22.128.0/24"], ["12.22.129.0/24", "12.22.130.0/23", "12.22.132.0/22", "12.22.136.0/21"]),
    (["8.8.0.0/17"], ["8.8.128.0/17"], ["8.8.0.0/16"]),
    (["8.8.0.0/32", "10.8.0.0/32"], ["9.8.128.0/32"], ["8.8.0.0/32", "9.8.128.0/32", "10.8.0.0/32"]),
    (["::/0"], ["::/0"], []),
    (["4444::/16"], ["1111::/16"], ["1111::/16", "4444::/16"])
])
def testIPSetXor(data, add, expected):
    import ipset_c
    ipset = ipset_c.IPSet(data)
    ipsetAdd = ipset_c.IPSet(add)
    ipsetFinal = ipset ^ ipsetAdd
    assert ipsetFinal.getCidrs() == expected


@pytest.mark.parametrize("data, sub, expected", [
    ([], [], []),
    (["8.8.8.8/32"], [], ["8.8.8.8/32"]),
    ([], ["8.8.8.8/32"], []),
    (["1.1.1.1/32"], ["1.1.1.1/32"], []),
    (["8.8.0.0/17", "8.24.0.0/17", "8.255.2.0/32"], ["8.0.0.0/8"], []),
    (["8.8.0.0/16"], ["8.8.0.0/17"], ["8.8.128.0/17"]),
    (["5.5.0.0/16"], ["19.8.0.0/17"], ["5.5.0.0/16"]),
    (
        ["8.8.0.0/31", "10.8.0.0/31", "30.0.0.0/8"],
        ["8.8.0.0/32", "10.8.0.0/32", "30.0.0.0/9"],
        ["8.8.0.1/32", "10.8.0.1/32", "30.128.0.0/9"]
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


@pytest.mark.parametrize("data, intersect, expected", [
    ([], [], []),
    (["6.6.6.0/24"], [], []),
    ([], ["6.6.6.0/24"], []),
    (["6.6.6.0/24"], ["6.6.6.0/24"], ["6.6.6.0/24"]),
    (["6.6.6.0/24"], ["6.6.6.0/28"], ["6.6.6.0/28"]),
    (["6.6.6.0/28"], ["6.6.6.0/24"], ["6.6.6.0/28"]),
    (["17.1.0.0/16", "17.2.0.0/16"], ["0.0.0.0/32", "0.0.0.2/32", "17.0.0.0/8"], ["17.1.0.0/16", "17.2.0.0/16"]),
    (["6.6.6.0/32", "6.6.6.6/32", "6.6.6.255/32"], ["6.6.6.0/24"], ["6.6.6.0/32", "6.6.6.6/32", "6.6.6.255/32"]),
    (["6.6.6.0/24"], ["6.6.6.0/32", "6.6.6.6/32", "6.6.6.255/32"], ["6.6.6.0/32", "6.6.6.6/32", "6.6.6.255/32"]),
    (
        ["6.6.6.0/32", "6.6.6.6/32", "6.6.6.255/32"],
        ["6.6.6.0/24", "7.6.6.0/24", "8.6.6.0/24", "9.6.6.0/24"],
        ["6.6.6.0/32", "6.6.6.6/32", "6.6.6.255/32"]
    ),
    (
        ["6.6.6.0/24", "7.6.6.0/24", "8.6.6.0/24", "9.6.6.0/24"],
        ["6.6.6.0/32", "6.6.6.6/32", "6.6.6.255/32"],
        ["6.6.6.0/32", "6.6.6.6/32", "6.6.6.255/32"]
    ),
    (
        ["0.0.0.0/24", "5.0.0.0/32", "5.0.0.64/32", "5.0.0.128/32"],
        ["0.0.0.0/32", "0.0.0.64/32", "0.0.0.128/32", "5.0.0.0/24"],
        ["0.0.0.0/32", "0.0.0.64/32", "0.0.0.128/32", "5.0.0.0/32", "5.0.0.64/32", "5.0.0.128/32"],
    ),
    (["8dcf:dcd4::/31"], ["8dcf:dcd5::/32"], ["8dcf:dcd5::/32"]),
    (
        ["1::/24", "5::/128", "5::128/128"],
        ["1::/128", "1::128/128", "5::/24"],
        ["1::/128", "1::128/128", "5::/128", "5::128/128"],
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


@pytest.mark.parametrize("data,equal,expected", [
    ([], [], True),
    (["222.222.222.222/32"], ["222.222.222.222/32"], True),
    (["222.222.222.222/32", "122.222.222.222/32"], ["222.222.222.222/32", "122.222.222.222/32"], True),
    (["222.222.222.220/32", "222.222.222.221/32"], ["222.222.222.220/31"], True),
    ([], ["222.222.222.222/32"], False),
    (["222.222.222.222/32"], [], False),
    (["222.222.222.222/32", "122.222.222.222/32"], ["222.222.222.222/32"], False),
    (["0.0.0.0/16"], ["0.0.0.0/24"], False),
    (["0.0.0.0/24"], ["0.0.0.0/16"], False),
    (["b4a0:310f:fc01:2732:b179:b518:01b1:04bd"], ["b4a0:310f:fc01:2732:b179:b518:01b1:04bd/128"], True),
    (["14a0:310f:fc01:2732:b179:b518:01b1:04bd/127"], ["b4a0:310f:fc01:2732:b179:b518:01b1:04bd/127"], False),
    (["b4a0:310f:fc01:2732:b179:b518:01b1:04bd"], ["b4a0:310f:fc01:2732:b179:b518:01b1:04bc/128"], False),
])
def testIPSetEqual(data, equal, expected):
    import ipset_c
    ipset = ipset_c.IPSet(data)
    ipsetEq = ipset_c.IPSet(equal)
    assert (ipset == ipsetEq) == expected
    assert (ipset != ipsetEq) != expected


@pytest.mark.parametrize("data, expected", [
    ([], False),
    (["20.19.18.1"], True),
])
def testIPSetBool(data, expected):
    import ipset_c
    ipset = ipset_c.IPSet(data)
    assert bool(ipset) == expected


@pytest.mark.parametrize("data, expected", [
    ([], 0),
    (["0.0.0.0/0"], 2**32),
    (["156.1.1.1/32"], 1),
    (["156.1.1.1/17"], 2**15),
    (["156.1.1.1/32", "67.9.8.8/30"], 5),
    (["1f5b:f7fe:1c8c:42b0:92ea:10bc:89c9:811a"], 1),
    (["1f5b:f7fe:1c8c:42b0:92ea:10bc:89c9:811a/100"], 2**28),
    (["1f5b:f7fe:1c8c:42b0:92ea:10bc:89c9:811a/0"], 2**128),
    (["1f5b:f7fe:1c8c:42b0:92ea:10bc:89c9:811a/3"], 2**125),
])
def testIPSetLenAndSize(data, expected):
    import ipset_c
    ipset = ipset_c.IPSet(data)
    if expected < sys.maxsize:
        assert len(ipset) == expected
    assert ipset.size == expected


@pytest.mark.parametrize("data,sec", [
    ([], None),
    ([], "32.42.43.43"),
    (["32.32.32.32"], {}),
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
        v = ipset ^ sec
    with pytest.raises(TypeError):
        v = ipset & sec
    with pytest.raises(TypeError):
        ipset_c.IPSet(data).isSubset(sec)
    with pytest.raises(TypeError):
        ipset_c.IPSet(data).isSuperset(sec)
    with pytest.raises(TypeError):
        v = ipset_c.IPSet(data) >= sec
    with pytest.raises(TypeError):
        v = ipset_c.IPSet(data) > sec
    with pytest.raises(TypeError):
        v = ipset_c.IPSet(data) <= sec
    with pytest.raises(TypeError):
        v = ipset_c.IPSet(data) < sec
    with pytest.raises(TypeError):
        ipset_c.IPSet(data).isSubset(sec)
    with pytest.raises(TypeError):
        v = ipset == sec


@pytest.mark.parametrize("data", [
    [],
    ["0.0.0.0/0"],
    ["0.0.0.0/32", "5.8.9.0/24", "255.0.0.0/8", "1.1.1.1/32", "3.3.3.3/32"],
    ["::/0"],
    ["b4a0:310f:fc01:2732:b179:b518:01b1:04bd/128"],
])
def testIPSetPickle(data):
    import ipset_c
    ipset = ipset_c.IPSet(data)
    v = pickle.dumps(ipset)
    assert ipset == pickle.loads(v)
