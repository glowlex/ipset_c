import timeit
from ipaddress import ip_network
from random import choices, randint, shuffle
from statistics import median
from typing import Sequence

import netaddr
import pytricia
import radix
import ipset_c

REPEAT_NUMBER = 10_000
REPEAT_REPEAT = 5
NAME_LENGHT = 80
NETS_NUM = 100
IS_IPV6 = False


def test(initNets, actionNets, onlySet: Sequence[int] = (0, 1, 2, 3)):
    ipsetcInit = f'from ipset_c import IPSet; a=IPSet({initNets}); b=IPSet({actionNets}); nets={initNets}; actnets={actionNets};'
    initNetaddr = f'from netaddr import IPSet; a=IPSet({initNets}); b=IPSet({actionNets}); nets={initNets}; actnets={actionNets};'
    initRad = (f'from radix import Radix; a=Radix(); [a.add(x) for x in {initNets}]; b=Radix();'
               f' [b.add(x) for x in {actionNets}]; nets={initNets}; actnets={actionNets};')
    initPt = (f'from pytricia import PyTricia; a=PyTricia({128 if IS_IPV6 else 32});'
              f'[a.insert(x, 0) for x in {initNets}]; b=PyTricia({128 if IS_IPV6 else 32});'
              f' [b.insert(x, 0) for x in {actionNets}]; nets={initNets}; actnets={actionNets};')
    commands = [
        ("IPSet(nets)", f"c=PyTricia({128 if IS_IPV6 else 32}); [c.insert(x, 0) for x in nets]",
         "c=Radix(); [c.add(x) for x in nets]", "IPSet(nets)"),
        ("c=IPSet([]); [c.addCidr(x) for x in nets]",
         f"c=PyTricia({128 if IS_IPV6 else 32}); [c.insert(x, 0) for x in nets]",
         "c=Radix();[c.add(x) for x in nets]", "c=IPSet([]);[c.add(x) for x in nets]"),
        ("a.getCidrs()", "a.keys();", "a.prefixes()", "list(a.iter_cidrs())"),
        ('a.isSuperset(b)', "all(x in a for x in b)",
         "all(a.search_worst(x) for x in b.prefixes())", 'a.issuperset(b)'),
        ('all(a.isContainsCidr(x) for x in actnets)', "all(x in a for x in actnets)",
         "all(a.search_worst(x) for x in actnets)", 'all(x in a for x in actnets)'),
        ('a.isSubset(b)', "all(x in b for x in a)",
         "all(b.search_worst(x) for x in a.prefixes())", 'a.issubset(b)'),
        ('a & b', 'pass', 'pass', 'a & b'),
        ('a | b', "[a.insert(x, 0) for x in b]", "[a.add(x) for x in b.prefixes()]", 'a | b'),
        ('a - b', "for x in b:\n try:\n  a.delete(x)\n except:\n  pass",
         "for x in b.prefixes():\n try:\n  a.delete(x)\n except:\n  pass", 'a - b'),
    ]
    for cStmt, pStmp, rStmt, nStmt in commands:
        tN = [1]*REPEAT_REPEAT
        if 0 in onlySet:
            tN = timeit.repeat(cStmt, ipsetcInit, number=REPEAT_NUMBER, repeat=REPEAT_REPEAT)
            print(f"ipset_c: {cStmt}".ljust(NAME_LENGHT, ' '), f": {median(tN):.6f}")
        if 1 in onlySet:
            tP = timeit.repeat(pStmp, initPt, number=REPEAT_NUMBER, repeat=REPEAT_REPEAT)
            print(f"pytricia: {pStmp[:NAME_LENGHT-7]}".ljust(NAME_LENGHT, ' '),
                  f": {median(tP):.6f} {median(tP)/median(tN):.2f}x")
        if 2 in onlySet:
            tR = timeit.repeat(rStmt, initRad, number=REPEAT_NUMBER, repeat=REPEAT_REPEAT)
            print(f"radix: {rStmt[:NAME_LENGHT-7]}".ljust(NAME_LENGHT, ' '),
                  f": {median(tR):.6f} {median(tR)/median(tN):.2f}x")
        if 3 in onlySet:
            tC = timeit.repeat(nStmt, initNetaddr, number=REPEAT_NUMBER//10, repeat=REPEAT_REPEAT)
            print(f"netaddr: {nStmt}".ljust(NAME_LENGHT, ' '), f": {median(tC)*10:.6f} {median(tC)*10/median(tN):.2f}x")
        print()


def main():
    data = [
        ip_network(
            (randint(0, 2**128-1 if IS_IPV6 else 2**32-1), randint(33, 128) if IS_IPV6 else randint(23, 32)),
            strict=False
        )
        for _ in range(NETS_NUM*2)
    ]
    data = [str(x) for x in data]
    nets = ipset_c.IPSet(data).getCidrs()
    shuffle(nets)
    nets = nets[:NETS_NUM]
    overlapsOrig = choices(nets, k=int(len(nets)*0.3))
    overlaps = []
    for net in overlapsOrig:
        net = ip_network(net, strict=False)
        if randint(0, 2) == 0:
            n = min(randint(1, 4), net.max_prefixlen - net.prefixlen)
            overlaps.extend(choices(list(net.subnets(n)), k=n))
        if randint(0, 2) == 1:
            overlaps.append(net.network_address)
        else:
            overlaps.append(net)
    overlaps = list(map(str, overlaps))
    print(f'{REPEAT_NUMBER=}')
    print(f'no overlapping networks. nets count: {len(nets)}')
    test(nets[:len(nets)//2], nets[len(nets)//2:])
    print()
    print(f'overlapping 30% original {len(nets)} networks. nets count: {len(nets) + len(overlaps)}')
    test(nets, overlaps)


if __name__ == '__main__':
    main()
