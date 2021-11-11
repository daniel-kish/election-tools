# -*- coding: UTF-8 -*-

import last_digit
import numpy as np
import matplotlib.pyplot as plt
import math

election = "duma2016"
db = r"C:\Users\danie\Desktop\elections\data\2021duma\fed\2016-2021.db"

bins = np.arange(0.1, 1.05, 0.05)
pvalues = []

for i in range(0,len(bins)):
    filter_str = 'turnout < {}'.format(bins[i])
    data = last_digit.get_data(db, election,
                               last_digit.default_params + ['ER', 'CPRF'], filter_str)
    pvalue = last_digit.DigitStats(data).chisquare.pvalue
    pvalues.append(pvalue)
    print "{}/{}\r".format(i,len(bins)-1),

plt.style.use('seaborn-colorblind')
plt.yscale("log")

bins = [b*100 for b in bins]
plt.plot(bins, pvalues, marker='o', label=u'УИК с явкой меньше $T_{max}$', zorder=3)
plt.axhline(0.05, color='red', label=u'P-значение = 0.05', zorder=2)
plt.axhline(pvalues[-1], color='green', label=u'Все УИК', zorder=2)

plt.xticks([bins[i] for i in range(0,len(bins), 2)])

plt.title(u'Выборы депутатов ГД 2016 г.\nP-значение в зависимости от явки')
plt.xlabel(u'$T_{max}$,%')
plt.ylabel(u'P-значение')
plt.legend()
plt.grid()
fig = plt.gcf()
fig.set_size_inches(6, 7)
plt.show()

fig.savefig('test2png.png', dpi=200)

# todo: args, automatic colors (maybe), separate data preparation and plotting
