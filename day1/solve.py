# DAY 1 - PROBLEM 1
file = open("day1/input.txt")
data = [int(s.strip()) for s in file.readlines()]
ans = sum([i//3-2 for i in data])

print(ans)


# DAY 1 - PROBLEM 2
file = open("day1/input.txt")
data = [int(s.strip()) for s in file.readlines()]
total = []
for i in data:
    cost = i//3-2
    next = cost//3-2
    while next > 0:
        cost += next
        next = next//3-2
    total.append(cost)

print(sum(total))