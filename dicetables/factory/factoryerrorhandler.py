

class EventsFactoryError(AssertionError):
    pass


class EventsFactoryErrorHandler(object):
    def __init__(self, factory):
        self._factory = factory
