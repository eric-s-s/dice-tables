import pytest

from dicetables import Die, ModDie, WeightedDie, ModWeightedDie
from dicetables.dicepool import DicePool


def test_dice_pool():
    pool = DicePool(Die(2), 3)
    assert pool.die == Die(2)
    assert pool.size == 3

    expected = {
        (1, 1, 1): 1,
        (1, 1, 2): 3,
        (1, 2, 2): 3,
        (2, 2, 2): 1,
    }
    assert pool.rolls == expected


def test_dice_pool_rolls_is_copy():
    pool = DicePool(Die(3), 4)
    assert pool.rolls is not pool.rolls


@pytest.mark.parametrize("size", [-1, 0, 1])
def test_dice_pool_size_must_be_gte_one(size):
    die = Die(2)
    if size < 1:
        with pytest.raises(ValueError, match="Minimum DicePool size is 1"):
            DicePool(die, size)
    else:
        assert DicePool(die, size)


@pytest.mark.parametrize("die", [Die(2), ModDie(2, 0), WeightedDie({1: 1, 2: 1})])
@pytest.mark.parametrize("size", [2, 4, 5])
def test_dice_pool_equality_true(die, size):
    assert DicePool(die, size) == DicePool(die, size)


@pytest.mark.parametrize("die", [Die(2), ModDie(2, 0), WeightedDie({1: 1, 2: 1})])
def test_dice_pool_equality_false_by_die(die):
    size = 3
    test_against = ModWeightedDie({1: 1, 2: 1}, 0)
    assert test_against.get_dict() == die.get_dict()
    assert test_against != die
    assert DicePool(die, size) != DicePool(test_against, size)


def test_dice_pool_equality_false_by_size():
    size = 3
    die = Die(2)
    assert DicePool(die, size) != DicePool(die, size + 1)
    assert DicePool(die, size) != DicePool(die, size - 1)


def test_dice_pool_equality_false_by_type():
    pool = DicePool(Die(2), 3)
    assert pool != 3
    assert 3 != pool


@pytest.mark.parametrize("die_size", [3, 4, 6])
@pytest.mark.parametrize("pool_size", [2, 4, 5])
def test_dice_pool_is_hashable(die_size, pool_size):
    die = Die(die_size)
    pool = DicePool(die, pool_size)
    assert hash(pool) == hash((die, pool_size))


def test_repr():
    die = Die(6)
    pool = DicePool(die, 3)
    expected = "DicePool(Die(6), 3)"
    assert repr(pool) == expected
