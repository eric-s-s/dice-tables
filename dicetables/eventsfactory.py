
import warnings


class ClassNotInFactoryWarning(Warning):
    pass


class EventsFactory(object):
    """

    :args: 'dictionary', 'dice', 'calc_bool'
    """
    def __init__(self):
        self.getters = {'dictionary': 'get_dict',
                        'dice': 'get_dice_items',
                        'calc_bool': 'calc_includes_zeroes'}

        self.empty_args = {'dictionary': {0: 1},
                           'dice': [],
                           'calc_bool': True}

        self.class_args = {'AdditiveEvents': ('dictionary',),
                           'DiceTable': ('dictionary', 'dice'),
                           'RichDiceTable': ('dictionary', 'dice', 'calc_bool')}

    def has_class(self, events_class):
        return events_class.__name__ in self.class_args

    def raise_warning(self, events_class):
        if not self.has_class(events_class):
            msg = ('{} not in Factory.  Will attempt to use parent class.\n'.format(events_class) +
                   'At the class level, please do -\n' +
                   '<parent class>.factory.add_class("CurrentClass", ("parameter kw 1", "parameter kw 2", ..)\n' +
                   'or see documentation at https://github.com/eric-s-s/dice-tables')
            warnings.warn(msg, ClassNotInFactoryWarning, stacklevel=2)

    def add_class(self, class_name, class_args_tuple):
        self._raise_error_for_bad_arg(class_args_tuple)
        if class_name not in self.class_args:
            self.class_args[class_name] = class_args_tuple

    def _raise_error_for_bad_arg(self, arg_tuple):
        if any(arg not in self.getters for arg in arg_tuple):
            legal_args = list(self.getters.keys())
            msg = ('in {}\nin method "add_class"\none or more args not in list: {}'.format(self, legal_args) +
                   '\nadd missing args and getters with add_arg method')
            raise AttributeError(msg)

    def add_arg(self, arg_name, getter_name, empty_value):
        self.getters[arg_name] = getter_name
        self.empty_args[arg_name] = empty_value

    def new(self, events_class):
        args = []
        for arg_type in self.class_args[events_class.__name__]:
            args.append(self.empty_args[arg_type])
        return events_class(*args)

    def from_dictionary(self, events, dictionary):
        passed_in_values = {'dictionary': dictionary}
        return self._make_new_object(events, passed_in_values)

    def from_dictionary_and_dice(self, events, dictionary, dice):
        passed_in_values = {'dictionary': dictionary, 'dice': dice}
        return self._make_new_object(events, passed_in_values)

    def _make_new_object(self, events, passed_in_values):
        new_args = []
        new_class = events.__class__
        for arg_type in self.class_args[new_class.__name__]:
            if arg_type in passed_in_values.keys():
                arg_value = passed_in_values.get(arg_type)
            else:
                getter = events.__getattribute__(self.getters[arg_type])
                arg_value = get_value(getter)
            new_args.append(arg_value)
        return new_class(*new_args)


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
