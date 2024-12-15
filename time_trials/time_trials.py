"""a rather messy module that shows time trials.  this is why i don't use Decimal (i am disappoint)
why i don't use Counter (also disappoint. while it is only marginally slower, it doesn't really improve the code).
they are slower, without really conferring any great advantages.  :("""

from __future__ import print_function

import time
from decimal import Decimal

from dicetables.additiveevents import AdditiveEvents
from dicetables.tools.dictcombiner import DictCombiner
from dicetables.eventsinfo import EventsInformation


def time_trial(times, func, *args):
    start = time.clock()
    for _ in range(times):
        func(*args)
    return time.clock() - start


def combine_trial(times, new_events, method, the_object):
    start = time.clock()
    method_dict = {
        "fastest": the_object.combine,
        "dictionary": the_object.combine_by_dictionary,
        "indexed_values": the_object.combine_by_indexed_values,
        "flattened_list": the_object.combine_by_flattened_list,
    }
    method_dict[method](new_events, times)
    result = time.clock() - start
    return result


def print_combine_trial(times, new_events, method, the_object):
    result = combine_trial(times, new_events, method, the_object)
    info = EventsInformation(new_events)
    start, stop = info.events_range()
    first = info.get_event(start)
    last = info.get_event(stop)
    print(
        "added [{} ... {}]  {} times using {}.  time: {:.3e}".format(
            first, last, times, method, result
        )
    )


def time_trial_output(times, text, func, *args):
    return "call using {} {} times: {:.5}".format(text, times, time_trial(times, func, *args))


# for demonstration that NumberFormatter.format() works better
def format_huge_int_using_decimal(huge_int, dig_len=4):
    return "{:.{}e}".format(Decimal(huge_int), dig_len - 1)


def get_int(question):
    """makes sure user input is an int. quit if "q" """
    while True:
        try:
            answer = raw_input(question + "\n>>>")
        except NameError:
            answer = input(question + "\n>>>")
        if answer == "q":
            raise SystemExit
        try:
            output = int(answer)
            return output
        except ValueError:
            print('must be int OR "q" to quit')
            continue


def get_answer(question, min_val, max_val):
    if max_val > 1000:
        to_format = "{} between {} and {:.2e}"
    else:
        to_format = "{} between {} and {}"
    question = to_format.format(question, min_val, max_val)
    raw_val = get_int(question)
    return min(max_val, (max(min_val, raw_val)))


def fastest_vs_tuple_indexed_ui():
    introduction = """
        this is a hastily cobbled together UI.  If you pick values that are too high,
        you'll have to restart your kernel.
        this shows that fastest is picking the fastest method.
        "q" will quit at any question prompt.
        """

    print(introduction)
    while True:
        print("\n\n")
        start_dict_size = get_answer("pick a start size for AdditiveEvents", 1, 1000)
        start_dict = dict([(event, 2 ** (event % 100)) for event in range(start_dict_size)])

        show_fastest_method_speed = DictCombiner(start_dict)
        flattened_list_control = AdditiveEvents(start_dict)
        flattened_list_fastest = AdditiveEvents(start_dict)
        tuple_list_control = AdditiveEvents(start_dict)
        tuple_list_fastest = AdditiveEvents(start_dict)

        added_events_size = get_answer("how long is new events to combine", 2, 1000)
        added_event_occurrences = get_answer("how many occurrences per event", 2, 10**300)
        gaps = get_answer("how many spaces between value", 0, 2)
        flat_events = AdditiveEvents(dict.fromkeys(range(0, added_events_size, gaps + 1), 1))
        tuple_events = AdditiveEvents(
            dict.fromkeys(range(0, added_events_size, gaps + 1), added_event_occurrences)
        )

        number_of_adds = get_answer("how many times to combine?", 1, 2000)

        print("\n get_fastest_method")
        print(
            time_trial_output(
                1,
                "get_fastest",
                show_fastest_method_speed.get_fastest_combine_method,
                flat_events.get_dict(),
                1,
            )
        )
        print("\nFASTEST with one occurrence")
        print_combine_trial(number_of_adds, flat_events, "fastest", flattened_list_fastest)
        print(EventsInformation(flattened_list_fastest).events_range())

        print("\nFLATTENED_LIST with one occurrence")
        print_combine_trial(number_of_adds, flat_events, "flattened_list", flattened_list_control)
        print(EventsInformation(flattened_list_control).events_range())

        print("\n\nFASTEST with many occurrence")
        print_combine_trial(number_of_adds, tuple_events, "fastest", tuple_list_fastest)
        print(EventsInformation(tuple_list_fastest).events_range())

        print("\nTUPLE_LIST with many occurrence")
        print_combine_trial(number_of_adds, tuple_events, "dictionary", tuple_list_control)
        print(EventsInformation(tuple_list_control).events_range())


if __name__ == "__main__":
    fastest_vs_tuple_indexed_ui()
