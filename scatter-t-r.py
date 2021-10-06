import sqlite3
import argparse
import numpy as np
import matplotlib.pyplot as plt

if __name__ == "__main__":
	parser = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter)
	parser.add_argument("--db", help="Path to results DB")
	parser.add_argument("--cand", help="Candidate name (case insensitive)")
	parser.add_argument("--election", help="Election name")
	parser.add_argument("--size", help="Dot size factor")
	parser.add_argument("--regions", nargs="*", help="Region(-s) (for federal election only)")
	parser.add_argument("--tik", help="TIK filter")

	args = parser.parse_args()

	if args.regions:
		uregions = [x.decode('cp1251').encode('utf-8').decode('utf-8') for x in args.regions]
	if args.tik:
		utik = args.tik.decode('cp1251').encode('utf-8').decode('utf-8')

	conn = sqlite3.connect(args.db)
	c = conn.cursor()

	query = u"""
SELECT 100.0*turnout, 100.0*{cand}_res, votersReg
FROM {election}
"""
	
	filters = []
	if args.regions:
		reg_filters = [u'region like "%{}%"'.format(uregion) for uregion in uregions]
		filters.append(u'(' + u' OR '.join(reg_filters) + u')')
	if args.tik:
		filters.append(u'tik like "%{}%"'.format(utik))
	if filters:
		query += u'WHERE ' + u' AND '.join(filters)

	query = query.format(cand=args.cand, election=args.election)
	print(query)

	x = []
	y = []
	w = []

	if args.size:
		size_factor = float(args.size)
	else:
		size_factor = 0.0001

	for row in c.execute(query):
		x.append(row[0])
		y.append(row[1])
		w.append(row[2]*size_factor)

	fig = plt.figure()
	ax = fig.add_subplot(111)

	ax.set_aspect(1)
	ax.set_xlim(0.0, 100.0)
	ax.set_ylim(0.0, 100.0)

	ax.set_xlabel("Turnout, %")
	ax.set_ylabel("{}'s result , %".format(args.cand))

	ax.scatter(x, y, s=w)

	plt.show()
