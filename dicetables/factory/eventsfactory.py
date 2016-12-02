
from dicetables.factory.factoryerrorhandler import EventsFactoryErrorHandler
from dicetables.factory.factorywarninghandler import EventsFactoryWarningHandler


class ClassNotInFactoryWarning(Warning):
    pass


class FactoryLoadError(AttributeError):
    pass


class Getter(object):
    def __init__(self, method_name, default_value, is_property=False):
        self._method_name = method_name
        self._default_value = default_value
        self._is_property = is_property

    def get_default(self):
        return self._default_value

    def get(self, obj):
        if self._is_property:
            return obj.__getattribute__(self._method_name)
        else:
            return obj.__getattribute__(self._method_name)()

    def __str__(self):
        is_property = {True: 'property', False: 'method'}
        return '{}: "{}", default: {}'.format(is_property[self._is_property], self._method_name, self._default_value)

    def __eq__(self, other):
        return (self.get_default(), self.__str__()) == (other.get_default(), other.__str__())

    def __ne__(self, other):
        return not self == other


class Loader(object):
    def __init__(self, factory):
        self.factory = factory

    def load(self, new_class):
        pass

    # @staticmethod
    # def raise_warning(events_class):
    #     if not EventsFactory.has_class(events_class):
    #         msg = ('{} not in Factory.  Will attempt to use parent class.\n'.format(events_class) +
    #                'At the class level, please do -\n' +
    #                '<parent class>.factory.add_class("CurrentClass", ("parameter kw 1", "parameter kw 2", ..)\n' +
    #                'or see documentation at https://github.com/eric-s-s/dice-tables')
    #         warnings.warn(msg, ClassNotInFactoryWarning, stacklevel=2)
    #
    # @staticmethod
    # def _raise_error_for_bad_arg(arg_tuple):
    #     if any(arg not in EventsFactory.getters for arg in arg_tuple):
    #         legal_args = sorted(EventsFactory.getters.keys())
    # msg = ('in {}\nin method "add_class"\none or more args not in list: {}'.format(EventsFactory, legal_args) +
    #                '\nadd missing args and getters with add_arg method')
    #         raise AttributeError(msg)


class EventsFactory(object):
    _getters = {'dictionary': Getter('get_dict', {0: 1}),
                'dice': Getter('get_dice_items', []),
                'calc_bool': Getter('calc_includes_zeroes', True, is_property=True)}

    _class_args = {'AdditiveEvents': ('dictionary',),
                   'DiceTable': ('dictionary', 'dice'),
                   'RichDiceTable': ('dictionary', 'dice', 'calc_bool')}

    @staticmethod
    def has_class(events_class):
        return events_class.__name__ in EventsFactory._class_args

    @staticmethod
    def has_getter_key(new_class_getter_keys):
        return all(getter in EventsFactory._getters for getter in new_class_getter_keys)

    @staticmethod
    def get_class_params(events_class_name):
        return EventsFactory._class_args[events_class_name]

    @staticmethod
    def update_class(class_name, class_args_tuple):
        if class_name in EventsFactory._class_args and EventsFactory.get_class_params(class_name) != class_args_tuple:
            EventsFactoryErrorHandler(EventsFactory).raise_error('CLASS OVERWRITE', class_name, class_args_tuple)
        EventsFactory._class_args[class_name] = class_args_tuple

    @staticmethod
    def update_getter_key(arg_name, getter_name, empty_value, is_property=False):
        new_getter = Getter(getter_name, empty_value, is_property)
        if EventsFactory.has_getter_key(arg_name) and EventsFactory._getters[arg_name] != new_getter:
            EventsFactoryErrorHandler(EventsFactory).raise_error('GETTER OVERWRITE', getter_name, new_getter)
        EventsFactory._getters[arg_name] = new_getter

    @staticmethod
    def new(events_class):
        in_factory = EventsFactory._get_class_in_factory(events_class)
        args = []
        for arg_type in EventsFactory._class_args[in_factory.__name__]:
            args.append(EventsFactory._getters[arg_type].get_default())
        return EventsFactory._construct(events_class, in_factory, args)

    @staticmethod
    def from_dictionary(events, dictionary):
        passed_in_values = {'dictionary': dictionary}
        return EventsFactory._construct_from(events, passed_in_values)

    @staticmethod
    def from_dictionary_and_dice(events, dictionary, dice):
        passed_in_values = {'dictionary': dictionary, 'dice': dice}
        return EventsFactory._construct_from(events, passed_in_values)

    @staticmethod
    def _construct_from(events, passed_in_values):
        new_args = []
        constructor_class = events.__class__
        in_factory = EventsFactory._get_class_in_factory(constructor_class)
        for arg_type in EventsFactory._class_args[in_factory.__name__]:
            if arg_type in passed_in_values.keys():
                arg_value = passed_in_values[arg_type]
            else:
                arg_value = EventsFactory._getters[arg_type].get(events)

            new_args.append(arg_value)
        return EventsFactory._construct(constructor_class, in_factory, new_args)

    @staticmethod
    def _construct(original_class, in_factory, args):
        try:
            return original_class(*args)
        except AttributeError:
            return in_factory(*args)

    @staticmethod
    def _get_class_in_factory(events_class):
        if not EventsFactory.has_class(events_class):
            try:
                EventsFactory._load_new(events_class)
            except FactoryLoadError:
                return EventsFactory._get_alternates(events_class)
        return events_class

    @staticmethod
    def _load_new(new_class):
        pass

    @staticmethod
    def _get_alternates(failed_class):
        pass

    @staticmethod
    def reset():
        default_getters = {'dictionary': Getter('get_dict', {0: 1}),
                           'dice': Getter('get_dice_items', []),
                           'calc_bool': Getter('calc_includes_zeroes', True, is_property=True)}

        default_class_args = {'AdditiveEvents': ('dictionary',),
                              'DiceTable': ('dictionary', 'dice'),
                              'RichDiceTable': ('dictionary', 'dice', 'calc_bool')}
        EventsFactory._getters = default_getters
        EventsFactory._class_args = default_class_args

    @staticmethod
    def current_state():
        indent = '    '
        out_str = 'CLASSES:\n'
        for key in sorted(EventsFactory._class_args.keys()):
            out_str += '{}{}: {}\n'.format(indent, key, EventsFactory._class_args[key])
        out_str += 'GETTERS:\n'
        for key in sorted(EventsFactory._getters.keys()):
            out_str += '{}{}: {}\n'.format(indent, key, EventsFactory._getters[key])
        return out_str.rstrip('\n')


