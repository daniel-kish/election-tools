# -*- coding: UTF-8 -*-

import argparse
import last_digit
import matplotlib.pyplot as plt
from collections import Counter
import math


if __name__ == "__main__":
    parser = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument("--db", help="Path to results DB", required=True)
    parser.add_argument("--election", help="Election name", required=True)
    args = parser.parse_args()
    
    # db = r"C:\Users\danie\Desktop\elections\data\2021duma\fed\2016-2021.db"

    data = last_digit.get_data(args.db, args.election, last_digit.default_params + ['ER', 'CPRF'], '')

    data = filter(lambda x: x > 0, data)

    lead_digits = [int(str(x)[0]) for x in data]

    counter = Counter(lead_digits)
    numbers_total = sum(counter.values())
    digits = [k for k,_ in counter.items()]
    freqs = [float(v)/numbers_total for _,v in counter.items()]
    benfords = [math.log10(float(d + 1)/d) for d in digits]

    plt.style.use('seaborn-colorblind')

    plt.bar(digits, freqs, ec='black', label=u'Наблюдаемая частота')
    plt.plot(digits, benfords, linestyle='--', marker='o', label=u'Частота по з-ну Бенфорда')

    plt.xticks(range(0,10))
    plt.xlabel(u'Цифра')
    plt.ylabel(u'Частота')

    plot_name = u"Частота первых цифр\n"
    plot_name += u"Чисел всего: {}".format(numbers_total)
    plt.title(plot_name)
    plt.legend()
    plt.tight_layout()
    plt.show()
