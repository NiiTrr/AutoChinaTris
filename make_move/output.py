from utils import *
from input import read_state


def output_move(filepath, move, height):
    file = open(filepath, mode='w')  # 临时文件,在AHK读取后被删除
    file.write(str(move)+','+str(height))
    file.close()

def update_pos(filepath, zi_update):
    zi, i, j = zi_update
    i, j = [int(i), int(j)]

    # 检查ages并根据scene校准
    progress, scene, ages = read_state(filepath)
    scene[i][j] = zi
    ages[i][j] = progress[0] + 1  # 当前步数
    output_state(filepath, [progress, scene, ages])

def output_state(filepath, state):
    none = '.'
    progress, scene, ages = state
    file = open(filepath, mode='w')

    for i, a in enumerate(progress):
        c = ' ' if i < len(progress) - 1 else '\n'
        file.write(str(a)+c)

    for i in range(rows):  # 2.写scene
        for j in range(cols):
            file.write(scene[i][j])
        file.write('\n')

    for i in range(rows):
        for j in range(cols):
            c = ' ' if j < cols - 1 else '\n'
            file.write(str(ages[i][j]) + c)

    file.close()

    return
