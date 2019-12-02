# DAY 2
file = open("day2/input.txt")
input = list(map(int, file.readline().split(",")))

def solve(noun,verb):
    data = input.copy()
    data[1] = noun
    data[2] = verb
    i = 0
    while i < len(data):
        if data[i] == 1:
            print
            data[data[i+3]] = data[data[i+1]] + data[data[i+2]]
            i+=4
        elif data[i] == 2:
            data[data[i+3]] = data[data[i+1]] * data[data[i+2]]
            i+=4
        elif data[i] == 99:
            break
        else:
            i+=1
    return data[0]

print(solve(12,2))

for n in range(100):
    for v in range(100):
        ans = solve(n,v)
        if ans == 19690720:
            print(n,v)
            print(100*n+v)
            break