
# from dicetables.baseevents import AdditiveEvents
# from dicetables.dicetable import DiceTable, RichDiceTable


class EventsFactory(object):
    """

    :args: 'dictionary', 'dice', 'calc_bool'
    """
    getters = {'dictionary': 'get_dict',
               'dice': 'get_dice_items',
               'calc_bool': 'calc_includes_zeroes'}

    empty_args = {'dictionary': {0: 1},
                  'dice': [],
                  'calc_bool': True}

    init_args = {'AdditiveEvents': ('dictionary',),
                 'DiceTable': ('dictionary', 'dice'),
                 'RichDiceTable': ('dictionary', 'dice', 'calc_bool')}

    @classmethod
    def from_dictionary(cls, events, dictionary):
        new_args = []
        new_class = events.__class__
        for arg_type in cls.init_args[new_class.__name__]:
            if arg_type == 'dictionary':
                new_args.append(dictionary)
            else:
                getter = events.__getattribute__(cls.getters[arg_type])
                new_args.append(get_value(getter))
        return new_class(*new_args)

    @classmethod
    def new(cls, events_class):
        args = []
        for arg_type in cls.init_args[events_class.__name__]:
            args.append(cls.empty_args[arg_type])
        return events_class(*args)


def get_value(getter):
    if callable(getter):
        return getter()
    else:
        return getter


class EventsFactory2(object):
    """

    :args: 'dictionary', 'dice', 'calc_bool'
    """
    def __init__(self):
        self.getters = {'dictionary': 'get_dict',
                        'dice': 'get_record_items',
                        'calc_bool': 'calc_includes_zeroes'}

        self.empty_args = {'dictionary': {0: 1},
                           'dice': [],
                           'calc_bool': True}

        self.init_args = {'AdditiveEvents': ('dictionary',),
                          'DiceTable': ('dictionary', 'dice'),
                          'RichDiceTable': ('dictionary', 'dice', 'calc_bool')}

    def add_class(self, class_name, args_tuple):
        self._raise_error_for_bad_arg(args_tuple)
        self.init_args[class_name] = args_tuple

    def _raise_error_for_bad_arg(self, arg_tuple):
        if any(arg not in self.getters for arg in arg_tuple):
            legal_args = list(self.getters.keys())
            raise AttributeError('arg not in list: {}. add arg and getter with add_arg method'.format(legal_args))

    def add_arg(self, arg_name, getter_name, empty_value):
        self.getters[arg_name] = getter_name
        self.empty_args[arg_name] = empty_value

    def from_dictionary(self, events, dictionary):
        pass

    def new(self, events_class):
        args = []
        for arg_type in self.init_args[events_class]:
            args.append(self.empty_args[arg_type])
        return events_class(*args)


# notes class.__bases__[0] = parent.
