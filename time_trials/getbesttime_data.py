"""
this module generates a txt file to get dictionaries.  it take a WHILE to run.
"""

from __future__ import print_function

import time
from dicetables.tools.dictcombiner import DictCombiner


def get_input_dict(input_dict_size, use_exponential_occurrences):
    if use_exponential_occurrences:
        input_dict = dict([(event, 1 + 2 ** (event % 1000)) for event in range(input_dict_size)])
    else:
        input_dict = dict([(event, 1 + event % 1000) for event in range(input_dict_size)])
    return input_dict


def get_control_and_indexed_values_times(combine_times, events_tuples, input_dict):
    control_events_action = get_control_action(input_dict, events_tuples)

    combiner = DictCombiner(input_dict)
    to_be_combined = dict(events_tuples)

    indexed_values_start = time.clock()
    combiner.combine_by_indexed_values(to_be_combined, combine_times)
    indexed_values_time = time.clock() - indexed_values_start

    control_start = time.clock()
    control_events_action(to_be_combined, combine_times)
    control_time = time.clock() - control_start
    return control_time, indexed_values_time


def get_control_action(input_dict, events_tuples):
    control_events = DictCombiner(input_dict)
    control_method_str = get_control_method_str(events_tuples)
    control_method_dict = {
        "tuple_list": control_events.combine_by_dictionary,
        "flattened_list": control_events.combine_by_flattened_list,
    }
    control_events_action = control_method_dict[control_method_str]
    return control_events_action


def get_control_method_str(prepped_list):
    if prepped_list[0][1] == 1:
        return "flattened_list"
    else:
        return "tuple_list"


def get_tuple_list(size, many_occurrences=False, step=1):
    if many_occurrences:
        occur = 10
    else:
        occur = 1
    return [(event, occur) for event in range(0, size, step)]


def get_indexed_advantage_ratio(start_dict_size, adds, tuple_list_sizes, many_occurrences):
    events_tuples = get_tuple_list(tuple_list_sizes, many_occurrences)
    input_dict = get_input_dict(start_dict_size, True)

    control_time, indexed_values_time = get_control_and_indexed_values_times(
        adds, events_tuples, input_dict
    )

    return control_time / indexed_values_time


def get_data_list(many_occurrences):
    # titles = ('TIMES', 'OBJ SIZE', 'INPUT SIZE', 'OCCUR MANY', 'RESULT')
    adds = [1, 2, 3, 4, 5, 10, 20, 50, 100, 500, 1000, 2000]
    start_dict_sizes = [1, 10, 50, 100, 200, 500, 1000, 2000, 5000]
    tuple_list_sizes = [2, 3, 4, 6, 8, 10, 20, 50, 100]
    all_data = []
    for add_time in adds:
        print(add_time)
        for start_size in start_dict_sizes:
            for tuple_size in tuple_list_sizes:
                if add_time * tuple_size <= 4000:
                    datum = get_indexed_advantage_ratio(
                        start_size, add_time, tuple_size, many_occurrences
                    )
                    data_line = (
                        float(add_time),
                        float(start_size),
                        float(tuple_size),
                        float(many_occurrences),
                        datum,
                    )
                    all_data.append(data_line)

    return all_data


def dict_maker(data_points):
    threshold = 1.2
    data_map = {}
    for times, obj_size, input_size, many, result in data_points[:]:
        if result >= threshold:
            input_size = int(input_size)
            obj_size = int(obj_size)
            times = int(times)
            second_map = data_map.get(input_size, {})
            data_map[input_size] = second_map
            obj_size_list = second_map.get(times, [])
            obj_size_list.append(obj_size)
            data_map[input_size][times] = obj_size_list

    for input_size in data_map.keys():
        for times in data_map[input_size].keys():
            first_obj_size_at_threshold = min(data_map[input_size][times])
            data_map[input_size][times] = first_obj_size_at_threshold

    return remove_excess_one_obj_size_results(data_map)


def remove_excess_one_obj_size_results(data_map):
    new_data_map = {}
    for input_size in data_map.keys():
        old_times_obj_size_map = data_map[input_size]
        times_obj_size_map = {}
        for times in sorted(old_times_obj_size_map.keys()):
            obj_size = old_times_obj_size_map[times]
            times_obj_size_map[times] = obj_size
            if obj_size == 1:
                break
        new_data_map[input_size] = times_obj_size_map
    return new_data_map


def write_dict_file(file_name):
    lines = []
    for suffix in range(10):
        print("on set {} of 9".format(suffix))
        flat = get_data_list(False)
        many = get_data_list(True)
        flat_str = str(dict_maker(flat))
        many_str = str(dict_maker(many))
        flat_str = "flat_{} = ".format(suffix) + flat_str
        many_str = "many_{} = ".format(suffix) + many_str
        lines.append(flat_str)
        lines.append(many_str)
        lines.append("")
    with open(file_name, "w") as file:
        file.write("\n".join(lines))


def write_two_txt_files_from_original(original_file_name):
    flat, many = convert_text_to_dicts_list(original_file_name)
    if original_file_name.endswith(".txt"):
        original_file_name = original_file_name[:-4]
    new_flat_str = group_dicts(flat)
    new_many_str = group_dicts(many)
    with open(original_file_name + "_flat.txt", "w") as file:
        file.write(new_flat_str)
    with open(original_file_name + "_many.txt", "w") as file:
        file.write(new_many_str)


def convert_text_to_dicts_list(file_name):
    with open(file_name, "r") as file:
        lines = file.read().split("\n")
    flat = []
    many = []
    for line in lines:
        if line.startswith("flat"):
            flat.append(eval(line[9:]))
        if line.startswith("many"):
            many.append(eval(line[9:]))
    return flat, many


def group_dicts(dic_list):
    common_keys = sorted(dic_list[0].keys())
    lines = []
    for input_size in common_keys:
        lines.append("input list: {}".format(input_size))
        times_list = get_all_times_keys_for_one_input_size(dic_list, input_size)
        for dic in dic_list:
            times_obj_size = dic[input_size]
            lines.append("    " + sorted_dict_as_single_line_str(times_obj_size, times_list))
        lines.append("")
    return "\n".join(lines)


def get_all_times_keys_for_one_input_size(dic_list, input_size):
    times_set = set()
    for dic in dic_list:
        times_set = times_set.union(set(dic[input_size].keys()))
    return sorted(times_set)


def sorted_dict_as_single_line_str(dic, key_list):
    width = 10
    blank = " " * width
    out_str = "{"
    for key in key_list:
        if key in dic.keys():
            new = "{}: {}, ".format(key, dic[key])
            out_str += new.ljust(width)
        else:
            out_str += blank
    return out_str


if __name__ == "__main__":
    # write_dict_file('dict_combiner.txt')
    write_two_txt_files_from_original("dict_combiner.txt")
