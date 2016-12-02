

class EventsFactoryError(AssertionError):
    pass


class EventsFactoryErrorHandler(object):
    def __init__(self, factory):
        self._factory = factory

    def raise_error(self, error_code, *params):
        codes = ['CLASS OVERWRITE', 'MISSING PARAM', 'GETTER OVERWRITE', 'WTF']

        msg = 'code: {}, params: {}, factory: {}'.format(error_code, params, self._factory)
        raise EventsFactoryError(msg)
