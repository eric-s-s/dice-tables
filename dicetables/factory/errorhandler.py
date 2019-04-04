class EventsFactoryError(AssertionError):
    pass


class EventsFactoryErrorHandler(object):
    def __init__(self, factory):
        self._factory = factory
        self._format_kwargs = {}

    def raise_error(self, error_code, *params):
        self.create_format_kwargs(error_code, params)
        msg_header = self.create_header(error_code, params[0])
        msg_body = self.create_error_body(error_code)
        raise EventsFactoryError(msg_header + msg_body)

    def create_format_kwargs(self, error_code, params):
        """
        param_keys = {
            'CLASS OVERWRITE': ('events_class', 'class_keys', 'class_args_tuple'),
            'MISSING GETTER': ('events_class', 'current_getters', 'getter_key'),
            'GETTER OVERWRITE': ('getter_key', 'factory_getter', 'new_getter'),
            'SIGNATURES DIFFERENT': ('events_class', 'signature_in_factory'),
            'WTF': ('events_class', 'factory_classes')
        }
        """
        self._assign_parameters(error_code, params)
        self._assign_kwargs_from_factory_class()

    def _assign_parameters(self, error_code, params):
        param_values = {
            'CLASS OVERWRITE': ('events_class', 'class_args_tuple'),
            'MISSING GETTER': ('events_class', 'getter_key'),
            'GETTER OVERWRITE': ('getter_key', 'new_getter'),
            'SIGNATURES DIFFERENT': ('events_class',),
            'WTF': ('events_class',),
        }
        for index, key_name in enumerate(param_values[error_code]):
            self._format_kwargs[key_name] = params[index]

    def _assign_kwargs_from_factory_class(self):
        factory_classes, current_getters = self._factory.get_keys()
        kwargs_from_factory = {
            'factory_classes': factory_classes,
            'current_getters': current_getters
        }
        if 'events_class' in self._format_kwargs:
            kwargs_from_factory['class_keys'] = self._factory.get_class_params(self._format_kwargs['events_class'])
        if 'getter_key' in self._format_kwargs:
            kwargs_from_factory['factory_getter'] = self._factory.get_getter_string(self._format_kwargs['getter_key'])

        self._format_kwargs.update(kwargs_from_factory)

    def create_header(self, error_code, bad_param):
        msg_start = 'Error Code: {}\nFactory:    {}\nError At:   '.format(error_code, self._factory)
        if error_code == 'GETTER OVERWRITE':
            msg_end = 'Factory Getter Key: {!r}\n'.format(bad_param)
        else:
            msg_end = '{}\n'.format(bad_param)

        return msg_start + msg_end

    def create_error_body(self, error_code):
        explanation = get_explanation(error_code)
        format_str = get_format_string(error_code)
        param_details = format_str.format(**self._format_kwargs)
        return explanation + param_details


def get_explanation(error_code):
    explanation_body = '\nAttempted to {}.\n'
    explanation_variables = {
        'CLASS OVERWRITE': 'add class already in factory but used different factory keys',
        'MISSING GETTER': 'add class with a getter key not in the factory',
        'GETTER OVERWRITE': 'add getter key already in factory but used different parameters',
        'SIGNATURES DIFFERENT': 'construct a class already present in factory, but with a different signature',
        'WTF': 'construct a class unrelated, in any way, to any class in the factory'
    }
    explanation = explanation_body.format(explanation_variables[error_code])
    return explanation


def get_format_string(error_code):
    line_params = {
        'CLASS OVERWRITE': ('class', 'factory class keys', 'input class keys'),
        'MISSING GETTER': ('class', 'factory getters', 'missing getter'),
        'GETTER OVERWRITE': ('getter key', 'factory getter info', 'input getter info'),
        'SIGNATURES DIFFERENT': ('class', 'class signature', 'reset'),
        'WTF': ('factory classes', 'searched MRO')
    }
    return get_lines(line_params[error_code])


def get_lines(line_keys):
    lines = {
        'class': 'Class: {events_class}\n',
        'factory class keys': 'Current Factory Keys: {class_keys}\n',
        'input class keys': 'Keys Passed In:       {class_args_tuple}\n',
        'missing getter': 'Key Passed In:        {getter_key!r}\n',
        'getter key': 'Key: {getter_key!r}\n',
        'factory getter info': 'Factory Parameter:    {factory_getter}\n',
        'input getter info': 'Passed In Parameters: {new_getter}\n',
        'class signature': 'Signature In Factory: {class_keys}\n',
        'reset': 'To reset the factory to its base state, use EventsFactory.reset()\n',
        'factory getters': 'Current Factory Keys: {current_getters}\n',
        'factory classes': 'EventsFactory can currently construct the following classes:\n{factory_classes}\n',
        'searched MRO': ('EventsFactory searched the MRO of {events_class},\n' +
                         'and found no matches to the classes in the factory.\n')
    }
    out_str = ''
    for line in line_keys:
        out_str += lines[line]
    return out_str
