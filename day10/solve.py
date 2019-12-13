# DAY 10
import math

file = open("day10/input.txt")
input = list(map(lambda x: x.strip(), file.readlines()))
asteroids = set()
sign = lambda a: (a>0) - (a<0)

for i in range(len(input)):
    for j in range(len(input[0])):
        if input[i][j] == '#': asteroids.add((j,i))

inter_count = set()
for a_orig in asteroids:
    all_angles = set()
    for a_other in asteroids:
        if a_orig != a_other:
            all_angles.add((math.degrees(math.atan2(a_other[1]-a_orig[1],a_other[0]-a_orig[0]))))
    inter_count.add((a_orig, len(all_angles)))
ans = max(inter_count, key=lambda x: x[1])
print(ans)

angles = {}
for a in asteroids:
    if a != ans[1]:
        angles[a] = (450 - (-math.degrees(math.atan2(a[1]-ans[0][1],a[0]-ans[0][0])))) % 360

angles = {k: v for k, v in sorted(angles.items(), key=lambda item: item[1])}

def dist(a1, a2): return abs(a2[0]-a1[0]) + abs(a2[1]-a1[1])

inter = {}
for i in asteroids:
    curr_inter = set()
    for j in asteroids:
        if i != ans[0] and j != ans[0] and i != j and angles[i] == angles[j] and dist(ans[0], i) > dist(ans[0], j):
            curr_inter.add(j)
    inter[i] = curr_inter

# won't actually destroy every asteroid
destroyed = []
last_angle = -1
for x in range(100):
    for i in angles.items():
        if i[0] not in destroyed:
            i_inter = inter[i[0]]
            next_destroy = True
            for j in i_inter:
                if j not in destroyed:
                    next_destroy = False
            if next_destroy and last_angle != i[1]:
                destroyed.append(i[0]) 
                last_angle = i[1]

sol = destroyed[199]
print(sol[0]*100+sol[1])
