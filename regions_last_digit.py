# -*- coding: UTF-8 -*-

import last_digit
import sqlite3
import matplotlib.pyplot as plt
import math
import csv
import sys
import numpy as np

election = "duma2016"
db = r"C:\Users\danie\Desktop\elections\data\2021duma\fed\2016-2021.db"

if sys.argv[1] == 'data':
    conn = sqlite3.connect(db)
    curs = conn.cursor()

    q = """
    SELECT region, sum({cand}), sum(votersReg)
    FROM {election}
    GROUP BY region
    """.format(cand="ER", election=election)

    regions = []
    cand_votes = []
    registered = []
    for row in curs.execute(q):
        regions.append(row[0])
        cand_votes.append(row[1])
        registered.append(row[2])

    pvalues = []
    i = 0
    for i in range(0,len(regions)):
        data = last_digit.get_data(db, election,
                                   last_digit.default_params + ['ER', 'CPRF'], u'region = "{}"'.format(regions[i]))
        pvalues.append(last_digit.DigitStats(data).chisquare.pvalue)

        print "{}/{}\r".format(i,len(regions)),
        i += 1

    with open('pvalues-regions.csv', 'wb') as csvfile:
        writer = csv.writer(csvfile, delimiter=',',
                                quotechar='"', quoting=csv.QUOTE_MINIMAL)
        for i in range(0,len(regions)):
            writer.writerow([regions[i].encode('utf-8'), cand_votes[i], registered[i], pvalues[i]])
else:
    data = []
    region = 0
    cand_votes = 1
    registered = 2
    pvalue = 3

    with open(sys.argv[1]) as f:
        reader = csv.reader(f, delimiter=',')
        for row in reader:
            data.append((row[0], int(row[1]), int(row[2]), float(row[3])))

    data = sorted(data, key=lambda x: x[3])

    for i in range(0,10):
        print data[i][0].decode('utf-8'), data[i][1], data[i][2], data[i][3]

    pvalue_thresholds = list(np.arange(0.0, 0.1, 0.01)) + list(np.arange(0.1, 1.0, 0.1))
    results = []

    for thresh in pvalue_thresholds:
        # get total result from the regions with pvalue > thresh
        filtered = filter(lambda x: x[3] > thresh, data)
        sum_votes = sum([x[1] for x in filtered])
        sum_registered = sum([x[2] for x in filtered])
        results.append(100.0*sum_votes/sum_registered)
        print len(filtered)
        if len(filtered) < 10:
            print thresh, ': ',
            for x in filtered: print x[0].decode('utf-8'),
            print '\n'

    plt.plot(pvalue_thresholds,results, marker='o')
    plt.show()
