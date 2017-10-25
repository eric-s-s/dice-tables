from dicetables import AdditiveEvents, EventsCalculations, DiceTable, Die, Modifier
from dicetables.eventsbases.integerevents import IntegerEvents
from time import clock
from itertools import product, combinations, permutations, combinations_with_replacement


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
            # key = sum(roll_tuple) - min(roll_tuple)  only works when just removing one die.
            master_dict[key] += 1
        print('time', clock() - start)
        return master_dict


    def get_dict(self):
        return self._dict.copy()

from bisect import bisect, insort
from functools import partial
def get_tup(input_tup, new_val):
    index = bisect(input_tup, new_val)
    return input_tup[:index] + (new_val, ) + input_tup[index:]

def get_tup_alt(input_tup, new_val):
    lst = list(input_tup)
    insort(lst, new_val)
    return tuple(lst)



def gen_insort(number, size):
    start = {(): 1}
    for num in range(number):
        new_dict = dict.fromkeys(combinations_with_replacement(range(1, size+1), num+1), 0)
        for key, val in start.items():
            for roll in range(1, size+1):
                index = bisect(key, roll)
                new_key = key[:index] + (roll,) + key[index:]
                new_dict[new_key] = val + new_dict[new_key]
        start = new_dict.copy()
    return start


def gen_insort_alt(number, size):
    keys = combinations_with_replacement(range(1, size+1), number)
    return {the_key: get_count(the_key) for the_key in keys}


from math import factorial
def get_count(lst):
    """simple calculation over tuple of sorted values and possibly repeating value
    to tell number of unique permutations.  so get_count((1, 2, 3)) = 3!.  get_count((1, 2, 2, 3, 3)) = 5!/(2!*2!)"""
    answer = factorial(len(lst))
    current = lst[0]
    count = 0
    for el in lst:
        if el == current:
            count += 1
        else:
            current = el
            answer //= factorial(count)
            count = 1
    return answer // factorial(count)

#  no good
from itertools import groupby
def get_count_alt(lst):
    answer = factorial(len(lst))
    for el, lst in groupby(lst):
        answer //= factorial(len(list(lst)))
    return answer





class BestOfExp(IntegerEvents):

    def __init__(self, total, select, die_size):
        self._dict = self._create_dict(total, select, die_size)

        super(BestOfExp, self).__init__()

    def get_dict(self):
        return self._dict.copy()

    def _create_dict(self, total, select, die_size):
        start = clock()
        select_range = range(select, select * die_size + 1)
        master_dict = {key: 0 for key in select_range}
        combos = gen_insort_alt(total, die_size)
        rm_index = total - select
        for roll_lst, num in combos.items():
            key = sum(roll_lst[rm_index:])
            master_dict[key] += num
        new_time = clock() - start
        print('exp time', new_time)
        return master_dict




class BestOfExperiment(IntegerEvents):

    def __init__(self, total, select, die_size):
        self._dict = self._create_dict(total, select, die_size)

        super(BestOfExperiment, self).__init__()

    def _create_dict(self, total, select, die_size):
        base_dict = dict.fromkeys(range(1, die_size+1), 1)
        master = {}
        for smallest in base_dict.keys():
            new_dict = {key: val for key, val in base_dict.items() if key >= smallest}
            base_add = AdditiveEvents.new().combine(AdditiveEvents(new_dict), total).get_dict()

            to_add = {key-smallest: val for key, val in base_add.items()}
            master = add_dict(master, to_add)

        return master

    def get_dict(self):
        return self._dict.copy()



def add_dict(dict1, dict2):
    out = dict1.copy()
    for key, val in dict2.items():
        out[key] = out.get(key, 0) + val
    return out


def get_count2(lst):
    """bad idea"""
    count = 0
    already = []
    for val in permutations(lst, len(lst)):
        if val not in already:
            already.append(val)
            count += 1
    return count








if __name__ == '__main__':
    #  3D3 = {3: 1, 4: 3, 5: 6, 6: 7, 7: 6, 8: 3, 9: 1}
    #  best 2 of 3D3 = {2: 1, 3: 3, 4: 7, 5: 9, 6: 7}

    #  2D3 = {2: 1, 3: 2, 4: 3, 5: 2, 6: 1}
    #  2D2 + 2 = {4: 1, 5: 2, 6: 1}
    #  2D1 + 4 = {6: 1}
    #  D2 + D3 + 1 = {3: 1, 4: 2, 5: 2, 6: 1}
    #  D2 + D1 + 3 = {5: 1, 6: 1} times two?
    #  D3 + D1 + 2 = {4: 1, 5: 1, 6: 1}
    x = BestOfCorrectButSlow(4, 3, 8)
    y = BestOfExp(4, 3, 8)

    print(x.get_dict())
    print(y.get_dict())
    pct = EventsCalculations(x).percentage_points()
    for key, val in pct:
        print('{:>2}: {:>5.2f}'.format(key, val))

    for key in range(3, 10):  # keys in 3D3
        number_of_ones = 0
        for dice in range(1, 4):  # 1, 2, or 3 dice containing ones
            if dice + 3 * (3 - dice) >= key:
                number_of_ones += 1
        print('key ', key, 'ones ', number_of_ones)
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
    start = clock()
    for val in combinations_with_replacement([1, 2, 3, 4, 5, 6, 7, 8], 5):
        get_count2(val)
    new_try = clock() - start

    start = clock()
    x = product([1, 2, 3, 4, 5, 6, 7, 8], repeat=5)
    for val in x:
        sorted(val)
        sum(val)
    sorting = clock() - start

    start = clock()
    x = product([1, 2, 3, 4, 5], repeat=5)
    for val in x:
        min(val)
        sum(val)
    minning = clock() - start

    print(new_try, sorting, sep='\n', end='\n\n')

    import matplotlib.pyplot as plt
    from itertools import cycle
    colors = cycle('rbg')
    for size in range(3, 10):
        color = next(colors)
        name = 'size: {}'.format(size)
        times = []
        for num in range(1, 38 - size*3):
            start = clock()
            to_test = gen_insort(size, num)
            other = gen_insort_alt(size, num)
            if to_test != other:
                print(to_test, other, sep='\n', end='\n\n\n')
            to_add = clock() - start
            times.append(to_add)


        plt.plot(times, '{}-o'.format(color), label=name)
    plt.grid(True)
    plt.legend()
    plt.show()


    # for size in range(1, 8):
    #     for val in combinations_with_replacement(range(1, size+1), size):
    #         print(val, get_count(val), sep=': ')

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


1: 1, 2: 1, 3: 1, 
      2: 1, 3: 1, 4: 1
            3: 1, 4: 1, 5: 1
                  4: 1, 5: 1, 6: 1




"""

