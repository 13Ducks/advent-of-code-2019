# DAY 10

file = open("day10/input.txt")
input = list(map(lambda x: x.strip(), file.readlines()))
astroids = set()
sign = lambda a: (a>0) - (a<0)

for i in range(len(input)):
    for j in range(len(input[0])):
        if input[i][j] == '#': astroids.add((j,i))

#print(astroids)
def inter(orig, target, between):
    match_sign = (sign(target[1]-orig[1]) == sign(between[1]-orig[1])) and (sign(target[0]-orig[0]) == sign(between[0]-orig[0]))
    try:
        s1 = (target[1]-orig[1])/(target[0]-orig[0])
        s2 = (between[1]-orig[1])/(between[0]-orig[0])
        #print(orig, target, between)
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
for a_orig in astroids: 
    c = 0
    #print("orig:",a_orig)
    for a_target in astroids:
        #print(a_target)
        in_sight = not a_orig == a_target 
        for a_between in astroids:
            if a_target != a_orig and a_target != a_between and inter(a_orig, a_target, a_between) and dist(a_orig, a_target, a_between):
                #print(a_orig, a_target, a_between)
                in_sight = False
        if in_sight: c+=1
        #print(in_sight)
    see[a_orig] = c

ans = max(see, key=lambda key: see[key])
print(ans, see[ans])