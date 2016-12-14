"""
sole purpose: the top function - get_string_from_list_of_ints
"""


def get_string_from_list_of_ints(input_list):
    to_use = sorted(input_list)
    list_of_sequences = split_at_gaps_larger_than_one(to_use)
    list_of_sequence_strings = format_sequences(list_of_sequences)
    return ', '.join(list_of_sequence_strings)


def split_at_gaps_larger_than_one(sorted_list):
    list_of_sequences = []
    for value in sorted_list:
        if not list_of_sequences or gap_is_larger_than_one(list_of_sequences, value):
            list_of_sequences.append([value])
        else:
            last_group = list_of_sequences[-1]
            last_group.append(value)
    return list_of_sequences


def gap_is_larger_than_one(list_of_sequences, value):
    max_gap_size = 1
    last_value_of_list = list_of_sequences[-1][-1]
    return value - last_value_of_list > max_gap_size


def format_sequences(list_of_sequences):
    string_list = []
    for sequence in list_of_sequences:
        string_list.append(format_one_sequence(sequence))
    return string_list


def format_one_sequence(sequence):
    first = sequence[0]
    last = sequence[-1]
    if first == last:
        return format_for_sequence_str(first)
    else:
        return '{}-{}'.format(format_for_sequence_str(first), format_for_sequence_str(last))


def format_for_sequence_str(num):
    return '({:,})'.format(num) if num < 0 else '{:,}'.format(num)
