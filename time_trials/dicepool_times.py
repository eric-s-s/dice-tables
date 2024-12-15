"""time trials from DicePool"""

from itertools import cycle
from time import perf_counter

import matplotlib.pyplot as plt

from dicetables.tools.orderedcombinations import count_unique_combination_keys
from dicetables import DicePool, Die


def get_max_combinations(die):
    limits = {2: 600, 3: 8700, 4: 30000, 5: 55000, 6: 70000, 7: 100000, 12: 200000, 30: 250000}
    die_size = die.get_size()
    limit = 0
    for key, val in sorted(limits.items()):
        if key > die_size:
            return limit
        limit = val
    return limit


def make_plots():
    colors = cycle("rbgyc")
    styles = cycle("o*+x")
    for size in [2, 3, 4, 5, 6, 7, 8, 10, 12, 20]:
        style = "{}{}-".format(next(colors), next(styles))
        label = "Die({})".format(size)
        die = Die(size)
        limit = get_max_combinations(die)

        step = 1 + 7 // size
        ys = []
        xs = []
        annotation = []
        pool_size = 2
        pool_entries = count_unique_combination_keys(die, pool_size)
        while pool_entries < limit:
            start = perf_counter()
            DicePool(die, pool_size)
            elapsed = perf_counter() - start

            xs.append(pool_entries)
            ys.append(elapsed)
            annotation.append(str(pool_size))

            pool_size += step
            pool_entries = count_unique_combination_keys(die, pool_size)

        plt.plot(xs, ys, style, label=label)
        if size > 5:
            for label, x, y in zip(annotation, xs, ys):
                plt.annotate(label, xy=(x, y))
    plt.legend()
    plt.xlabel("keys in pool")
    plt.ylabel("time")
    plt.show()


if __name__ == "__main__":
    make_plots()
