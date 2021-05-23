from copy import deepcopy, copy

from input import *
from output import *
from simulate import *
from utils import *

from timeit import default_timer as timer

introduction_print = True

def main():
    # 运行: &python d:/AutoHotkey/Scripts/AutoChinaTris/make_move/calc.py -a 水 -b 田 -c 4 -t 沝,淼,果,森,淋
    # 改阵: -s
    # 读取当前字、目标、布局、规则
    start_time = timer()
    total_time = start_time

    chars, cnt, targets = read_commands()
    if not cnt and not targets:  # 更新state位置
        update_pos(r'.\当前状态.txt', chars)
        return

    cnt = int(cnt)  # 由于本来每次都要获取新chars, cnt, targets, 目前不更新cnt
    state = read_state('当前状态.txt')
    all_rules = read_rules('合成规则.txt')  # 无限模式当前八个基础字的全部规则, 用于合字和打分
    rules = get_target_rules(targets, all_rules)  # 用于消字和打分
    # 读取Time < 0.001s

    # 用于评分
    base_chars = read_base('基字.txt')
    all_zi, zi_dist = init_dist(base_chars, all_rules)  # all_zi暂时未使用

    print(f'计时初始化dist:{timer()-start_time: 1.4f} sec(s)')
    start_time = timer()

    # TODO: 新题获取字若不足6个,可能没测准,需每次重新获取整个存字区,大于也是(AHK也修改)

    debug_print(f'状态矩阵:\n{mat2str(state[1])}{mat2str(state[2], "n")}'
                f'规则矩阵(全规则):\n{all_rules}\n规则矩阵(当前题):\n{rules}'
                f'命令行:\n{chars, cnt, targets}', introduction_print)

    best_moves, best_state, max_score = [['0'], None, -999991]  # 字全满/余1且当前步不可消时,返回初值0

    for i in range(16):
        moves = [(i % 4) - 2, (i // 4) - 2]
        # simulate消字时会消去对应的rule. 每次模拟应复原state, rules
        score, new_state = simulate_move(
            deepcopy(state), cnt, chars, copy(targets), all_rules, moves, zi_dist)
        debug_print(f'移动{moves}, 分数{score}, 状态矩阵:\n'
                    f'{mat2str(new_state[1])}{mat2str(new_state[2], "n")}')

        if score > max_score or not i:
            max_score, best_moves, best_state = [  # 只有score是标量值不需深拷贝
                score, deepcopy(moves), deepcopy(new_state)]
    # print(f'计时模拟16种步骤+评分:{timer()-start_time: 1.4f} sec(s)')
    # start_time = timer()
    # Time ~= 0.034s

    # TODO: update_progress(state[0])  # 更新progress
    debug_print(f'最佳移动为[{best_moves}],移动后状态为:\n'
                f'{best_state[0]}\n{best_state[1]}\n{best_state[2]}', True)

    top = get_top(best_state[1])  # 写距离, 方便根据离顶部位置加速下落
    output_move(r'.\move.txt', best_moves[0], 1+top[fall_j+best_moves[0]])
    output_state(r'.\当前状态.txt', best_state)

    print(f'总处理用时:{timer()-total_time: 1.4f} sec(s)')
    # 总时间Time ~= 0.044s

main()
