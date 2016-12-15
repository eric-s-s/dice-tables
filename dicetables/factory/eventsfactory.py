
from dicetables.factory.errorhandler import EventsFactoryErrorHandler
from dicetables.factory.warninghandler import EventsFactoryWarningHandler
from dicetables.factory.factorytools import StaticDict, Getter
from dicetables.tools.eventerrors import InvalidEventsError, DiceRecordError


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

    __default_getters = {'dictionary': Getter('get_dict', {0: 1}),
                         'dice': Getter('dice_data', {}),
                         'calc_bool': Getter('calc_includes_zeroes', True, is_property=True)}

    __default_class_args = {'AdditiveEvents': ('dictionary',),
                            'DiceTable': ('dictionary', 'dice'),
                            'RichDiceTable': ('dictionary', 'dice', 'calc_bool')}

    _getters = StaticDict(__default_getters)
    _class_args = StaticDict(__default_class_args)

    @classmethod
    def reset(cls):
        cls._getters = StaticDict(cls.__default_getters)
        cls._class_args = StaticDict(cls.__default_class_args)

    @classmethod
    def has_class(cls, events_class):
        return events_class.__name__ in cls._class_args.keys()

    @classmethod
    def has_getter(cls, getter_key):
        return getter_key in cls._getters.keys()

    @classmethod
    def get_class_params(cls, events_class):
        return cls._class_args.get(events_class.__name__)

    @classmethod
    def get_getter_string(cls, getter_key):
        return cls._getters.get(getter_key).__str__()

    @classmethod
    def get_keys(cls):
        return sorted(cls._class_args.keys()), sorted(cls._getters.keys())

    @classmethod
    def add_class(cls, events_class, getter_key_words):
        cls._check_against_factory_classes(events_class, getter_key_words)
        cls._check_for_missing_getters(events_class, getter_key_words)
        cls._class_args = cls._class_args.set(events_class.__name__, getter_key_words)

    @classmethod
    def _check_against_factory_classes(cls, events_class, class_args_tuple):
        if cls.has_class(events_class) and cls.get_class_params(events_class) != class_args_tuple:
            EventsFactoryErrorHandler(cls).raise_error('CLASS OVERWRITE', events_class, class_args_tuple)

    @classmethod
    def _check_for_missing_getters(cls, events_class, class_args_tuple):
        for getter_key in class_args_tuple:
            if not cls.has_getter(getter_key):
                EventsFactoryErrorHandler(cls).raise_error('MISSING GETTER', events_class, getter_key)

    @classmethod
    def add_getter(cls, getter_key, getter_method, empty_value, type_str='method'):
        is_property = False
        if type_str == 'property':
            is_property = True
        new_getter = Getter(getter_method, empty_value, is_property)
        cls._check_against_factory_getters(getter_key, new_getter)
        cls._getters = cls._getters.set(getter_key, new_getter)

    @classmethod
    def _check_against_factory_getters(cls, getter_key, new_getter):
        if cls.has_getter(getter_key) and cls._getters.get(getter_key) != new_getter:
            EventsFactoryErrorHandler(cls).raise_error('GETTER OVERWRITE', getter_key, new_getter)

    @classmethod
    def check(cls, events_class):
        if not cls.has_class(events_class):
            try:
                Loader(cls).load(events_class)
            except LoaderError:
                EventsFactoryWarningHandler(cls).raise_warning('CHECK', events_class)

    @classmethod
    def from_dictionary(cls, events, dictionary):
        passed_in_values = {'dictionary': dictionary}
        return cls._construct_from(events, passed_in_values)

    @classmethod
    def from_dictionary_and_dice(cls, events, dictionary, dice):
        passed_in_values = {'dictionary': dictionary, 'dice': dice}
        return cls._construct_from(events, passed_in_values)

    @classmethod
    def from_params(cls, events, name_value_param_dict):
        return cls._construct_from(events, name_value_param_dict)

    @classmethod
    def _construct_from(cls, events, passed_in_values):
        constructor_class = events.__class__
        factory_class = cls._get_nearest_factory_class(constructor_class)
        args = cls._get_args(events, factory_class, passed_in_values)
        return cls._construct(constructor_class, factory_class, args)

    @classmethod
    def new(cls, events_class):
        factory_class = cls._get_nearest_factory_class(events_class)
        args = cls._get_default_args(factory_class)
        return cls._construct(events_class, factory_class, args)

    @classmethod
    def _get_nearest_factory_class(cls, events_class):
        if not cls.has_class(events_class):
            try:
                Loader(cls).load(events_class)
            except LoaderError:
                return cls._walk_the_mro(events_class)
        return events_class

    @classmethod
    def _walk_the_mro(cls, failed_class):
        for parent_class in failed_class.mro():
            if cls.has_class(parent_class):
                EventsFactoryWarningHandler(cls).raise_warning('CONSTRUCT', failed_class, parent_class)
                return parent_class
        EventsFactoryErrorHandler(cls).raise_error('WTF', failed_class)
        return object

    @classmethod
    def _get_default_args(cls, in_factory):
        args = []
        for getter_key in cls.get_class_params(in_factory):
            getter = cls._getters.get(getter_key)
            args.append(getter.get_default())
        return args

    @classmethod
    def _get_args(cls, events, factory_class, passed_in_values):
        new_args = []
        for getter_key in cls.get_class_params(factory_class):
            if getter_key in passed_in_values.keys():
                arg_value = passed_in_values[getter_key]
            else:
                getter = cls._getters.get(getter_key)
                arg_value = getter.get_from(events)
            new_args.append(arg_value)
        return new_args

    @classmethod
    def _construct(cls, original_class, factory_class, args):
        try:
            return original_class(*args)
        except (TypeError, AttributeError, DiceRecordError, InvalidEventsError):
            if original_class == factory_class:
                EventsFactoryErrorHandler(cls).raise_error('SIGNATURES DIFFERENT', original_class)
            return factory_class(*args)
