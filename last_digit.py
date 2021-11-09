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


def check(numbers):
	cnt = Counter(numbers)
	n_digits = len(cnt.values())
	p = 1.0 / n_digits
	q = 1.0 - p
	sigma = math.sqrt(p*q/sum(cnt.values()))
	ocs = []

	print("Numbers in total: {}".format(sum(cnt.values())))
	print("3*sigma: {}\n".format(3.0*sigma))

	digits = []
	frequencies = []
	for digit, occurences in cnt.items():
		ocs.append(occurences)
		freq = float(occurences)/len(numbers)
		print("{}: {} {}".format(digit, freq, freq > p - 3*sigma and freq < p + 3*sigma))
		digits.append(digit)
		frequencies.append(freq)

	max_f = max(frequencies)
	min_f = min(frequencies)

	print "\nChi-square test:"
	chs = chisquare(f_obs=ocs)
	print("pvalue: {}".format(chs.pvalue))
	pvalue_log = int(math.log(chs.pvalue, 10))
	print("pvalue log10: {}".format(pvalue_log))

	prob_of_zero = 1.0*cnt[0]/sum(cnt.values())
	zeros_too_frequent = prob_of_zero > p + 3*sigma

	print("Signs of fraud: {}".format("yes" if zeros_too_frequent and chs.pvalue < 0.05 else "no"))

	plt.style.use('tableau-colorblind10')
	fig, ax = plt.subplots()
	plt.bar(digits, frequencies, label=u'Наблюдаемая', zorder=3, edgecolor = 'black', width=0.5, linewidth=1)
	
	next_color = next(ax._get_lines.prop_cycler)['color']
	next_color = next(ax._get_lines.prop_cycler)['color']

	plt.axhline(p, label=u'Ожидаемая', color=next_color, zorder=2, linewidth=3)
	
	next_color = next(ax._get_lines.prop_cycler)['color']

	plt.axhline(p + 3*sigma, label=ur'Ожидаемая + 3$\sigma$', color=next_color, zorder=2, linewidth=3)
	plt.axhline(p - 3*sigma, label=ur'Ожидаемая - 3$\sigma$', color=next_color, zorder=2, linewidth=3)

	plt.xticks(range(0,10))
	plt.ylim([min_f*0.8, max_f*1.1])
	plt.xlabel(u'Цифра')
	plt.ylabel(u'Частота')
	title_tmplt = u'''Распределение последних цифр Чисел всего: {}, P-значение хи-квадрат: {:.3}, $\sigma$={:.3}'''
	plt.title(title_tmplt.format(len(numbers), chs.pvalue, sigma))
	plt.grid()
	plt.legend()
	plt.tight_layout()
	plt.show()

	return chs.pvalue


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
		freq_by_digit += "{}: {:8.5} {}\n".format(digit, freq, freq > stats.p - 3*stats.sigma and freq < stats.p + 3*stats.sigma)

	zeros_too_frequent = stats.digit_frequencies[0] > stats.p + 3*stats.sigma
	fraud = "yes" if zeros_too_frequent and stats.chisquare.pvalue < 0.05 else "no"

	return report_template.format(num_total=stats.numbers_total,
						   three_sigma=3*stats.sigma,
						   freq_by_digit=freq_by_digit,
						   chisq_stat=stats.chisquare.statistic,
						   chisq_p=stats.chisquare.pvalue,
						   fraud=fraud)


def get_data(db, election, params, filter_str, base):
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
	# print "Query:\n", q

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
	parser.add_argument("--spec-params", nargs="*", help="Parameters to add to basic")
	parser.add_argument("--base", help="Number base", default=10)
	parser.add_argument("--include-zeros", action='store_true', help="Whether to filter out zeros")

	args = parser.parse_args()

	data = get_data(args.db, args.election, args.basic_params + args.spec_params, "", 10)

	if not args.include_zeros:
		data = filter(lambda x: x > 0, data)

	dist_data = DigitStats(data)

	print detailed_report(dist_data)





	# cases = [
	# 	# [params, u"", 10,],
	# 	# [params, u"", 7,],
	# 	# [params, u"turnout < 0.75", 10,],
	# 	[params, u"region like '%Москва%'", 10,],
	# ]

	# ans = []
	# for case in cases:
	# 	pvalue = analyze(db=args.db, election=args.election, params=case[0],
	# 						 filter_str=case[1], base=case[2])
	# 	ans.append(pvalue)

	# for i in range(0, len(cases)):
	# 	print("{} '{:20}' {:3} {:4}".format('+'.join(cases[i][0]), cases[i][1], cases[i][2], ans[i]))
