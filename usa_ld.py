import last_digit as ld
from scipy.stats import chisquare

with open(r"C:\Users\danie\Desktop\tmp.txt") as f:
	lines = f.readlines()

print(len(lines))

numbers = [int(x) for x in lines if len(x) > 0 and int(x) > 0]

print(len(numbers))


dist_data = ld.DigitStats(numbers, base=10)
print(ld.detailed_report(dist_data))

ld.show_plot(dist_data, '')

# ld.show_hist(numbers, 1)
