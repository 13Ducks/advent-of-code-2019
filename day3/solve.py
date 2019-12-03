# DAY 3

file = open("day3/input.txt")
data = list(map(lambda x: x.strip().split(","), file.readlines()))

direction = {
    "R":(1,0),
    "L":(-1,0),
    "U":(0,1),
    "D":(0,-1)
}

def get_points(data):
    points = {}
    x=0
    y=0
    steps=0
    for i in data:
        d = direction[i[0]]
        for _ in range(int(i[1:])):
            x += d[0]
            y += d[1]
            steps += 1
            if (x,y) not in points:
                points[(x,y)] = steps
    return points

wire1 = get_points(data[0])
wire2 = get_points(data[1])
intersect = set(wire1.keys()).intersection(set(wire2.keys()))

dist = [abs(x) + abs(y) for (x,y) in intersect]
print(min(dist))

signal = [wire1[point] + wire2[point] for point in intersect]
print(min(signal))