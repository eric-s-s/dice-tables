

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
        codes = ['CLASS OVERWRITE', 'MISSING GETTER', 'GETTER OVERWRITE', 'WTF', 'SIGNATURES DIFFERENT']

        msg = 'code: {}, params: {}, factory: {}'.format(error_code, params, self._factory)
        raise EventsFactoryError(msg)
