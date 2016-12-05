

class EventsFactoryError(AssertionError):
    pass


class EventsFactoryErrorHandler(object):
    def __init__(self, factory):
        self._factory = factory

    def raise_error(self, error_code, *params):
        """

        class overwrite = events_class, arg tuple
        missing param = events_class, getter key
        param overwrite = getter key, new getter object
        signatures different = events_class
        wtf = events
        """
        msg_header = self.create_header(error_code, params[0])
        msg_body = self.create_error_body(error_code, params)
        raise EventsFactoryError(msg_header + msg_body)

    def create_header(self, error_code, bad_param):
        msg_start = 'Error Code: {}\nFactory:    {}\nError At:   '.format(error_code, self._factory)
        if error_code == 'GETTER OVERWRITE':
            msg_end = 'Factory Getter Key: {!r}\n'.format(bad_param)
        else:
            msg_end = '{}\n'.format(bad_param)

        return msg_start + msg_end

    def create_error_body(self, error_code, params):

        explanation = get_explanation(error_code)
        format_str = get_format_string(error_code)
        kwargs_dict = self._get_kwargs_dict(format_str, params)
        param_details = format_str.format(**kwargs_dict)
        return explanation + param_details

    def _get_kwargs_dict(self, format_str, params):
        kwargs_dict = {'class_keys': self._factory.get_class_params,
                       'getter': self._factory.get_getter_string,
                       'signature': self._factory.get_class_params,
                       'classes': self._factory.get_keys()[0],
                       'getters': self._factory.get_keys()[1]
                       }
        out_put_dict = {'params': params}
        for key_word, value in kwargs_dict.items():
            if '{{{}}}'.format(key_word) in format_str:
                if key_word in ('class_keys', 'getter', 'signature'):
                    value = value(params[0])
                out_put_dict[key_word] = value
        return out_put_dict


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
        'class': 'Class: {params[0]}\n',
        'factory class keys': 'Current Factory Keys: {class_keys}\n',
        'input class keys': 'Keys Passed In:       {params[1]}\n',
        'missing getter': 'Key Passed In:        {params[1]!r}\n',
        'getter key': 'Key: {params[0]!r}\n',
        'factory getter info': 'Factory Parameter:    {getter}\n',
        'input getter info': 'Passed In Parameters: {params[1]}\n',
        'class signature': 'Signature In Factory: {signature}\n',
        'reset': 'To reset the factory to its base state, use EventsFactory.reset()\n',
        'factory getters': 'Current Factory Keys: {getters}\n',
        'factory classes': 'EventsFactory can currently construct the following classes:\n{classes}\n',
        'searched MRO': ('EventsFactory searched the MRO of {params[0]},\n' +
                         'and found no matches to the classes in the factory.\n')
    }
    out_str = ''
    for line in line_keys:
        out_str += lines[line]
    return out_str
