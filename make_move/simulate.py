import numpy as np
from scores import *
from utils import *


def match(zi_list, age_list, rule_dict):
    cnt = len(zi_list)
    pos = np.argmin(np.array(age_list))  # 只返回首次出现的最小值
    new_zi = rule_dict.get(tuple(zi_list))
    # TODO: "待验证的游戏情况: 无组合字后出现可组合的同age的情况"

    if new_zi != None:
        return pos, new_zi
    return -1, ''

def row_detect(row, zi, tmp_zi, rules, use_mark, age_mark):
    w_cnt = [cols - 3, cols - 2]  # 4大小(cnt=3)的窗口有cols-3个, ~. if cols = 4, then [1, 2]
    is_row = True
    for w in range(3 * cols - 6):  # w: 窗口个数, 用于计算cnt和col
        cnt = 4 - (w >= w_cnt[0]) - (w >= w_cnt[0] + w_cnt[1])  # = 4, 3, 2
        col = w - w_cnt[0] * (cnt <= 3) - w_cnt[1] * (cnt <= 2)
        exists_unused = sum([not use_mark[row][col + i] for i in range(cnt)])
        if not exists_unused:  # 都标记为用于合成过,则非法
            continue

        zi_list = [zi[row][col + i] for i in range(cnt)]
        age_list = [age_mark[row][col + i] for i in range(cnt)]
        rule_dict = rules[is_row][cnt - 2]

        pos, new_zi = match(zi_list, age_list, rule_dict)  # 新字位置与zi_list[pos]的相同,列为col + pos
        if pos < 0:  # 无可合成的字
            continue
        for i in range(cnt):
            use_mark[row][col + i] = True
        tmp_zi[row][col + pos] = new_zi

        # TODO: "待验证的游戏机制: 组合字时,age(影响中间落字的3字合成方向)取组合中的最小值."
        age_mark[row][col + pos] = min(age_list)
    return

def col_detect(col, zi, tmp_zi, rules, use_mark, age_mark):
    w_cnt = [rows - 3, rows - 2]  # if rows = 9, then [6, 5]
    is_row = False
    for w in range(3 * rows - 6):  # 含义同row_detect
        cnt = 3 - (w >= w_cnt[0]) - (w >= w_cnt[0] + w_cnt[1])  # = 3, 2, 1
        row = w - w_cnt[0] * (cnt <= 2) - w_cnt[1] * (cnt <= 1)
        exists_unused = sum([not use_mark[row + i][col] for i in range(cnt)])
        if not exists_unused:
            continue

        zi_list = [zi[row + i][col] for i in range(cnt)]
        age_list = [age_mark[row + i][col] for i in range(cnt)]
        rule_dict = rules[is_row][cnt - 2]

        pos, new_zi = match(zi_list, age_list, rule_dict)
        if pos == -1:
            continue
        for i in range(cnt):
            use_mark[row + i][col] = True
        tmp_zi[row + pos][col] = new_zi

        # TODO: 同row_detect()
        age_mark[row + pos][col] = min(age_list)
    return

def step(zi, age_mark, targets, rules, fall, cnt):
    none = '.'  # 表示没有字
    use_mark = [[0 for _ in range(cols)] for _ in range(rows)]

    # Step 1. Check where can be Eliminated & Combined
    tmp_zi = [['.' for _ in range(cols)] for _ in range(rows)]
    if len(fall) == 2: # 初始改变的字只包含落字,初次只检测落字所在行列
        row_detect(fall[0], zi, tmp_zi, rules, use_mark, age_mark)
        col_detect(fall[1], zi, tmp_zi, rules, use_mark, age_mark)
        fall = []  # 之后则不为初次落字
    else:
        for row in range(rows):  # 1.1 检测行
            row_detect(row, zi, tmp_zi, rules, use_mark, age_mark)

        for col in range(cols):  # 1.2 检测列
            col_detect(col, zi, tmp_zi, rules, use_mark, age_mark)

    # Step 2. Combine and Eliminate
    rm_cnt = 0
    is_new_target = False
    for i in range(rows):
        for j in range(cols-1, -1, -1):
            if use_mark[i][j]:  # 也是是否改变过的标记
                zi[i][j] = tmp_zi[i][j]
                if tmp_zi[i][j] in targets and not is_new_target:  # 消除目标字和目标
                    targets.remove(tmp_zi[i][j])
                    zi[i][j] = none
                    rm_cnt += 1
                    if rm_cnt >= cnt:
                        is_new_target = True
                    # TODO: 待验证的游戏机制: 只剩1个时是否能同时消除2个,否则顺序 目前不考虑(少见)
    tmp_zi = []

    # Step 3. Apply Falling and Update Changes
    is_new_fall = False
    for j in range(cols):  # 按列模拟下落,age的值也要下落
        fall_cnt = 0
        for i in range(rows-1, -1, -1):
            if zi[i][j] == none:
                fall_cnt += 1
            elif fall_cnt:  # 无fall_cnt时不下落
                zi[i-fall_cnt][j] = zi[i][j]
                age_mark[i-fall_cnt][j] = age_mark[i][j]
                is_new_fall = True
        for i in range(fall_cnt):  # fall_cnt在循环后等于列顶空的个数
            zi[i][j] = none
            age_mark[i][j] = 0

    # CHECK: 最后一个目标消除后导致悬空时, 先落下再消一行(不完全确定)
    if is_new_target:
        for j in range(cols):  # 每列消除底部1个,全部下落1格,age同
            zi[rows-1][j] = none
            for i in range(rows-2, 0, -1):
                zi[i-1][j] = zi[i][j]
                age_mark[i-1][j] = age_mark[i][j]
            zi[0][j] = none
            age_mark[0][j] = 0

    return is_new_fall, rm_cnt  # 消除个数作为评分重要依据

def simulate_move(state, cnt, chars, targets, all_rules, moves, zi_dist):
    progress, scene, ages = [state[0], state[1], state[2]]
    fall_id = progress[0]

    rm_cnt_sum = 0
    for i, move in enumerate(moves):
        tops = get_top(scene)  # 返回顶部空字位置,-1表示无空位
        if not i:
            debug_print(f'顶部列表:\n{tops}', False)

        y = fall_j + move  # 落点为(x,y)
        x = tops[y]
        if x == -1:  # 移动非法,不修改scene和ages直接返回
            return -999999, [scene, ages]
        scene[x][y] = chars[i]  # 落字为chars[i]
        ages[x][y] = fall_id  # 记录落字age
        fall_id += 1

        new_fall = True  # 有字下落过，需检测并有必要时更新
        fall = [x, y]  # fall传引用,在step内被修改

        rm_cnt_sum = 0
        while new_fall:  # 每次整个changes更新1次为1步
            # TODO: "待验证的游戏情况: 无一行两个重叠2字的3字合成的情况"
            new_fall, rm_cnt = step(scene, ages, targets, all_rules, fall, cnt)  # scene, rules在内部被修改
            rm_cnt_sum += rm_cnt
            debug_print(f'走\'{moves[0]}\'后当前状态矩阵为:\n'
                        f'{mat2str(scene)}\n当前步数矩阵为:\n{mat2str(ages, "n")}', False)

    # 更新state
    progress[0] += 1
    progress[1] += rm_cnt_sum  # TODO: [2]: 过题数, [3]: 时长 未记录

    return get_score(scene, rm_cnt, targets, all_rules, zi_dist), [progress, scene, ages]
