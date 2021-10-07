import sqlite3
import argparse
import json
import numpy as np
import matplotlib.pyplot as plt

if __name__ == "__main__":
	parser = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter)
	parser.add_argument("--config", help="JSON config")
	parser.add_argument("--size", help="Dot size factor")

	args = parser.parse_args()

	with open(args.config) as f:
		config = json.load(f)

	query = u"""
SELECT 100.0*turnout, 100.0*{cand}_res, votersReg
FROM {election}
WHERE region = "{region}"
"""

	if args.size:
		size_factor = float(args.size)
	else:
		size_factor = 0.0001

	x = []
	y = []
	w = []

	for elec in config:
		q = query.format(election=elec['table_name'], cand=elec['cand'],
			                 region=elec['region'])
		print q
		conn = sqlite3.connect(elec['db_path'])
		curs = conn.cursor()
		for row in curs.execute(q):
			x.append(row[0])
			y.append(row[1])
			w.append(row[2]*size_factor)

	fig = plt.figure()
	ax = fig.add_subplot(111)

	ax.set_aspect(1)
	ax.set_xlim(0.0, 100.0)
	ax.set_ylim(0.0, 100.0)

	ax.set_xlabel("Turnout, %")
	ax.set_ylabel("winner's result , %")

	ax.scatter(x, y, s=w)

	plt.show()
