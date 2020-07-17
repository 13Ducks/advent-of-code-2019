# DAY 14

from collections import defaultdict
import math

file = open("day14/input.txt")
input = list(map(lambda x: x.strip().replace(",","").split(" "), file.readlines()))
reactions = {}
gen = {}

for i in input:
    reactions["".join(i[-1])] = i[:-3] 
    gen[i[-1]] = int(i[-2])
    
need = reactions['FUEL'].copy()
react = True
while react:
    new_need = []
    for i in range(1, len(need), 2):
        curr_react = False
        if 'ORE' not in reactions[need[i]]:
            curr_react = True
            c = reactions[need[i]]
            for j in range(1, len(c), 2):
                amnt = math.ceil(int(need[i-1]) / gen[need[i]])
                new_need.append(str(int(c[j-1])*amnt))
                new_need.append(c[j])
        else:
            new_need.extend(need[i-1:i+1])
        react = curr_react

    need = []
    merge = defaultdict(list)
    for i, item in enumerate(new_need):
        merge[item].append(i)
    
    for k,v in merge.items():
        try:
            int(k)
        except:
            need.extend([sum(map(int, [new_need[j-1] for j in v])), k])

print(need)
base = defaultdict(lambda: 0)
for i in range(1,len(need),2):
    base[need[i]] += int(need[i-1])
print("base",base)
cost = 0
for k,v in base.items():
    c = math.ceil(v/gen[k])
    cost += c*int(reactions[k][0])

print(cost)