# DAY 10
import math

file = open("day10/input.txt")
input = list(map(lambda x: x.strip(), file.readlines()))
astroids = set()
sign = lambda a: (a>0) - (a<0)

for i in range(len(input)):
    for j in range(len(input[0])):
        if input[i][j] == '#': astroids.add((j,i))

def inter(orig, target, between):
    match_sign = (sign(target[1]-orig[1]) == sign(between[1]-orig[1])) and (sign(target[0]-orig[0]) == sign(between[0]-orig[0]))
    try:
        s1 = (target[1]-orig[1])/(target[0]-orig[0])
        s2 = (between[1]-orig[1])/(between[0]-orig[0])
        if s1 == s2 and match_sign:
            return True
        return False
    except ZeroDivisionError:
        if target[0]-orig[0] == between[0]-orig[0] and match_sign:
            return True
        return False

def dist(orig, target, between):
    return (abs(orig[0]-target[0])+abs(orig[1]-target[1])) > (abs(orig[0]-between[0])+abs(orig[1]-between[1]))

see = {}
intersect = {}
max_val = (11,13)
for a_orig in astroids: 
    if a_orig == (max_val):
        c = 0
        for a_target in astroids:
            in_sight = not a_orig == a_target
            all_between = set()                
            for a_between in astroids:
                if a_target != a_orig and a_target != a_between and inter(a_orig, a_target, a_between) and dist(a_orig, a_target, a_between):
                    in_sight = False
                    all_between.add(a_between)
            if in_sight: c+=1
            intersect[a_target] = all_between
        see[a_orig] = c

ans = max(see, key=lambda key: see[key])
print(ans, see[ans])

angles = {}
for a in astroids:
    if a != max_val:
        angles[a] = (450 - (-math.degrees(math.atan2(a[1]-max_val[1],a[0]-max_val[0])))) % 360

angles = {k: v for k, v in sorted(angles.items(), key=lambda item: item[1])}

destroyed = []
last_angle = 1000
# DOES NOT WORK FOR EXAMPLE BOTH PARTS PLS FIX
for x in range(100):
    for i in angles.items():
        if i[0] not in destroyed:
            #print(i)
            i_inter = intersect[i[0]]
            next_destroy = True
            for j in i_inter:
                if j not in destroyed:
                    next_destroy = False
            if next_destroy and last_angle != i[1]:
                destroyed.append(i[0]) 
                last_angle = i[1]

print(destroyed[199])