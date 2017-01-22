from dicetables.eventsbases.integerevents import IntegerEvents


class ProtoDie(IntegerEvents):
    """
    base object for any kind of die.


    :all Die objects need: get_size(), get_weight(), weight_info(), multiply_str(), get_dict()
    :get_dict(): must return {int: int >0}

    """
    def __init__(self):
        super(ProtoDie, self).__init__()

    def get_size(self):
        raise NotImplementedError

    def get_weight(self):
        raise NotImplementedError

    def get_dict(self):
        raise NotImplementedError

    def weight_info(self):
        """return detailed info of how the die is weighted"""
        raise NotImplementedError

    def multiply_str(self, number):
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
        if not isinstance(other, ProtoDie):
            return False
        return (
            (self.get_size(), self.get_weight(), sorted(self.get_dict().items()), repr(self)) ==
            (other.get_size(), other.get_weight(), sorted(other.get_dict().items()), repr(other))
        )

    def __ne__(self, other):
        return not self == other

    def __le__(self, other):
        return self < other or self == other

    def __gt__(self, other):
        return not self <= other

    def __ge__(self, other):
        return self == other or self > other