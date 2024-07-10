from random import randint, shuffle, choices
from statistics import median
import timeit

import netaddr
import ipset_c
import radix
import pytricia

REPEAT_NUMBER = 10_000
REPEAT_REPEAT = 5
NAME_LENGHT = 50
NETS_NUM = 100


def test(initNets, actionNets, onlySet=None):
    ipsetcInit = f'from ipset_c import IPSet; a=IPSet({initNets}); b=IPSet({actionNets}); nets={initNets};'
    initNetaddr = f'from netaddr import IPSet; a=IPSet({initNets}); b=IPSet({actionNets}); nets={initNets};'
    initRad = (f'from radix import Radix; a=Radix(); [a.add(x) for x in {initNets}]; b=Radix();'
               f' [b.add(x) for x in {actionNets}]; nets={initNets};')
    initPt = (f'from pytricia import PyTricia; a=PyTricia(); [a.insert(x, 0) for x in {initNets}]; b=PyTricia();'
               f' [b.insert(x, 0) for x in {actionNets}]; nets={initNets};')
    commands = [
        ("IPSet(nets)", "c=PyTricia(); [c.insert(x, 0) for x in nets]",
         "c=Radix(); [c.add(x) for x in nets]", "IPSet(nets)"),
        ("c=IPSet([]); [c.addCidr(x) for x in nets]", "c=PyTricia(); [c.insert(x, 0) for x in nets]",
         "c=Radix();[c.add(x) for x in nets]", "c=IPSet([]);[c.add(x) for x in nets]"),
        ('a.isSuperset(b)', "all(x in a for x in b)",
         "all(a.search_best(x) for x in b.prefixes())", 'a.issuperset(b)'),
        ('a.isSubset(b)', "all(x in b for x in a)",
         "all(b.search_best(x) for x in a.prefixes())", 'a.issubset(b)'),
        ('a & b', 'pass', 'pass', 'a & b'),
        ('a | b', "[a.insert(x, 0) for x in b]", "[a.add(x) for x in b.prefixes()]", 'a | b'),
        ('a - b', "for x in b:\n try:\n  a.delete(x)\n except:\n  pass",
         "for x in b.prefixes():\n try:\n  a.delete(x)\n except:\n  pass", 'a - b'),
    ]
    for cStmt, pStmp, rStmt, nStmt in commands:
        tN = [1]*REPEAT_REPEAT
        if onlySet is None or onlySet == 0:
            tN = timeit.repeat(cStmt, ipsetcInit, number=REPEAT_NUMBER, repeat=REPEAT_REPEAT)
            print(f"ipset_c: {cStmt}".ljust(NAME_LENGHT, ' '), f": {median(tN):.6f}")
        if onlySet is None or onlySet == 1:
            tP = timeit.repeat(pStmp, initPt, number=REPEAT_NUMBER, repeat=REPEAT_REPEAT)
            print(f"pytricia: {pStmp[:NAME_LENGHT-7]}".ljust(NAME_LENGHT, ' '),
                  f": {median(tP):.6f} {median(tP)/median(tN):.2f}x")
        if onlySet is None or onlySet == 2:
            tR = timeit.repeat(rStmt, initRad, number=REPEAT_NUMBER, repeat=REPEAT_REPEAT)
            print(f"radix: {rStmt[:NAME_LENGHT-7]}".ljust(NAME_LENGHT, ' '),
                  f": {median(tR):.6f} {median(tR)/median(tN):.2f}x")
        if onlySet is None or onlySet == 3:
            tC = timeit.repeat(nStmt, initNetaddr, number=REPEAT_NUMBER, repeat=REPEAT_REPEAT)
            print(f"netaddr: {nStmt}".ljust(NAME_LENGHT, ' '), f": {median(tC):.6f} {median(tC)/median(tN):.2f}x")
        print()


def main():
    data = [f"{randint(0, 255)}.{randint(0, 255)}.{randint(0, 255)}.{randint(0, 255)}/{randint(25, 32)}"
            for _ in range(NETS_NUM)]
    nets = ipset_c.IPSet(data).getCidrs()
    shuffle(data)
    print(f'{REPEAT_NUMBER=}')
    print(f'no overlapping networks. nets count: {len(nets)}')
    test(nets[:len(nets)//2], nets[len(nets)//2:])
    print()
    print(f'overlapping networks 30%. nets count: {len(nets)}')
    test(nets, choices(nets, k=int(len(nets)*0.3)))


if __name__ == '__main__':
    main()
