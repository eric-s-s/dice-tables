from dicetables.dieevents import Die

from dicetables.dicetable import DiceTable


from time import perf_counter


def time_adds():
    x = DiceTable.new()
    y = DiceTable.new()
    start_regular = perf_counter()
    x.add_die(Die(6), 200)
    stop_regular = perf_counter()

    start_new = perf_counter()
    y.combine_numpy(Die(6), 200)
    stop_new = perf_counter()

    print(x.get_dict() == y.get_dict())
    print(stop_regular - start_regular)
    print(stop_new - start_new)
    print((stop_new - start_new) / (stop_regular - start_regular))

time_adds()
