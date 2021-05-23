from utils import *


def init_dist(base_zi, rules):
    is_start = dict()
    all_zi = set()
    for i in range(6):
        for item in rules[i % 2][i // 2].items():
            all_zi = all_zi.union(set(item[1]))
    node_zi = all_zi - set(base_zi)

    rev = dict()
    dist = dict()
    from copy import deepcopy
    for i in range(6):
        for item in rules[i % 2][i // 2].items():
            if not rev.get(item[1]):
                rev[item[1]] = [item[0]]
            else:
                rev[item[1]] =  [item[0], rev[item[1]]]

    for a in base_zi:
        dist[a] = 1

    def get_dist(a):
        if dist.get(a):
            return dist[a]
        md = 999
        new_rev = rev[a]
        while True:
            rule = new_rev[0]
            md = min(md, sum([get_dist(x) for x in rule]))
            if len(new_rev) == 1:
                break
            new_rev = new_rev[1]
        dist[a] = md
        return md

    for a in node_zi:
        get_dist(a)

    return all_zi, dist

def get_score(zi, rm_cnt, rules, all_rules, zi_dist):
    import math
    none = '.'
    w_cnt = [cols - 3, cols - 2]  # 含义同step中w_cnt
    top = get_top(zi)

    # 简单对当前局面进行评价(根据经验设定), 需根据例子验证
    score = -math.pow(10, 4 - max(top)) * cols
    for row, zi_row in enumerate(zi):
        for a in zi_row:
            if a == none:
                continue
            # 单字(char)评价: 位置越靠下,没消掉的字越简单,减得越少
            score -= zi_dist[a] * math.exp(rows - row - 1)

    return score + math.exp(rm_cnt - 2) * 32
