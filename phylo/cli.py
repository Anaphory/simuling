from phylo.phylo import Phylogeny
import lingpy


def run(times=100, signs=1000, fields=50,
        taxa=list('abcdefghijklmnopqrst'.upper()),
        change_range=2000,
        change_min=1900,
        basic_list=list(range(200))):
    """
    Run one phylo-simulation.
    """
    dists1, dists2, dists3 = [], [], []
    for i in range(times):
        # print('[i] analyzing setting {0}'.format(i+1))
        phy = Phylogeny(signs, fields)

        # change range: maximal number of changes, change_min: minimal number
        # of changes (if it's not enough, nothing will change)
        phy.prepare(taxa,
                    change_range=change_range,
                    change_min=change_min)
        # "basic" is the number of words we afterwards use to to infer
        # phylogeny with neighbor-joining
        phy.start(basic=basic_list)
        wl = phy.wordlist()

        wl.add_entries('cog2', 'concept,cogid',
                       lambda x, y: str(x[y[0]]) + '-' + str(x[y[1]]))
        wl.renumber('cog2')
        wl.calculate('diversity', ref='cog2id')

        wl.calculate('tree', ref='cog2id', tree_calc='neighbor')
        t2 = lingpy.upgma(wl.distances, wl.taxa)

        d1 = phy.tree.get_distance(wl.tree, distance='rf')
        d2 = phy.tree.get_distance(t2, distance='rf')
        d3 = phy.tree.get_distance(
            lingpy.basic.tree.Tree(lingpy.basic.tree.random_tree(taxa)),
            distance='rf')
        dists1 += [d1]
        dists2 += [d2]
        dists3 += [d3]

        adist = sum([sum(x) for x in wl.distances]) / (len(wl.distances) ** 2)
        wlen = len(phy.words)
        print(
            "[i] generated tree {0} with distance of "
            "NJ: {1:.2f} vs. UPGMA: {2:.2f} vs. RANDOM: {4:.2f} ({3:.2f}, {5} "
            "DIV: {6:.2f}).".format(
                i+1,
                d1,
                d2,
                adist,
                d3,
                wlen,
                wl.diversity))
    print('Neighbor: {0:.2f}'.format(sum(dists1) / len(dists1)))
    print('UGPMA:    {0:.2f}'.format(sum(dists2) / len(dists2)))
    print('RANDOM:    {0:.2f}'.format(sum(dists3) / len(dists3)))


def parse_dash(dash, datatype, args, default):
    if '-'+dash in args:
        return datatype(args[args.index('-'+dash)+1])
    return default


def main():

    from sys import argv

    times = parse_dash('t', int, argv, 100)
    cmax = parse_dash('-max', int, argv, 1000)
    cmin = parse_dash('-min', int, argv, 500)
    signs = parse_dash('s', int, argv, 1000)
    fields = parse_dash('f', int, argv, 50)
    taxa = parse_dash(
            'l',
            lambda x: list(x.upper()),
            argv,
            list('abcdefghijklmn'.upper())
            )
    basic = parse_dash('b', lambda x: list(range(int(x))), argv, list(range(200)))

    if 'run' in argv:
        run(times=times, signs=signs, fields=fields, taxa=taxa,
            change_range=cmax, change_min=cmin, basic_list=basic)
