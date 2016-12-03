
import warnings


class EventsFactoryWarning(Warning):
    pass


class EventsFactoryWarningHandler(object):
    def __init__(self, factory):
        self._factory = factory

    def raise_warning(self, warning_code, *params):
        codes = ['CHECK', 'CONSTRUCT']
        param_names = [param.__name__ for param in params]
        msg = 'factory: {}, code: {}, params: {}'.format(self._factory, warning_code, param_names)
        warnings.warn(msg, EventsFactoryWarning, stacklevel=2)
