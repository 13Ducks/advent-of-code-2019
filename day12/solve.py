# DAY 12
file = open("day12/input.txt")
input = list(map(lambda x: x.strip()[1:-1].split(", "), file.readlines()))
pos = [[int(j[i][2:]) for i in range(3)] for j in input]
vel = [[0,0,0],[0,0,0],[0,0,0],[0,0,0]]
sign = lambda a: (a>0) - (a<0)
past_x = set()
past_y = set()
past_z = set()
same = [0,0,0]

def step(num):
    for i,m in enumerate(pos):
        for n in pos:
            for x in range(3):
                vel[i][x] += sign(n[x]-m[x])
    for i,m in enumerate(pos):
        for x in range(3):
            m[x] += vel[i][x]
    x = (tuple(i[0] for i in pos),tuple(i[0] for i in vel))
    y = (tuple(i[1] for i in pos),tuple(i[1] for i in vel))
    z = (tuple(i[2] for i in pos),tuple(i[2] for i in vel))
    if x in past_x and not same[0]: same[0] = num
    if y in past_y and not same[1]: same[1] = num
    if z in past_z and not same[2]: same[2] = num
    past_x.add(x)
    past_y.add(y)
    past_z.add(z)


        
num_steps = 0
while 0 in same:
    step(num_steps)
    num_steps+=1
print(num_steps)

total = 0
for i in range(len(pos)):
    pe = sum(map(abs,pos[i]))
    ke = sum(map(abs,vel[i]))
    total += pe*ke
print(total)

def gcd (a,b):
    if a < b : a , b = b,a
    while b:
        a , b = b , a % b
    return a

def lcm (a , b):
    n= (a*b) / gcd(a,b)
    return n

print(same)
print(lcm(same[2], lcm(same[0],same[1])))