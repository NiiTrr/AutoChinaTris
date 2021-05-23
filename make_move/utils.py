rows = 9
cols = 4
fall_j = 2

def debug_print(content, debugging=False):
    print(content*debugging, end=['', '\n'][debugging])

def mat2str(src_list, dst='mat'):  # src_list为二重list
    s = ''
    if dst == 'matrix' or dst == 'mat' or dst == 'm':
        for x in src_list:
            for a in x:
                s += a
            s += '\n'
    elif dst == 'digits' or dst == 'number' or dst == 'num' or dst == 'n':
        for x in src_list:
            for a in x:
                s += f'{a:4}, '
            s = s[:-1] + '\n'
    return s

def get_top(mat):  # 获取每列顶部空字位置
    tops = []
    for j in range(cols):
        top_pos = rows - 1  # 一列都没有字时的顶部位置
        for i in range(rows):
            if mat[i][j] != '.':
                top_pos = i - 1
                break
        tops.append(top_pos)
    return tops
