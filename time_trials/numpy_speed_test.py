from dicetables.dieevents import Die

from dicetables.dicetable import DiceTable

from time import perf_counter


def time_adds():
    x = DiceTable.new()
    y = DiceTable.new()

    die = Die(6)
    times = 900

    start_regular = perf_counter()
    x.add_die(die, times)
    stop_regular = perf_counter()

    start_new = perf_counter()
    y.combine_numpy(die, times)
    stop_new = perf_counter()

    print(x.get_dict() == y.get_dict())
    print(stop_regular - start_regular)
    print(stop_new - start_new)
    print((stop_new - start_new) / (stop_regular - start_regular))


time_adds()
