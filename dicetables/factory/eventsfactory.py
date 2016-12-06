
from dicetables.factory.factoryerrorhandler import EventsFactoryErrorHandler
from dicetables.factory.factorywarninghandler import EventsFactoryWarningHandler


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

    def get_bool(self):
        return self._is_property

    def get_name(self):
        return self._method_name

    def __str__(self):
        is_property = {True: 'property', False: 'method'}
        return '{}: "{}", default: {!r}'.format(is_property[self._is_property], self._method_name, self._default_value)

    def __eq__(self, other):
        try:
            return ((self.get_default(), self.get_bool(), self.get_name()) ==
                    (other.get_default(), other.get_bool(), other.get_name()))
        except AttributeError:
            return False

    def __ne__(self, other):
        return not self == other


class LoaderError(AttributeError):
    pass


class Loader(object):
    def __init__(self, factory):
        self.factory = factory

    def load(self, new_class):
        if 'factory_keys' in new_class.__dict__:
            factory_keys = new_class.factory_keys
        else:
            raise LoaderError

        new_keys = ()
        if 'new_keys' in new_class.__dict__:
            new_keys = new_class.new_keys

        for key in new_keys:
            self.factory.add_getter(*key)
        self.factory.add_class(new_class, factory_keys)


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
    def has_getter(getter_key):
        return getter_key in EventsFactory._getters

    @staticmethod
    def get_class_params(events_class):
        return EventsFactory._class_args[events_class.__name__]

    @staticmethod
    def get_getter_string(getter_key):
        return EventsFactory._getters[getter_key].__str__()

    @staticmethod
    def get_keys():
        return sorted(EventsFactory._class_args.keys()), sorted(EventsFactory._getters.keys())

    @staticmethod
    def add_class(events_class, getter_key_words):
        EventsFactory._check_against_factory_classes(events_class, getter_key_words)
        EventsFactory._check_for_missing_getters(events_class, getter_key_words)
        EventsFactory._class_args[events_class.__name__] = getter_key_words

    @staticmethod
    def _check_against_factory_classes(events_class, class_args_tuple):
        if EventsFactory.has_class(events_class) and EventsFactory.get_class_params(events_class) != class_args_tuple:
            EventsFactoryErrorHandler(EventsFactory).raise_error('CLASS OVERWRITE', events_class, class_args_tuple)

    @staticmethod
    def _check_for_missing_getters(events_class, class_args_tuple):
        for getter_key in class_args_tuple:
            if not EventsFactory.has_getter(getter_key):
                EventsFactoryErrorHandler(EventsFactory).raise_error('MISSING GETTER', events_class, getter_key)

    @staticmethod
    def add_getter(getter_key, getter_method, empty_value, type_str='method'):
        is_property = False
        if type_str == 'property':
            is_property = True
        new_getter = Getter(getter_method, empty_value, is_property)
        EventsFactory._check_against_factory_getters(getter_key, new_getter)
        EventsFactory._getters[getter_key] = new_getter

    @staticmethod
    def _check_against_factory_getters(getter_key, new_getter):
        if EventsFactory.has_getter(getter_key) and EventsFactory._getters[getter_key] != new_getter:
            EventsFactoryErrorHandler(EventsFactory).raise_error('GETTER OVERWRITE', getter_key, new_getter)

    @staticmethod
    def check(events_class):
        if not EventsFactory.has_class(events_class):
            try:
                Loader(EventsFactory).load(events_class)
            except LoaderError:
                EventsFactoryWarningHandler(EventsFactory).raise_warning('CHECK', events_class)

    @staticmethod
    def new(events_class):
        in_factory = EventsFactory._get_nearest_factory_class(events_class)
        args = EventsFactory._get_default_args(in_factory)
        return EventsFactory._construct(events_class, in_factory, args)

    @staticmethod
    def _get_default_args(in_factory):
        args = []
        for arg_type in EventsFactory.get_class_params(in_factory):
            args.append(EventsFactory._getters[arg_type].get_default())
        return args

    @staticmethod
    def from_dictionary(events, dictionary):
        passed_in_values = {'dictionary': dictionary}
        return EventsFactory._construct_from(events, passed_in_values)

    @staticmethod
    def from_dictionary_and_dice(events, dictionary, dice):
        passed_in_values = {'dictionary': dictionary, 'dice': dice}
        return EventsFactory._construct_from(events, passed_in_values)

    @staticmethod
    def from_params(events, name_value_param_dict):
        return EventsFactory._construct_from(events, name_value_param_dict)

    @staticmethod
    def _construct_from(events, passed_in_values):

        constructor_class = events.__class__
        in_factory = EventsFactory._get_nearest_factory_class(constructor_class)
        args = EventsFactory._get_args(events, in_factory, passed_in_values)
        return EventsFactory._construct(constructor_class, in_factory, args)

    @staticmethod
    def _get_args(events, in_factory, passed_in_values):
        new_args = []
        for arg_type in EventsFactory.get_class_params(in_factory):
            if arg_type in passed_in_values.keys():
                arg_value = passed_in_values[arg_type]
            else:
                arg_value = EventsFactory._getters[arg_type].get(events)
            new_args.append(arg_value)
        return new_args

    @staticmethod
    def _construct(original_class, in_factory, args):
        try:
            return original_class(*args)
        except (TypeError, AttributeError):
            if original_class == in_factory:
                EventsFactoryErrorHandler(EventsFactory).raise_error('SIGNATURES DIFFERENT', original_class)
            return in_factory(*args)

    @staticmethod
    def _get_nearest_factory_class(events_class):
        if not EventsFactory.has_class(events_class):
            try:
                Loader(EventsFactory).load(events_class)
            except LoaderError:
                return EventsFactory._walk_the_mro(events_class)
        return events_class

    @staticmethod
    def _walk_the_mro(failed_class):
        for parent_class in failed_class.mro():
            if EventsFactory.has_class(parent_class):
                EventsFactoryWarningHandler(EventsFactory).raise_warning('CONSTRUCT', failed_class, parent_class)
                return parent_class
        EventsFactoryErrorHandler(EventsFactory).raise_error('WTF', failed_class)
        return object

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
