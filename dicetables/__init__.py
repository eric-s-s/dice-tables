'''All major classes for dicetables can be improted directly as dicetables.Class
or from original module as dicetables.module.Class.  '''

import dicetables.dicestats
import dicetables.longintmath
import dicetables.tableinfo
from dicetables.longintmath import long_int_div, long_int_pow, long_int_times,\
                                        LongIntTable
from dicetables.dicestats import Die, ModDie, WeightedDie, ModWeightedDie,\
                                    DiceTable
from dicetables.tableinfo import full_table_string, graph_pts, \
                                    graph_pts_overflow, stats
