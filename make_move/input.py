import utils
import re
import sys
from sys import argv
import getopt
from utils import *


def read_commands():  # 获取(命令行)参数
    # 命令格式示例： -a 水 -b 田 -c 4 -t 沝,淼,果,森,淋
    debug_print(f'接收到的命令行参数:[长度={len(argv[1:])}]{argv[1:]}', True)

    try:
        opts, args = getopt.getopt(argv[1:], 'a:b:c:t:s:')
    except getopt.GetoptError:
        sys.exit(-103)
    zi_a, zi_b, count, targetStr = [None, None, None, None]

    for opt, arg in opts:
        if opt == '-a': zi_a = arg
        elif opt == '-b': zi_b = arg
        elif opt == '-c': count = arg
        elif opt == '-t': targetStr = arg
        elif opt == '-s':
            zi_info = arg.split(',')  # zi_info是list形式
            return [zi_info, None, None]
            # zi = arg.split(',')
            # return [[zi[j*9:j*9+9] for j in range(cols)], None, None]

    target_cnt = len(targetStr) // 2 + 1
    targets = [targetStr[i * 2] for i in range(target_cnt)]

    return [zi_a, zi_b], count, targets

def read_state(filepath):
    file = open(filepath, mode='r', encoding='gbk')
    lines = file.readlines()
    file.close()

    progress = lines[0].split(sep=' ')
    progress = list(map(int, progress))
    scene = [[lines[i + 1][j] for j in range(cols)] for i in range(rows)]
    ages = [lines[i + rows + 1][:-1].split(sep=' ') for i in range(rows)]
    ages = list(map(lambda x:list(map(int, x)), ages))

    return [progress, scene, ages]

def read_base(filepath):
    file = open(filepath, mode='r', encoding='utf_8')
    chars = file.readlines()[0][:-1]
    return list(chars)

def read_rule_raw(filepath):
    file = open(filepath, mode='r', encoding='utf_8')
    lines = file.readlines()
    rule_raw_lines = [x for x in lines if not re.match('\n', x)]  # 去空行
    file.close()
    return rule_raw_lines

def read_rules(filepath):
    dict_table = [
        [dict(), dict(), dict()],  # is_row == 0, store column rules
        [dict(), dict(), dict()]   # is_row == 1, store row rules
    ]  # cnt = 0, 1, 2
    rule_lines = read_rule_raw(filepath)

    for rule in rule_lines:  # 把rule读入list table
        op = rule[1]  # 组合符号，为+,-,/
        dst = rule[-2]
        op_num = (len(rule) - 2) // 2  # 组合个数，为2,3,4
        is_row = (op != '/')  # 是否按行组合

        rule_dict = dict_table[is_row][op_num - 2]  # 涉及list为引用
        src_list = [rule[i*2] for i in range(op_num)]
        rule_dict[tuple(src_list)] = dst  # 加入映射{元组(运算1，运算2)->目标}
        if op == '-' and op_num == 2 and rule[0] != rule[2]:  # '-'表示允许交换
            rule_dict[tuple([rule[4], rule[2]])] = rule[0]

    return dict_table

def get_target_rules(targets, all_rules):
    rules = [
        [dict(), dict(), dict()],
        [dict(), dict(), dict()]
    ]
    for i in range(6):
        for item in all_rules[i%2][i//2].items():
            if item[1] not in targets:
                continue
            rules[i%2][i//2][item[0]] = item[1]

    return rules
