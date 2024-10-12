import pandas as pd
from enum import Enum
from app.controller.parsingtree import *
import os
import matplotlib.pyplot as plt

print(os.getcwd())
step = 0


class rulelist(Enum):
    S1 = 36
    S = 37
    E = 38
    D = 39
    G = 40
    T = 41
    I = 42
    V = 43
    U = 44
    K = 45
    L = 46
    F = 47
    Q = 48
    Y = 49
    Z = 50
    W = 51


class Token(object):

    def __init__(self, n, v, t):
        # 每个token用一个值代表
        self.num = n
        self.val = v
        self.type = t
        # 0: NUMBER 中文数字
        # 1: LEXEME 今|又|有
        # 2: TYPE 田|广|从|周|径|弦|矢
        # 3: PREFIX 圭|邪|箕|圆|宛|弧|环|头|正|畔|舌|踵|下|中|外
        # 4: UNIT 步|里|人|钱
        # 5: QUESTION 问|为|馀|得|各|约之|合之|几何|减多益少|孰|多|而|平
        # 6: FUNCTION 分|之|减其
        # 7: PUNCTUATION ，。？、
        # 8: OTHER
        # 9: $


class Nonterminal(object):

    def __init__(self, n, v):
        # 每个Nonterminal一个值代表
        self.num = n
        self.val = v


ER = -1
今 = Token(0, '今', 1)
有 = Token(1, '有', 1)
句号 = Token(2, '。', 7)
问号 = Token(3, '？', 7)
又 = Token(4, '又', 1)
逗号 = Token(5, '，', 7)
TYPE = Token(6, 'type', 2)

一 = Token(7, '一', 8)
顿号 = Token(8, '、', 7)
NUM = Token(9, 'num', 0)
UNIT = Token(10, 'unit', 4)
分 = Token(11, '分', 6)
之 = Token(12, '之', 6)
太 = Token(13, '太', 6)
半 = Token(14, '半', 6)
少 = Token(15, '少', 6)
太半 = Token(16, '太半', 6)
少半 = Token(17, '少半', 6)
FUN = Token(18, 'fun', 6)
# 其 = Token(19, '其', 8)
其 = Token(19, '其', 8)
问 = Token(20, '问', 5)
欲 = Token(21, '欲', 5)
为 = Token(22, '为', 5)
率之 = Token(23, '率之', 5)
# adj = Token(25, 'adj', 8)
求 = Token(24, '求', 5)
几何 = Token(25, '几何', 5)
孰多 = Token(26, '孰多', 5)
多 = Token(27, '多', 5)
减多益少 = Token(28, '减多益少', 5)
各 = Token(29, '各', 5)
而平 = Token(30, '而平', 5)
得 = Token(31, '得', 5)
馀 = Token(32, '馀', 5)
约之 = Token(33, '约之', 5)
合之 = Token(34, '合之', 5)
DOLLAR = Token(35, '$', 9)

all_token_list = [今, 有, 句号, 问号, 又, 逗号, TYPE, 一, 顿号, NUM, UNIT, 分, 之, 太, 半, 少, 太半, 少半, FUN, 其, 问, 欲, 为, 率之, 求, 几何, 孰多, 多,
                  减多益少, 各, 而平, 得, 馀, 约之, 合之, DOLLAR]
S1 = Nonterminal(36, "S'")
S = Nonterminal(37, 'S')
E = Nonterminal(38, 'E')
D = Nonterminal(39, 'D')
G = Nonterminal(40, 'G')
T = Nonterminal(41, 'T')
I = Nonterminal(42, 'P')
V = Nonterminal(43, 'V')
U = Nonterminal(44, 'U')
K = Nonterminal(45, 'K')
L = Nonterminal(46, 'L')
F = Nonterminal(47, 'F')
Q = Nonterminal(48, 'Q')
Y = Nonterminal(49, 'Y')
Z = Nonterminal(50, 'Z')
W = Nonterminal(51, 'W')

# 数据读取预处理
data = pd.read_excel('parsing.xlsx', skiprows=1, sheet_name=0)
data = data.iloc[:, 1:]
data.fillna(-1, inplace=True)
#print(data.shape)
for i in range(0, data.shape[0]):
    data.replace("s" + str(i), i, inplace=True)
    data.replace("r" + str(i), i + data.shape[0], inplace=True)
data.replace("acc", data.shape[0], inplace=True)
#print(data)
data.to_excel('parsing2.xlsx', index=False)
table = pd.read_excel('parsing2.xlsx', sheet_name=0)
#print(table)
space = ' '


class Stack(object):
    def __init__(self):
        self.stack = []  # 存放元素的栈

    def push(self, data):
        self.stack.append(data)

    def pop(self):
        # 判断是否为空栈
        if self.stack:
            return self.stack.pop()
        else:
            raise IndexError("从空栈执行弹栈操作")

    def peek(self):
        # 判断栈是否为空
        if self.stack:
            return self.stack[-1]

    def peekn(self, n):
        # 判断栈是否为空
        if self.stack:
            return self.stack[-n]

    def find(self, i):

        if self.stack:
            return self.stack[i]

    def is_empty(self):
        # 栈为非空时，self.stack为True，再取反，为False
        return not bool(self.stack)

    def size(self):
        return len(self.stack)

    def clear(self):
        while self.stack:
            self.stack.pop()


stack = Stack()
string_to_print = ""


def pstack(s):
    global step
    global string_to_print
    print(f"Step {step}: <0, ", end="")
    string_to_print = string_to_print + "<p style='text-align:left'>Step " + str(
        step) + ":</p> <span style='float:left'><0, "
    step = step + 1
    for i in range(1, s.size()):
        if i % 2 == 0:
            print(f"{s.find(i)}, ", end="")
            string_to_print = string_to_print + str(s.find(i)) + ", "
        else:
            if s.find(i) == 0:
                print("今, ", end="")
                string_to_print = string_to_print + "今, "
            elif s.find(i) == 1:
                print("有, ", end="")
                string_to_print = string_to_print + "有, "
            elif s.find(i) == 2:
                print("。, ", end="")
                string_to_print = string_to_print + "。, "
            elif s.find(i) == 3:
                print("?, ", end="")
                string_to_print = string_to_print + "?, "
            elif s.find(i) == 4:
                print("又, ", end="")
                string_to_print = string_to_print + "又, "
            elif s.find(i) == 5:
                print(",, ", end="")
                string_to_print = string_to_print + ",, "
            elif s.find(i) == 6:
                print("type, ", end="")
                string_to_print = string_to_print + "type, "
            elif s.find(i) == 7:
                print("一, ", end="")
                string_to_print = string_to_print + "一, "
            elif s.find(i) == 8:
                print("`、 ", end="")
                string_to_print = string_to_print + "`、, "
            elif s.find(i) == 9:
                print("num, ", end="")
                string_to_print = string_to_print + "num, "
            elif s.find(i) == 10:
                print("unit, ", end="")
                string_to_print = string_to_print + "unit, "
            elif s.find(i) == 11:
                print("分, ", end="")
                string_to_print = string_to_print + "分, "
            elif s.find(i) == 12:
                print("之, ", end="")
                string_to_print = string_to_print + "之, "
            elif s.find(i) == 13:
                print("太, ", end="")
                string_to_print = string_to_print + "太, "
            elif s.find(i) == 14:
                print("半, ", end="")
                string_to_print = string_to_print + "半, "
            elif s.find(i) == 15:
                print("少, ", end="")
                string_to_print = string_to_print + "少, "
            elif s.find(i) == 16:
                print("太半, ", end="")
                string_to_print = string_to_print + "太半, "
            elif s.find(i) == 17:
                print("少半, ", end="")
                string_to_print = string_to_print + "少半, "
            elif s.find(i) == 18:
                print("fun, ", end="")
                string_to_print = string_to_print + "fun, "

            elif s.find(i) == 19:
                print("其, ", end="")
                string_to_print = string_to_print + "其, "
            elif s.find(i) == 20:
                print("问, ", end="")
                string_to_print = string_to_print + "问, "
            elif s.find(i) == 21:
                print("欲, ", end="")
                string_to_print = string_to_print + "欲, "
            elif s.find(i) == 22:
                print("为, ", end="")
                string_to_print = string_to_print + "为, "
            elif s.find(i) == 23:
                print("率之, ", end="")
                string_to_print = string_to_print + "率之, "

            elif s.find(i) == 24:
                print("求, ", end="")
                string_to_print = string_to_print + "求, "
            elif s.find(i) == 25:
                print("几何, ", end="")
                string_to_print = string_to_print + "几何, "
            elif s.find(i) == 26:
                print("孰多, ", end="")
                string_to_print = string_to_print + "孰多, "
            elif s.find(i) == 27:
                print("多, ", end="")
                string_to_print = string_to_print + "多, "
            elif s.find(i) == 28:
                print("减多益少, ", end="")
                string_to_print = string_to_print + "减多益少, "
            elif s.find(i) == 29:
                print("各, ", end="")
                string_to_print = string_to_print + "各, "
            elif s.find(i) == 30:
                print("而平, ", end="")
                string_to_print = string_to_print + "而平, "
            elif s.find(i) == 31:
                print("得, ", end="")
                string_to_print = string_to_print + "得, "
            elif s.find(i) == 32:
                print("馀, ", end="")
                string_to_print = string_to_print + "馀, "
            elif s.find(i) == 33:
                print("约之, ", end="")
                string_to_print = string_to_print + "约之, "
            elif s.find(i) == 34:
                print("合之, ", end="")
                string_to_print = string_to_print + "合之, "
            elif s.find(i) == 35:
                print("$, ", end="")
                string_to_print = string_to_print + "$, "

            elif s.find(i) == 36:
                print("S', ", end="")
                string_to_print = string_to_print + "S, "
            elif s.find(i) == 37:
                print("S, ", end="")
                string_to_print = string_to_print + "S, "
            elif s.find(i) == 38:
                print("E, ", end="")
                string_to_print = string_to_print + "E, "
            elif s.find(i) == 39:
                print("D, ", end="")
                string_to_print = string_to_print + "D, "
            elif s.find(i) == 40:
                print("G, ", end="")
                string_to_print = string_to_print + "G, "
            elif s.find(i) == 41:
                print("T, ", end="")
                string_to_print = string_to_print + "T, "
            elif s.find(i) == 42:
                print("I, ", end="")
                string_to_print = string_to_print + "I, "
            elif s.find(i) == 43:
                print("V, ", end="")
                string_to_print = string_to_print + "V, "
            elif s.find(i) == 44:
                print("U, ", end="")
                string_to_print = string_to_print + "U, "
            elif s.find(i) == 45:
                print("K, ", end="")
                string_to_print = string_to_print + "K, "
            elif s.find(i) == 46:
                print("L, ", end="")
                string_to_print = string_to_print + "L, "
            elif s.find(i) == 47:
                print("F, ", end="")
                string_to_print = string_to_print + "F, "
            elif s.find(i) == 48:
                print("Q, ", end="")
                string_to_print = string_to_print + "Q, "
            elif s.find(i) == 49:
                print("Y, ", end="")
                string_to_print = string_to_print + "Y, "
            elif s.find(i) == 50:
                print("Z, ", end="")
                string_to_print = string_to_print + "Z, "
            elif s.find(i) == 51:
                print("W, ", end="")
                string_to_print = string_to_print + "W, "
            else:
                print("error!\n")
                string_to_print = string_to_print + "error! </span> <div style='clear: both;'></div>\n"
                return -1
    return 0


def parse(token1, origin_value):
    global string_to_print
    j = None
    while True:
        token = token1.num
        # print('nikanzhe', stack.peek())
        action = table.iloc[stack.peek(), token]
        # print(action)
        # if action<97:
        #     print('shift:', action)
        # else:
        #     print('reduce:', action-97)
        # print('token:', token)
        if action == -1:
            return -1
        elif action < 97:
            stack.push(token)
            stack.push(action)
            update_tree(action, token, origin_value)
            state = action
            print('action: ',action)
            pstack(stack)
            print("\t\t%20cShift %d\n" % (space, action))
            string_to_print = string_to_print + "</span> <br> <span style='float: left; color: blue'>  Shift " + str(
                action) + "</span> <div style='clear: both;'></div>\n"
            return 1
        elif action == 97:
            pstack(stack)
            print('$>\t\tAccept!')
            string_to_print = string_to_print + "$> </span> <br> <span style='float: left; color: blue'>Accept! </span> <div style='clear: both;'></div>\n"
            return 1
        else:
            while action >= 97 and action <= 144:
                update_tree(action, token, origin_value)
                case = action - 96
                print('第几个rule:',case)
                if case == 1:
                    pstack(stack)
                    print('$>\t\tAccept!')
                    string_to_print = string_to_print + "$> </span> <br> <span style='float: left; color: blue'>Accept! </span> <div style='clear: both;'></div>\n"
                    return 1
                elif case == ER:
                    return -1
                # rule length=1
                elif case in [1, 4, 8, 9, 11, 13, 15, 22, 26, 27, 28, 29, 30, 43, 44, 45, 46, 47]:
                    # print(case)
                    stack.pop()
                    stack.pop()
                    state = table.iloc[stack.peek(), rule_list[action - 97]]
                    if state != -1:
                        stack.push(rule_list[action - 97])
                        stack.push(state)
                    else:
                        return -1
                # rule length=2
                elif case in [7, 12, 14, 17, 20, 21, 24, 25, 32, 38, 39]:
                    for j in range(4):
                        stack.pop()
                    state = table.iloc[stack.peek(), rule_list[action - 97]]
                    if state != ER:
                        stack.push(rule_list[action - 97])
                        stack.push(state)
                    else:
                        return -1
                # rule length=3
                elif case in [5, 6, 10, 16, 19, 31,34, 35, 37, 42]:
                    for j in range(6):
                        stack.pop()
                    state = table.iloc[stack.peek(), rule_list[action - 97]]
                    if state != ER:
                        stack.push(rule_list[action - 97])
                        stack.push(state)
                    else:
                        return -1
                # rule length=4
                elif case in [23, 33, 36, 40]:
                    for j in range(8):
                        stack.pop()
                    state = table.iloc[stack.peek(), rule_list[action - 97]]
                    if state != ER:
                        stack.push(rule_list[action - 97])
                        stack.push(state)
                    else:
                        return -1
                # rule length=5
                elif case in [18, 41]:
                    for j in range(10):
                        stack.pop()
                    state = table.iloc[stack.peek(), rule_list[action - 97]]
                    if state != ER:
                        stack.push(rule_list[action - 97])
                        stack.push(state)
                    else:
                        return -1
                else:
                    for j in range(12):
                        stack.pop()
                    state = table.iloc[stack.peek(), rule_list[action - 97]]
                    if state != ER:
                        stack.push(rule_list[action - 97])
                        stack.push(state)
                    else:
                        return -1
                pstack(stack)
                print("\t\t%-20cReduce %d\n" % (space, case - 1))
                string_to_print = string_to_print + "$> </span> <br> <span style='float: left; color: blue'> Reduce " + str(
                    case - 1) + "</span> <div style='clear: both;'></div>\n"
                action = table.iloc[stack.peek(), token]
                print('after reduce:',action)
                if action < 97:
                    stack.push(token)
                    stack.push(action)
                    update_tree(action, token, origin_value)
                    state = action
                    pstack(stack)
                    print("\t\t%20cShift %d\n" % (space, action))
                    string_to_print = string_to_print + "</span> <br> <span style='float: left; color: blue'>Shift " + str(
                        action) + "</span> <div style='clear: both;'></div>\n"
                    return 1

final_result = ''

def parse_tokens(token_types, token_value):
    global step
    global string_to_print
    global final_result
    sum_setzero()
    step = 0
    print('开始测试！！！\n')
    print("token types from lexer")
    print(token_types)
    print(token_value)
    token_to_parse = []
    for type in token_types:
        for token in all_token_list:
            if type == token.val:
                token_to_parse.append(token)

    print("token types after extract:")
    stack.push(0)
    for token, original_val in zip(token_to_parse, token_value):
        print("1111111", token.val, original_val)
        flag = parse(token, original_val)

    # 如果paring/type checking出错，则不做后续内容
    if flag == -1:
        string_to_print = "语法错误"
        fig, ax = plt.subplots(figsize=(8, 6), dpi=120)
        # 添加文本
        text_content = "语法错误，不能生成Parse Tree"
        plt.text(x=0.5, y=0.5, s=text_content, fontsize=40, color='red', ha='center', va='center')
        # 隐藏坐标轴
        ax.set_axis_off()
        plt.savefig('./app/static/parse_tree.png')
        plt.clf()

        fig, ax = plt.subplots(figsize=(8, 6), dpi=120)
        # 添加文本
        text_content = "语法错误，不能计算值"
        plt.text(x=0.5, y=0.5, s=text_content, fontsize=40, color='red', ha='center', va='center')
        # 隐藏坐标轴
        ax.set_axis_off()
        plt.savefig('./app/static/value_tree.png')
        plt.clf()
        final_result = "无结果"
        return string_to_print
    
    p_tree(ptree)
    visualize_tree(ptree) #可视化parse tree
    visualize_value_tree(ptree)
    #提取最终结果
    final_result = str(ptree[sum_val-1].value2[0])
    push_final_result()
    stack.clear()
    ptree.clear()
    # print(string_to_print)
    string_to_print = string_to_print.replace('\n', '<br>')
    lexer.symbol_table.print_symbols()
    lexer.symbol_table.clear_symbols()
    return string_to_print #返回parsing的结果



# 将最终的结果传回user，使之打印到html里
def push_final_result():
    return final_result
