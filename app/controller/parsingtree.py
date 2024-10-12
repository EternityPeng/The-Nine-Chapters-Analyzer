from app.controller.lexer import SymbolTable,Lexer,lexer,UnitConversion,convert_symbol_units
import networkx as nx
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
plt.rcParams['font.sans-serif'] = ['SimHei']
def convert_value(q):  # input is target type
    last_symbol = lexer.symbol_table.get_last_symbol()
    p = last_symbol['type']  # fetch from symbol table
    # print(p)
    value_p = last_symbol['value']
    if p in ['粟', '粝米', '稗米', '绺米', '御米', '小䵂', '大䵂', '粝饭', '稗饭', '绺饭', '御饭', '菽', '答', '麻', '麦', '稻', '豉', '飧', '熟菽',
             '櫱', '米', '坚', '穿地', '壤']:
        if q in ['粟', '粝米', '稗米', '绺米', '御米', '小䵂', '大䵂', '粝饭', '稗饭', '绺饭', '御饭', '菽', '答', '麻', '麦', '稻', '豉', '飧',
                 '熟菽', '櫱', '米']:
            values = [100, 60, 54, 48, 42, 27, 108, 150, 108, 96, 84, 90,90,90,90, 120, 126, 180, 207, 350, 60]
            index_q = ['粟', '粝米', '稗米', '绺米', '御米', '小䵂', '大䵂', '粝饭', '稗饭', '绺饭', '御饭', '菽', '答', '麻', '麦', '稻', '豉',
                       '飧', '熟菽', '櫱', '米'].index(q)
            index_p = ['粟', '粝米', '稗米', '绺米', '御米', '小䵂', '大䵂', '粝饭', '稗饭', '绺饭', '御饭', '菽', '答', '麻', '麦', '稻', '豉',
                       '飧', '熟菽', '櫱', '米'].index(p)
            rate = values[index_q] / values[index_p]
            value_q = rate * float(value_p)
        elif q in ['坚', '穿地', '壤']:
            values = [3, 4, 5]
            index_q = ['坚', '穿地', '壤'].index(q)
            index_p = ['坚', '穿地', '壤'].index(p)
            rate = values[index_q] / values[index_p]
            value_q = rate * value_p
        else:
            value_q = None
    else:
        value_q = None
    return value_q
class Node:
    def __init__(self):
        self.value = -1
        self.parent = -1
        self.children = [-1]*6
        self.cnum = 0
        self.level = 0
        self.value2 = []

sum_val = 0  # number of elements in the tree
def sum_setzero():
    global sum_val
    sum_val=0
#rule_list = [23, 24, 24, 25, 25, 26, 27, 27, 27, 28, 28, 28, 29, 29, 29, 30, 30, 30, 30, 31, 31, 32, 32, 33, 33, 34, 34, 35, 35, 36, 36, 36]
rule_list=[36,37,37,38,38,38,39,39,39,39,40,40,41,41,42,42,43,43,43,43,43,44,44,44,44,45,45,45,46,46,47,48,48,49,49,49,50,50,50,50,50,50,51,51,51,51,51]
mi_list=['粟','粝米','稗米','绺米','御米','小䵂','大䵂','粝饭','稗饭','绺饭','御饭','菽','答','麻','麦','稻','豉','飧','熟菽','櫱','米','穿地','坚','壤']
chuandi_list=['穿地','坚','壤']
mai_list=['出','买瓴甓','买竹','买漆','买缣','买羽','买矢簳']
case1_list=['田','圭田','邪田','箕田','圆田','宛田','弧田','环田','广','从','周','径','弦','矢','头广','舌广','踵广','上广','下广','正从','高','袤','深','方','上方','下方','上周','下周','上袤','下袤','中周','外周','上中周','下中周','积','勾','股','城','垣','堤','沟','聢','穿渠','渠','堑','方堡壔','圆堡壔','方亭','圆亭','圆锥','方锥','堑堵','阳马','刍童','曲池','盘池','冥谷','鳖臑','羡除','刍甍','仓','圆困','委粟平地','委菽依垣','委米依垣内角']
case2_list=['粟','粝米','稗米','绺米','御米','小䵂','大䵂','粝饭','稗饭','绺饭','御饭','菽','答','麻','麦','稻','豉','飧','熟菽','櫱','米','坚','穿地','壤']
unit_list=['步','里','尺','寸','匹','丈','亩','顷','斗','升','斛','钱','枚','个','石','钧','斤','两','铢','翭']
# 初始化树
ptree = []
part_type_list=['田' ,'圭田' ,'邪田' ,'箕田' ,'圆田' ,'宛田' ,'弧田' ,'环田' ,'广' ,'从' ,'周' ,'径' ,'弦' ,'矢' ,'头广' ,'舌广' ,'踵广' ,'上广' ,'下广' ,'正从' ,'高' ,'袤' ,'深' ,'方' ,'上方' ,'下方' ,'上周' ,'下周' ,'上袤' ,'下袤' ,'中周' ,'外周' ,'上中周' ,'下中周' ,'积' ,'勾' ,'股' ,'城' ,'垣' ,'堤' ,'沟' ,'聢' ,'穿渠' ,'渠' ,'堑' ,'方堡壔' ,'圆堡壔' ,'方亭' ,'圆亭' ,'圆锥' ,'方锥' ,'堑堵' ,'阳马' ,'刍童' ,'曲池' ,'盘池' ,'冥谷' ,'鳖臑' ,'羡除' ,'刍甍' ,'仓' ,'圆困' ,'委粟平地' ,'委菽依垣' ,'委米依垣内角']
changdu_list=['步','里','尺','寸','匹','丈']
def get_rule_r(r):
    switcher = {
        1: 1, 4: 1, 8: 1, 9: 1, 11: 1, 13: 1, 15: 1, 22: 1, 26: 1, 27: 1, 28: 1, 29: 1, 30: 1, 43: 1, 44: 1, 45: 1, 46: 1, 47: 1,
        7: 2, 12: 2, 14: 2, 17: 2, 20: 2, 21: 2, 24: 2, 25: 2, 32: 2, 38: 2, 39: 2,
        5: 3, 6: 3, 10: 3, 16: 3, 19: 3, 31: 3,34: 3, 35: 3, 37: 3, 42: 3,
        23: 4, 33: 4, 36: 4, 40: 4, 
        18: 5, 41: 5,
        2: 6, 3: 6
    }
    return switcher.get(r, -1)

def get_rule_l(r):
    return rule_list[r-1]

def get_root(n):
    if ptree[n].parent == -1:
        return n
    else:
        return get_root(ptree[n].parent)

def print_token(t):
    switcher = {
        0: "今", 1: "有", 2: "。", 3: "？", 4: "又", 5: "，", 6: "type", 7: "一", 8: "、", 9: "num",
        10: "unit", 11: "分", 12: "之", 13: "太", 14: "半", 15: "少", 16: "太半", 17: "少半", 18: "fun",
        19: "者", 20: "问", 21: "欲", 22: "为", 23: "率之", 24: "求", 25: "几何", 26: "孰多", 27: "多", 28: "减多益少",
        29: "各", 30: "而平", 31: "得", 32: "馀", 33: "约之", 34: "合之", 35: "$", 36: "S'", 37: "S", 38: "E", 39: "D",
        40: "G", 41: "T", 42: "I", 43: "V", 44: "U", 45: "K", 46: "L", 47: "F", 48: "Q", 49: "Y", 50: "Z", 51: "W"
    }
    return switcher.get(t, "error!")

def print_children(rt):
    if ptree[rt].children[0] == -1:
        print(print_token(ptree[rt].value))
        return
    else:
        print("\t", end="")
        print(print_token(rt), end="")
        print("\t", end="")
        for i in range(ptree[rt].cnum):
            print_children(ptree[rt].children[i])

def p_tree(pt):
    global sum_val
    print("SUM:", sum_val)
    for i in range(sum_val):
        print("<{}: {} {}\t\tparent: {}>".format(i, print_token(pt[i].value),pt[i].value2, pt[i].parent if pt[i].parent != -1 else "NULL"))
    #sum_val=0

#可视化树
def visualize_tree(pt):
    G = nx.DiGraph()
    G.clear()
    global sum_val
    for i in range(sum_val):
        G.add_node(i, desc=print_token(pt[i].value))
        if pt[i].parent != -1 :
            G.add_edge(pt[i].parent, i)

    compute_positions(G, pt, sum_val-1, x=0, y=0, dx=2000)
    
    # 设置节点位置以便更好地可视化
    pos = nx.get_node_attributes(G, "pos")    
    nx.draw(G, pos, node_color='white')
    node_labels = nx.get_node_attributes(G, 'desc')
    nx.draw_networkx_labels(G, pos, labels=node_labels)
    plt.rcParams['figure.figsize']= (20, 8) 
    plt.savefig('./app/static/parse_tree.png')
    plt.clf()
    G.clear()


#可视化value树
def visualize_value_tree(pt):
    G = nx.DiGraph()
    G.clear()
    global sum_val
    for i in range(sum_val):
        G.add_node(i, desc=str(pt[i].value2[0]))
        if pt[i].parent != -1 :
            G.add_edge(pt[i].parent, i)

    compute_positions(G, pt, sum_val-1, x=0, y=0, dx=2000)
    
    # 设置节点位置以便更好地可视化
    pos = nx.get_node_attributes(G, "pos")    
    nx.draw(G, pos, node_color='white')
    node_labels = nx.get_node_attributes(G, 'desc')
    nx.draw_networkx_labels(G, pos, labels=node_labels)
    plt.rcParams['figure.figsize']= (20, 8) 
    plt.savefig('./app/static/value_tree.png')
    plt.clf()
    G.clear()

# 计算节点的位置, 用于布局node节点，生成更美观的树状图
def compute_positions(G, pt, i, x, y, dx):
    print("x: ", x)
    
    G.nodes[i]["pos"] = (x, y)
    num_children = pt[i].cnum
    # print("num_children ", num_children)
    if num_children > 0:
        dx_child = dx / num_children
        for index in range(num_children):
            print("dx next: ",x+(index-num_children/2)*dx_child)
            node = pt[i].children[index]
            compute_positions(G, pt, node, x+(index-num_children/2)*dx_child, y - 1, dx_child)

def update_tree(action, token,origin_value):
    global sum_val
    rule_num = 0
    l = 0
    clevel = 0
    if action < 97:
        # shift action
        ptree.append(Node())
        ptree[sum_val].value = token
        if token == 9:
            ptree[sum_val].value2.append(float(origin_value))
        else:
            ptree[sum_val].value2.append(origin_value)
        #print(ptree[sum_val].value2)
        sum_val += 1
    elif 97 < action < 145:
        ptree.append(Node())
        # reduce action
        rule_num = action - 96
        l = get_rule_r(rule_num)
        j = 0
        i = 0
        while j < l:
            while ptree[sum_val - 1 - i].level != 0:
                i = i+1
            #只读取level=0的node
            ptree[sum_val - 1 - i].parent = sum_val
            ptree[sum_val].children[l - 1 - j] = sum_val - 1 - i
            #print(sum_val,'children:',ptree[sum_val].children[l - 1 - j])
            ptree[sum_val - 1 - i].level = -1
            j=j+1
            i=i+1
            #if clevel < ptree[sum_val - 1 - i].level:
            #    clevel = ptree[sum_val - 1 - i].level
        ptree[sum_val].value = get_rule_l(rule_num)
        ptree[sum_val].cnum = l
        #print(ptree[sum_val].children)
        if rule_num in [1,4,5,13,14,15,22, 38, 39, 40, 41, 42, 43, 44, 45, 46, 47]:
            for value in ptree[ptree[sum_val].children[0]].value2:
                ptree[sum_val].value2.append(value)
        elif rule_num == 7:
            symbol_name=lexer.symbol_table.extract_name(ptree[ptree[sum_val].children[0]].value2[0])
            symbol_type=ptree[ptree[sum_val].children[0]].value2[0]
            symbol_value=ptree[ptree[sum_val].children[1]].value2[0]
            symbol_unit=ptree[ptree[sum_val].children[1]].value2[1]
            lexer.symbol_table.add_symbol(symbol_type,symbol_value,symbol_unit)
            ptree[sum_val].value2.append(None)
        elif rule_num == 8:
            symbol_name=lexer.symbol_table.extract_name(ptree[ptree[sum_val].children[0]].value2[0])
            symbol_type="量纲量"
            symbol_value=float(ptree[ptree[sum_val].children[0]].value2[0])
            symbol_unit=ptree[ptree[sum_val].children[0]].value2[1]
            lexer.symbol_table.add_symbol(symbol_type,symbol_value,symbol_unit)
            ptree[sum_val].value2.append(None)
        elif rule_num == 9:
            symbol_name=lexer.symbol_table.extract_name(ptree[ptree[sum_val].children[0]].value2[0])
            symbol_type="无量纲量"
            symbol_value=float(ptree[ptree[sum_val].children[0]].value2[0])
            symbol_unit=None
            lexer.symbol_table.add_symbol(symbol_type,symbol_value,symbol_unit)
            ptree[sum_val].value2.append(None)
        elif rule_num == 10:
            symbol_name=lexer.symbol_table.extract_name(ptree[ptree[sum_val].children[1]].value2[0])
            symbol_type=ptree[ptree[sum_val].children[1]].value2[0]
            symbol_value=ptree[ptree[sum_val].children[2]].value2[0]
            symbol_unit=ptree[ptree[sum_val].children[2]].value2[1]
            lexer.symbol_table.add_symbol(symbol_type,symbol_value,symbol_unit)
            ptree[sum_val].value2.append(None)
        elif rule_num in [11,12]:
            symbol_name=lexer.symbol_table.extract_name(ptree[ptree[sum_val].children[0]].value2[0])
            symbol_type=ptree[ptree[sum_val].children[0]].value2[0]
            symbol_value=None
            symbol_unit=None
            lexer.symbol_table.add_symbol(symbol_type,symbol_value,symbol_unit)
            ptree[sum_val].value2.append(None)    
        elif rule_num == 16:
            V_value=ptree[ptree[sum_val].children[0]].value2[0]
            V_unit=ptree[ptree[sum_val].children[0]].value2[1]
            I_value=ptree[ptree[sum_val].children[2]].value2[0]
            I_unit=ptree[ptree[sum_val].children[2]].value2[1]
            if V_unit==I_unit:
                ptree[sum_val].value2.append(float(V_value)+float(I_value))
                ptree[sum_val].value2.append(I_unit)
            if V_unit in changdu_list and I_unit in ['亩','顷']:     
                ptree[sum_val].value2.append((UnitConversion.AREA_CONVERSION['平方'+V_unit]/UnitConversion.AREA_CONVERSION[I_unit])*float(V_value)+float(I_value))
                ptree[sum_val].value2.append(I_unit)
            elif V_unit== '亩' and I_unit== '顷':
                ptree[sum_val].value2.append(100*float(V_value)+float(I_value))
                ptree[sum_val].value2.append('顷')
            else:
                # print('22222222qian:   ', V_value,V_unit,I_value,I_unit)
                val1,val2,smallest_unit=UnitConversion.compare_and_convert_units(V_value,V_unit,I_value,I_unit)
                # if V_unit!=smallest_unit:
                #     ptree[ptree[sum_val].children[0]].value2[0]=val1
                #     ptree[ptree[sum_val].children[0]].value2[1]=smallest_unit
                # print('22222222222:  ',val1,val2,smallest_unit)
                ptree[sum_val].value2.append(float(val1)+float(val2))
                ptree[sum_val].value2.append(smallest_unit)
        elif rule_num == 17:
            ptree[sum_val].value2.append(float(ptree[ptree[sum_val].children[0]].value2[0]))
            ptree[sum_val].value2.append(ptree[ptree[sum_val].children[1]].value2[0])
        elif rule_num == 18:
            ptree[sum_val].value2.append(float(ptree[ptree[sum_val].children[4]].value2[0])/float(ptree[ptree[sum_val].children[0]].value2[0]))
            ptree[sum_val].value2.append(ptree[ptree[sum_val].children[2]].value2[0])
        elif rule_num == 19:
            ptree[sum_val].value2.append(float(ptree[ptree[sum_val].children[0]].value2[0])+float(ptree[ptree[sum_val].children[2]].value2[0]))
            ptree[sum_val].value2.append(ptree[ptree[sum_val].children[1]].value2[0])
        elif rule_num in [20,21]:
            ptree[sum_val].value2.append(ptree[ptree[sum_val].children[0]].value2[0])
            ptree[sum_val].value2.append(ptree[ptree[sum_val].children[1]].value2[0])
        elif rule_num == 23:
            ptree[sum_val].value2.append(float(ptree[ptree[sum_val].children[3]].value2[0])/float(ptree[ptree[sum_val].children[0]].value2[0]))
        elif rule_num in [24,25]:
            ptree[sum_val].value2.append(float(ptree[ptree[sum_val].children[0]].value2[0])+float(ptree[ptree[sum_val].children[1]].value2[0]))
        elif rule_num == 26:
            ptree[sum_val].value2.append(3/4)
        elif rule_num == 27:
            ptree[sum_val].value2.append(1/2)
        elif rule_num == 28:
            ptree[sum_val].value2.append(1/4)
        elif rule_num == 29:
            ptree[sum_val].value2.append(2/3)
        elif rule_num == 30:
            ptree[sum_val].value2.append(1/3)
        elif rule_num == 31:
            last_symbol= lexer.symbol_table.get_last_symbol()
            new_value=float(last_symbol['value'])-float(ptree[ptree[sum_val].children[2]].value2[0])
            print("new_value = ", new_value)
            lexer.symbol_table.update_symbol(last_symbol['type'], new_value, last_symbol['unit'])
            ptree[sum_val].value2.append(last_symbol['type'])
            ptree[sum_val].value2.append(new_value)
        elif rule_num in [32, 35, 37]:
            for value in ptree[ptree[sum_val].children[1]].value2:
                ptree[sum_val].value2.append(value)

        elif rule_num == 33:
            for value in ptree[ptree[sum_val].children[3]].value2:
                ptree[sum_val].value2.append(value)

        elif rule_num in [6,34]:
            for value in ptree[ptree[sum_val].children[2]].value2:
                ptree[sum_val].value2.append(value)

        elif rule_num == 36:
            symbol_name = lexer.symbol_table.extract_name(ptree[ptree[sum_val].children[1]].value2[0])
            symbol_type=ptree[ptree[sum_val].children[1]].value2[0]
            symbol_value=ptree[ptree[sum_val].children[2]].value2[0]
            symbol_unit=ptree[ptree[sum_val].children[3]].value2[0]
            lexer.symbol_table.add_symbol(symbol_type,symbol_value,symbol_unit)
            ptree[sum_val].value2.append(None)
        elif rule_num in [2,3]:
            # ptree[ptree[sum_val].children[4]].value2[0] = '田'
            if ptree[ptree[sum_val].children[4]].value2[0] in case1_list:
                # 因为圭田是none，为函数调用
                function_type = lexer.symbol_table.get_types_needing_processing()
                print("function_type = ", function_type[0])
                function_type = function_type[0]

                lexer.symbol_table.add_symbol(ptree[ptree[sum_val].children[4]].value2[0], None, None)

                print("-----先分组------")
                # 先分组
                classify_symbol = lexer.symbol_table.classify_symbols()
                print("classify_symbol = ", classify_symbol)

                print("----找到长度中最小的单位，默认-------")

                # 找到长度中最小的单位，默认
                units = lexer.symbol_table.find_units_by_name("长度")
                # print(units)
                smallest_unit = UnitConversion.find_smallest_unit(units, '长度')
                print(f"The smallest unit by conversion rate is: {smallest_unit}")

                print("----更新列表中的长度都为最小的单位-------")
                update_length = convert_symbol_units(classify_symbol['长度'], smallest_unit, '长度')
                print("update_length = ", update_length)
                print("-----更新列表中的面积都为最小的单位------")
                names = [symbol['name'] for symbol in lexer.symbol_table.symbols.values()]
                for name in names:
                    if name == "面积":
                        # smallest_unit2 = UnitConversion.find_smallest_unit(units, '面积')

                        update_area = convert_symbol_units(classify_symbol['面积'], smallest_unit, '面积')
                        lexer.symbol_table.update_symbols_list(update_area)
                        break
                    if name == "体积":
                        # smallest_unit2 = UnitConversion.find_smallest_unit(units, '体积')

                        update_area = convert_symbol_units(classify_symbol['体积'], smallest_unit, '体积')
                        lexer.symbol_table.update_symbols_list(update_area)
                        break
                print("update_area = ", update_area)
                print("-----执行更新------")
                print("-----更新前的表------")
                lexer.symbol_table.print_symbols()
                lexer.symbol_table.update_symbols_list(update_length)
                lexer.symbol_table.update_symbols_list(update_area)
                print("-----更新后的表------")
                lexer.symbol_table.print_symbols()
                print("-----执行函数------")
                # 从function_type计算target这个结果
                # symbol_table.execute_function_by_type(function_type, smallest_unit)
                return_value=lexer.symbol_table.execute_function_by_type(function_type)
                ptree[sum_val].value2.append(str(return_value)+str(smallest_unit))
                print("最后结果的值： ", return_value)
                print("最后结果的单位：", smallest_unit)

            if ptree[ptree[sum_val].children[4]].value2[0] in case2_list:
                return_value = convert_value(ptree[ptree[sum_val].children[4]].value2[0])
                print("最后结果的值： ", return_value)
                last_symbol = lexer.symbol_table.get_last_symbol()
                print("最后结果的单位：", last_symbol['unit'])
                ptree[sum_val].value2.append(str(return_value)+str(last_symbol['unit']))
                
            if ptree[ptree[sum_val].children[4]].value2[0] in unit_list:# 率之
                result = lexer.symbol_table.calculate_value_ratio(ptree[ptree[sum_val].children[4]].value2[0])
                print("结果： ", result)
                ptree[sum_val].value2.append(str(result))
            if ptree[ptree[sum_val].children[4]].value2[0] =='馀':
                lexer.symbol_table.print_symbols()
                last_symbol = lexer.symbol_table.get_last_symbol()
                if last_symbol['unit'] == None:
                    ptree[sum_val].value2.append(str(last_symbol['value']))
                else:
                    print("最后结果的值： ", last_symbol['value'])
                    print("最后结果的单位：", last_symbol['unit'])
                    ptree[sum_val].value2.append(str(last_symbol['value'])+str(last_symbol['unit']))

            if ptree[ptree[sum_val].children[4]].value2[0] =='约之':
                last_symbol = lexer.symbol_table.get_last_symbol()
                if last_symbol['unit'] == None:
                    ptree[sum_val].value2.append(str(last_symbol['value']))
                else:
                    print("最后结果的值： ", last_symbol['value'])
                    print("最后结果的单位：", last_symbol['unit'])
                    ptree[sum_val].value2.append(str(last_symbol['value'])+str(last_symbol['unit']))

            if ptree[ptree[sum_val].children[4]].value2[0] =='合之':
    # same_unit_flag=lexer.symbol_table.check_symbols()
                lexer.symbol_table.print_symbols()
                result = lexer.symbol_table.sum_converted_values()
                print("合之 = ", result)
                if result[1] == None:
                    ptree[sum_val].value2.append(str(result[0]))
                else:
                    ptree[sum_val].value2.append(str(result[0])+str(result[1]))

            if ptree[ptree[sum_val].children[4]].value2[0] =='孰多':
                result = lexer.symbol_table.symbol_compare_values()
                print("孰多 = ", result)
                ptree[sum_val].value2.append(str(result))

            if ptree[ptree[sum_val].children[4]].value2[0] =='减多益少':
                result = lexer.symbol_table.symbol_average_values()
                print("减多益少 = ", result)
                ptree[sum_val].value2.append(str(result))
                            
        sum_val += 1
    
    else:
        return -1  # error action value
    


