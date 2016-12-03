

class EventsFactoryError(AssertionError):
    pass


class EventsFactoryErrorHandler(object):
    def __init__(self, factory):
        self._factory = factory

    def raise_error(self, error_code, *params):
        """

        class overwrite = events, arg tuple
        missing param = events, getter key
        getter overwrite = getter key, new getter object
        wtf = events
        """
        codes = ['CLASS OVERWRITE', 'MISSING PARAM', 'GETTER OVERWRITE', 'WTF']

        msg = 'code: {}, params: {}, factory: {}'.format(error_code, params, self._factory)
        raise EventsFactoryError(msg)
