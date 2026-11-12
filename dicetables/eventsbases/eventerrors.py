"""
Errors raised at instantiation of IntegerEvents and DiceRecord
"""


class InvalidEventsError(ValueError):
    def __init__(self, message="", *args, **kwargs):
        super().__init__(message, *args, **kwargs)


class DiceRecordError(ValueError):
    def __init__(self, message="", *args, **kwargs):
        super().__init__(message, *args, **kwargs)
