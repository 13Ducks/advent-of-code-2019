# DAY 13

file = open("day13/input.txt")
input = list(map(int, file.readline().split(","))) + list(map(int,list('0'*10000)))

def intcode(code):
    i = 0
    rel_base = 0
    num_args = {'01':3,'02':3,'03':1,'04':1,'05':2,'06':2,'07':3,'08':3,'09':1,'99':0}

    def index(param, off):
        if param == '0':
            return code[i+off]
        elif param == '1':
            return i+off
        else:
            return code[i+off]+rel_base

    while True:
        op = str(code[i])[-2:].zfill(2)
        param = str(code[i])[:-2].zfill(3)
        
        if num_args[op] >= 1: arg1 = int(index(param[2], 1))
        if num_args[op] >= 2: arg2 = int(index(param[1], 2))
        if num_args[op] >= 3: arg3 = int(index(param[0], 3))
        jump = False

        if op == '01':
            code[arg3] = code[arg1] + code[arg2]
        elif op == '02':
            code[arg3] = code[arg1] * code[arg2]
        elif op == '03':
            code[arg1] = yield 'needinput'
        elif op == '04':
            yield code[arg1]
        elif op == '05':
            if code[arg1] != 0:
                i = code[arg2]
                jump = True
        elif op == '06':
            if code[arg1] == 0:
                i = code[arg2]
                jump = True
        elif op == '07':
            code[arg3] = int(code[arg1] < code[arg2])
        elif op == '08':
            code[arg3] = int(code[arg1] == code[arg2])
        elif op == '09':
            rel_base += code[arg1]
        elif op == '99':
            yield 'break'
            break
        else:
            print(op)
        
        if not jump: i+=num_args[op]+1

comp = intcode(input.copy())
cnt = 0

try:
    while True:
        curr = [next(comp) for _ in range(3)]
        if curr[2] == 2: cnt+=1
except StopIteration:
    print(cnt)


ball_x = paddle_x = 0

input[0] = 2
comp = intcode(input)
score = 0

try:
    while True:
        a = next(comp)
        while a == 'needinput':
            move = 1 if ball_x > paddle_x else 0 if ball_x == paddle_x else -1
            a = comp.send(move) 
        b = next(comp)
        c = next(comp)
        if c == 3:
            paddle_x = a
        if c == 4:
            ball_x = a
        if (a,b) == (-1,0):
            score = c
except StopIteration:
    print(score)