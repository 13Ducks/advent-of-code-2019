# DAY 6

file = open("day6/input.txt")
data = list(map(lambda x: x.strip().split(")"), file.readlines()))
orbit = {}
for i in data:
    orbit[i[1]] = i[0]

cnt = 0
for key in orbit:
    next = orbit.get(key, False)
    while next:
        cnt += 1
        next = orbit.get(next, False)

print(cnt)

seen = set()
seen.add("SAN")
next = (orbit['SAN'], 1)
q = [next]
dist = 0

while len(q) != 0:
    next = q.pop(0)
    if next[0] == 'YOU':
        print(next[1] - 2)
        break
    if orbit.get(next[0], False) and orbit[next[0]] not in seen:
        q.append((orbit[next[0]], next[1]+1))
        seen.add(next[0])

    if next[0] in list(orbit.values()):
        poss = [x for x, y in orbit.items() if y == next[0]]
        for i in poss:
            if i not in seen:
                q.append((i, next[1]+1))
                seen.add(i)

    



