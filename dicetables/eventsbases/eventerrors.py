"""
Errors raised at instantiation of IntegerEvents and DiceRecord
"""


class InvalidEventsError(ValueError):
    def __init__(self, message='', *args, **kwargs):
        super(InvalidEventsError, self).__init__(message, *args, **kwargs)


class DiceRecordError(ValueError):
    def __init__(self, message='', *args, **kwargs):
        super(DiceRecordError, self).__init__(message, *args, **kwargs)
