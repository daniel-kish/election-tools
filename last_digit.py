# -*- coding: UTF-8 -*-

import sqlite3
import argparse
import matplotlib.pyplot as plt
from collections import Counter
import math
from scipy.stats import chisquare
import random
import matplotlib.pyplot as plt
import numpy as np


class DigitStats:
    def __init__(self, numbers, base=10):
        self.numbers = numbers
        self.counter = Counter([n % base for n in numbers])
        self.digits_number = len(self.counter.values())
        self.numbers_total = sum(self.counter.values())
        self.p = 1.0 / self.digits_number
        self.q = 1.0 - self.p
        self.sigma = math.sqrt(self.p * self.q / self.numbers_total)
        self.max_frequency = float(max(self.counter.values()))/self.numbers_total
        self.min_frequency = float(min(self.counter.values()))/self.numbers_total
        self.chisquare = chisquare(self.counter.values())

        self.digit_frequencies = dict()
        for digit, occurences in self.counter.items():
            frequency = float(occurences) / self.numbers_total
            self.digit_frequencies[digit] = frequency

    def three_sigma_outliers(self):
        ans = []
        for digit, freq in self.digit_frequencies:
            if freq > self.p + 3*self.sigma:
                ans.append((digit, freq, "greater"))
            elif freq < self.p - 3*self.sigma:
                ans.append((digit, freq, "smaller"))
        return ans


def detailed_report(stats):
    report_template = '''
Numbers in total: {num_total}
3*sigma: {three_sigma}

{freq_by_digit}
Chi-square test
---------------
Chi-square statistic: {chisq_stat}
Chi-square pvalue: {chisq_p}
Strong signs of possible fraud: {fraud}
'''

    freq_by_digit = ''

    for digit, freq in stats.digit_frequencies.items():
        freq_by_digit += "{}: {:<08.5} {}\n".format(digit, freq, freq > stats.p - 3*stats.sigma and freq < stats.p + 3*stats.sigma)

    zeros_too_frequent = stats.digit_frequencies[0] > stats.p + 3*stats.sigma
    fraud = "yes" if zeros_too_frequent and stats.chisquare.pvalue < 0.05 else "no"

    return report_template.format(num_total=stats.numbers_total,
                           three_sigma=3*stats.sigma,
                           freq_by_digit=freq_by_digit,
                           chisq_stat=stats.chisquare.statistic,
                           chisq_p=stats.chisquare.pvalue,
                           fraud=fraud)


def show_plot(stats, extra_text):
    plt.style.use('seaborn-colorblind')
    fig, ax = plt.subplots()

    digits = [k for k,_ in stats.digit_frequencies.items()]
    frequencies = [v for _,v in stats.digit_frequencies.items()]
    plt.bar(digits, frequencies, label=u'Наблюдаемая', zorder=3, edgecolor = 'black', width=0.5, linewidth=1)

    next_color = next(ax._get_lines.prop_cycler)['color']
    next_color = next(ax._get_lines.prop_cycler)['color']

    plt.axhline(stats.p, label=u'Ожидаемая', color=next_color, zorder=2, linewidth=3)

    next_color = next(ax._get_lines.prop_cycler)['color']

    plt.axhline(stats.p + 3*stats.sigma, label=ur'Ожидаемая + 3$\sigma$', color=next_color, zorder=2, linewidth=3)
    plt.axhline(stats.p - 3*stats.sigma, label=ur'Ожидаемая - 3$\sigma$', color=next_color, zorder=2, linewidth=3)

    plt.xticks(range(0,stats.digits_number))

    range_e = max(stats.max_frequency, stats.p + 3*stats.sigma)
    range_b = min(stats.min_frequency, stats.p - 3*stats.sigma)
    mid_y = (range_b + range_e)*0.5
    range_len = abs(range_b - range_e)
    plt.ylim([mid_y - range_len, mid_y + range_len])
    plt.xlabel(u'Цифра')
    plt.ylabel(u'Частота')

    extra_str = ''
    if extra_text:
        extra_str = extra_text + '\n'

    plot_name = u"Распределение последних цифр\n"

    if extra_text:
        plot_name += extra_text + u'\n'
    plot_name += u"Чисел всего: {}, P-значение хи-квадрат: {:.3}, $\sigma$={:.3}"

    plt.title(plot_name.format(stats.numbers_total, stats.chisquare.pvalue, stats.sigma))
    plt.grid()
    plt.legend()
    plt.tight_layout()
    plt.show()


def get_data(db, election, params, filter_str):
    conn = sqlite3.connect(db)
    c = conn.cursor()

    query_tmplt = """
SELECT {params}
FROM {election}
"""

    params_str = ', '.join(params)
    q = query_tmplt.format(params=params_str, election=election)
    if filter_str:
        q += "WHERE " + filter_str

    numbers = []
    print u"Query:\n", q

    for row in c.execute(q):
        for elm in row:
            numbers.append(int(elm))

    return numbers


if __name__ == "__main__":
    """Example usage string:
    `last_digit.py --db 2021.db --election pres2018 --params `
    """

    default_params = [
        "votersReg",
        "ballotsIssuedOnStation",
        "validBallots",
    ]

    parser = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument("--db", help="Path to results DB", required=True)
    parser.add_argument("--election", help="Election name", required=True)
    parser.add_argument("--basic-params", nargs="*", help="Basic parameters to analyze", default=default_params)
    parser.add_argument("--spec-params", nargs="*", help="Parameters to add to basic", default=[])
    parser.add_argument("--base", help="Number base", default=10)
    parser.add_argument("--include-zeros", action='store_true', help="Whether to filter out zeros")
    parser.add_argument("--plot", action='store_true', help="Show plot")
    parser.add_argument("--region", help="Show data from specified region")
    parser.add_argument("--turnout-higher", help="Show data from precincts with turnout higher than specified")
    parser.add_argument("--turnout-lower", help="Show data from precincts with turnout lower than specified")

    args = parser.parse_args()

    filter_str = ""
    uregion = u""
    extra_text = u""
    if args.region:
        uregion = args.region.decode('cp1251').encode('utf-8').decode('utf-8')
        filter_str=u'region = "{}"'.format(uregion)
        extra_text = uregion
    elif args.turnout_higher:
        filter_str=u'turnout > {}'.format(float(args.turnout_higher))
        extra_text = u"Явка выше {}".format(float(args.turnout_higher))
    elif args.turnout_lower:
        filter_str=u'turnout <= {}'.format(float(args.turnout_lower))
        extra_text = u"Явка ниже {}".format(float(args.turnout_lower))

    data = get_data(args.db, args.election, args.basic_params + args.spec_params, filter_str)

    if not args.include_zeros:
        data = filter(lambda x: x > 0, data)

    dist_data = DigitStats(data, base=int(args.base))

    if args.plot:
        show_plot(dist_data, extra_text)
    else:
        print detailed_report(dist_data)
