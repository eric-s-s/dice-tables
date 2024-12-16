# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added

### Fixed

- readthedocs.org jobs fixed.
- coveralls now fixed with github actions.

### Changed

- updated infrastructure and readme for modern-ness
- use pre-commit
- use pyproject.toml
- run CI/CD with github actions

### Removed

- tox.ini
- travis ci

## [4.0.2] - 2020-12-20

This release is missing in Github

### Added

### Fixed

fixed bug in Parser.  Before `Parser().parse_die("Die(1, 2, 3)")` returned `Die(1)`.  Now, it raises a ParserError.
`Parser().parse_die("ModDie(1, 2, modifier=3")` also raises `ParserError` as does not enough arguments.

### Changed

### Removed

## [4.0.0] - 2020-12-20

This release is missing in Github

closest release is [4.0.1](https://github.com/eric-s-s/dice-tables/releases/tag/4.0.1)

### Added

### Fixed

### Changed

**Breaking change again!**

Revamped DicePools and the Parser.

#### Dice Pools

BestOfDicePool, WorstOfDicePool, UpperMidOfDicePool and LowerMidOfDicePool are now ProtoDie
wrappers around a DicePool object.  :code:`DicePool(Die(6), 4)` is now a non-IntegerEvents
object. It is immutable and can get passed around to various DicePoolCollection objects which
are ProtoDie.  So now it is:

```pycon
>>> import dicetables as dt
>>> pool = dt.DicePool(dt.Die(6), 4)
>>> best_of = dt.BestOfDicePool(pool=pool, select=3)
>>> worst_of = dt.BestOfDicePool(pool=pool, select=3)
>>> super_best_of = dt.BestOfDicePool(pool=pool, select=1)
```

#### Parser

The parser now takes a LimitChecker object.  This defaults to a NoOpLimitChecker
which doesn't check limits and there's a class method to make a parser with a useful
limit checker that is the same as the old behavior.  You can pass in your own limit
checker provided that it inherits from
`dicetables.tools.limit_checker.AbstractLimitChecker`.

```pycon
>>> from dicetables import Parser, Die, LimitsError
>>> no_limit = Parser()
>>> Die(1000) == no_limit.parse_die("Die(1000)")
True
>>> limited = Parser.with_limits()
>>> limited.parse_die("Die(1000)")
Traceback (most recent call last):
File "<stdin>", line 1, in <module>
LimitsError: Max die_size: 500
```

### Removed


## [3.0.0](https://github.com/eric-s-s/dice-tables/releases/tag/v3.0.0) - 2020-09-20

**Python 2 is no longer supported**

### Added

- type hinting

### Fixed

### Changed

### Removed

- python2 support


## [2.6.0](https://github.com/eric-s-s/dice-tables/releases/tag/2.6.0) - 2020-04-04

Last stable release that support python2 and python3

### Added

- `Roller`

### Fixed

### Changed

- [DicePool](http://dice-tables.readthedocs.io/en/stable/the_dice.html#dice-pools)

### Removed


## [2.5.0]

### Added

- `DicePool` die objects:
  - `BestOfDicePool`
  - `WorstOfDicePool`
  - `UpperMidOfDicePool`
  - `LowerMidOfDicePool`

### Fixed

### Changed

- `Parser().add_die_size_limit_kwarg` and `Parser().add_explosions_limit_kwarg` are removed. Use
  `Parser().add_limits_kwarg`
### Removed


## [2.4.0]

### Added

- added `max_power_for_commaed` option to `EventsCalculations.full_table_string`.
- added `max_power_for_commaed` and `min_power_for_fixed_pt` to `EventsCalculations.stats_strings`.

### Fixed

- fixed error where `parse_die_within_limits` failed when using default values for dice.
- `Parser` can parse strings with leading and trailing whitespaces.
- `parse_die_within_limits` now raises `LimitsError`
-
### Changed

### Removed


## [2.2.0]

### Added

- Added `parse_die_within_limits` function to parser. Also added limit values. Changed getters to properties.
-
### Fixed

- Improved ExplodingOn speed.

### Changed

### Removed


## [2.1.0]

### Added

- EventsCalculations added functions log10_points and log10_axes
- New dice: Exploding(other_die, explosions=2), ExplodingOn(other_die, explodes_on, explosions=2)
- New object: `Parser`. It converts strings to dice objects.

### Fixed

### Changed

### Removed
