# -*- coding: UTF-8 -*-

import sqlite3
import argparse
import io

def region_city_tiks(db, election, region, city):
	conn = sqlite3.connect(args.db)
	c = conn.cursor()

	query_tmplt = u"""
SELECT DISTINCT tik
FROM {election}
WHERE region = "{region}" and tik like "{tik_filter}"
"""
	
	# 1) Try to do with "%{city}, %"
	query = query_tmplt.format(election=args.election, region=region, tik_filter=u"%{}, %".format(city))

	tiks = []
	for row in c.execute(query):
		tiks.append(row[0])

	if tiks:
		return tiks

	# 2) Get rid of the comma and try to search by name
	# gradually removing last character
	
	n = 0
	while not tiks and n < 5:
		name = city
		if n > 0:
			name = city[:-n]
		query = query_tmplt.format(election=args.election, region=region,
		                           tik_filter=u"%{}%".format(name))
		for row in c.execute(query):
			tiks.append(row[0])

		n += 1

	if not tiks:
		raise Exception("Failed to find anything")
	if len(tiks) == 1:
		return tiks

	return filter(lambda t: u"городская" in t, tiks)


if __name__ == "__main__":
	parser = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter)
	parser.add_argument("--db", help="Path to results DB")
	parser.add_argument("--election", help="Election name")
	parser.add_argument("--region", help="Region name")
	parser.add_argument("--city", help="Name of the city")
	parser.add_argument("--reg-list", help="List of regions and cities")

	args = parser.parse_args()

	conn = sqlite3.connect(args.db)
	c = conn.cursor()

	query_tmplt = u"""
SELECT DISTINCT tik
FROM {election}
WHERE region = "{region}" and tik like "{tik_filter}"
"""
	
	if args.city:
		ucity = args.city.decode('cp1251').encode('utf-8').decode('utf-8')
	if args.region:
		uregion = args.region.decode('cp1251').encode('utf-8').decode('utf-8')

	if not args.reg_list:
		tiks = region_city_tiks(args.db, args.election, uregion, ucity)
		for t in tiks:
			print(t)
	else:
		with io.open(args.reg_list, mode="r", encoding="utf-8") as f:
			data = f.read()
			lines = data.split('\n')
			for l in lines:
				reg, city = l.split('\t')
				tiks = region_city_tiks(args.db, args.election, reg, city)
				print(reg + u":")
				for t in tiks:
					print u"\t" + t
