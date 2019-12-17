# DAY 12
file = open("day12/input.txt")
input = list(map(lambda x: x.strip()[1:-1].split(", "), file.readlines()))
pos = [[int(j[i][2:]) for i in range(3)] for j in input]
vel = [[0,0,0],[0,0,0],[0,0,0],[0,0,0]]
sign = lambda a: (a>0) - (a<0)
past = [set() for _ in range(3)]
same = [0,0,0]

def step(num):
    for i,m in enumerate(pos):
        for n in pos:
            for x in range(3):
                vel[i][x] += sign(n[x]-m[x])
    for i,m in enumerate(pos):
        for x in range(3):
            m[x] += vel[i][x]

    coord = [(tuple(i[j] for i in pos),tuple(i[j] for i in vel)) for j in range(3)]
    
    for i in range(3):
        if coord[i] in past[i] and not same[i]: same[i] = num
        past[i].add(coord[i])

def total():
    ans = 0
    for i in range(len(pos)):
        pe = sum(map(abs,pos[i]))
        ke = sum(map(abs,vel[i]))
        ans += pe*ke
    return ans

num_steps = 0
while 0 in same or num_steps < 1000:
    step(num_steps)
    if num_steps == 999:
        print(total())
    num_steps+=1

def gcd (a,b):
    if a < b : a,b = b,a
    while b:
        a,b = b, a%b
    return a

def lcm (a , b):
    n= (a*b) / gcd(a,b)
    return n

print(same)
print(int(lcm(same[2], lcm(same[0],same[1]))))