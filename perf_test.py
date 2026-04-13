import timeit
from ipaddress import ip_network
from random import choices, randint, shuffle
from statistics import mean as median
from typing import Sequence

from py_markdown_table.markdown_table import markdown_table

import netaddr
import pytricia
import radix
import ipset_c

IS_PRINT_TABLE = False
ONLY_SET = (0, 1, 2)
REPEAT_NUMBER = 10
REPEAT_REPEAT = 1
NAME_LENGHT = 80
NETS_NUM = 100_000
IS_IPV6 = True


def test(initNets, actionNets, onlySet: Sequence[int] = ONLY_SET):
    ipsetcInit = f"from ipset_c import IPSet; nets={initNets}; actnets={actionNets}; a=IPSet(nets); b=IPSet(actnets);"
    initNetaddr = f"from netaddr import IPSet; nets={initNets}; actnets={actionNets}; a=IPSet(nets); b=IPSet(actnets);"
    initRad = (
        "from radix import Radix; a=Radix(); b=Radix();"
        f"nets={initNets}; actnets={actionNets};"
        "\nfor x in nets: a.add(x);"
        "\nfor x in actnets: b.add(x);"
    )
    initPt = (
        f"from pytricia import PyTricia; a=PyTricia({128 if IS_IPV6 else 32}); b=PyTricia({128 if IS_IPV6 else 32});"
        f"nets={initNets}; actnets={actionNets};"
        "\nfor x in nets: a[x]=0;"
        "\nfor x in actnets: b[x]=0;"
    )
    commands = [
        (
            "IPSet(nets)",
            f"c=PyTricia({128 if IS_IPV6 else 32});\nfor x in nets: c[x] = 0",
            "c=Radix();\nfor x in nets: c.add(x)",
            "IPSet(nets)",
            "IPSet(nets)",
        ),
        (
            "c=IPSet([]);\nfor x in nets: c.addCidr(x)",
            f"c=PyTricia({128 if IS_IPV6 else 32});\nfor x in nets: c[x] = 0",
            "c=Radix();\nfor x in nets: c.add(x)",
            "c=IPSet([]);\nfor x in nets: c.add(x)",
            "c=IPSet([]);\nfor x in nets: c.addCidr(x)",
        ),
        ("a.getCidrs()", "a.keys();", "a.prefixes()", "list(a.iter_cidrs())", "a.getCidrs()"),
        (
            "a.isSuperset(b)",
            "all(x in a for x in b)",
            "all(a.search_worst(x) for x in b.prefixes())",
            "a.issuperset(b)",
            "a.isSuperset(b)",
        ),
        (
            "all(a.isContainsCidr(x) for x in actnets)",
            "all(x in a for x in actnets)",
            "all(a.search_worst(x) for x in actnets)",
            "all(x in a for x in actnets)",
            "all(a.isContainsCidr(x) for x in actnets)",
        ),
        (
            "a.isSubset(b)",
            "all(x in b for x in a)",
            "all(b.search_worst(x) for x in a.prefixes())",
            "a.issubset(b)",
            "a.isSubset(b)",
        ),
        (
            "a.isIntersects(b)",
            "bool(any(x in a for x in b) or any(x in b for x in a))",
            "bool(any(a.search_worst(x) for x in b.prefixes()) or any(b.search_worst(x) for x in a.prefixes()))",
            "not a.isdisjoint(b)",
            "a.isIntersects(b)",
        ),
        (
            "a & b",
            f"c=PyTricia({128 if IS_IPV6 else 32});\nfor x in a.keys():\n if x in b: c[x] = 0\nfor x in b.keys():\n if x in a: c[x] = 0",
            "c=Radix();\nfor x in a.prefixes():\n if b.search_worst(x): c.add(x)\nfor x in b.prefixes():\n if a.search_worst(x): c.add(x)",
            "a & b",
            "a & b",
        ),
        ("a ^ b", "pass", "pass", "a ^ b", "a ^ b"),
        (
            "a | b",
            f"c=PyTricia({128 if IS_IPV6 else 32});\nfor x in a: c[x] = 0\nfor x in b: c[x] = 0",
            "c=Radix();\nfor x in a.prefixes(): c.add(x)\nfor x in b.prefixes(): c.add(x)",
            "a | b",
            "a | b",
        ),
        (
            "a - b",
            f"c=PyTricia({128 if IS_IPV6 else 32});\nfor x in a: c[x] = 0\nfor x in b:\n try:\n  del c[x]\n except:\n  pass",
            "c=Radix();\nfor x in a.prefixes(): c.add(x)\nfor x in b.prefixes():\n try:\n  c.delete(x)\n except:\n  pass",
            "a - b",
            "a - b",
        ),
    ]
    res = []
    nameMap = ["ipset_c", "pytricia", "radix", "netaddr", "ipset_c_new"]

    def printRes(name: str, op: str, tms: list, tn: list):
        op = op.replace("\n", "")
        print(
            f"{name}: {op[: NAME_LENGHT - 7]}".ljust(NAME_LENGHT, " "),
            f": {median(tms):.6f} {median(tms) / median(tn):.2f}x",
        )

    for cStmt, pStmp, rStmt, nStmt, cStmtNew in commands:
        tN = [1] * REPEAT_REPEAT
        tP = [0]
        tC = [0]
        tR = [0]
        tNn = [0]
        if 0 in onlySet:
            tN = timeit.repeat(cStmt, ipsetcInit, number=REPEAT_NUMBER, repeat=REPEAT_REPEAT)
            printRes(nameMap[0], cStmt, tN, tN)
        if 1 in onlySet:
            tP = timeit.repeat(pStmp, initPt, number=REPEAT_NUMBER, repeat=REPEAT_REPEAT)
            printRes(nameMap[1], pStmp, tP, tN)
        if 2 in onlySet:
            tR = timeit.repeat(rStmt, initRad, number=REPEAT_NUMBER, repeat=REPEAT_REPEAT)
            printRes(nameMap[2], rStmt, tR, tN)
        if 3 in onlySet:
            tC = timeit.repeat(nStmt, initNetaddr, number=REPEAT_NUMBER // 10, repeat=REPEAT_REPEAT)
            tC = [x * 10 for x in tC]
            printRes(nameMap[3], nStmt, tC, tN)
        if 4 in onlySet:
            tNn = timeit.repeat(cStmtNew, ipsetcInit, number=REPEAT_NUMBER, repeat=REPEAT_REPEAT)
            printRes(nameMap[4], cStmtNew, tNn, tN)
        print()
        run = []
        for i, [op, tm] in enumerate(((cStmt, tN), (pStmp, tP), (rStmt, tR), (nStmt, tC), (cStmtNew, tNn))):
            if i not in onlySet:
                continue
            run.append(
                {
                    "operation": op.replace("\n", ""),
                    "name": nameMap[i],
                    "time": tm if op != "pass" else [],
                }
            )
        res.append(run)
    return res


def printTable(data):
    res = []
    for run in data:
        tN = median(run[0]["time"])
        r = {
            "operation": run[-1]["operation"].replace("|", "\\|"),
        }
        for d in run:
            r[d["name"]] = f"{median(d['time']) / tN:.2f}" if d["time"] else "x"
        res.append(r)
    mt = markdown_table(res)
    mt.set_params(row_sep="markdown", padding_weight="right")
    mt.quote = False
    print(mt.get_markdown())
    print()


def main():
    data = [
        ip_network(
            (randint(0, 2**128 - 1 if IS_IPV6 else 2**32 - 1), randint(33, 128) if IS_IPV6 else randint(23, 32)),
            strict=False,
        )
        for _ in range(NETS_NUM * 2)
    ]
    data = [str(x) for x in data]
    nets = ipset_c.IPSet(data).getCidrs()
    shuffle(nets)
    nets = nets[:NETS_NUM]
    overlapsOrig = choices(nets, k=int(len(nets) * 0.3))
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
    print(f"IPv{6 if IS_IPV6 else 4}")
    print(f"{REPEAT_NUMBER=}")
    print(f"no overlapping networks. nets count: {len(nets)}")
    res_no = test(nets[: len(nets) // 2], nets[len(nets) // 2 :])
    print()
    print(f"overlapping 30% original {len(nets)} networks. nets count: {len(nets) + len(overlaps)}")
    res_part = test(nets, overlaps)
    print(f"overlapping 100% original {len(nets)} networks. nets count: {len(nets) + len(nets[len(nets) // 2 :])}")
    res_full = test(nets, nets[len(nets) // 2 :])
    if IS_PRINT_TABLE:
        printTable(res_no)
        printTable(res_part)
        printTable(res_full)
        res_part = [[{**y, "operation": y["operation"] + " olap 30% "} for y in x] for x in res_part]
        res_full = [[{**y, "operation": y["operation"] + " olap full"} for y in x] for x in res_full]
        res_combine = [y for x in zip(res_no, res_part, res_full) for y in x]
        printTable(res_combine)


if __name__ == "__main__":
    main()
