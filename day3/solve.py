# DAY 3

file = open("day3/input.txt")
data = list(map(lambda x: x.strip().split(","), file.readlines()))
direction = {
    "R":(1,0),
    "L":(-1,0),
    "U":(0,1),
    "D":(0,-1)
}

def solve(index):
    points = set()
    seen = set()
    x=0
    y=0
    steps=0
    for i in data[index]:
        d = direction[i[0]]
        #print(i)
        for j in range(int(i[1:])):
            x += d[0]
            y += d[1]
            if (x,y) not in seen:
                points.add((x,y,steps))
            seen.add((x,y))
            steps+=1
    return points

wire1 = solve(0)
wire2 = solve(1)

print(len(wire1))
print(len(wire2))
wire10 = set(map(lambda x: (x[0],x[1]), wire2))
wire20 = set(map(lambda x: (x[0],x[1]), wire1))
intersect_wire1 = {p for p in wire1 if (p[0],p[1]) in wire10}
intersect_wire2 = {p for p in wire2 if (p[0],p[1]) in wire20}
print(len(intersect_wire1))
signal = []
for s in intersect_wire1:
    for p in intersect_wire2:
        if s[0] == p[0] and s[1] == p[1]:
            #print(s,p)
            #print(s[2]+p[2])
            signal.append(s[2]+p[2])
print(min(signal))

#print(intersect_wire1)
dist = list(map(lambda x: abs(x[0])+abs(x[1]), intersect_wire1))
dist2 = list(map(lambda x: abs(x[0])+abs(x[1]), intersect_wire2))
#print(intersect_wire1, intersect_wire2)
print(min(dist))