# DAY 4

file = open("day4/input.txt")
data = list(map(int, file.readline().strip().split("-")))
total = 0

def valid(num):
    pair = False
    for i in range(len(num) - 1):
        if num[i] > num[i+1]:
            return False
        if num[i] == num[i+1]:
            if i == 0 or num[i] != num[i-1]:
                if i == len(num) - 2 or num[i] != num[i+2]:
                    pair = True
    return pair

for i in range(data[0], data[1]):
    if valid(str(i)):
        total += 1

print(total)

# Alternate Solution
from collections import Counter

total_part1 = total_part2 = 0
for i in range(data[0], data[1]):
    if sorted(list(str(i))) == list(str(i)):
        c = Counter(str(i)).values()
        if max(c) > 1:
            total_part1 += 1
        if 2 in c:
            total_part2 += 1

print(total_part1, total_part2)