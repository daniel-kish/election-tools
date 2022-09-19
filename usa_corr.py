import csv
import matplotlib.pyplot as plt
import numpy as np

def show_scatter_plot(x, y, s):
	fig, ax = plt.subplots()
	ax.set_aspect(1)
	ax.set_xlim(0, 1)
	ax.set_ylim(0, 1)
	ax.scatter(x,y,s=s)
	plt.show()


data16 = dict()

with open(r'C:\Users\danie\Desktop\2016.txt') as f:
	reader = csv.reader(f, delimiter='\t')
	for row in reader:
		data16[row[0]] = list(row[1:])

print(len(data16))

data20 = dict()

with open(r'C:\Users\danie\Desktop\2020.txt') as f:
	reader = csv.reader(f, delimiter='\t')
	for row in reader:
		data20[row[0]] = list(row[1:])

print(len(data20))

common_ids = set(data16.keys()).intersection(set(data20.keys()))
rep16vs = []
rep20vs = []
dem16vs = []
dem20vs = []

turn16 = []
turn20 = []
s = []
factor = 0.0005
for id in common_ids:
	# print(id, data16[id], data20[id])
	reg16 = int(data16[id][0]) + int(data16[id][1])
	voted16 = int(data16[id][2])
	rep16 = int(data16[id][3])
	dem16 = int(data16[id][4])

	reg20 = int(data20[id][0]) + int(data20[id][1])
	voted20 = int(data20[id][2])
	rep20 = int(data20[id][3])
	dem20 = int(data20[id][4])

	if voted20 == 0 or voted16 == 0:
		continue
	rep16vs.append(1.0*rep16/voted16)
	rep20vs.append(1.0*rep20/voted20)

	dem16vs.append(1.0*dem16/voted16)
	dem20vs.append(1.0*dem20/voted20)

	turn16.append(1.0*voted16/reg16)
	turn20.append(1.0*voted20/reg20)

	s.append(reg16*factor)

show_scatter_plot(turn16, rep16vs, s)
