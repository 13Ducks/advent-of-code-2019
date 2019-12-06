# DAY 6

from queue import LifoQueue

file = open("day6/input.txt")
data = list(map(lambda x: x.strip().split(")"), file.readlines()))

orbit = {}
for i in data:
    orbit[i[1]] = i[0]

orbit_cnt = 0
for key in orbit:
    next = orbit.get(key, False)
    while next:
        orbit_cnt += 1
        next = orbit.get(next, False)

print(orbit_cnt)

seen = set(["SAN"])
next = (orbit['SAN'], 1)
q = LifoQueue()
q.put(next)

while not q.empty():
    next = q.get()
    if next[0] == 'YOU':
        print(next[1] - 2)
        break

    if orbit.get(next[0], False) and orbit[next[0]] not in seen:
        q.put((orbit[next[0]], next[1]+1))
        seen.add(next[0])
    
    poss = [x for x, y in orbit.items() if y == next[0]]
    for i in poss:
        if i not in seen:
            q.put((i, next[1]+1))
            seen.add(i)
