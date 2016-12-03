
import warnings


class EventsFactoryWarning(Warning):
    pass


class EventsFactoryWarningHandler(object):
    def __init__(self, factory):
        self._factory = factory

    def raise_warning(self, warning_code, *params):
        failed_class = params[0]
        msg_start = (
            '\nfactory: {}\n'.format(self._factory) +
            'Warning code: {}\n'.format(warning_code) +
            'Failed to find/add the following class to the EventsFactory - \n' +
            'class: {}\n'.format(failed_class)
        )
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
        instructions = (
            'SOLUTION:\n' +
            '  class variable: factory_keys = (names of factory keys for getters)\n'
            '  current factory keys are: {}\n'.format(self._factory.get_keys()[1]) +
            '  class variable: new_keys = [(info for each key not already in factory)]\n' +
            '  Each tuple in "new_keys" is (key_name, getter_name, default_value, "property"/"method")\n'
            '  ex:\n' +
            '  NewClass(Something):\n' +
            '      factory_keys = ("dictionary", "dice", "thingy", "other")\n' +
            '      new_keys = [("thingy", "get_thingy", 0, "method"),\n' +
            '                  ("other", "label", "", "property")]\n\n' +
            '      def __init__(self, events_dict, dice_list, new_thingy, label):\n' +
            '          ....\n'
        )

        warnings.warn(msg_start + msg_middle + instructions, EventsFactoryWarning, stacklevel=2)
