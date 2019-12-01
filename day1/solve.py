# DAY 1

file = open("day1/input.txt")
data = map(lambda x: int(x.strip()), file.readlines())
total1 = []
total2 = []
for i in data:
    cost = i//3-2
    total1.append(cost)
    next = cost//3-2
    while next > 0:
        cost += next
        next = next//3-2
    total2.append(cost)

print(sum(total1))
print(sum(total2))