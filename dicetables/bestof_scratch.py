from dicetables import AdditiveEvents, EventsCalculations, DiceTable, Die
from dicetables.eventsbases.integerevents import IntegerEvents
from time import clock
from itertools import product


class BestOfCorrectButSlow(IntegerEvents):

    def __init__(self, total, select, die_size):
        self._dict = self._create_dict(total, select, die_size)

        super(BestOfCorrectButSlow, self).__init__()

    def _create_dict(self, total, select, die_size):
        start = clock()
        select_range = range(select, select*die_size + 1)
        master_dict = {key: 0 for key in select_range}
        allrolls = product(range(1, die_size+1), repeat=total)
        exclude_index = total - select
        for roll_tuple in allrolls:
            key = sum(sorted(roll_tuple)[exclude_index:])
            master_dict[key] += 1
        print('time', clock() - start)
        return master_dict


    def get_dict(self):
        return self._dict.copy()

def add_dict(dict1, dict2):
    out = dict1.copy()
    for key, val in dict2.items():
        out[key] = out.get(key, 0) + val
    return out

if __name__ == '__main__':
    x = BestOfCorrectButSlow(4, 3, 6)

    print(x.get_dict())
    pct = EventsCalculations(x).percentage_points()
    for key, val in pct:
        print('{:>2}: {:>5.2f}'.format(key, val))
    # start = clock()
    # master = {key: [] for key in range(3, 19)}
    # other_master = {key: 0 for key in range(3, 19)}
    # for a in range(1, 7):
    #     for b in range(1, 7):
    #         for c in range(1, 7):
    #             for d in range(1, 7):
    #                 lst = [a, b, c, d]
    #                 key = sum(sorted(lst)[1:])
    #                 val = ','.join([str(val) for val in lst])
    #                 master[key].append(val)
    #                 other_master[key] += 1
    # print(other_master)
    # print(other_master == x.get_dict())
    # for key in range(3, 19):
    #     print('{}:{}'.format(key, master[key]))
    # for key in range(3, 19):
    #     print('{:>2}: {}'.format(key, other_master[key]))
    #
    # master = {key: [] for key in range(2, 13)}
    # other_master = {key: 0 for key in range(2, 13)}
    # for a in range(1, 7):
    #     for b in range(1, 7):
    #         for c in range(1, 7):
    #             for d in range(1, 7):
    #                 lst = [a, b, c, d]
    #                 key = sum(sorted(lst)[2:])
    #                 val = ','.join([str(val) for val in lst])
    #                 master[key].append(val)
    #                 other_master[key] += 1
    # print(other_master)
    # print(other_master == x.get_dict())
    # for key in range(2, 13):
    #     print('{}:{}'.format(key, master[key]))
    # for key in range(2, 13):
    #     print('{:>2}: {}'.format(key, other_master[key]))
    # print(clock() - start)
"""
11
12 21 
22

111
112 121 211
221 212 122
222

11
12 21
22 13 31 
23 32
33

11
21 12 22
13 31 23 32 33



3  111
4  211 121 112
5  311 131 113 221 212 122
6  123 132 213 231 321 312 222
7  322 232 223 331 313 133
8  332 323 233
9  333

2  111
3  211 121 112
4  311 131 113 221 212 122 222
5  322 232 223 
6  331 313 133 332 323 233 333

2  11
3  21 12
4  31 13 22
5  32 23
6  33

22
23 32
33

33


3: 1, 4: 2, 5: 3, 6: 2, 7: 1 +1
      4: 1, 5: 2, 6: 3, 7: 2, 8: 1 +2
            5: 1, 6: 2, 7: 3, 8: 2, 9: 1 +3


1111

"""

