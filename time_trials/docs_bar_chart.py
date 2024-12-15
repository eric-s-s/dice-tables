import matplotlib.pyplot as plt

import dicetables as dt

for_bar_chart = (
    dt.DetailedDiceTable.new().add_die(dt.Die(6), 2).add_die(dt.WeightedDie({1: 1, 2: 3}))
)

data_left = list(zip(*for_bar_chart.get_dict().items()))
data_right = for_bar_chart.calc.percentage_axes()

fig, ax1 = plt.subplots()
ax1.bar(*data_left)
ax1.set_xlabel("Rolls")
ax1.set_ylabel("Occurrences")
ax1.tick_params("y", colors="b")

ax2 = ax1.twinx()
ax2.bar(*data_right)
ax2.set_ylabel("Percent Chance")
ax2.tick_params("y", colors="r")

fig.tight_layout()
plt.show()
