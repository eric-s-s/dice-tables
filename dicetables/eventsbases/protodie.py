"""
The abstract class for any die represented by a set of events
"""
from dicetables.eventsbases.integerevents import IntegerEvents


class ProtoDie(IntegerEvents):
    """
    This is the basis for all the dice classes.

    all Die objects need:

    - get_size() - returns: int > 0
    - get_weight() - returns: int >= 0
    - weight_info() - returns: str
    - multiply_str() - returns: str
    - get_dict() - returns: {int: int > 0}
    - __repr__
    - __str__
    """

    def __init__(self):
        super(ProtoDie, self).__init__()

    def get_size(self) -> int:
        raise NotImplementedError

    def get_weight(self) -> int:
        raise NotImplementedError

    def get_dict(self):
        super(ProtoDie, self).get_dict()

    def weight_info(self) -> str:
        """return detailed info of how the die is weighted"""
        raise NotImplementedError

    def multiply_str(self, number: int) -> str:
        """return a string that is the die string multiplied by a number. i.e.,
        D6+1 times 3 is '3D6+3' """
        raise NotImplementedError

    def __str__(self):
        raise NotImplementedError

    def __repr__(self):
        raise NotImplementedError

    def __hash__(self):
        return hash('hash of {!r}, {}, {}, {}'.format(self,
                                                      self.get_size(),
                                                      self.get_weight(),
                                                      self.get_dict()))

    def __lt__(self, other):
        return (
                (self.get_size(), self.get_weight(), sorted(self.get_dict().items()), repr(self)) <
                (other.get_size(), other.get_weight(), sorted(other.get_dict().items()), repr(other))
        )

    def __eq__(self, other):
        return (super(ProtoDie, self).__eq__(other) and
                (self.get_size(), self.get_weight(), repr(self)) ==
                (other.get_size(), other.get_weight(), repr(other))
                )

    def __le__(self, other):
        return self < other or self == other

    def __gt__(self, other):
        return not self <= other

    def __ge__(self, other):
        return self == other or self > other
