'''All major classes for dicetables can be improted directly as dicetables.Class
or from original module as dicetables.module.Class.
DiceTable() is a LongIntTable with a list of dice added by method add_die()
  to see all methods, help(DiceTable) of note,
        stddev, mean, total_frequency
4 dice, Die, ModDie, WeightedDie, ModWeightedDie.
functions for getting info from tables:
    full_table_string, graph_pts, graph_pts_overflow, stats, ascii_graph
'''
from __future__ import absolute_import


from dicetables import dicestats
from dicetables import longintmath
from dicetables import tableinfo
from dicetables.longintmath import long_int_div, long_int_pow, long_int_times,\
                                        LongIntTable
from dicetables.dicestats import Die, ModDie, WeightedDie, ModWeightedDie,\
                                    DiceTable
from dicetables.tableinfo import full_table_string, graph_pts, \
                                    graph_pts_overflow, stats, scinote
