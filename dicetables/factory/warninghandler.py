import warnings


class EventsFactoryWarning(Warning):
    pass


class EventsFactoryWarningHandler(object):
    def __init__(self, factory):
        self._factory = factory

    def raise_warning(self, warning_code, *params):
        failed_class = params[0]
        msg_start = self._get_msg_start(failed_class, warning_code)
        msg_middle = self._get_error_code_body(params, warning_code)
        instructions = self._get_solution_message()

        warnings.warn(msg_start + msg_middle + instructions, EventsFactoryWarning, stacklevel=5)

    def _get_msg_start(self, failed_class, warning_code):
        msg_start = (
                '\nfactory: {}\n'.format(self._factory) +
                'Warning code: {}\n'.format(warning_code) +
                'Failed to find/add the following class to the EventsFactory - \n' +
                'class: {}\n'.format(failed_class)
        )
        return msg_start

    @staticmethod
    def _get_error_code_body(params, warning_code):
        msg_middle = ''
        if warning_code == 'CONSTRUCT':
            in_factory_class = params[1]
            msg_middle = (
                    '\nClass found in factory: {}\n'.format(in_factory_class) +
                    'attempted object construction using its signature. tried to return instance of original class.\n' +
                    'If that had failed, returned instance of the class found in EventsFactory.\n\n'
            )
        if warning_code == 'CHECK':
            msg_middle = (
                '\nWarning raised while performing check at instantiation\n\n'
            )
        return msg_middle

    def _get_solution_message(self):
        instructions = (
                'SOLUTION:\n' +
                '  class variable: factory_keys = (getter method/property names)\n'
                '  current factory keys are: {}\n'.format(self._factory.get_keys()[1]) +
                '  class variable: new_keys = [(info for each key not already in factory)]\n' +
                '  Each tuple in "new_keys" is (getter_name, default_value, "property"/"method")\n'
                'ex:\n' +
                '  NewClass(Something):\n' +
                '      factory_keys = ("dice_data", "get_dict", "get_thingy", "label")\n' +
                '      new_keys = [("get_thingy", 0, "method"),\n' +
                '                  ("label", "", "property")]\n\n' +
                '      def __init__(self, events_dict, dice_list, new_thingy, label):\n' +
                '          ....\n'
        )
        return instructions
