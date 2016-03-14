'''All major classes for dicetables can be improted directly as dicetables.Class
or from original module as dicetables.module.Class.  '''

import dicetables.graphing_and_printing
import dicetables.dicestats
import dicetables.longintmath
from dicetables.longintmath import long_int_div, long_int_pow, long_int_times,\
                                        LongIntTable
from dicetables.dicestats import Die, ModDie, WeightedDie, ModWeightedDie,\
                                    DiceTable
