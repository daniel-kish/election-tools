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

params = [
	"votersReg",
	"ballotsIssuedOnStation",
	"validBallots",
	"ER",
	"CPRF",
]

election = "duma2016"

def check(numbers):
	cnt = Counter(numbers)
	n_digits = len(cnt.values())
	p = 1.0 / n_digits
	q = 1.0 - p
	sigma = math.sqrt(p*q/sum(cnt.values()))
	ocs = []
	
	print("Numbers in total: {}".format(sum(cnt.values())))
	print("3*sigma: {}\n".format(3.0*sigma))
	
	for digit, occurences in cnt.items():
		ocs.append(occurences)
		freq = float(occurences)/len(numbers)
		print("{}: {} {}".format(digit, freq, freq > p - 3*sigma and freq < p + 3*sigma))

	print('\n')
	for digit, occurences in cnt.items():
		freq = float(occurences)/len(numbers)
		print freq

	print "\nChi-square test:"
	chs = chisquare(f_obs=ocs)
	print("pvalue: {}".format(chs.pvalue))
	pvalue_log = abs(int(math.log(chs.pvalue, 10)))
	print("pvalue log10: {}".format(pvalue_log))


if __name__ == "__main__":
	parser = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter)
	parser.add_argument("--db", help="Path to results DB")
	parser.add_argument("--election", help="Election name")

	args = parser.parse_args()

	conn = sqlite3.connect(args.db)
	c = conn.cursor()

	query_tmplt = """
SELECT {params}
FROM {election}
"""

	filter_str = u''
	params_str = ', '.join(params)
	q = query_tmplt.format(params=params_str, election=election)
	if filter_str:
		q += "WHERE " + filter_str

	numbers = []
	print(q)
	for row in c.execute(q):
		for elm in row:
			numbers.append(int(elm))

	numbers = [n % 10 for n in numbers]

	check(numbers)
