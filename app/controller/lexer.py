# coding=utf-8
# 上面的行是必需的，它定义了Python文件的编码格式为UTF-8
import re
from flask import Flask, request, jsonify
from enum import Enum, auto
import math


class Token:
    """
    Token类用于表示文本中的一个词法单元（token）。

    Attributes:
        type (str): Token的类型，如'NUMBER'、'LEXEME'等，表示该token的词法角色。
        value (str): Token的值，即文本中token对应的具体字符串。
    """

    def __init__(self, type, value):
        """
        Token类的构造函数。

        Parameters:
            type (str): Token的类型。
            value (str): Token的值。
        """
        self.type = type
        self.value = value

    def __repr__(self):
        """
        生成Token的字符串表示形式。

        Returns:
            str: 表示Token的字符串，格式为"(type='token_type', value='token_value')"。
        """
        return f"(type='{self.type}', value='{self.value}')"


# 读取外部文件进入正则
def load_regex_from_file(file_path):
    """从指定的文件路径加载正则表达式字符串。"""
    with open(file_path, 'r', encoding='utf-8') as file:
        regex_pattern = file.read().replace('\n', '')
    return regex_pattern


CN_UNIT = {
    '十': 10,
    '拾': 10,
    '百': 100,
    '佰': 100,
    '千': 1000,
    '仟': 1000,
    '万': 10000,
    '萬': 10000,
    '亿': 100000000,
    '億': 100000000,
    '兆': 1000000000000,
}

CN_NUM = {
    '〇': 0, '一': 1, '二': 2, '三': 3, '四': 4, '五': 5, '六': 6, '七': 7, '八': 8, '九': 9, '零': 0, '壹': 1, '贰': 2,
    '叁': 3, '肆': 4, '伍': 5, '陆': 6, '柒': 7, '捌': 8, '玖': 9, '貮': 2, '两': 2, }


# ???
def chinese_to_arabic_fractions(chinese_num):
    # 创建一个字典，映射中文数字到阿拉伯数字
    chinese_arabic_map = {'一': 1, '二': 2, '三': 3, '四': 4, '五': 5, '六': 6, '七': 7, '八': 8, '九': 9, '十': 10}
    return chinese_arabic_map.get(chinese_num, None)


def chinese_to_arabic(cn: str) -> int:
    """中文汉字转阿拉伯数字"""
    # if isinstance(cn, int):  # Check if input is an integer
    #     cn = str(cn)  # Convert integer to string
    unit = 0  # current
    ldig = []  # digest
    for cndig in reversed(cn):
        if cndig in CN_UNIT:
            unit = CN_UNIT.get(cndig)
            if unit == 10000 or unit == 100000000:
                ldig.append(unit)
                unit = 1
        else:
            dig = CN_NUM.get(cndig)
            if unit:
                dig *= unit
                unit = 0
            ldig.append(dig)
    if unit == 10:
        ldig.append(10)
    val, tmp = 0, 0
    for x in reversed(ldig):
        if x == 10000 or x == 100000000:
            val += tmp * x
            tmp = 0
        else:
            tmp += x
    val += tmp
    return val


def get_category_name(word):
    categories = {
        '面积': [
            "田", "圭田", "邪田", "箕田", "圆田", "宛田", "弧田", "环田"
        ],
        '长度': [
            "广", "从", "周", "径", "弦", "矢", "头广", "舌广", "踵广", "上广", "下广", "末广", "正从",
            "高", "袤", "深", "方", "上方", "下方", "上周", "下周", "上袤", "下袤", "中周", "外周",
            "上中周", "下中周", "立圆径", "立方", "圆周", "方", "买布", "买缣", "勾"
        ],
        '体积': [
            "城", "垣", "堤", "沟", "聢", "穿渠", "渠", "堑", "方堡壔", "圆堡壔", "方亭", "圆亭", "圆锥", "方锥",
            "堑堵", "阳马", "刍童", "曲池", "盘池", "冥谷", "鳖臑", "羡除", "刍甍", "仓", "圆困", "委粟平地",
            "委菽依垣", "委米依垣内角", "积"
        ],
        '容积': [
            "粟", "粝米", "稗米", "绺米", "御米", "小䵂", "大䵂", "粝饭", "稗饭", "绺饭", "御饭", "菽", "答", "麻",
            "麦", "稻", "豉", "飧", "熟菽", "櫱", "米", "买漆"
        ],

        '重量': ["买丝"],

        '数量钱': ["出"],
        '数量枚': ["买瓴甓", "买矢簳"],
        '数量个': ["买竹"],
        '数量翭': ["买羽"],
        '无量纲量': ["无量纲量"],
        '量纲量': ["量纲量"],
    }
    for category, words in categories.items():
        if word in words:
            return category

    return None  # 如果词语不在任何类别中，则返回None


# ???
# 根据symbol_table中的没有值和没有单位的是构造类，需要计算赋值
def process_symbols_based_on_type(lexer, unit=None):
    # 获取所有需要处理的类型名称
    types_to_process = lexer.symbol_table.get_types_needing_processing()

    for type_name in types_to_process:
        # 获取当前类型的详细信息
        current_symbol = lexer.symbol_table.get_symbol(type_name)
        print(current_symbol)

        # 没有值和没有单位的是构造类，需要计算赋值，都为空的话就是要构造的type，只是unit为空的话可以是无量纲量
        if current_symbol and (current_symbol['value'] is None and current_symbol['unit'] is None):
            complete_symbols = lexer.symbol_table.get_complete_symbols()
            print("complete_symbols = ", complete_symbols)

            symbol_types = [symbol['type'] for symbol in complete_symbols]  # 提取类型名称列表
            print("symbol_types =", symbol_types)

            # 调用 compare_symbol_units 方法比较多个符号单位
            # 这里传的是type的名称，不是一整个symbol
            smallest_unit = lexer.symbol_table.compare_symbol_units(symbol_types)
            print("smallest_unit = ", smallest_unit)
            print("type_name = ", type_name)
            # 执行该类型对应的计算函数
            result = lexer.symbol_table.execute_function_by_type(type_name, smallest_unit)
            print("result = ", result)
            if result:
                # value = result
                value, unit = result[0], result[1]
                # print('@@@@@')
                # print(value,unit)
                # 更新符号表中的条目
                lexer.symbol_table.update_symbol(type_name, value, unit)
                print(f"已更新类型 {type_name} 的数据: {value} {unit}")
            else:
                print(f"无法计算类型 {type_name} 的数据。")
        else:
            print(f"类型 {type_name} 已有完整的数据或不存在。")


class Lexer:
    def __init__(self):
        # 加载正则表达式
        regex_file_path = 'billion.txt'  # 替换为你的文件实际路径
        chinese_number_pattern = load_regex_from_file(regex_file_path)
        # 合之,馀放在type
        self.token_patterns = {
            'NUMBER': rf'({chinese_number_pattern})',
            'LEXEME': r'(今|又|有)',
            'TYPE': r'(田|圭田|邪田|箕田|圆田|宛田|弧田|环田|广|从|周|径|弦|矢|头广|舌广|踵广|上广|下广|末广|正从|高|袤|深|上方|下方|上周|下周|上袤|下袤|中周|外周|上中周|下中周|立圆径|立方|圆周|积|粟|粝米|稗米|绺米|御米|小䵂|大䵂|粝饭|稗饭|绺饭|御饭|菽|答|麻|麦|稻|豉|飧|熟菽|櫱|米|穿地|坚|壤|城|垣|堤|沟|聢|穿渠|渠|堑堵|方堡壔|圆堡壔|方亭|圆亭|圆锥|方锥|堑|阳马|刍童|曲池|盘池|冥谷|鳖臑|羡除|刍甍|仓|圆困|委粟平地|委菽依垣|委米依垣内角|出|买瓴甓|买布|买丝|买竹|买漆|买缣|买羽|买矢簳|勾|股|方)',
            'UNIT': r'(步|里|尺|寸|匹|丈|亩|顷|斗|升|斛|钱|枚|个|石|钧|斤|两|铢|翭)',
            'QUESTION': r'(问|为|减多益少|得|各|求|约之|几何|孰多|多|而平|欲|率之|馀|合之|分|之|其|太半|少半|太|半|少)',  # 孰多、孰少这些增强可以后面补
            'FUNCTION': r'(减)',
            'PUNCTUATION': r'(。|？|、|，)',
            'OTHER': r'[^一二三四五六七八九亿万千百十步里人钱今又有田广从周径弦失圭邪箕圆宛弧环头正畔舌踵下中外问为馀得各约之合之几何减多益少分之减其孰，。？、田圭田邪田箕田圆田宛田弧田环田广从周径弦矢头广舌广踵广上广下广正从高袤深方上方下方上周下周上袤下袤中周外周上中周下中周立圆径立方圆周积方粟粝米稗米绺米御米小䵂大䵂粝饭稗饭绺饭御饭菽答麻麦稻豉飧熟菽櫱米穿地坚壤城垣堤沟聢穿渠渠堑方堡壔圆堡壔方亭圆亭圆锥方锥堑堵阳马刍童曲池盘冥谷鳖臑羡除刍甍仓圆困委粟平地委菽依垣委米依垣内角出买瓴甓买布买丝买竹买漆买缣买羽买矢簳勾股步里尺寸匹丈亩顷斗升斛钱枚个石钧斤两铢翭问为馀得各约之合之几何减多益少孰多而平太半少太半少半]+ '
            # 除本章以外的词
        }

        # 生成一个总的正则表达式，用于查找上述所有类型的标记
        self.token_regex = '|'.join(f'(?P<{type}>{pattern})' for type, pattern in self.token_patterns.items())

        # 定义状态转换表，用于指导如何根据当前标记类型转换到下一个状态
        self.state_transition_table = {
            'START': {'NUMBER': 'ERROR', 'LEXEME': 'LEXEME', 'TYPE': 'ERROR', 'PREFIX': 'ERROR', 'UNIT': 'ERROR',
                      'QUESTION': 'ERROR', 'FUNCTION': 'ERROR', 'PUNCTUATION': 'ERROR', 'OTHER': 'ERROR'},
            'NUMBER': {'NUMBER': 'ERROR', 'LEXEME': 'ERROR', 'TYPE': 'TYPE', 'PREFIX': 'PREFIX', 'UNIT': 'UNIT',
                       'QUESTION': 'QUESTION', 'FUNCTION': 'FUNCTION', 'PUNCTUATION': 'PUNCTUATION', 'OTHER': 'ERROR'},
            'LEXEME': {'NUMBER': 'NUMBER', 'LEXEME': 'LEXEME', 'TYPE': 'TYPE', 'PREFIX': 'PREFIX', 'UNIT': 'ERROR',
                       'QUESTION': 'ERROR', 'FUNCTION': 'ERROR', 'PUNCTUATION': 'ERROR', 'OTHER': 'ERROR'},
            'TYPE': {'NUMBER': 'NUMBER', 'LEXEME': 'ERROR', 'TYPE': 'TYPE', 'PREFIX': 'ERROR', 'UNIT': 'ERROR',
                     'QUESTION': 'QUESTION', 'FUNCTION': 'FUNCTION', 'PUNCTUATION': 'PUNCTUATION', 'OTHER': 'ERROR'},
            'PREFIX': {'NUMBER': 'ERROR', 'LEXEME': 'ERROR', 'TYPE': 'TYPE', 'PREFIX': 'ERROR', 'UNIT': 'ERROR',
                       'QUESTION': 'ERROR', 'FUNCTION': 'ERROR', 'PUNCTUATION': 'ERROR', 'OTHER': 'ERROR'},
            'UNIT': {'NUMBER': 'NUMBER', 'LEXEME': 'ERROR', 'TYPE': 'ERROR', 'PREFIX': 'ERROR', 'UNIT': 'ERROR',
                     'QUESTION': 'QUESTION', 'FUNCTION': 'FUNCTION', 'PUNCTUATION': 'PUNCTUATION', 'OTHER': 'ERROR'},
            'QUESTION': {'NUMBER': 'NUMBER', 'LEXEME': 'ERROR', 'TYPE': 'TYPE', 'PREFIX': 'ERROR', 'UNIT': 'UNIT',
                         'QUESTION': 'QUESTION', 'FUNCTION': 'FUNCTION', 'PUNCTUATION': 'PUNCTUATION',
                         'OTHER': 'ERROR'},
            'FUNCTION': {'NUMBER': 'NUMBER', 'LEXEME': 'ERROR', 'TYPE': 'TYPE', 'PREFIX': 'ERROR', 'UNIT': 'UNIT',
                         'QUESTION': 'QUESTION', 'FUNCTION': 'FUNCTION', 'PUNCTUATION': 'PUNCTUATION',
                         'OTHER': 'ERROR'},
            'PUNCTUATION': {'NUMBER': 'NUMBER', 'LEXEME': 'LEXEME', 'TYPE': 'TYPE', 'PREFIX': 'PREFIX', 'UNIT': 'ERROR',
                            'QUESTION': 'QUESTION', 'FUNCTION': 'FUNCTION', 'PUNCTUATION': 'ERROR', 'OTHER': 'ERROR'},
            'OTHER': {'NUMBER': 'ERROR', 'LEXEME': 'ERROR', 'TYPE': 'ERROR', 'PREFIX': 'ERROR', 'UNIT': 'ERROR',
                      'QUESTION': 'ERROR', 'FUNCTION': 'ERROR', 'PUNCTUATION': 'ERROR', 'OTHER': 'ERROR'},
        }
        # 确定初始状态
        self.current_state = 'START'
        # 初始化symbol_table
        # 在 Lexer 类的构造函数中初始化 SymbolTable 的实例
        self.symbol_table = SymbolTable()

    # 根据匹配到的文本返回对应的标记类型
    def get_token_type(self, match):
        for token_type, pattern in self.token_patterns.items():
            if re.fullmatch(pattern, match):
                return token_type
        return 'ERROR'

    # 对输入的文本进行标记化处理
    def tokenize(self, text):
        tokens = []
        for match in re.finditer(self.token_regex, text):
            token_value = match.group()
            token_type = self.get_token_type(token_value)
            if token_type == 'ERROR':
                print("lexer error detected")
                break  # 跳过无法识别的标记
            next_state = self.state_transition_table[self.current_state].get(token_type)
            if next_state == 'ERROR':
                print("lexer error detected")
                self.current_state = 'START'  # 遇到错误重置状态
                break
            else:
                self.current_state = next_state  # 转移到下一个状态
                token = Token(token_type, token_value)  # 创建 Token 实例
                tokens.append(token)  # 放进token中
        return tokens

    def extract_values(self, tokens):
        token_value = []
        for token in tokens:
            if token.type == "NUMBER":
                value = chinese_to_arabic(str(token.value))
                token_value.append(str(value))
            # 提取每个token的 'value' 键对应的值，并返回这些值的列表
            else:
                token_value.append(token.value)

        token_value.append("$")
        return token_value

    # 把token加入symbol table中
    # def add_tokens_to_symbol_table(self, tokens):
    #     print("tokens长度", len(tokens))
    #     for i, token in enumerate(tokens):
    #         if token.type == 'TYPE':
    #             unit_value = None
    #             # print('!!!!!!!!!找到type为TYPE的')
    #             # print(tokens[i].type)
    #             # print(tokens[i].value)
    #             # print(tokens[i + 1].type)
    #             # print(tokens[i + 1].value)
    #             if i + 1 < len(tokens) and tokens[i + 1].type == 'NUMBER' and tokens[i + 2].type == 'UNIT':
    #                 print('--------进入加入symbol')
    #                 type_value_str = tokens[i + 1].value
    #                 print(type_value_str)
    #                 type_value = chinese_to_arabic(type_value_str)
    #                 print(type_value)
    #                 unit_value = tokens[i + 2].value
    #                 # 把该type所属于的类传去name
    #                 name = get_category_name(token.value)
    #                 self.symbol_table.add_symbol(name, token.value, type_value, unit_value)
    #                 # self.symbol_table.print_symbols()
    #             elif i + 1 < len(tokens):
    #                 # 把该type所属于的类传去name
    #                 name = get_category_name(token.value)
    #                 self.symbol_table.add_symbol(name, token.value, None, None)
    #
    #     # self.symbol_table.print_symbols()

    # ???
    def add_tokens_to_symbol_table(self, tokens):
        print("tokens长度", len(tokens))
        i = 0
        while i < len(tokens):
            token = tokens[i]
            # 检查当前token是否是数字
            if token.type == 'NUMBER':
                # 检查后续token是否形成“分数”结构：'数字' + '分' + '之' + '数字'， 该结构为无量纲量
                if (i + 2 < len(tokens) and tokens[i + 1].type == 'FUNCTION' and tokens[i + 1].value == '分' and
                        tokens[i + 2].type == 'FUNCTION' and tokens[i + 2].value == '之' and
                        i + 3 < len(tokens) and tokens[i + 3].type == 'NUMBER'):

                    print('--------进入加入symbol，处理分数')
                    denominator = chinese_to_arabic(token.value)  # 当前token作为分母
                    numerator = chinese_to_arabic(tokens[i + 3].value)  # 第四个token作为分子

                    if numerator is not None and denominator is not None:
                        fraction_value = numerator / denominator  # 计算分数值
                        print(f"分数: {fraction_value}")
                        # 分数的类别处理可能需要额外逻辑
                        name = "分数"  # 假设所有分数都归类为"Fraction"
                        # self.symbol_table.add_symbol(name, f"{denominator}分之{numerator}", fraction_value, None)
                        self.symbol_table.add_symbol(name, "无量纲量", fraction_value, None)
                        i += 3  # 跳过处理过的token
                # 整数结构
                elif tokens[i - 1].type != 'TYPE':
                    # 量纲量
                    if tokens[i + 1].type == 'UNIT':
                        integer = chinese_to_arabic(token.value)
                        name = "整数"
                        unit_value = tokens[i + 1].value
                        self.symbol_table.add_symbol(name, "量纲量", integer, unit_value)
                    # 无量纲量
                    else:
                        integer = chinese_to_arabic(token.value)
                        name = "整数"
                        self.symbol_table.add_symbol(name, "无量纲量", integer, None)

            if token.type == 'TYPE':
                if i + 1 < len(tokens) and tokens[i + 1].type == 'NUMBER' and tokens[i + 2].type == 'UNIT':
                    print('--------进入加入symbol')
                    type_value_str = tokens[i + 1].value
                    print("type_value_str = ", type_value_str)
                    # 把中文数字转成阿拉伯数字用于计算
                    type_value = chinese_to_arabic(type_value_str)
                    print("type_value = ", type_value)
                    unit_value = tokens[i + 2].value
                    # 把该type所属于的类传去name
                    name = get_category_name(token.value)
                    self.symbol_table.add_symbol(name, token.value, type_value, unit_value)
                    # self.symbol_table.print_symbols()

                else:
                    # 处理其他类型的token
                    name = get_category_name(token.value)
                    self.symbol_table.add_symbol(name, token.value, None, None)
            i += 1

    #  单文本处理
    def tokenize_texts(self, texts):
        tokens = []  # 初始化一个空列表来存储所有的 tokens
        for text in texts:
            self.current_state = 'START'  # 重置 lexer 状态为 START
            tokens.extend(self.tokenize(text))  # 使用 extend 而不是 append 来添加元素
        return tokens

    # 单文本输出
    def format_and_display_results(self, tokens):
        formatted_results_with_numbers = []

        for i, token in enumerate(tokens, start=1):
            formatted_token = f"Token {i}: Type='{token.type}', Value='{token.value}'"
            formatted_results_with_numbers.append(formatted_token)

        # 显示格式化结果
        for formatted_result in formatted_results_with_numbers:
            print(formatted_result)

    # ----------------华丽的单多文本分界线-----------------

    # # 多文本处理
    # def tokenize_texts(self, texts):
    #     results = []
    #     for text in texts:
    #         self.current_state = 'START'  # 重置 lexer 状态为 START
    #         tokens = self.tokenize(text)  # 直接获取 tokens 列表
    #         results.append((text, tokens))  # 将 (text, tokens) 元组添加到结果中
    #     return results
    #
    # # 多文本输出
    # def format_and_display_results(self, results):
    #     formatted_results_with_numbers = []
    #
    #     for i, (text, tokens) in enumerate(results, start=1):
    #         formatted_text = f"Text {i}: {text}\nTokens:\n"
    #         formatted_tokens = "\n".join([f"  - {token.type}: '{token.value}'" for token in tokens])
    #         formatted_results_with_numbers.append(formatted_text + formatted_tokens)
    #
    #     # Displaying formatted results with numbers for the first few entries
    #     for formatted_result in formatted_results_with_numbers:
    #         print(formatted_result)
    #         print("\n---\n")

    def extract_token_types(self, tokens):
        """
        从Token列表中提取每个Token的type或value，并根据条件转换特定type。
        特定标点符号转换为对应的描述字符串，并在列表结尾添加"DOLLAR"。

        参数:
        - tokens (list): Token对象列表。

        返回:
        - list: 根据Token类型条件和特定标点符号返回的type、value或描述字符串组成的列表，末尾加上"DOLLAR"。
        """

        result = []
        for token in tokens:
            if token.type == 'NUMBER':
                result.append('num')  # 将"NUMBER"转换为"NUM"
            elif token.type == 'TYPE':
                result.append('type')  # 将"TYPE"转换为"type" (parser那边的val是小写)
            elif token.type == 'UNIT':
                result.append('unit')  # 将"UNIT"转换为"unit" (parser那边的val是小写)
            elif token.type == 'FUNCTION':
                result.append('fun')  # 将"UNIT"转换为"unit" (parser那边的val是小写)
            else:
                result.append(token.value)  # 返回Token的值

        # 在列表结尾添加"DOLLAR"
        result.append('$')

        return result


class SymbolTable:
    def __init__(self):
        # 使用字典来存储符号及其属性
        self.symbols = {}

    def add_symbol(self, type, value, unit):
        """
        添加一个符号到符号表中，如果符号已存在，则修改名字使其唯一。

        参数:
            name (str): 单位的名称或标识符。
            unit (str): 单位的描述或类型。
            value (float): 与单位相关联的数值。
        """
        unique_name = self.generate_unique_name(type)
        name = get_category_name(type)
        self.symbols[unique_name] = {"name": name, "type": unique_name, "value": value, "unit": unit}

    def generate_unique_name(self, type):
        """
        生成一个唯一的名称，如果类型已存在，则添加数字后缀。
        """
        base_name = type
        count = 1
        new_name = base_name
        # 当新名称已存在于符号表中时，生成一个新的名称
        while new_name in self.symbols:
            new_name = f"{base_name}{count}"
            count += 1
        return new_name

    def update_symbol(self, name, value, unit):
        if name in self.symbols:
            self.symbols[name]['value'] = value
            self.symbols[name]['unit'] = unit
        else:
            print(f"Symbol {name} not found.")

    def update_symbols_list(self, update_list):
        """
        更新符号表中的符号值和单位。

        参数:
            update_list (list of dict): 包含符号更新信息的列表，每个字典包含 'name', 'type', 'value', 'unit'.
        """
        for update in update_list:
            if update['type'] in self.symbols:
                # 如果符号存在，则更新其值和单位
                self.symbols[update['type']]['value'] = update['value']
                self.symbols[update['type']]['unit'] = update['unit']
            else:
                # 如果符号不存在，可以选择添加新符号或者忽略/记录错误
                print(f"Symbol with type '{update['type']}' not found in symbol table.")

    def get_symbol(self, type):
        """
        从符号表中检索一个单位符号的信息。

        参数:
            name (str): 要检索的单位的名称或标识符。

        返回:
            dict: 检索到的单位符号的信息，如果不存在则返回 None。
        """
        return self.symbols.get(type)

    def classify_symbols(self):
        """
        将所有符号按名称进行分类，并返回一个包含所有类别的字典。

        返回:
            dict: 键为符号名称，值为包含相同名称的所有符号信息的列表。
        """
        classified_symbols = {}
        for name, symbol_info in self.symbols.items():
            type_name = self.extract_name(name)
            if type_name not in classified_symbols:
                classified_symbols[type_name] = []
            classified_symbols[type_name].append(symbol_info)  # 将符号信息加入到对应名称的列表中
        return classified_symbols

    def update_all_symbol_names(self, new_name):
        """
        更新符号表中所有符号的名称。

        参数:
            new_name (str): 所有符号将被更新为这个新名称。
        """
        for symbol in self.symbols.values():
            symbol['name'] = new_name

    @classmethod
    def determine_unit_category(cls, units):
        """
        确定单位列表是否属于同一类型。

        参数:
            units (list): 单位的字符串列表。

        返回:
            tuple: (bool, str) 布尔值表示是否所有单位属于同一类型，字符串表示类型名称。
        """

        # 映射各类型名称对应的单位列表
        unit_categories = {
            '长度': ['里', '匹', '丈', '步', '尺', '寸'],
            '面积': ['顷', '亩'],
            '容积': ['斛', '斗', '升'],
            '重量': ['石', '钧', '斤', '两', '铢'],
            '数量钱': ["钱"],
            '数量枚': ["枚"],
            '数量个': ["个"],
            '数量翭': ["翭"],
        }
        # 遍历单位列表，查找它们的类型
        types_found = set()
        for unit in units:
            for category, category_units in unit_categories.items():
                if unit in category_units:
                    types_found.add(category)
                    break  # 已找到该单位类型，跳出内层循环

        # 检查是否所有单位都有同一类型
        if len(types_found) == 1:
            return True, types_found.pop()  # 返回True和类型名称
        else:
            return False, None  # 类型不一致或未找到

    def get_symbol_count(self):
        """
        返回符号表中符号的总数。

        返回:
            int: 符号的总数。
        """
        return len(self.symbols)

    def print_symbols(self):
        """
        打印符号表中所有单位符号的详细信息。
        """
        if not self.symbols:
            print("Symbol table is empty.")
            return
        for name, info in self.symbols.items():
            print(f"Name: {info['name']}, Type: {info['type']}, Value: {info['value']}, Unit: {info['unit']}")

    def check_and_sum_symbols(self):
        result = 0
        unit_list = []
        if not self.symbols:
            print("Symbol table is empty.")
            return
        for name, info in self.symbols.items():
            unit_list.append(info['name'])
        if len(set(unit_list)):
            for name, info in self.symbols.items():
                result += float(info['value'])

        return result

    def extract_name(self, type_name):
        """
        根据唯一标识符从字典中提取 'name' 键的值。

        参数:
            type_name (str): 要提取名称的符号的唯一标识符。

        返回:
            str: 'name' 键对应的值，如果不存在则返回 None。
        """
        symbol = self.symbols.get(type_name)
        if symbol:
            return symbol.get('name')
        return None

        # def execute_function_by_type(self, type, unit='步'):

    def execute_function_by_type(self, type):

        """
        从function_type计算target这个结果
        """
        if type in total_types:
            print("获取类型:", type)
            # 假设每种类型都需要一组特定的维度键来实例化
            dimensions_needed = {
                '田': ['广', '从', '田1'],
                '圭田': ['广', '正从', '田'],
                '邪田': ['头广', '头广1', '正从', '田'],
                '箕田': ['舌广', '踵广', '正从', '田'],
                '圆田': ['周', '径', '田'],
                '宛田': ['下周', '径', '田'],
                '弧田': ['弦', '矢', '田'],
                '环田': ['中周', '外周', '径', '田'],
                '城': ['上广', '下广', '高', '袤', '积'],
                '垣': ['上广', '下广', '高', '袤', '积'],
                '堤': ['上广', '下广', '高', '袤', '积'],
                '沟': ['上广', '下广', '深', '袤', '积'],
                '聢': ['上广', '下广', '深', '袤', '积'],
                '穿渠': ['上广', '下广', '深', '袤', '积'],
                '渠': ['上广', '下广', '深', '袤', '积'],
                '堑': ['上广', '下广', '深', '袤', '积'],
                '方堡壔': ['方', '高', '积'],
                '圆堡壔': ['周', '高', '积'],
                '方亭': ['上方', '下方', '高', '积'],
                '圆亭': ['上周', '下周', '高', '积'],
                '圆锥': ['下周', '高', '积'],
                '方锥': ['下方', '高', '积'],
                '堑堵': ['下广', '袤', '高', '积'],
                '阳马': ['广', '袤', '高', '积'],
                '刍童': ['上广', '下广', '上袤', '下袤', '高', '积'],
                '曲池': ['上中周', '下中周', '外周', '外周1', '上广', '下广', '深', '积'],
                '盘池': ['上广', '下广', '上袤', '下袤', '深', '积'],
                '冥谷': ['上广', '下广', '上袤', '下袤', '深', '积'],
                '鳖臑': ['下广', '上袤', '高', '积'],
                '羡除': ['上广', '下广', '末广', '深', '袤', '积'],
                '刍甍': ['下袤', '上袤', '下广', '高', '积'],
                '仓': ['广', '高', '袤', '积'],
                '圆困': ['周', '高', '积'],
                '委粟平地': ['下周', '高', '积'],
                '委菽依垣': ['下周', '高', '积'],
                '委米依垣内角': ['下周', '高', '积'],
                # # Add other mappings as needed
            }
            dimensions = {}
            # 检查该类型是否在所需维度的列表中
            if type in dimensions_needed:
                # 根据key和type对应，从列表中找到对应的元素
                for dimension in dimensions_needed[type]:
                    symbol = self.get_symbol(dimension)
                    print("方程list中的symbol = ", symbol)
                    if symbol:
                        dimensions[dimension] = (symbol['value'], symbol['unit'])
                    else:
                        print(f"警告: 找不到必要的维度 '{dimension}'")
                        return None
                # print("type = ", type)
                print("把symbol转换成字典，维度")
                print("dimensions = ", dimensions)
                # 生成该类型的实例并计算，从total_types中通过方程名字找对应的函数并执行
                print("生成该类型的实例并计算，从total_types中通过方程名字找对应的函数并执行")
                instance = total_types[type](type, dimensions)
                print("instance = ", instance)
                # print(f"创建的 {type} 实例: {instance}")
                # print("instance_value = ", instance.value(unit))
                # return instance.value(unit)
                print("执行方程后的值 instance_value = ", instance.value())
                return instance.value()
                print("没有定义这种类型的所需维度")
        else:
            print("在total type中未找到类型:", type)
        return None

    def get_types_needing_processing(self):
        # 这个方法返回所有缺少值或单位的类型名称
        types_needing_processing = []
        for name, details in self.symbols.items():
            if details['value'] is None or details['unit'] is None:
                types_needing_processing.append(name)
        return types_needing_processing

        # def adjust_unit_based_on_type_name(self, name):
        #     """
        #     根据符号的类型自动调整单位名称。
        #
        #     参数:
        #         type_name (str): 符号名称，type的类型，需要检查其类型并可能修改其单位。
        #
        #     返回:
        #         None，但会直接在符号表中更新单位。
        #     """
        #     symbol = self.get_symbol(name)
        #     if symbol:
        #         unit = symbol['unit']
        #         # 检查符号类型是否与面积或体积相关
        #         if '面积' in symbol['name'] and unit in ["里", "匹", "丈", "步", "尺", "寸"]:
        #             symbol['unit'] = f"平方{unit}"
        #         elif '体积' in symbol['name'] and unit in ["里", "匹", "丈", "步", "尺", "寸"]:
        #             symbol['unit'] = f"立方{unit}"
        #         # 更新符号表中的信息
        #         self.symbols[name] = symbol
        #     else:
        #         print(f"符号 {name} 未找到，无法调整单位。")

    def find_symbols_by_name(self, search_name):
        """
        查找所有名称匹配指定搜索名称的符号，并返回它们的详细信息字典列表。

        参数:
            search_name (str): 要搜索的符号名称。

        返回:
            list of dict: 符号详细信息的字典列表。
        """
        results = []
        for symbol_key, info in self.symbols.items():
            if info['name'] == search_name:
                results.append(info)  # 直接添加符号信息的字典到结果列表
        return results

    def find_units_by_name(self, search_name):
        """
        查找所有名称匹配指定搜索名称的符号的单位，并以列表形式返回它们。

        参数:
            search_name (str): 要搜索的符号名称。

        返回:
            list of str: 找到的单位列表。
        """
        units = []
        for symbol_key, info in self.symbols.items():
            if info['name'] == search_name:
                units.append(info['unit'])  # 添加符号的单位到列表中
        return units


    def get_last_symbol(self):
        """
        获取符号表中最后添加的符号的信息。

        返回:
            dict: 最后添加的符号的信息，如果符号表为空则返回 None。
        """
        if self.symbols:
            last_key = next(reversed(self.symbols.keys()))
            return self.symbols[last_key]
        return None

    def get_complete_symbols(self):
        """
        返回所有具有完整信息（即同时具有 value 和 unit）的符号。

        返回:
            list of dict: 包含完整信息的符号列表。
        """
        complete_symbols = []
        for symbol in self.symbols.values():
            if 'value' in symbol and 'unit' in symbol and symbol['value'] is not None and symbol['unit'] is not None:
                complete_symbols.append(symbol)
        return complete_symbols

    def compare_symbol_units(self, symbol_types):
        """
        根据符号类型名称列表比较符号单位，并返回具有最小单位转换率的单位名称。

        参数:
            symbol_types (list of str): 符号的类型名称列表。

        返回:
            str: 具有最小单位转换率的单位名称；如果列表为空或任何符号不存在，则返回 None。
        """
        # print("####")
        # print(symbol_types)
        symbols = [self.get_symbol(type) for type in symbol_types if self.get_symbol(type)]
        # print("####")
        print("symbols单位转换中： ", symbols)
        if not symbols:
            return None
        smallest_symbol = UnitConversion.find_smallest_unit_symbol(symbols)
        print("smallest_symbol单位转换中： ", smallest_symbol)
        return smallest_symbol['unit'] if smallest_symbol else None

    def calculate_value_ratio(self, target_unit):
        """
        计算第一个符号的值与转换为目标单位后第二个符号的值的比率。

        参数:
            target_unit (str): 第二个符号的目标单位。

        返回:
            str: 格式化的比率结果字符串。
        """
        if len(self.symbols) != 2:
            return "错误：符号表中必须正好有两个符号。"

        symbols = list(self.symbols.values())
        symbol1, symbol2 = symbols[0], symbols[1]

        print("symbol2['unit'] = ", symbol2['unit'])
        print("symbol2['value'] = ", symbol2['value'])
        print(symbol2)
        if symbol2['unit'] != target_unit:
            # 将第二个符号的单位转换为指定的目标单位， 返回的是一个元组，需要e.g.(60.0, '寸')需要取第一位
            converted_value, converted_unit = UnitConversion.convert_units(symbol2['value'], symbol2['unit'],
                                                                           target_unit,
                                                                           symbol2['name'])
            # print(converted_value)
            if converted_value == 0:
                return "错误：除零错误。"

            # 计算值的比率
            print("symbol1 = ", symbol1)
            print(symbol1['value'])
            print("converted_value = ", converted_value)
            value_ratio = symbol1['value'] / converted_value

        else:
            value_ratio = symbol1['value'] / symbol2['value']
        result = f"一{target_unit},{value_ratio}{symbol1['unit']}"
        return result

    def clear_symbols(self):
        """
        清空符号表中的所有符号。
        """
        self.symbols.clear()  # 使用字典的 clear 方法来清空符号表

    def sum_converted_values(self):
        """
        如果所有符号的名称相同，则将它们的值转换为共同的最小单位后累加。

        返回:
            float 或 None: 所有符号值的总和，如果符号表为空则返回 None。
        """
        if not self.symbols:
            return None

        # 确保所有符号名称相同
        first_symbol_name = next(iter(self.symbols.values()))['name']
        if not all(symbol['name'] == first_symbol_name for symbol in self.symbols.values()):
            return None

        # 提取所有符号的单位
        units = [symbol['unit'] for symbol in self.symbols.values()]
        unit_type = first_symbol_name  # 或者是 '长度', '体积' 等，根据具体的情况确定
        print("units1 = ", units)
        print("unit_type =", unit_type)
        if unit_type == "量纲量":
            print(unit_type)
            flag, type_name = SymbolTable.determine_unit_category(units)
            print("flag =", flag)
            print("type_name =", type_name)
            if not flag:
                return None

            self.update_all_symbol_names(type_name)
            self.print_symbols()

            smallest_unit = UnitConversion.find_smallest_unit(units, type_name)
            print(smallest_unit)
            if smallest_unit is None:
                return None

            # 转换所有值到最小单位并累加
            total_value = 0.0
            for symbol in self.symbols.values():
                converted_value, _ = UnitConversion.convert_units(symbol['value'], symbol['unit'], smallest_unit,
                                                                  type_name)
                print("converted_value = ", converted_value)
                if converted_value is not None:
                    total_value += converted_value

            return total_value, smallest_unit

        elif unit_type == "无量纲量":
            values = [symbol['value'] for symbol in self.symbols.values()]
            total_value = sum(values)
            return total_value, None

        else:
            # 找到最小单位
            smallest_unit = UnitConversion.find_smallest_unit(units, unit_type)
            if smallest_unit is None:
                return None

            # 转换所有值到最小单位并累加
            total_value = 0.0
            for symbol in self.symbols.values():
                converted_value, _ = UnitConversion.convert_units(symbol['value'], symbol['unit'], smallest_unit,
                                                                  unit_type)
                print("converted_value = ", converted_value)
                if converted_value is not None:
                    total_value += converted_value

            return total_value, smallest_unit
            return total_value, smallest_unit

    def symbol_compare_values(self):
        """
        如果所有符号的名称相同，则将它们的值转换为共同的最小单位后累加。

        返回:
            float 或 None: 所有符号值的总和，如果符号表为空则返回 None。
        """
        if len(self.symbols) != 2:
            return "错误：符号表中必须正好有两个符号。"

        if not self.symbols:
            return None

        # 确保所有符号名称相同
        first_symbol_name = next(iter(self.symbols.values()))['name']
        if not all(symbol['name'] == first_symbol_name for symbol in self.symbols.values()):
            return None

        units = [symbol['unit'] for symbol in self.symbols.values()]
        unit_type = first_symbol_name
        if unit_type == "量纲量":
            print(unit_type)
            flag, type_name = SymbolTable.determine_unit_category(units)
            print("flag =", flag)
            print("type_name =", type_name)
            if not flag:
                return None

            self.update_all_symbol_names(type_name)
            self.print_symbols()

            smallest_unit = UnitConversion.find_smallest_unit(units, type_name)
            print(smallest_unit)
            if smallest_unit is None:
                return None

            values_list = []
            for symbol in self.symbols.values():
                converted_value, _ = UnitConversion.convert_units(symbol['value'], symbol['unit'], smallest_unit,
                                                                  type_name)
                values_list.append(converted_value)

            print(values_list)
            # 将值转换为最小单位后比较大小
            value1 = values_list[0]
            value2 = values_list[1]
            types = [symbol['type'] for symbol in self.symbols.values()]

            type1 = types[0]
            type2 = types[1]

            difference = abs(value1 - value2)

            if value1 > value2:
                # max_value = value1
                return f"{value1}多，多{difference}{smallest_unit}"
            elif value1 < value2:
                # max_value = value2
                return f"{value2}多，多{difference}{smallest_unit}"
            else:
                return f"一样多，多{difference}{smallest_unit}"

        elif unit_type == "无量纲量":
            values = [symbol['value'] for symbol in self.symbols.values()]
            value1 = values[0]
            value2 = values[1]
            difference = abs(value1 - value2)

            if value1 > value2:
                # max_value = value1
                return f"{value1}多，多{difference}"
            elif value1 < value2:
                # max_value = value2
                return f"{value2}多，多{difference}"
            else:
                # max_value = value2
                f"一样多，多{difference}"


        else:
            # 提取所有符号的单位
            units = [symbol['unit'] for symbol in self.symbols.values()]
            unit_type = first_symbol_name  # 或者是 '长度', '体积' 等，根据具体的情况确定
            print(units)

            # 找到最小单位
            smallest_unit = UnitConversion.find_smallest_unit(units, unit_type)
            if smallest_unit is None:
                return None

            values_list = []
            for symbol in self.symbols.values():
                converted_value, _ = UnitConversion.convert_units(symbol['value'], symbol['unit'], smallest_unit,
                                                                  unit_type)
                values_list.append(converted_value)

            print(values_list)
            # 将值转换为最小单位后比较大小
            value1 = values_list[0]
            value2 = values_list[1]
            types = [symbol['type'] for symbol in self.symbols.values()]

            type1 = types[0]
            type2 = types[1]

            difference = abs(value1 - value2)

            if value1 > value2:
                # max_value = value1
                return f"{type1}多，多{difference}{smallest_unit}"
            elif value1 < value2:
                # max_value = value2
                return f"{type2}多，多{difference}{smallest_unit}"
            else:
                return f"一样多，多{difference}{smallest_unit}"

    def symbol_average_values(self):
        """
        如果所有符号的名称相同，则将它们的值转换为共同的最小单位后累加。

        返回:
            float 或 None: 所有符号值的总和，如果符号表为空则返回 None。
        """
        if len(self.symbols) != 2:
            return "错误：符号表中必须正好有两个符号。"

        if not self.symbols:
            return None

        # 确保所有符号名称相同
        first_symbol_name = next(iter(self.symbols.values()))['name']
        if not all(symbol['name'] == first_symbol_name for symbol in self.symbols.values()):
            print(first_symbol_name)
            return None

        units = [symbol['unit'] for symbol in self.symbols.values()]
        unit_type = first_symbol_name

        if unit_type == "量纲量":
            print(unit_type)
            flag, type_name = SymbolTable.determine_unit_category(units)
            print("flag =", flag)
            print("type_name =", type_name)
            if not flag:
                return None

            self.update_all_symbol_names(type_name)
            self.print_symbols()

            smallest_unit = UnitConversion.find_smallest_unit(units, type_name)
            print(smallest_unit)
            if smallest_unit is None:
                return None

            values_list = []
            for symbol in self.symbols.values():
                converted_value, _ = UnitConversion.convert_units(symbol['value'], symbol['unit'], smallest_unit,
                                                                  type_name)
                values_list.append(converted_value)

            print(values_list)
            # 将值转换为最小单位后比较大小
            value1 = values_list[0]
            value2 = values_list[1]

            types = [symbol['type'] for symbol in self.symbols.values()]
            type1 = types[0]
            type2 = types[1]

            average = (value1 + value2) / 2

            if value1 > value2:
                big_value = value1 - average
                # small_value = average - value2
                return "减" + type1 + "者" + str(big_value) + smallest_unit + "，" + "益" + type2 + "者" + str(
                    big_value) + smallest_unit + "，" + "而各平于" + str(average)
            else:
                big_value = value2 - average
                # small_value = average - value1
                return "减" + type2 + "者" + str(big_value) + smallest_unit + "，" + "益" + type1 + "者" + str(
                    big_value) + smallest_unit + "，" + "而各平于" + str(average)

        elif first_symbol_name == '无量纲量':
            values_list = [symbol['value'] for symbol in self.symbols.values()]
            print(values_list)
            # 将值转换为最小单位后比较大小
            value1 = values_list[0]
            value2 = values_list[1]
            average = (value1 + value2) / 2

            if value1 > value2:
                big_value = value1 - average
                # small_value = average - value2
                return "减" + str(value1) + "者" + str(big_value) + "，" + "益" + str(value2) + "者" + str(
                    big_value) + "，" + "而各平于" + str(average)
            else:
                big_value = value2 - average
                # small_value = average - value1
                return "减" + str(value2) + "者" + str(big_value) + "，" + "益" + str(value1) + "者" + str(
                    big_value) + "，" + "而各平于" + str(average)

        else:

            # 提取所有符号的单位
            units = [symbol['unit'] for symbol in self.symbols.values()]
            unit_type = first_symbol_name  # 或者是 '长度', '体积' 等，根据具体的情况确定
            print(units)

            # 找到最小单位
            smallest_unit = UnitConversion.find_smallest_unit(units, unit_type)
            if smallest_unit is None:
                return None

            values_list = []
            for symbol in self.symbols.values():
                converted_value, _ = UnitConversion.convert_units(symbol['value'], symbol['unit'], smallest_unit,
                                                                  unit_type)
                values_list.append(converted_value)

            print(values_list)
            # 将值转换为最小单位后比较大小
            value1 = values_list[0]
            value2 = values_list[1]

            types = [symbol['type'] for symbol in self.symbols.values()]
            type1 = types[0]
            type2 = types[1]

            average = (value1 + value2) / 2

            if value1 > value2:
                big_value = value1 - average
                # small_value = average - value2
                return "减" + type1 + "者" + str(big_value) + smallest_unit + "，" + "益" + type2 + "者" + str(
                    big_value) + smallest_unit + "，" + "而各平于" + str(average)
            else:
                big_value = value2 - average
                # small_value = average - value1
                return "减" + type2 + "者" + str(big_value) + smallest_unit + "，" + "益" + type1 + "者" + str(
                    big_value) + smallest_unit + "，" + "而各平于" + str(average)

# 使用示例

class UnitConversion:
    # 单位转换率，基准单位为 '里'
    # 1 顷 = 100 亩
    # 1 亩 = 240（平方）步 = 6 ^ 2 * 240 （平方)）尺
    # 分组单位转换率
    CONVERSION_RATES = {
        '里': 1,
        '匹': 45,
        '丈': 180,
        '步': 300,
        '尺': 1800,
        '寸': 18000,

        '顷': 0.0125,
        '亩': 1.25,

        '斛': 10,
        '斗': 100,
        '升': 1000,

        '石': 1,
        '钧': 4,
        '斤': 120,
        '两': 1920,
        '铢': 46080,
        # 可以添加更多的单位换算关系
        '钱': 1,
        '枚': 1,
        '个': 1,
        '翭': 1,
    }
    LENGTH_CONVERSION = {
        '里': 1,
        '匹': 45,
        '丈': 180,
        '步': 300,
        '尺': 1800,
        '寸': 18000
    }

    AREA_CONVERSION = {
        '顷': 1 / 100,
        '亩': 1,
        # 下面的都表示平方
        '里': 240 * (1 / 300) * (1 / 300),
        '匹': 240 * (45 / 300) * (45 / 300),
        '丈': 240 * (180 / 300) * (180 / 300),
        '步': 240,
        '尺': 240 * (1800 / 300) * (1800 / 300),
        '寸': 240 * (18000 / 300) * (18000 / 300)
    }

    VOLUME_CONVERSION = {
        # 下面的都表示立方
        '里': (1 / 300) * (1 / 300) * (1 / 300),
        '匹': (45 / 300) * (45 / 300) * (45 / 300),
        '丈': (180 / 300) * (180 / 300) * (180 / 300),
        '步': 1,
        '尺': (1800 / 300) * (1800 / 300) * (1800 / 300),
        '寸': (18000 / 300) * (18000 / 300) * (18000 / 300)
    }

    CAPACITY_CONVERSION = {
        '斛': 1,
        '斗': 10,
        '升': 100
    }

    WEIGHT_CONVERSION = {
        '石': 1,
        '钧': 4,
        '斤': 120,
        '两': 1920,
        '铢': 46080
    }

    MONEY_CONVERSION = {
        '钱': 1,
    }

    MEI_CONVERSION = {
        '枚': 1,
    }

    GE_CONVERSION = {
        '个': 1,
    }

    HOU_CONVERSION = {
        '翭': 1,
    }

    @classmethod
    def convert(cls, value, from_unit, to_unit):
        """
        将数值从一个单位转换为另一个单位。

        参数:
            value (float): 需要转换的数值。
            from_unit (str): 原始单位。
            to_unit (str): 目标单位。

        返回:
            float: 转换后的数值。
        """
        if from_unit == to_unit:
            return value  # 如果单位相同，则无需转换
        # 按照目标单位和原始单位的换算比例进行转换
        return value * cls.CONVERSION_RATES[to_unit] / cls.CONVERSION_RATES[from_unit]

    @classmethod
    def compare_and_convert_units(cls, value1, unit1, value2, unit2):
        """
        比较两个单位的大小并统一单位，然后返回更新后的值和单位。

        参数:
            value1 (float): 第一个值。
            unit1 (str): 第一个值的单位。
            value2 (float): 第二个值。
            unit2 (str): 第二个值的单位。

        返回:
            tuple: 包含更新后的两个值和统一的单位。
        """
        rate1 = cls.CONVERSION_RATES[unit1]
        rate2 = cls.CONVERSION_RATES[unit2]

        # 比较两个单位的转换率，转换率大的单位更小
        if rate1 > rate2:
            # unit1 是较大单位，转换 value2 到 unit1
            converted_value2 = cls.convert(value2, unit2, unit1)
            return value1, converted_value2, unit1
        else:
            # unit2 是较大单位，转换 value1 到 unit2
            converted_value1 = cls.convert(value1, unit1, unit2)
            return converted_value1, value2, unit2

    @classmethod
    def convert_units(cls, value, from_unit, to_unit, unit_type):
        """
        单纯的单位转换，先判断是否可以转换，然后进行转换。

        Args:
            value (float): 需要转换的数值。
            from_unit (str): 原始单位。
            to_unit (str): 目标单位。
            unit_type (str): 单位类型，如'长度'、'面积'。

        Returns:
            tuple: 包含转换后的值和单位。
        """
        conversion_dict = cls.get_conversion_rate(unit_type)
        if conversion_dict is None:
            print("Error: Unsupported unit type.")
            return None, None

        if from_unit not in conversion_dict or to_unit not in conversion_dict:
            print("Error: Conversion from or to the specified unit cannot be performed.")
            return None, None

        # 获取转换率并计算新的值
        from_rate = conversion_dict[from_unit]
        to_rate = conversion_dict[to_unit]
        converted_value = value * (to_rate / from_rate)

        return converted_value, to_unit

    @classmethod
    def find_smallest_unit(cls, unit_list, unit_type):
        """
        在给定的符号列表中找出具有最大转换率的最小单位。
        """
        # 初始化最小的
        smallest_unit = None
        largest_conversion_rate = float('-inf')
        print(unit_type)
        conversion_dict = cls.get_conversion_rate(unit_type)
        print("conversion_dict = ", conversion_dict)
        if conversion_dict is None:
            return None

        # 判断最小的单位
        for unit in unit_list:
            if unit in conversion_dict:
                conversion_rate = conversion_dict[unit]
                if conversion_rate > largest_conversion_rate:
                    largest_conversion_rate = conversion_rate
                    smallest_unit = unit

        return smallest_unit

    def get_conversion_rate(unit_type):
        # 相应的转换率字典
        if unit_type == '长度':
            return UnitConversion.LENGTH_CONVERSION
        elif unit_type == '数量钱':
            return UnitConversion.MONEY_CONVERSION
        elif unit_type == '数量枚':
            return UnitConversion.MEI_CONVERSION
        elif unit_type == '数量个':
            return UnitConversion.GE_CONVERSION
        elif unit_type == '数量翭':
            return UnitConversion.HOU_CONVERSION
        elif unit_type == '面积':
            return UnitConversion.AREA_CONVERSION
        elif unit_type == '体积':
            return UnitConversion.VOLUME_CONVERSION
        elif unit_type == '容积':
            return UnitConversion.CAPACITY_CONVERSION
        elif unit_type == '重量':
            return UnitConversion.WEIGHT_CONVERSION

        else:
            return None


def convert_symbol_units(symbol_list, target_unit, symbol_name):
    """
    将符号列表中的所有符号单位转换为目标单位，包括单位类型的自动检测。

    参数:
        symbol_list (list of dict): 包含符号的列表，每个符号是一个字典，包含'name', 'type', 'value', 'unit'。
        target_unit (str): 目标单位。

    返回:
        list of dict: 转换后的符号列表。
    """
    updated_symbols = []
    conversion_dict = UnitConversion.get_conversion_rate(symbol_name)  # 获取对应类型的转换率字典
    print("获取对应类型的转换率字典: ", conversion_dict)
    # conversion_dict = UnitConversion.get_conversion_rate(target_unit_type)

    for symbol in symbol_list:
        if symbol['value'] is None or symbol['unit'] is None:
            # 如果符号没有定义值或单位，则不进行转换，直接添加到结果列表
            # updated_symbol = symbol.copy()
            # updated_symbol['unit'] = target_unit  # 仍然设置目标单位
            # updated_symbols.append(updated_symbol)
            continue

        current_unit = symbol['unit']
        current_value = symbol['value']

        # 检查是否需要转换
        if current_unit != target_unit:
            # 如果单位不相同，执行转换
            from_rate = conversion_dict.get(current_unit)
            to_rate = conversion_dict.get(target_unit)
            if from_rate is None or to_rate is None:
                print(f"无法找到从 {current_unit} 到 {target_unit} 的转换率。")
                converted_value = None  # 转换失败
            else:
                converted_value = current_value * (to_rate / from_rate)

            updated_symbol = {
                'name': symbol['name'],
                'type': symbol['type'],
                'value': converted_value,
                'unit': target_unit
            }
        else:
            # 单位相同，无需转换
            updated_symbol = symbol.copy()

        updated_symbols.append(updated_symbol)

    return updated_symbols


# result = UnitConversion.compare_and_convert_units(10, '步', 1, '里')
# print("更新后的值和单位:", result)

# # 示例代码find_smallest_unit_symbol
# symbol_table = SymbolTable()
# symbol_table.add_symbol("Symbol1", "Type1", 100, "尺")
# symbol_table.add_symbol("Symbol2", "Type2", 200, "丈")
# symbol_table.add_symbol("Symbol3", "Type3", 300, "里")
#
# # 调用方法比较多个符号单位
# smallest_unit_symbol_name = symbol_table.compare_symbol_units(["Type1", "Type2", "Type3"])
# print("单位最小的符号是:", smallest_unit_symbol_name)

# # 创建 SymbolTable 实例
# symbol_table = SymbolTable()
#
# # 添加符号到符号表中
# symbol_table.add_symbol("符号1", "类型1", 100.0, "丈")
# symbol_table.add_symbol("符号2", "类型2", 200.0, "尺")
# symbol_table.add_symbol("符号3", "类型3", 150.0, "丈")  # 另一个使用 "丈" 单位的符号
#
# # 调用比较符号单位的方法
# result = symbol_table.compare_symbol_units("类型1", "类型2")
# print("比较结果（类型1 vs 类型2）:", result)
#
# # 比较两个相同单位的符号
# result_same_unit = symbol_table.compare_symbol_units("类型1", "类型3")
# print("比较结果（类型1 vs 类型3）:", result_same_unit)
#
# # 尝试比较一个不存在的符号
# result_non_existent = symbol_table.compare_symbol_units("类型1", "不存在的符号")
# print("比较结果（类型1 vs 不存在的符号）:", result_non_existent)


# class 面积:
#     def __init__(self, name, dimensions):
#         """
#         初始化一个新的田地对象。
#
#         参数:
#             name (str): 田地的名称。
#             dimensions (dict): 田地的尺寸，带单位，例如 {'广': (100, '步'), '从': (50, '步')}
#         """
#         self.name = name
#         self.dimensions = dimensions
#
#     def area(self):
#         """
#         计算田地的面积。该方法应该被子类实现。
#
#         抛出:
#             NotImplementedError: 表示子类需要实现这个方法。
#         """
#         raise NotImplementedError("每个具体的田地类型都必须实现自己的面积计算方法。")
#
#     def convert_unit(self, value, from_unit, target_unit):
#         """
#         将测量值从一个单位转换为另一个单位。
#
#         参数:
#             value (float): 要转换的值。
#             from_unit (str): 原始单位。
#             target_unit (str): 目标单位。
#
#         返回:
#             float: 新单位下的值。
#         """
#         return UnitConversion.convert(value, from_unit, target_unit)
#
#     def __str__(self):
#         """
#         返回田地对象的字符串表示形式。
#
#         返回:
#             str: 包括其名称和尺寸的田地描述。
#         """
#         return f"{self.name}，{self.dimensions}"

class Structure:
    def __init__(self, name, dimensions):
        """
        初始化一个新的构造对象。

        参数:
            name (str): 名称。
            dimensions (dict): 尺寸，带单位，例如 {'广': (100, '步'), '从': (50, '步')}
        """
        self.name = name
        self.dimensions = dimensions

    def value(self):
        """
        计算该结构的值。该方法应该被子类实现。

        抛出:
            NotImplementedError: 表示子类需要实现这个方法。
        """
        raise NotImplementedError("每个具体的类型都必须实现自己的面积计算方法。")

    def convert_unit(self, value, from_unit, target_unit):
        """
        将测量值从一个单位转换为另一个单位。

        参数:
            value (float): 要转换的值。
            from_unit (str): 原始单位。
            target_unit (str): 目标单位。

        返回:
            float: 新单位下的值。
        """
        return UnitConversion.convert(value, from_unit, target_unit)

    def __str__(self):
        """
        返回对象的字符串表示形式。

        返回:
            str: 包括其名称和尺寸描述。
        """
        return f"{self.name}，{self.dimensions}"


# # 田：广，从 （长方形田）
# class 田(Structure):
#     def value(self, target_unit):
#         """
#         计算矩形田地的面积，并以指定单位返回。
#
#         参数:
#             target_unit (str): 面积计算使用的目标单位。
#
#         返回:
#             float: 目标单位下的矩形面积。
#         """
#         # 提取每个维度并转换为目标单位，然后计算面积
#         width = self.dimensions['广'][0]
#         width_unit = self.dimensions['广'][1]
#         length = self.dimensions['从'][0]
#         length_unit = self.dimensions['从'][1]
#
#         width_in_target_unit = self.convert_unit(width, width_unit, target_unit)
#         length_in_target_unit = self.convert_unit(length, length_unit, target_unit)
#
#         value = width_in_target_unit * length_in_target_unit
#
#         # 计算并返回面积和单位
#         return value, target_unit
#
#     def __str__(self, target_unit='步'):
#         """
#         返回矩形田地的详细字符串描述，包括面积信息。
#
#         参数:
#             target_unit (str): 面积描述使用的单位（默认为'步'）。
#
#         返回:
#             str: 包括名称、尺寸和面积的详细描述。
#         """
#         # 取返回area函数的第一个参数
#         area_in_target_unit = self.value(target_unit)[0]
#         return f"{self.name}，广: {self.dimensions['广'][0]}{self.dimensions['广'][1]}，从: {self.dimensions['从'][0]}{self.dimensions['从'][1]}，面积: {area_in_target_unit}{target_unit}²"


# # 圭田：广，从 （三角形田）
# class 圭田(Structure):
#     def value(self, target_unit='步'):
#         """
#         计算三角形田地的面积，并以指定单位返回。
#
#         参数:
#             target_unit (str): 面积计算使用的目标单位，默认为'步'。
#
#         返回:
#             float: 目标单位下的三角形面积。
#         """
#         # 三角形面积 = 0.5 * 底 * 高
#         base = self.dimensions['广'][0]
#         base_unit = self.dimensions['广'][1]
#         height = self.dimensions['正从'][0]
#         height_unit = self.dimensions['正从'][1]
#
#         base_in_target_unit = self.convert_unit(base, base_unit, target_unit)
#         height_in_target_unit = self.convert_unit(height, height_unit, target_unit)
#
#         value = 0.5 * base_in_target_unit * height_in_target_unit
#         return value, target_unit
#
#     def __str__(self, target_unit='步'):
#         """
#         返回三角形田地的详细字符串描述，包括面积信息。
#
#         参数:
#             target_unit (str): 面积描述使用的单位（默认为'步'）。
#
#         返回:
#             str: 包括名称、尺寸和面积的详细描述。
#         """
#         area_in_target_unit = self.value(target_unit)[0]
#         return f"{self.name}，广（底）: {self.dimensions['广'][0]}{self.dimensions['广'][1]}，从（高）: {self.dimensions['正从'][0]}{self.dimensions['正从'][1]}，面积: {area_in_target_unit}{target_unit}²"

#
# class 圭田(Structure):
#     def __init__(self, name, dimensions):
#         super().__init__(name, dimensions)
#
#     def value(self, target_unit='步'):
#         """
#         根据提供的参数计算缺失的尺寸或面积。
#
#         参数:
#             target_unit (str): 计算结果的单位，默认为'步'。
#
#         返回:
#             float: 缺失参数的计算值，以指定的单位返回。
#         """
#         # 检查哪个参数缺失，并计算它
#         if '广' not in self.dimensions:
#             # 缺少底，已知面积和高
#             area = self.dimensions['田'][0]
#             height = self.dimensions['正从'][0]
#             height_unit = self.dimensions['正从'][1]
#             height_in_target_unit = self.convert_unit(height, height_unit, target_unit)
#             base = (2 * area) / height_in_target_unit
#             return self.convert_unit(base, '步', target_unit)  # 计算底的长度
#         elif '正从' not in self.dimensions:
#             # 缺少高，已知面积和底
#             area = self.dimensions['田'][0]
#             base = self.dimensions['广'][0]
#             base_unit = self.dimensions['广'][1]
#             base_in_target_unit = self.convert_unit(base, base_unit, target_unit)
#             height = (2 * area) / base_in_target_unit
#             return self.convert_unit(height, '步', target_unit)  # 计算高的长度
#         elif '田' not in self.dimensions:
#             # 缺少面积，已知底和高
#             base = self.dimensions['广'][0]
#             base_unit = self.dimensions['广'][1]
#             height = self.dimensions['正从'][0]
#             height_unit = self.dimensions['正从'][1]
#             base_in_target_unit = self.convert_unit(base, base_unit, target_unit)
#             height_in_target_unit = self.convert_unit(height, height_unit, target_unit)
#             area = 0.5 * base_in_target_unit * height_in_target_unit
#             return area, target_unit  # 计算面积
#
#     def __str__(self, target_unit='步'):
#         try:
#             missing_value = self.calculate_missing(target_unit)
#             return f"{self.name}，计算出的缺失值: {missing_value}{target_unit}²"
#         except Exception as e:
#             return str(e)

class 圭田(Structure):
    def value(self):
        """
        根据提供的参数计算缺失的尺寸或面积。

        返回:
            float: 缺失参数的计算值，以指定的单位返回。
        """
        # 检查哪个参数缺失，并计算它
        if self.dimensions['广'][0] is None and self.dimensions['广'][1] is None:
            # 缺少底，已知面积和高
            area = self.dimensions['田'][0]
            height = self.dimensions['正从'][0]
            base = (2 * area) / height
            return base  # 计算底的长度

        elif self.dimensions['正从'][0] is None and self.dimensions['正从'][1] is None:
            # 缺少高，已知面积和底
            area = self.dimensions['田'][0]
            base = self.dimensions['广'][0]
            height = (2 * area) / base
            return height  # 计算高的长度

        elif self.dimensions['田'][0] is None and self.dimensions['田'][1] is None:
            # 缺少面积，已知底和高
            base = self.dimensions['广'][0]
            height = self.dimensions['正从'][0]
            area = 1 / 2 * base * height
            return area  # 计算面积


class 委米依垣内角(Structure):
    def value(self):
        """
        根据提供的参数计算缺失的尺寸或面积。

        返回:
            float: 缺失参数的计算值，以指定的单位返回。
        """
        # 检查哪个参数缺失，并计算它
        if self.dimensions['下周'][0] is None and self.dimensions['下周'][1] is None:
            # 缺少下周，已知体积和高
            v = self.dimensions['积'][0]
            h = self.dimensions['高'][0]
            c = math.sqrt((9 * v) / h)
            return c  # 下周

        elif self.dimensions['高'][0] is None and self.dimensions['高'][1] is None:
            # 缺少高，已知体积和下周
            v = self.dimensions['积'][0]
            c = self.dimensions['下周'][0]
            h = (9 * v) / (c * c)
            return h  # 计算高

        elif self.dimensions['积'][0] is None and self.dimensions['积'][1] is None:
            # 缺少体积，已知下周和高
            c = self.dimensions['下周'][0]
            h = self.dimensions['高'][0]
            v = c * c * h / 9
            return v  # 计算面积


class 委菽依垣(Structure):
    def value(self):
        """
        根据提供的参数计算缺失的尺寸或面积。

        返回:
            float: 缺失参数的计算值，以指定的单位返回。
        """
        # 检查哪个参数缺失，并计算它
        if self.dimensions['下周'][0] is None and self.dimensions['下周'][1] is None:
            # 缺少下周，已知体积和高
            v = self.dimensions['积'][0]
            h = self.dimensions['高'][0]
            c = math.sqrt((18 * v) / h)
            return c  # 下周

        elif self.dimensions['高'][0] is None and self.dimensions['高'][1] is None:
            # 缺少高，已知体积和下周
            v = self.dimensions['积'][0]
            c = self.dimensions['下周'][0]
            h = (18 * v) / (c * c)
            return h  # 计算高

        elif self.dimensions['积'][0] is None and self.dimensions['积'][1] is None:
            # 缺少体积，已知下周和高
            c = self.dimensions['下周'][0]
            h = self.dimensions['高'][0]
            v = c * c * h / 18
            return v  # 计算面积


class 委粟平地(Structure):
    def value(self):
        """
        根据提供的参数计算缺失的尺寸或面积。

        返回:
            float: 缺失参数的计算值，以指定的单位返回。
        """
        # 检查哪个参数缺失，并计算它
        if self.dimensions['下周'][0] is None and self.dimensions['下周'][1] is None:
            # 缺少下周，已知体积和高
            v = self.dimensions['积'][0]
            h = self.dimensions['高'][0]
            c = math.sqrt((36 * v) / h)
            return c  # 下周

        elif self.dimensions['高'][0] is None and self.dimensions['高'][1] is None:
            # 缺少高，已知体积和下周
            v = self.dimensions['积'][0]
            c = self.dimensions['下周'][0]
            h = (36 * v) / (c * c)
            return h  # 计算高

        elif self.dimensions['积'][0] is None and self.dimensions['积'][1] is None:
            # 缺少体积，已知下周和高
            c = self.dimensions['下周'][0]
            h = self.dimensions['高'][0]
            v = c * c * h / 36
            return v  # 计算面积


class 圆困(Structure):
    def value(self):
        """
        根据提供的参数计算缺失的尺寸或面积。

        返回:
            float: 缺失参数的计算值，以指定的单位返回。
        """
        # 检查哪个参数缺失，并计算它
        if self.dimensions['周'][0] is None and self.dimensions['周'][1] is None:
            # 缺少周，已知体积和高
            v = self.dimensions['积'][0]
            h = self.dimensions['高'][0]
            c = math.sqrt((12 * v) / h)
            return c  # 下周

        elif self.dimensions['高'][0] is None and self.dimensions['高'][1] is None:
            # 缺少高，已知体积和周
            v = self.dimensions['积'][0]
            c = self.dimensions['周'][0]
            h = (12 * v) / (c * c)
            return h  # 计算高

        elif self.dimensions['积'][0] is None and self.dimensions['积'][1] is None:
            # 缺少体积，已知周和高
            c = self.dimensions['周'][0]
            h = self.dimensions['高'][0]
            v = c * c * h / 12
            return v  # 计算面积


class 仓(Structure):
    def value(self):
        """
        根据提供的参数计算缺失的尺寸或面积。

        返回:
            float: 缺失参数的计算值，以指定的单位返回。
        """
        # 检查哪个参数缺失，并计算它
        if self.dimensions['广'][0] is None and self.dimensions['广'][1] is None:
            # 缺少广，已知体积和袤，高
            v = self.dimensions['积'][0]
            h = self.dimensions['高'][0]
            m = self.dimensions['袤'][0]
            g = v / (h * m)
            return g  # 广

        elif self.dimensions['高'][0] is None and self.dimensions['高'][1] is None:
            # 缺少高，已知体积和周
            v = self.dimensions['积'][0]
            g = self.dimensions['广'][0]
            m = self.dimensions['袤'][0]
            h = v / (g * m)
            return h  # 计算高

        elif self.dimensions['积'][0] is None and self.dimensions['积'][1] is None:
            # 缺少体积，已知周和高
            g = self.dimensions['广'][0]
            m = self.dimensions['袤'][0]
            h = self.dimensions['高'][0]
            v = g * m * h
            return v  # 体积


class 刍甍(Structure):
    def value(self):
        """
        根据提供的参数计算缺失的尺寸或面积。

        返回:
            float: 缺失参数的计算值，以指定的单位返回。
        """
        # 检查哪个参数缺失，并计算它
        if self.dimensions['下袤'][0] is None and self.dimensions['下袤'][1] is None:
            v = self.dimensions['积'][0]
            h = self.dimensions['高'][0]
            m = self.dimensions['上袤'][0]
            n = self.dimensions['下广'][0]
            g = (((6 * v) / (h * n)) - m) / 2
            return g

        elif self.dimensions['上袤'][0] is None and self.dimensions['上袤'][1] is None:
            v = self.dimensions['积'][0]
            h = self.dimensions['高'][0]
            m = self.dimensions['下袤'][0]
            n = self.dimensions['下广'][0]
            g = ((6 * v) / (h * n)) - (2 * m)
            return g

        elif self.dimensions['下广'][0] is None and self.dimensions['下广'][1] is None:
            v = self.dimensions['积'][0]
            h = self.dimensions['高'][0]
            m = self.dimensions['下袤'][0]
            n = self.dimensions['上袤'][0]
            g = (6 * v) / (h * (2 * m + n))
            return g

        elif self.dimensions['高'][0] is None and self.dimensions['高'][1] is None:
            v = self.dimensions['积'][0]
            h = self.dimensions['下广'][0]
            m = self.dimensions['下袤'][0]
            n = self.dimensions['上袤'][0]
            g = (6 * v) / (h * (2 * m + n))
            return g

        elif self.dimensions['积'][0] is None and self.dimensions['积'][1] is None:
            h = self.dimensions['高'][0]
            g = self.dimensions['下广'][0]
            m = self.dimensions['下袤'][0]
            n = self.dimensions['上袤'][0]
            v = (m * 2 + n) * g * h / 6
            return v


class 羡除(Structure):
    def value(self):
        """
        根据提供的参数计算缺失的尺寸或面积。

        返回:
            float: 缺失参数的计算值，以指定的单位返回。
        """
        # 检查哪个参数缺失，并计算它
        if self.dimensions['下广'][0] is None and self.dimensions['下广'][1] is None:
            b = self.dimensions['上广'][0]
            c = self.dimensions['末广'][0]
            h1 = self.dimensions['深'][0]
            h2 = self.dimensions['袤'][0]
            v = self.dimensions['积'][0]
            a = ((6 * v) / (h1 * h2)) - b - c
            return a

        elif self.dimensions['上广'][0] is None and self.dimensions['上广'][1] is None:
            a = self.dimensions['下广'][0]
            c = self.dimensions['末广'][0]
            h1 = self.dimensions['深'][0]
            h2 = self.dimensions['袤'][0]
            v = self.dimensions['积'][0]
            b = ((6 * v) / (h1 * h2)) - a - c
            return g

        elif self.dimensions['末广'][0] is None and self.dimensions['末广'][1] is None:
            a = self.dimensions['下广'][0]
            b = self.dimensions['上广'][0]
            h1 = self.dimensions['深'][0]
            h2 = self.dimensions['袤'][0]
            v = self.dimensions['积'][0]
            c = ((6 * v) / (h1 * h2)) - a - b
            return c

        elif self.dimensions['深'][0] is None and self.dimensions['深'][1] is None:
            a = self.dimensions['下广'][0]
            b = self.dimensions['上广'][0]
            c = self.dimensions['末广'][0]
            h2 = self.dimensions['袤'][0]
            v = self.dimensions['积'][0]
            h1 = ((6 * v) / (a + b + c)) / h2
            return h1

        elif self.dimensions['袤'][0] is None and self.dimensions['袤'][1] is None:
            a = self.dimensions['下广'][0]
            b = self.dimensions['上广'][0]
            c = self.dimensions['末广'][0]
            h1 = self.dimensions['深'][0]
            v = self.dimensions['积'][0]
            h2 = ((6 * v) / (a + b + c)) / h1
            return h2

        elif self.dimensions['积'][0] is None and self.dimensions['积'][1] is None:
            a = self.dimensions['下广'][0]
            b = self.dimensions['上广'][0]
            c = self.dimensions['末广'][0]
            h1 = self.dimensions['深'][0]
            h2 = self.dimensions['袤'][0]
            v = (a + b + c) * h1 * h2 / 6
            return v


class 鳖臑(Structure):
    def value(self):
        """
        根据提供的参数计算缺失的尺寸或面积。

        返回:
            float: 缺失参数的计算值，以指定的单位返回。
        """
        # 检查哪个参数缺失，并计算它
        if self.dimensions['下广'][0] is None and self.dimensions['下广'][1] is None:
            h1 = self.dimensions['高'][0]
            h2 = self.dimensions['上袤'][0]
            v = self.dimensions['积'][0]
            a = 6 * v / (h1 * h2)
            return a

        elif self.dimensions['上袤'][0] is None and self.dimensions['上袤'][1] is None:
            h1 = self.dimensions['高'][0]
            h2 = self.dimensions['下广'][0]
            v = self.dimensions['积'][0]
            a = 6 * v / (h1 * h2)
            return a

        elif self.dimensions['高'][0] is None and self.dimensions['高'][1] is None:
            h1 = self.dimensions['上袤'][0]
            h2 = self.dimensions['下广'][0]
            v = self.dimensions['积'][0]
            a = 6 * v / (h1 * h2)
            return a

        elif self.dimensions['积'][0] is None and self.dimensions['积'][1] is None:
            a = self.dimensions['下广'][0]
            h1 = self.dimensions['高'][0]
            h2 = self.dimensions['上袤'][0]
            v = a * h2 * h1 / 6
            return v


class 堑堵(Structure):
    def value(self):
        """
        根据提供的参数计算缺失的尺寸或面积。

        返回:
            float: 缺失参数的计算值，以指定的单位返回。
        """
        # 检查哪个参数缺失，并计算它
        if self.dimensions['下广'][0] is None and self.dimensions['下广'][1] is None:
            h1 = self.dimensions['高'][0]
            h2 = self.dimensions['袤'][0]
            v = self.dimensions['积'][0]
            a = 2 * v / (h1 * h2)
            return a

        elif self.dimensions['袤'][0] is None and self.dimensions['袤'][1] is None:
            h1 = self.dimensions['高'][0]
            h2 = self.dimensions['下广'][0]
            v = self.dimensions['积'][0]
            a = 2 * v / (h1 * h2)
            return a

        elif self.dimensions['高'][0] is None and self.dimensions['高'][1] is None:
            h1 = self.dimensions['袤'][0]
            h2 = self.dimensions['下广'][0]
            v = self.dimensions['积'][0]
            a = 2 * v / (h1 * h2)
            return a

        elif self.dimensions['积'][0] is None and self.dimensions['积'][1] is None:
            a = self.dimensions['下广'][0]
            h1 = self.dimensions['高'][0]
            h2 = self.dimensions['袤'][0]
            v = a * h2 * h1 / 2
            return v


class 阳马(Structure):
    def value(self):
        """
        根据提供的参数计算缺失的尺寸或面积。

        返回:
            float: 缺失参数的计算值，以指定的单位返回。
        """
        # 检查哪个参数缺失，并计算它
        if self.dimensions['广'][0] is None and self.dimensions['广'][1] is None:
            h1 = self.dimensions['高'][0]
            h2 = self.dimensions['袤'][0]
            v = self.dimensions['积'][0]
            a = 3 * v / (h1 * h2)
            return a

        elif self.dimensions['袤'][0] is None and self.dimensions['袤'][1] is None:
            h1 = self.dimensions['高'][0]
            h2 = self.dimensions['广'][0]
            v = self.dimensions['积'][0]
            a = 3 * v / (h1 * h2)
            return a

        elif self.dimensions['高'][0] is None and self.dimensions['高'][1] is None:
            h1 = self.dimensions['袤'][0]
            h2 = self.dimensions['广'][0]
            v = self.dimensions['积'][0]
            a = 3 * v / (h1 * h2)
            return a

        elif self.dimensions['积'][0] is None and self.dimensions['积'][1] is None:
            a = self.dimensions['广'][0]
            h1 = self.dimensions['高'][0]
            h2 = self.dimensions['袤'][0]
            v = a * h2 * h1 / 3
            return v


class 刍童(Structure):
    def value(self):
        """
        根据提供的参数计算缺失的尺寸或面积。

        返回:
            float: 缺失参数的计算值，以指定的单位返回。
        """
        if self.dimensions['积'][0] is None and self.dimensions['积'][1] is None:
            b = self.dimensions['上袤'][0]
            c = self.dimensions['下袤'][0]
            d = self.dimensions['上广'][0]
            e = self.dimensions['下广'][0]
            f = self.dimensions['高'][0]
            a = ((b * 2 + c) * d + (c * 2 + b) * e) * f / 6
            return a

        elif self.dimensions['上袤'][0] is None and self.dimensions['上袤'][1] is None:
            a = self.dimensions['积'][0]
            c = self.dimensions['下袤'][0]
            d = self.dimensions['上广'][0]
            e = self.dimensions['下广'][0]
            f = self.dimensions['高'][0]
            b = (6 * a - c * d * f - 2 * c * e * f) / (2 * d * f + e * f)
            return b

        elif self.dimensions['下袤'][0] is None and self.dimensions['下袤'][1] is None:
            a = self.dimensions['积'][0]
            b = self.dimensions['上袤'][0]
            d = self.dimensions['上广'][0]
            e = self.dimensions['下广'][0]
            f = self.dimensions['高'][0]
            c = (6 * a - 2 * b * d * f - b * e * f) / (d * f + 2 * e * f)
            return c

        elif self.dimensions['上广'][0] is None and self.dimensions['上广'][1] is None:
            a = self.dimensions['积'][0]
            b = self.dimensions['上袤'][0]
            c = self.dimensions['下袤'][0]
            e = self.dimensions['下广'][0]
            f = self.dimensions['高'][0]
            d = (6 * a - 2 * c * e * f - b * e * f) / (2 * b * f + c * f)
            return d

        elif self.dimensions['下广'][0] is None and self.dimensions['下广'][1] is None:
            a = self.dimensions['积'][0]
            b = self.dimensions['上袤'][0]
            c = self.dimensions['下袤'][0]
            d = self.dimensions['上广'][0]
            f = self.dimensions['高'][0]
            e = (6 * a - 2 * b * d * f - c * d * f) / (2 * c * f + b * f)
            return e
        elif self.dimensions['高'][0] is None and self.dimensions['高'][1] is None:
            a = self.dimensions['积'][0]
            b = self.dimensions['上袤'][0]
            c = self.dimensions['下袤'][0]
            d = self.dimensions['上广'][0]
            e = self.dimensions['下广'][0]
            f = 6 * a / ((2 * b + c) * d + (2 * c + b) * e)
            return f


class 盘池(Structure):
    def value(self):
        """
        根据提供的参数计算缺失的尺寸或面积。

        返回:
            float: 缺失参数的计算值，以指定的单位返回。
        """
        if self.dimensions['积'][0] is None and self.dimensions['积'][1] is None:
            b = self.dimensions['上袤'][0]
            c = self.dimensions['下袤'][0]
            d = self.dimensions['上广'][0]
            e = self.dimensions['下广'][0]
            f = self.dimensions['深'][0]
            a = ((b * 2 + c) * d + (c * 2 + b) * e) * f / 6
            return a

        elif self.dimensions['上袤'][0] is None and self.dimensions['上袤'][1] is None:
            a = self.dimensions['积'][0]
            c = self.dimensions['下袤'][0]
            d = self.dimensions['上广'][0]
            e = self.dimensions['下广'][0]
            f = self.dimensions['深'][0]
            b = (6 * a - c * d * f - 2 * c * e * f) / (2 * d * f + e * f)
            return b

        elif self.dimensions['下袤'][0] is None and self.dimensions['下袤'][1] is None:
            a = self.dimensions['积'][0]
            b = self.dimensions['上袤'][0]
            d = self.dimensions['上广'][0]
            e = self.dimensions['下广'][0]
            f = self.dimensions['深'][0]
            c = (6 * a - 2 * b * d * f - b * e * f) / (d * f + 2 * e * f)
            return c

        elif self.dimensions['上广'][0] is None and self.dimensions['上广'][1] is None:
            a = self.dimensions['积'][0]
            b = self.dimensions['上袤'][0]
            c = self.dimensions['下袤'][0]
            e = self.dimensions['下广'][0]
            f = self.dimensions['深'][0]
            d = (6 * a - 2 * c * e * f - b * e * f) / (2 * b * f + c * f)
            return d

        elif self.dimensions['下广'][0] is None and self.dimensions['下广'][1] is None:
            a = self.dimensions['积'][0]
            b = self.dimensions['上袤'][0]
            c = self.dimensions['下袤'][0]
            d = self.dimensions['上广'][0]
            f = self.dimensions['深'][0]
            e = (6 * a - 2 * b * d * f - c * d * f) / (2 * c * f + b * f)
            return e
        elif self.dimensions['深'][0] is None and self.dimensions['深'][1] is None:
            a = self.dimensions['积'][0]
            b = self.dimensions['上袤'][0]
            c = self.dimensions['下袤'][0]
            d = self.dimensions['上广'][0]
            e = self.dimensions['下广'][0]
            f = 6 * a / ((2 * b + c) * d + (2 * c + b) * e)
            return f


class 冥谷(Structure):
    def value(self):
        """
        根据提供的参数计算缺失的尺寸或面积。

        返回:
            float: 缺失参数的计算值，以指定的单位返回。
        """
        if self.dimensions['积'][0] is None and self.dimensions['积'][1] is None:
            b = self.dimensions['上袤'][0]
            c = self.dimensions['下袤'][0]
            d = self.dimensions['上广'][0]
            e = self.dimensions['下广'][0]
            f = self.dimensions['深'][0]
            a = ((b * 2 + c) * d + (c * 2 + b) * e) * f / 6
            return a

        elif self.dimensions['上袤'][0] is None and self.dimensions['上袤'][1] is None:
            a = self.dimensions['积'][0]
            c = self.dimensions['下袤'][0]
            d = self.dimensions['上广'][0]
            e = self.dimensions['下广'][0]
            f = self.dimensions['深'][0]
            b = (6 * a - c * d * f - 2 * c * e * f) / (2 * d * f + e * f)
            return b

        elif self.dimensions['下袤'][0] is None and self.dimensions['下袤'][1] is None:
            a = self.dimensions['积'][0]
            b = self.dimensions['上袤'][0]
            d = self.dimensions['上广'][0]
            e = self.dimensions['下广'][0]
            f = self.dimensions['深'][0]
            c = (6 * a - 2 * b * d * f - b * e * f) / (d * f + 2 * e * f)
            return c

        elif self.dimensions['上广'][0] is None and self.dimensions['上广'][1] is None:
            a = self.dimensions['积'][0]
            b = self.dimensions['上袤'][0]
            c = self.dimensions['下袤'][0]
            e = self.dimensions['下广'][0]
            f = self.dimensions['深'][0]
            d = (6 * a - 2 * c * e * f - b * e * f) / (2 * b * f + c * f)
            return d

        elif self.dimensions['下广'][0] is None and self.dimensions['下广'][1] is None:
            a = self.dimensions['积'][0]
            b = self.dimensions['上袤'][0]
            c = self.dimensions['下袤'][0]
            d = self.dimensions['上广'][0]
            f = self.dimensions['深'][0]
            e = (6 * a - 2 * b * d * f - c * d * f) / (2 * c * f + b * f)
            return e
        elif self.dimensions['深'][0] is None and self.dimensions['深'][1] is None:
            a = self.dimensions['积'][0]
            b = self.dimensions['上袤'][0]
            c = self.dimensions['下袤'][0]
            d = self.dimensions['上广'][0]
            e = self.dimensions['下广'][0]
            f = 6 * a / ((2 * b + c) * d + (2 * c + b) * e)
            return f


class 曲池(Structure):
    def value(self):
        """
        根据提供的参数计算缺失的尺寸或面积。

        返回:
            float: 缺失参数的计算值，以指定的单位返回。
        """
        # 检查哪个参数缺失，并计算它
        if self.dimensions['积'][0] is None and self.dimensions['积'][1] is None:
            b = self.dimensions['上中周'][0]
            c = self.dimensions['外周'][0]
            d = self.dimensions['上广'][0]
            e = self.dimensions['下中周'][0]
            f = self.dimensions['外周1'][0]
            g = self.dimensions['下广'][0]
            h = self.dimensions['深'][0]
            a = ((b + c + (e + f) / 2) * d + (e + f + (b + c) / 2) * g) * h / 6
            return a

        elif self.dimensions['上中周'][0] is None and self.dimensions['上中周'][1] is None:
            a = self.dimensions['积'][0]
            c = self.dimensions['外周'][0]
            d = self.dimensions['上广'][0]
            e = self.dimensions['下中周'][0]
            f = self.dimensions['外周1'][0]
            g = self.dimensions['下广'][0]
            h = self.dimensions['深'][0]
            b = ((6 * a / h) - c * d - d * e / 2 - d * f / 2 - e * g - f * g - c * g / 2) / (d + g / 2)
            return b

        elif self.dimensions['外周'][0] is None and self.dimensions['外周'][1] is None:
            a = self.dimensions['积'][0]
            b = self.dimensions['上中周'][0]
            d = self.dimensions['上广'][0]
            e = self.dimensions['下中周'][0]
            f = self.dimensions['外周1'][0]
            g = self.dimensions['下广'][0]
            h = self.dimensions['深'][0]
            c = ((6 * a / h) - b * d - d * e / 2 - d * f / 2 - e * g - f * g - b * g / 2) / (d + g / 2)
            return c

        elif self.dimensions['上广'][0] is None and self.dimensions['上广'][1] is None:
            a = self.dimensions['积'][0]
            b = self.dimensions['上中周'][0]
            c = self.dimensions['外周'][0]
            e = self.dimensions['下中周'][0]
            f = self.dimensions['外周1'][0]
            g = self.dimensions['下广'][0]
            h = self.dimensions['深'][0]
            d = ((6 * a / h) - e * g - f * g - b * g / 2 - c * g / 2) / (b + c + e / 2 + f / 2)
            return d

        elif self.dimensions['下中周'][0] is None and self.dimensions['下中周'][1] is None:
            a = self.dimensions['积'][0]
            b = self.dimensions['上中周'][0]
            c = self.dimensions['外周'][0]
            d = self.dimensions['上广'][0]
            f = self.dimensions['外周1'][0]
            g = self.dimensions['下广'][0]
            h = self.dimensions['深'][0]
            e = ((6 * a / h) - b * d - c * d - d * f / 2 - f * g - b * g / 2 - c * g / 2) / (d / 2 + g)
            return e

        elif self.dimensions['外周1'][0] is None and self.dimensions['外周1'][1] is None:
            a = self.dimensions['积'][0]
            b = self.dimensions['上中周'][0]
            c = self.dimensions['外周'][0]
            d = self.dimensions['上广'][0]
            e = self.dimensions['下中周'][0]
            g = self.dimensions['下广'][0]
            h = self.dimensions['深'][0]
            f = ((6 * a / h) - b * d - c * d - d * e / 2 - e * g - b * g / 2 - c * g / 2) / (d / 2 + f)
            return f
        elif self.dimensions['下广'][0] is None and self.dimensions['下广'][1] is None:
            a = self.dimensions['积'][0]
            b = self.dimensions['上中周'][0]
            c = self.dimensions['外周'][0]
            d = self.dimensions['上广'][0]
            e = self.dimensions['下中周'][0]
            f = self.dimensions['外周1'][0]
            h = self.dimensions['深'][0]
            g = ((6 * a / h) - b * d - c * d - d * e / 2 - d * f / 2) / (e + f + b / 2 + c / 2)
            return g
        elif self.dimensions['深'][0] is None and self.dimensions['深'][1] is None:
            a = self.dimensions['积'][0]
            b = self.dimensions['上中周'][0]
            c = self.dimensions['外周'][0]
            d = self.dimensions['上广'][0]
            e = self.dimensions['下中周'][0]
            f = self.dimensions['外周1'][0]
            g = self.dimensions['下广'][0]
            h = 6 * a / (b * d + c * d + e * d / 2 + f * d / 2 + e * g + f * g + b * g / 2 + c * g / 2)
            return h


class 田(Structure):
    def value(self):
        """
        根据提供的参数计算缺失的尺寸或面积。

        返回:
            float: 缺失参数的计算值，以指定的单位返回。
        """
        # 检查哪个参数缺失，并计算它
        if self.dimensions['广'][0] is None and self.dimensions['广'][1] is None:
            # 缺少广
            area = self.dimensions['田1'][0]
            height = self.dimensions['从'][0]
            base = area / height
            return base

        elif self.dimensions['从'][0] is None and self.dimensions['从'][1] is None:
            # 缺少高，已知面积和底
            area = self.dimensions['田1'][0]
            base = self.dimensions['广'][0]
            height = area / base
            return height  # 计算高的长度

        elif self.dimensions['田1'][0] is None and self.dimensions['田1'][1] is None:
            # 缺少面积，已知底和高
            base = self.dimensions['广'][0]
            height = self.dimensions['从'][0]
            area = base * height
            return area  # 计算面积


class 邪田(Structure):
    def value(self):
        """
        根据提供的参数计算缺失的尺寸或面积。

        返回:
            float: 缺失参数的计算值，以指定的单位返回。
        """
        # 检查哪个参数缺失，并计算它
        if self.dimensions['头广'][0] is None and self.dimensions['头广'][1] is None:
            # 缺少头广
            touguang1 = self.dimensions['头广1'][0]
            zhengcong = self.dimensions['正从'][0]
            area = self.dimensions['田'][0]
            return (2 * area / zhengcong) - touguang1

        elif self.dimensions['头广1'][0] is None and self.dimensions['头广1'][1] is None:
            # 缺少头广1
            touguang = self.dimensions['头广'][0]
            zhengcong = self.dimensions['正从'][0]
            area = self.dimensions['田'][0]
            return (2 * area / zhengcong) - touguang

        elif self.dimensions['正从'][0] is None and self.dimensions['正从'][1] is None:
            # 缺少正从
            guang = self.dimensions['头广'][0] + self.dimensions['头广1'][0]
            area = self.dimensions['田'][0]
            return 2 * area / guang

        elif self.dimensions['田'][0] is None and self.dimensions['田'][1] is None:
            # 缺少正从
            guang = self.dimensions['头广'][0] + self.dimensions['头广1'][0]
            zhengcong = self.dimensions['正从'][0]
            return guang * zhengcong / 2


class 箕田(Structure):
    def value(self):
        """
        根据提供的参数计算缺失的尺寸或面积。

        返回:
            float: 缺失参数的计算值，以指定的单位返回。
        """
        # 检查哪个参数缺失，并计算它
        if self.dimensions['舌广'][0] is None and self.dimensions['舌广'][1] is None:
            # 缺少舌广
            zhongguang = self.dimensions['踵广'][0]
            zhengcong = self.dimensions['正从'][0]
            area = self.dimensions['田'][0]
            return 2 * area / zhengcong - zhongguang

        elif self.dimensions['踵广'][0] is None and self.dimensions['踵广'][1] is None:
            # 缺少踵广
            sheguang = self.dimensions['舌广'][0]
            zhengcong = self.dimensions['正从'][0]
            area = self.dimensions['田'][0]
            return (2 * area / zhengcong) - sheguang

        elif self.dimensions['正从'][0] is None and self.dimensions['正从'][1] is None:
            # 缺少正从
            guang = self.dimensions['踵广'][0] + self.dimensions['舌广'][0]
            area = self.dimensions['田'][0]
            return 2 * area / guang

        elif self.dimensions['田'][0] is None and self.dimensions['田'][1] is None:
            # 缺少正从
            guang = self.dimensions['踵广'][0] + self.dimensions['舌广'][0]
            zhengcong = self.dimensions['正从'][0]
            return guang * zhengcong / 2


class 圆田(Structure):
    def value(self):
        """
        根据提供的参数计算缺失的尺寸或面积。

        返回:
            float: 缺失参数的计算值，以指定的单位返回。
        """
        # 检查哪个参数缺失，并计算它
        if self.dimensions['周'][0] is None and self.dimensions['周'][1] is None:
            # 缺少周
            jing = self.dimensions['径'][0]
            area = self.dimensions['田'][0]
            return 4 * area / jing

        elif self.dimensions['径'][0] is None and self.dimensions['径'][1] is None:
            # 缺少径
            zhou = self.dimensions['周'][0]
            area = self.dimensions['田'][0]
            return 4 * area / zhou

        elif self.dimensions['田'][0] is None and self.dimensions['田'][1] is None:
            # 缺少田
            zhou = self.dimensions['周'][0]
            jing = self.dimensions['径'][0]
            return zhou * jing / 4


class 宛田(Structure):
    def value(self):
        """
        根据提供的参数计算缺失的尺寸或面积。

        返回:
            float: 缺失参数的计算值，以指定的单位返回。
        """
        # 检查哪个参数缺失，并计算它
        if self.dimensions['下周'][0] is None and self.dimensions['下周'][1] is None:
            # 缺少下周
            jing = self.dimensions['径'][0]
            area = self.dimensions['田'][0]
            return 4 * area / jing

        elif self.dimensions['径'][0] is None and self.dimensions['径'][1] is None:
            # 缺少径
            zhou = self.dimensions['下周'][0]
            area = self.dimensions['田'][0]
            return 4 * area / zhou

        elif self.dimensions['田'][0] is None and self.dimensions['田'][1] is None:
            # 缺少田
            zhou = self.dimensions['下周'][0]
            jing = self.dimensions['径'][0]
            return zhou * jing / 4


class 弧田(Structure):
    def value(self):
        """
        根据提供的参数计算缺失的尺寸或面积。

        返回:
            float: 缺失参数的计算值，以指定的单位返回。
        """
        # 检查哪个参数缺失，并计算它
        if self.dimensions['弦'][0] is None and self.dimensions['弦'][1] is None:
            shi = self.dimensions['矢'][0]
            area = self.dimensions['田'][0]
            return (2 * area - shi * shi) / shi

        elif self.dimensions['矢'][0] is None and self.dimensions['矢'][1] is None:
            xian = self.dimensions['弦'][0]
            area = self.dimensions['田'][0]
            delta = xian * xian + 8 * area
            x1 = (-xian + math.math.sqrt(delta)) / 2
            x2 = (-xian - math.math.sqrt(delta)) / 2
            if x1 > x2:
                return x1
            else:
                return x2

        elif self.dimensions['田'][0] is None and self.dimensions['田'][1] is None:
            shi = self.dimensions['矢'][0]
            xian = self.dimensions['弦'][0]
            return (xian * shi + shi * shi) / 2


class 环田(Structure):
    def value(self):
        """
        根据提供的参数计算缺失的尺寸或面积。

        返回:
            float: 缺失参数的计算值，以指定的单位返回。
        """
        # 检查哪个参数缺失，并计算它
        if self.dimensions['中周'][0] is None and self.dimensions['中周'][1] is None:
            waizhou = self.dimensions['外周'][0]
            jing = self.dimensions['径'][0]
            area = self.dimensions['田'][0]
            return (2 * area / jing) - waizhou

        elif self.dimensions['外周'][0] is None and self.dimensions['外周'][1] is None:
            zhongzhou = self.dimensions['中周'][0]
            jing = self.dimensions['径'][0]
            area = self.dimensions['田'][0]
            return (2 * area / jing) - zhongzhou

        elif self.dimensions['田'][0] is None and self.dimensions['田'][1] is None:
            # 缺少田
            zhongzhou = self.dimensions['中周'][0]
            waizhou = self.dimensions['外周'][0]
            jing = self.dimensions['径'][0]
            return (zhongzhou + waizhou) * jing / 2

        elif self.dimensions['径'][0] is None and self.dimensions['径'][1] is None:
            # 缺少径
            zhongzhou = self.dimensions['中周'][0]
            waizhou = self.dimensions['外周'][0]
            area = self.dimensions['田'][0]
            return (area * 2) / (zhongzhou + waizhou)


class 城(Structure):
    def value(self):
        """
        根据提供的参数计算缺失的尺寸或面积。

        返回:
            float: 缺失参数的计算值，以指定的单位返回。
        """
        # 检查哪个参数缺失，并计算它
        if self.dimensions['上广'][0] is None and self.dimensions['上广'][1] is None:
            xiaguang = self.dimensions['下广'][0]
            gao = self.dimensions['高'][0]
            mao = self.dimensions['袤'][0]
            ji = self.dimensions['积'][0]
            return (2 * ji) / (gao * mao) - xiaguang

        elif self.dimensions['下广'][0] is None and self.dimensions['下广'][1] is None:
            shangguang = self.dimensions['上广'][0]
            gao = self.dimensions['高'][0]
            mao = self.dimensions['袤'][0]
            ji = self.dimensions['积'][0]
            return (2 * ji) / (gao * mao) - shangguang

        elif self.dimensions['高'][0] is None and self.dimensions['高'][1] is None:
            guang = self.dimensions['上广'][0] + self.dimensions['下广'][0]
            mao = self.dimensions['袤'][0]
            ji = self.dimensions['积'][0]
            return (2 * ji) / (guang * mao)

        elif self.dimensions['袤'][0] is None and self.dimensions['袤'][1] is None:
            guang = self.dimensions['上广'][0] + self.dimensions['下广'][0]
            gao = self.dimensions['高'][0]
            ji = self.dimensions['积'][0]
            return (2 * ji) / (guang * gao)

        elif self.dimensions['积'][0] is None and self.dimensions['积'][1] is None:
            guang = self.dimensions['上广'][0] + self.dimensions['下广'][0]
            gao = self.dimensions['高'][0]
            mao = self.dimensions['袤'][0]
            return (guang * gao * mao) / 2


class 垣(Structure):
    def value(self):
        """
        根据提供的参数计算缺失的尺寸或面积。

        返回:
            float: 缺失参数的计算值，以指定的单位返回。
        """
        # 检查哪个参数缺失，并计算它
        if self.dimensions['上广'][0] is None and self.dimensions['上广'][1] is None:
            xiaguang = self.dimensions['下广'][0]
            gao = self.dimensions['高'][0]
            mao = self.dimensions['袤'][0]
            ji = self.dimensions['积'][0]
            return (2 * ji) / (gao * mao) - xiaguang

        elif self.dimensions['下广'][0] is None and self.dimensions['下广'][1] is None:
            shangguang = self.dimensions['上广'][0]
            gao = self.dimensions['高'][0]
            mao = self.dimensions['袤'][0]
            ji = self.dimensions['积'][0]
            return (2 * ji) / (gao * mao) - shangguang

        elif self.dimensions['高'][0] is None and self.dimensions['高'][1] is None:
            guang = self.dimensions['上广'][0] + self.dimensions['下广'][0]
            mao = self.dimensions['袤'][0]
            ji = self.dimensions['积'][0]
            return (2 * ji) / (guang * mao)

        elif self.dimensions['袤'][0] is None and self.dimensions['袤'][1] is None:
            guang = self.dimensions['上广'][0] + self.dimensions['下广'][0]
            gao = self.dimensions['高'][0]
            ji = self.dimensions['积'][0]
            return (2 * ji) / (guang * gao)

        elif self.dimensions['积'][0] is None and self.dimensions['积'][1] is None:
            guang = self.dimensions['上广'][0] + self.dimensions['下广'][0]
            gao = self.dimensions['高'][0]
            mao = self.dimensions['袤'][0]
            return (guang * gao * mao) / 2


class 堤(Structure):
    def value(self):
        """
        根据提供的参数计算缺失的尺寸或面积。

        返回:
            float: 缺失参数的计算值，以指定的单位返回。
        """
        # 检查哪个参数缺失，并计算它
        if self.dimensions['上广'][0] is None and self.dimensions['上广'][1] is None:
            xiaguang = self.dimensions['下广'][0]
            gao = self.dimensions['高'][0]
            mao = self.dimensions['袤'][0]
            ji = self.dimensions['积'][0]
            return (2 * ji) / (gao * mao) - xiaguang

        elif self.dimensions['下广'][0] is None and self.dimensions['下广'][1] is None:
            shangguang = self.dimensions['上广'][0]
            gao = self.dimensions['高'][0]
            mao = self.dimensions['袤'][0]
            ji = self.dimensions['积'][0]
            return (2 * ji) / (gao * mao) - shangguang

        elif self.dimensions['高'][0] is None and self.dimensions['高'][1] is None:
            guang = self.dimensions['上广'][0] + self.dimensions['下广'][0]
            mao = self.dimensions['袤'][0]
            ji = self.dimensions['积'][0]
            return (2 * ji) / (guang * mao)

        elif self.dimensions['袤'][0] is None and self.dimensions['袤'][1] is None:
            guang = self.dimensions['上广'][0] + self.dimensions['下广'][0]
            gao = self.dimensions['高'][0]
            ji = self.dimensions['积'][0]
            return (2 * ji) / (guang * gao)

        elif self.dimensions['积'][0] is None and self.dimensions['积'][1] is None:
            guang = self.dimensions['上广'][0] + self.dimensions['下广'][0]
            gao = self.dimensions['高'][0]
            mao = self.dimensions['袤'][0]
            return (guang * gao * mao) / 2


class 沟(Structure):
    def value(self):
        """
        根据提供的参数计算缺失的尺寸或面积。

        返回:
            float: 缺失参数的计算值，以指定的单位返回。
        """
        # 检查哪个参数缺失，并计算它
        if self.dimensions['上广'][0] is None and self.dimensions['上广'][1] is None:
            xiaguang = self.dimensions['下广'][0]
            shen = self.dimensions['深'][0]
            mao = self.dimensions['袤'][0]
            ji = self.dimensions['积'][0]
            return (2 * ji) / (shen * mao) - xiaguang

        elif self.dimensions['下广'][0] is None and self.dimensions['下广'][1] is None:
            shangguang = self.dimensions['上广'][0]
            shen = self.dimensions['深'][0]
            mao = self.dimensions['袤'][0]
            ji = self.dimensions['积'][0]
            return (2 * ji) / (shen * mao) - shangguang

        elif self.dimensions['深'][0] is None and self.dimensions['深'][1] is None:
            guang = self.dimensions['上广'][0] + self.dimensions['下广'][0]
            mao = self.dimensions['袤'][0]
            ji = self.dimensions['积'][0]
            return (2 * ji) / (guang * mao)

        elif self.dimensions['袤'][0] is None and self.dimensions['袤'][1] is None:
            guang = self.dimensions['上广'][0] + self.dimensions['下广'][0]
            shen = self.dimensions['深'][0]
            ji = self.dimensions['积'][0]
            return (2 * ji) / (guang * shen)

        elif self.dimensions['积'][0] is None and self.dimensions['积'][1] is None:
            guang = self.dimensions['上广'][0] + self.dimensions['下广'][0]
            shen = self.dimensions['深'][0]
            mao = self.dimensions['袤'][0]
            return (guang * shen * mao) / 2


class 聢(Structure):
    def value(self):
        """
        根据提供的参数计算缺失的尺寸或面积。

        返回:
            float: 缺失参数的计算值，以指定的单位返回。
        """
        # 检查哪个参数缺失，并计算它
        if self.dimensions['上广'][0] is None and self.dimensions['上广'][1] is None:
            xiaguang = self.dimensions['下广'][0]
            shen = self.dimensions['深'][0]
            mao = self.dimensions['袤'][0]
            ji = self.dimensions['积'][0]
            return (2 * ji) / (shen * mao) - xiaguang

        elif self.dimensions['下广'][0] is None and self.dimensions['下广'][1] is None:
            shangguang = self.dimensions['上广'][0]
            shen = self.dimensions['深'][0]
            mao = self.dimensions['袤'][0]
            ji = self.dimensions['积'][0]
            return (2 * ji) / (shen * mao) - shangguang

        elif self.dimensions['深'][0] is None and self.dimensions['深'][1] is None:
            guang = self.dimensions['上广'][0] + self.dimensions['下广'][0]
            mao = self.dimensions['袤'][0]
            ji = self.dimensions['积'][0]
            return (2 * ji) / (guang * mao)

        elif self.dimensions['袤'][0] is None and self.dimensions['袤'][1] is None:
            guang = self.dimensions['上广'][0] + self.dimensions['下广'][0]
            shen = self.dimensions['深'][0]
            ji = self.dimensions['积'][0]
            return (2 * ji) / (guang * shen)

        elif self.dimensions['积'][0] is None and self.dimensions['积'][1] is None:
            guang = self.dimensions['上广'][0] + self.dimensions['下广'][0]
            shen = self.dimensions['深'][0]
            mao = self.dimensions['袤'][0]
            return (guang * shen * mao) / 2


class 穿渠(Structure):
    def value(self):
        """
        根据提供的参数计算缺失的尺寸或面积。

        返回:
            float: 缺失参数的计算值，以指定的单位返回。
        """
        # 检查哪个参数缺失，并计算它
        if self.dimensions['上广'][0] is None and self.dimensions['上广'][1] is None:
            xiaguang = self.dimensions['下广'][0]
            shen = self.dimensions['深'][0]
            mao = self.dimensions['袤'][0]
            ji = self.dimensions['积'][0]
            return (2 * ji) / (shen * mao) - xiaguang

        elif self.dimensions['下广'][0] is None and self.dimensions['下广'][1] is None:
            shangguang = self.dimensions['上广'][0]
            shen = self.dimensions['深'][0]
            mao = self.dimensions['袤'][0]
            ji = self.dimensions['积'][0]
            return (2 * ji) / (shen * mao) - shangguang

        elif self.dimensions['深'][0] is None and self.dimensions['深'][1] is None:
            guang = self.dimensions['上广'][0] + self.dimensions['下广'][0]
            mao = self.dimensions['袤'][0]
            ji = self.dimensions['积'][0]
            return (2 * ji) / (guang * mao)

        elif self.dimensions['袤'][0] is None and self.dimensions['袤'][1] is None:
            guang = self.dimensions['上广'][0] + self.dimensions['下广'][0]
            shen = self.dimensions['深'][0]
            ji = self.dimensions['积'][0]
            return (2 * ji) / (guang * shen)

        elif self.dimensions['积'][0] is None and self.dimensions['积'][1] is None:
            guang = self.dimensions['上广'][0] + self.dimensions['下广'][0]
            shen = self.dimensions['深'][0]
            mao = self.dimensions['袤'][0]
            return (guang * shen * mao) / 2


class 渠(Structure):
    def value(self):
        """
        根据提供的参数计算缺失的尺寸或面积。

        返回:
            float: 缺失参数的计算值，以指定的单位返回。
        """
        # 检查哪个参数缺失，并计算它
        if self.dimensions['上广'][0] is None and self.dimensions['上广'][1] is None:
            xiaguang = self.dimensions['下广'][0]
            shen = self.dimensions['深'][0]
            mao = self.dimensions['袤'][0]
            ji = self.dimensions['积'][0]
            return (2 * ji) / (shen * mao) - xiaguang

        elif self.dimensions['下广'][0] is None and self.dimensions['下广'][1] is None:
            shangguang = self.dimensions['上广'][0]
            shen = self.dimensions['深'][0]
            mao = self.dimensions['袤'][0]
            ji = self.dimensions['积'][0]
            return (2 * ji) / (shen * mao) - shangguang

        elif self.dimensions['深'][0] is None and self.dimensions['深'][1] is None:
            guang = self.dimensions['上广'][0] + self.dimensions['下广'][0]
            mao = self.dimensions['袤'][0]
            ji = self.dimensions['积'][0]
            return (2 * ji) / (guang * mao)

        elif self.dimensions['袤'][0] is None and self.dimensions['袤'][1] is None:
            guang = self.dimensions['上广'][0] + self.dimensions['下广'][0]
            shen = self.dimensions['深'][0]
            ji = self.dimensions['积'][0]
            return (2 * ji) / (guang * shen)

        elif self.dimensions['积'][0] is None and self.dimensions['积'][1] is None:
            guang = self.dimensions['上广'][0] + self.dimensions['下广'][0]
            shen = self.dimensions['深'][0]
            mao = self.dimensions['袤'][0]
            return (guang * shen * mao) / 2


class 堑(Structure):
    def value(self):
        """
        根据提供的参数计算缺失的尺寸或面积。

        返回:
            float: 缺失参数的计算值，以指定的单位返回。
        """
        # 检查哪个参数缺失，并计算它
        if self.dimensions['上广'][0] is None and self.dimensions['上广'][1] is None:
            xiaguang = self.dimensions['下广'][0]
            shen = self.dimensions['深'][0]
            mao = self.dimensions['袤'][0]
            ji = self.dimensions['积'][0]
            return (2 * ji) / (shen * mao) - xiaguang

        elif self.dimensions['下广'][0] is None and self.dimensions['下广'][1] is None:
            shangguang = self.dimensions['上广'][0]
            shen = self.dimensions['深'][0]
            mao = self.dimensions['袤'][0]
            ji = self.dimensions['积'][0]
            return (2 * ji) / (shen * mao) - shangguang

        elif self.dimensions['深'][0] is None and self.dimensions['深'][1] is None:
            guang = self.dimensions['上广'][0] + self.dimensions['下广'][0]
            mao = self.dimensions['袤'][0]
            ji = self.dimensions['积'][0]
            return (2 * ji) / (guang * mao)

        elif self.dimensions['袤'][0] is None and self.dimensions['袤'][1] is None:
            guang = self.dimensions['上广'][0] + self.dimensions['下广'][0]
            shen = self.dimensions['深'][0]
            ji = self.dimensions['积'][0]
            return (2 * ji) / (guang * shen)

        elif self.dimensions['积'][0] is None and self.dimensions['积'][1] is None:
            guang = self.dimensions['上广'][0] + self.dimensions['下广'][0]
            shen = self.dimensions['深'][0]
            mao = self.dimensions['袤'][0]
            return (guang * shen * mao) / 2


class 方堡壔(Structure):
    def value(self):
        """
        根据提供的参数计算缺失的尺寸或面积。

        返回:
            float: 缺失参数的计算值，以指定的单位返回。
        """
        # 检查哪个参数缺失，并计算它
        if self.dimensions['方'][0] is None and self.dimensions['方'][1] is None:
            gao = self.dimensions['高'][0]
            ji = self.dimensions['积'][0]
            return math.math.sqrt(ji / gao)

        elif self.dimensions['高'][0] is None and self.dimensions['高'][1] is None:
            fang = self.dimensions['方'][0]
            ji = self.dimensions['积'][0]
            return ji / (fang * fang)

        elif self.dimensions['积'][0] is None and self.dimensions['积'][1] is None:
            gao = self.dimensions['高'][0]
            fang = self.dimensions['方'][0]
            return fang * fang * gao


class 圆堡壔(Structure):
    def value(self):
        """
        根据提供的参数计算缺失的尺寸或面积。

        返回:
            float: 缺失参数的计算值，以指定的单位返回。
        """
        # 检查哪个参数缺失，并计算它
        if self.dimensions['周'][0] is None and self.dimensions['周'][1] is None:
            gao = self.dimensions['高'][0]
            ji = self.dimensions['积'][0]
            return math.math.sqrt(12 * ji / gao)

        elif self.dimensions['高'][0] is None and self.dimensions['高'][1] is None:
            zhou = self.dimensions['周'][0]
            ji = self.dimensions['积'][0]
            return (12 * ji) / (zhou * zhou)

        elif self.dimensions['积'][0] is None and self.dimensions['积'][1] is None:
            zhou = self.dimensions['周'][0]
            gao = self.dimensions['高'][0]
            return (zhou * gao * zhou) / 12


class 方亭(Structure):
    def value(self):
        """
        根据提供的参数计算缺失的尺寸或面积。

        返回:
            float: 缺失参数的计算值，以指定的单位返回。
        """
        # 检查哪个参数缺失，并计算它
        if self.dimensions['上方'][0] is None and self.dimensions['上方'][1] is None:
            xiafang = self.dimensions['下方'][0]
            gao = self.dimensions['高'][0]
            ji = self.dimensions['积'][0]
            delta = xiafang * xiafang - 4 * (xiafang * xiafang - 3 * ji / gao)
            if delta >= 0:
                x1 = (-xiafang + math.math.sqrt(delta)) / 2
                x2 = (-xiafang - math.math.sqrt(delta)) / 2
                if x1 > x2:
                    return x1
                else:
                    return x2
            else:
                return -1

        elif self.dimensions['下方'][0] is None and self.dimensions['下方'][1] is None:
            shangfang = self.dimensions['上方'][0]
            gao = self.dimensions['高'][0]
            ji = self.dimensions['积'][0]
            delta = shangfang * shangfang - 4 * (shangfang * shangfang - 3 * ji / gao)
            if delta >= 0:
                x1 = (-shangfang + math.math.sqrt(delta)) / 2
                x2 = (-shangfang - math.math.sqrt(delta)) / 2
                if x1 > x2:
                    return x1
                else:
                    return x2
            else:
                return -1

        elif self.dimensions['高'][0] is None and self.dimensions['高'][1] is None:
            shangfang = self.dimensions['上方'][0]
            xiafang = self.dimensions['下方'][0]
            ji = self.dimensions['积'][0]
            return (3 * ji) / (shangfang * xiafang + shangfang * shangfang + xiafang * xiafang)

        elif self.dimensions['积'][0] is None and self.dimensions['积'][1] is None:
            shangfang = self.dimensions['上方'][0]
            xiafang = self.dimensions['下方'][0]
            gao = self.dimensions['高'][0]
            return (shangfang * xiafang + shangfang * shangfang + xiafang * xiafang) * gao / 3


class 圆亭(Structure):
    def value(self):
        """
        根据提供的参数计算缺失的尺寸或面积。

        返回:
            float: 缺失参数的计算值，以指定的单位返回。
        """
        # 检查哪个参数缺失，并计算它
        if self.dimensions['上周'][0] is None and self.dimensions['上周'][1] is None:
            xiafang = self.dimensions['下周'][0]
            gao = self.dimensions['高'][0]
            ji = self.dimensions['积'][0]
            delta = xiafang * xiafang - 4 * (xiafang * xiafang - 36 * ji / gao)
            if delta >= 0:
                x1 = (-xiafang + math.math.sqrt(delta)) / 2
                x2 = (-xiafang - math.math.sqrt(delta)) / 2
                if x1 > x2:
                    return x1
                else:
                    return x2
            else:
                return -1

        elif self.dimensions['下周'][0] is None and self.dimensions['下周'][1] is None:
            shangfang = self.dimensions['上周'][0]
            gao = self.dimensions['高'][0]
            ji = self.dimensions['积'][0]
            delta = shangfang * shangfang - 4 * (shangfang * shangfang - 36 * ji / gao)
            if delta >= 0:
                x1 = (-shangfang + math.math.sqrt(delta)) / 2
                x2 = (-shangfang - math.math.sqrt(delta)) / 2
                if x1 > x2:
                    return x1
                else:
                    return x2
            else:
                return -1

        elif self.dimensions['高'][0] is None and self.dimensions['高'][1] is None:
            shangfang = self.dimensions['上周'][0]
            xiafang = self.dimensions['下周'][0]
            ji = self.dimensions['积'][0]
            return (36 * ji) / (shangfang * xiafang + shangfang * shangfang + xiafang * xiafang)

        elif self.dimensions['积'][0] is None and self.dimensions['积'][1] is None:
            shangfang = self.dimensions['上周'][0]
            xiafang = self.dimensions['下周'][0]
            gao = self.dimensions['高'][0]
            return (shangfang * xiafang + shangfang * shangfang + xiafang * xiafang) * gao / 36


class 圆锥(Structure):
    def value(self):
        """
        根据提供的参数计算缺失的尺寸或面积。

        返回:
            float: 缺失参数的计算值，以指定的单位返回。
        """
        # 检查哪个参数缺失，并计算它
        if self.dimensions['下周'][0] is None and self.dimensions['下周'][1] is None:
            gao = self.dimensions['高'][0]
            ji = self.dimensions['积'][0]
            return math.math.sqrt((ji * 36) / gao)

        elif self.dimensions['高'][0] is None and self.dimensions['高'][1] is None:
            xiazhou = self.dimensions['下周'][0]
            ji = self.dimensions['积'][0]
            return 36 * ji / (xiazhou * xiazhou)

        elif self.dimensions['积'][0] is None and self.dimensions['积'][1] is None:
            xiazhou = self.dimensions['下周'][0]
            gao = self.dimensions['高'][0]
            return (xiazhou * xiazhou) * gao / 36


class 方锥(Structure):
    def value(self):
        """
        根据提供的参数计算缺失的尺寸或面积。

        返回:
            float: 缺失参数的计算值，以指定的单位返回。
        """
        # 检查哪个参数缺失，并计算它
        if self.dimensions['下方'][0] is None and self.dimensions['下方'][1] is None:
            gao = self.dimensions['高'][0]
            ji = self.dimensions['积'][0]
            return math.math.sqrt((ji * 3) / gao)

        elif self.dimensions['高'][0] is None and self.dimensions['高'][1] is None:
            xiafang = self.dimensions['下方'][0]
            ji = self.dimensions['积'][0]
            return 3 * ji / (xiafang * xiafang)

        elif self.dimensions['积'][0] is None and self.dimensions['积'][1] is None:
            xiafang = self.dimensions['下方'][0]
            gao = self.dimensions['高'][0]
            return (xiafang * xiafang) * gao / 3


# # 邪田：一头广，一头广（直角梯形）
# class 邪田(Structure):
#     def value(self, target_unit='步'):
#         """
#         计算梯形田地的面积，并以指定单位返回。

#         参数:
#             target_unit (str): 面积计算使用的目标单位，默认为'步'。

#         返回:
#             float: 目标单位下的梯形面积。
#         """
#         # 梯形面积 = (上底 + 下底) * 高 / 2
#         top_base = self.dimensions['头广'][0]
#         bottom_base = self.dimensions['头广1'][0]
#         height = self.dimensions['正从'][0]

#         top_base_unit = self.dimensions['头广'][1]
#         bottom_base_unit = self.dimensions['头广1'][1]
#         height_unit = self.dimensions['正从'][1]

#         top_base_in_target_unit = self.convert_unit(top_base, top_base_unit, target_unit)
#         bottom_base_in_target_unit = self.convert_unit(bottom_base, bottom_base_unit, target_unit)
#         height_in_target_unit = self.convert_unit(height, height_unit, target_unit)

#         value = (top_base_in_target_unit + bottom_base_in_target_unit) * height_in_target_unit / 2
#         return value, target_unit

#     def __str__(self, target_unit='步'):
#         """
#         返回梯形田地的详细字符串描述，包括面积信息。

#         参数:
#             target_unit (str): 面积描述使用的单位（默认为'步'）。

#         返回:
#             str: 包括名称、尺寸和面积的详细描述。
#         """
#         area_in_target_unit = self.value(target_unit)[0]
#         return f"{self.name}，头广（上底）: {self.dimensions['头广'][0]}{self.dimensions['头广'][1]}，头广（下底）: {self.dimensions['头广1'][0]}{self.dimensions['头广1'][1]}，正从（高）: {self.dimensions['正从'][0]}{self.dimensions['正从'][1]}，面积: {area_in_target_unit}{target_unit}²"


# # 箕田：舌广，踵广，正从 （梯形田，上底，下底，高）
# class 箕田(Structure):
#     def value(self, target_unit='步'):
#         """
#         计算梯形田地的面积，并以指定单位返回。

#         参数:
#             target_unit (str): 面积计算使用的目标单位，默认为'步'。

#         返回:
#             float: 目标单位下的梯形面积。
#         """
#         # 梯形面积 = (上底 + 下底) * 高 / 2
#         top_base = self.dimensions['舌广'][0]
#         bottom_base = self.dimensions['踵广'][0]
#         height = self.dimensions['正从'][0]

#         top_base_unit = self.dimensions['舌广'][1]
#         bottom_base_unit = self.dimensions['踵广'][1]
#         height_unit = self.dimensions['正从'][1]

#         top_base_in_target_unit = self.convert_unit(top_base, top_base_unit, target_unit)
#         bottom_base_in_target_unit = self.convert_unit(bottom_base, bottom_base_unit, target_unit)
#         height_in_target_unit = self.convert_unit(height, height_unit, target_unit)

#         value = (top_base_in_target_unit + bottom_base_in_target_unit) * height_in_target_unit / 2
#         return value, target_unit

#     def __str__(self, target_unit='步'):
#         """
#         返回梯形田地的详细字符串描述，包括面积信息。

#         参数:
#             target_unit (str): 面积描述使用的单位（默认为'步'）。

#         返回:
#             str: 包括名称、尺寸和面积的详细描述。
#         """
#         area_in_target_unit = self.value(target_unit)[0]
#         return f"{self.name}，舌广（上底）: {self.dimensions['舌广'][0]}{self.dimensions['舌广'][1]}，踵广（下底）: {self.dimensions['踵广'][0]}{self.dimensions['踵广'][1]}，正从（高）: {self.dimensions['正从'][0]}{self.dimensions['正从'][1]}，面积: {area_in_target_unit}{target_unit}²"


# # 圆田：周，径（周长，直径）
# # 田 = 周 * 径 / 4
# # (2πr * 2r) / 4 = πr^2
# class 圆田(Structure):
#     def value(self, target_unit='步'):
#         """
#         计算圆形田地的面积，并以指定单位返回。

#         参数:
#             target_unit (str): 面积计算使用的目标单位，默认为'步'。

#         返回:
#             float: 目标单位下的圆形面积。
#         """
#         perimeter = self.dimensions['周'][0]
#         diameter = self.dimensions['径'][0]

#         perimeter_unit = self.dimensions['周'][1]
#         diameter_unit = self.dimensions['径'][1]

#         perimeter_in_target_unit = self.convert_unit(perimeter, perimeter_unit, target_unit)
#         diameter_in_target_unit = self.convert_unit(diameter, diameter_unit, target_unit)

#         value = perimeter_in_target_unit * diameter_in_target_unit / 4

#         return value, target_unit

#     def __str__(self, target_unit='步'):
#         """
#         返回圆形田地的详细字符串描述，包括面积信息。

#         参数:
#             target_unit (str): 面积描述使用的单位（默认为'步'）。

#         返回:
#             str: 包括名称、尺寸和面积的详细描述。
#         """
#         area_in_target_unit = self.value(target_unit)[0]

#         return f"{self.name}，周（周长）: {self.dimensions['周'][0]}{self.dimensions['周'][1]}，径（直径）: {self.dimensions['径'][0]}{self.dimensions['径'][1]}，面积: {area_in_target_unit}{target_unit}²"


# # 宛田：下周，径（扇形，弧长，直径）
# # 田 = 下周 * 径 / 4
# class 宛田(Structure):
#     def value(self, target_unit='步'):
#         """
#         计算扇形田地的面积，并以指定单位返回。

#         参数:
#             target_unit (str): 面积计算使用的目标单位，默认为'步'。

#         返回:
#             float: 目标单位下的扇形面积。
#         """
#         perimeter = self.dimensions['下周'][0]
#         diameter = self.dimensions['径'][0]

#         perimeter_unit = self.dimensions['下周'][1]
#         diameter_unit = self.dimensions['径'][1]

#         perimeter_in_target_unit = self.convert_unit(perimeter, perimeter_unit, target_unit)
#         diameter_in_target_unit = self.convert_unit(diameter, diameter_unit, target_unit)

#         value = perimeter_in_target_unit * diameter_in_target_unit / 4

#         return value, target_unit

#     def __str__(self, target_unit='步'):
#         """
#         返回扇形田地的详细字符串描述，包括面积信息。

#         参数:
#             target_unit (str): 面积描述使用的单位（默认为'步'）。

#         返回:
#             str: 包括名称、尺寸和面积的详细描述。
#         """
#         area_in_target_unit = self.value(target_unit)[0]

#         return f"{self.name}，下周（弧长）: {self.dimensions['下周'][0]}{self.dimensions['下周'][1]}，径（直径）: {self.dimensions['径'][0]}{self.dimensions['径'][1]}，面积: {area_in_target_unit}{target_unit}²"


# # 弧田：弦，矢（弓形高）
# # 田 = （弦*矢+矢*矢）/ 2
# class 弧田(Structure):
#     def value(self, target_unit='步'):
#         """
#         计算弧形田地的面积，并以指定单位返回。

#         参数:
#             target_unit (str): 面积计算使用的目标单位，默认为'步'。

#         返回:
#             float: 目标单位下的弧形面积。
#         """
#         # 提取每个维度并转换为目标单位，然后计算面积
#         chord = self.dimensions['弦'][0]
#         arrow = self.dimensions['矢'][0]

#         chord_unit = self.dimensions['弦'][1]
#         arrow_unit = self.dimensions['矢'][1]

#         chord_in_target_unit = self.convert_unit(chord, chord_unit, target_unit)
#         arrow_in_target_unit = self.convert_unit(arrow, arrow_unit, target_unit)

#         value = (chord_in_target_unit * arrow_in_target_unit + arrow_in_target_unit * arrow_in_target_unit) / 2

#         # 计算并返回面积和单位
#         return value, target_unit

#     def __str__(self, target_unit='步'):
#         """
#         返回弧形田地的详细字符串描述，包括面积信息。

#         参数:
#             target_unit (str): 面积描述使用的单位（默认为'步'）。

#         返回:
#             str: 包括名称、尺寸和面积的详细描述。
#         """
#         area_in_target_unit = self.value(target_unit)[0]

#         return f"{self.name}，弦: {self.dimensions['弦'][0]}{self.dimensions['弦'][1]}，矢（弓形高）: {self.dimensions['矢'][0]}{self.dimensions['矢'][1]}，面积: {area_in_target_unit}{target_unit}²"


# # 环田：中周，外周，径
# # 田 = （中周+外周）*径/2
# class 环田(Structure):
#     def value(self, target_unit='步'):
#         """
#         计算环形田地的面积，并以指定单位返回。

#         参数:
#             target_unit (str): 面积计算使用的目标单位，默认为'步'。

#         返回:
#             float: 目标单位下的环形面积。
#         """
#         inner = self.dimensions['中周'][0]
#         outer = self.dimensions['外周'][0]
#         diameter = self.dimensions['径'][0]

#         inner_unit = self.dimensions['中周'][1]
#         outer_unit = self.dimensions['外周'][1]
#         diameter_unit = self.dimensions['径'][1]

#         inner_in_target_unit = self.convert_unit(inner, inner_unit, target_unit)
#         outer_in_target_unit = self.convert_unit(outer, outer_unit, target_unit)
#         diameter_target_unit = self.convert_unit(diameter, diameter_unit, target_unit)

#         value = (inner_in_target_unit + outer_in_target_unit) * diameter_target_unit / 2

#         return value, target_unit

#     def __str__(self, target_unit='步'):
#         """
#         返回环形田地的详细字符串描述，包括面积信息。

#         参数:
#             target_unit (str): 面积描述使用的单位（默认为'步'）。

#         返回:
#             str: 包括名称、尺寸和面积的详细描述。
#         """
#         area_in_target_unit = self.value(target_unit)[0]

#         return f"{self.name}，中周: {self.dimensions['中周'][0]}{self.dimensions['中周'][1]}，外周: {self.dimensions['外周'][0]}{self.dimensions['外周'][1]}，径: {self.dimensions['径'][0]}{self.dimensions['径'][1]}，面积: {area_in_target_unit}{target_unit}²"


# class 合之(Structure):
#     def value(self, target_unit=None):
#         """
#         计算列表中所有数值的总和。

#         返回:
#             float: 列表中所有数值的总和。
#         """
#         if '无量纲量' in self.dimensions and '无量纲量1' in self.dimensions:
#             first = self.dimensions['无量纲量'][0]
#             second = self.dimensions['无量纲量1'][0]
#         elif '量纲量' in self.dimensions and '无量纲量' in self.dimensions:
#             first = self.dimensions['量纲量'][0]
#             second = self.dimensions['无量纲量'][0]
#         else:
#             return None, None  # 如果维度不符，返回None

#         return first + second, target_unit

#     def __str__(self):
#         """
#         返回一个描述此类及其计算的总和的详细字符串。

#         返回:
#             str: 包含初始化的数值列表和计算的总和的详细描述。
#         """
#         # 调用求和方法，获取总和
#         sum = self.value()
#         # 格式化字符串，展示类的内容
#         if '无量纲量' in self.dimensions and '无量纲量1' in self.dimensions:
#             return f"{self.name}，第一个数: {self.dimensions['无量纲量'][0]}，第二个数: {self.dimensions['无量纲量1'][0]}，合之（和）: {sum}"
#         elif '量纲量' in self.dimensions and '无量纲量' in self.dimensions:
#             return f"{self.name}，第一个数: {self.dimensions['量纲量'][0]}，第二个数: {self.dimensions['无量纲量'][0]}，合之（和）: {sum}"


# class 馀(Structure):
#     def value(self, target_unit=None):
#         """
#         根据初始化的维度计算差值。

#         参数:
#             target_unit (str): 计算结果的单位（如果需要）。

#         返回:
#             tuple: 包含计算结果和单位的元组。
#         """
#         # 提取维度列表中的第一个和第二个数值
#         if '无量纲量' in self.dimensions and '无量纲量1' in self.dimensions:
#             first = self.dimensions['无量纲量'][0]
#             second = self.dimensions['无量纲量1'][0]
#         elif '量纲量' in self.dimensions and '无量纲量' in self.dimensions:
#             first = self.dimensions['量纲量'][0]
#             second = self.dimensions['无量纲量'][0]
#         else:
#             return None, None  # 如果维度不符，返回None

#         return first - second, target_unit

#     def __str__(self):
#         """
#         返回一个描述此类及其计算的总和的详细字符串。

#         返回:
#             str: 包含初始化的数值列表和计算的总和的详细描述。
#         """
#         # 调用求和方法，获取总和
#         different = self.value()
#         # 格式化字符串，展示类的内容
#         if '无量纲量' in self.dimensions and '无量纲量1' in self.dimensions:
#             return f"{self.name}，第一个数: {self.dimensions['无量纲量'][0]}，第二个数: {self.dimensions['无量纲量1'][0]}，馀（差）: {different}"
#         elif '量纲量' in self.dimensions and '无量纲量' in self.dimensions:
#             return f"{self.name}，第一个数: {self.dimensions['量纲量'][0]}，第二个数: {self.dimensions['无量纲量'][0]}，馀（差）: {different}"


# # 城：上广，下广，高， 袤
# # 上下底均为梯形的正四棱柱，【上广】为底面梯形的上底，【下广】为下底，【高】或【深】为梯形的高，【袤】为四棱柱的高。其体积属性记为【积】。
# # 积 = （上广 + 下广）/ 2 * 高 * 袤
# class 城(Structure):
#     def value(self, target_unit='步'):
#         """
#         计算城的体积，并以指定单位返回。

#         参数:
#             target_unit (str): 面积计算使用的目标单位，默认为'步'。

#         返回:
#             float: 目标单位下的体积。
#         """

#         top_base = self.dimensions['上广'][0]
#         bottom_base = self.dimensions['下广'][0]
#         height = self.dimensions['高'][0]
#         mao = self.dimensions['袤'][0]

#         top_base_unit = self.dimensions['上广'][1]
#         bottom_base_unit = self.dimensions['下广'][1]
#         height_unit = self.dimensions['高'][1]
#         mao_unit = self.dimensions['袤'][1]

#         top_base_in_target_unit = self.convert_unit(top_base, top_base_unit, target_unit)
#         bottom_base_in_target_unit = self.convert_unit(bottom_base, bottom_base_unit, target_unit)
#         height_in_target_unit = self.convert_unit(height, height_unit, target_unit)
#         mao_in_target_unit = self.convert_unit(mao, mao_unit, target_unit)

#         value = (top_base_in_target_unit + bottom_base_in_target_unit) / 2 * height_in_target_unit * mao_in_target_unit
#         return value, target_unit

#     def __str__(self, target_unit='步'):
#         """
#         返回梯形田地的详细字符串描述，包括面积信息。

#         参数:
#             target_unit (str): 面积描述使用的单位（默认为'步'）。

#         返回:
#             str: 包括名称、尺寸和面积的详细描述。
#         """
#         area_in_target_unit = self.value(target_unit)[0]
#         return f"{self.name}，上广（上底）: {self.dimensions['上广'][0]}{self.dimensions['上广'][1]}，下广（下底）: {self.dimensions['下广'][0]}{self.dimensions['下广'][1]}，高（梯形的高）: {self.dimensions['高'][0]}{self.dimensions['高'][1]}，袤（四棱柱的高）: {self.dimensions['袤'][0]}{self.dimensions['袤'][1]}，体积: {area_in_target_unit}{target_unit}³"


# class 垣(Structure):
#     def value(self, target_unit='步'):
#         """
#         计算城的体积，并以指定单位返回。

#         参数:
#             target_unit (str): 面积计算使用的目标单位，默认为'步'。

#         返回:
#             float: 目标单位下的体积。
#         """

#         top_base = self.dimensions['上广'][0]
#         bottom_base = self.dimensions['下广'][0]
#         height = self.dimensions['高'][0]
#         mao = self.dimensions['袤'][0]

#         top_base_unit = self.dimensions['上广'][1]
#         bottom_base_unit = self.dimensions['下广'][1]
#         height_unit = self.dimensions['高'][1]
#         mao_unit = self.dimensions['袤'][1]

#         top_base_in_target_unit = self.convert_unit(top_base, top_base_unit, target_unit)
#         bottom_base_in_target_unit = self.convert_unit(bottom_base, bottom_base_unit, target_unit)
#         height_in_target_unit = self.convert_unit(height, height_unit, target_unit)
#         mao_in_target_unit = self.convert_unit(mao, mao_unit, target_unit)

#         value = (top_base_in_target_unit + bottom_base_in_target_unit) / 2 * height_in_target_unit * mao_in_target_unit
#         return value, target_unit

#     def __str__(self, target_unit='步'):
#         """
#         返回梯形田地的详细字符串描述，包括面积信息。

#         参数:
#             target_unit (str): 面积描述使用的单位（默认为'步'）。

#         返回:
#             str: 包括名称、尺寸和面积的详细描述。
#         """
#         area_in_target_unit = self.value(target_unit)[0]
#         return f"{self.name}，上广（上底）: {self.dimensions['上广'][0]}{self.dimensions['上广'][1]}，下广（下底）: {self.dimensions['下广'][0]}{self.dimensions['下广'][1]}，高（梯形的高）: {self.dimensions['高'][0]}{self.dimensions['高'][1]}，袤（四棱柱的高）: {self.dimensions['袤'][0]}{self.dimensions['袤'][1]}，体积: {area_in_target_unit}{target_unit}³"


# class 堤(Structure):
#     def value(self, target_unit='步'):
#         """
#         计算城的体积，并以指定单位返回。

#         参数:
#             target_unit (str): 面积计算使用的目标单位，默认为'步'。

#         返回:
#             float: 目标单位下的体积。
#         """

#         top_base = self.dimensions['上广'][0]
#         bottom_base = self.dimensions['下广'][0]
#         height = self.dimensions['高'][0]
#         mao = self.dimensions['袤'][0]

#         top_base_unit = self.dimensions['上广'][1]
#         bottom_base_unit = self.dimensions['下广'][1]
#         height_unit = self.dimensions['高'][1]
#         mao_unit = self.dimensions['袤'][1]

#         top_base_in_target_unit = self.convert_unit(top_base, top_base_unit, target_unit)
#         bottom_base_in_target_unit = self.convert_unit(bottom_base, bottom_base_unit, target_unit)
#         height_in_target_unit = self.convert_unit(height, height_unit, target_unit)
#         mao_in_target_unit = self.convert_unit(mao, mao_unit, target_unit)

#         value = (top_base_in_target_unit + bottom_base_in_target_unit) / 2 * height_in_target_unit * mao_in_target_unit
#         return value, target_unit

#     def __str__(self, target_unit='步'):
#         """
#         返回梯形田地的详细字符串描述，包括面积信息。

#         参数:
#             target_unit (str): 面积描述使用的单位（默认为'步'）。

#         返回:
#             str: 包括名称、尺寸和面积的详细描述。
#         """
#         area_in_target_unit = self.value(target_unit)[0]
#         return f"{self.name}，上广（上底）: {self.dimensions['上广'][0]}{self.dimensions['上广'][1]}，下广（下底）: {self.dimensions['下广'][0]}{self.dimensions['下广'][1]}，高（梯形的高）: {self.dimensions['高'][0]}{self.dimensions['高'][1]}，袤（四棱柱的高）: {self.dimensions['袤'][0]}{self.dimensions['袤'][1]}，体积: {area_in_target_unit}{target_unit}³"


# class 沟(Structure):
#     def value(self, target_unit='步'):
#         """
#         计算城的体积，并以指定单位返回。

#         参数:
#             target_unit (str): 面积计算使用的目标单位，默认为'步'。

#         返回:
#             float: 目标单位下的体积。
#         """

#         top_base = self.dimensions['上广'][0]
#         bottom_base = self.dimensions['下广'][0]
#         depth = self.dimensions['深'][0]
#         mao = self.dimensions['袤'][0]

#         top_base_unit = self.dimensions['上广'][1]
#         bottom_base_unit = self.dimensions['下广'][1]
#         depth_unit = self.dimensions['高'][1]
#         mao_unit = self.dimensions['袤'][1]

#         top_base_in_target_unit = self.convert_unit(top_base, top_base_unit, target_unit)
#         bottom_base_in_target_unit = self.convert_unit(bottom_base, bottom_base_unit, target_unit)
#         depth_in_target_unit = self.convert_unit(depth, depth_unit, target_unit)
#         mao_in_target_unit = self.convert_unit(mao, mao_unit, target_unit)

#         value = (top_base_in_target_unit + bottom_base_in_target_unit) / 2 * depth_in_target_unit * mao_in_target_unit
#         return value, target_unit

#     def __str__(self, target_unit='步'):
#         """
#         返回梯形田地的详细字符串描述，包括面积信息。

#         参数:
#             target_unit (str): 面积描述使用的单位（默认为'步'）。

#         返回:
#             str: 包括名称、尺寸和面积的详细描述。
#         """
#         area_in_target_unit = self.value(target_unit)[0]
#         return f"{self.name}，上广（上底）: {self.dimensions['上广'][0]}{self.dimensions['上广'][1]}，下广（下底）: {self.dimensions['下广'][0]}{self.dimensions['下广'][1]}，高（梯形的高）: {self.dimensions['高'][0]}{self.dimensions['高'][1]}，袤（四棱柱的高）: {self.dimensions['袤'][0]}{self.dimensions['袤'][1]}，体积: {area_in_target_unit}{target_unit}³"


# class 聢(Structure):
#     def value(self, target_unit='步'):
#         """
#         计算城的体积，并以指定单位返回。

#         参数:
#             target_unit (str): 面积计算使用的目标单位，默认为'步'。

#         返回:
#             float: 目标单位下的体积。
#         """

#         top_base = self.dimensions['上广'][0]
#         bottom_base = self.dimensions['下广'][0]
#         depth = self.dimensions['深'][0]
#         mao = self.dimensions['袤'][0]

#         top_base_unit = self.dimensions['上广'][1]
#         bottom_base_unit = self.dimensions['下广'][1]
#         depth_unit = self.dimensions['高'][1]
#         mao_unit = self.dimensions['袤'][1]

#         top_base_in_target_unit = self.convert_unit(top_base, top_base_unit, target_unit)
#         bottom_base_in_target_unit = self.convert_unit(bottom_base, bottom_base_unit, target_unit)
#         depth_in_target_unit = self.convert_unit(depth, depth_unit, target_unit)
#         mao_in_target_unit = self.convert_unit(mao, mao_unit, target_unit)

#         value = (top_base_in_target_unit + bottom_base_in_target_unit) / 2 * depth_in_target_unit * mao_in_target_unit
#         return value, target_unit

#     def __str__(self, target_unit='步'):
#         """
#         返回梯形田地的详细字符串描述，包括面积信息。

#         参数:
#             target_unit (str): 面积描述使用的单位（默认为'步'）。

#         返回:
#             str: 包括名称、尺寸和面积的详细描述。
#         """
#         area_in_target_unit = self.value(target_unit)[0]
#         return f"{self.name}，上广（上底）: {self.dimensions['上广'][0]}{self.dimensions['上广'][1]}，下广（下底）: {self.dimensions['下广'][0]}{self.dimensions['下广'][1]}，高（梯形的高）: {self.dimensions['高'][0]}{self.dimensions['高'][1]}，袤（四棱柱的高）: {self.dimensions['袤'][0]}{self.dimensions['袤'][1]}，体积: {area_in_target_unit}{target_unit}³"


# class 渠(Structure):
#     def value(self, target_unit='步'):
#         """
#         计算城的体积，并以指定单位返回。

#         参数:
#             target_unit (str): 面积计算使用的目标单位，默认为'步'。

#         返回:
#             float: 目标单位下的体积。
#         """

#         top_base = self.dimensions['上广'][0]
#         bottom_base = self.dimensions['下广'][0]
#         depth = self.dimensions['深'][0]
#         mao = self.dimensions['袤'][0]

#         top_base_unit = self.dimensions['上广'][1]
#         bottom_base_unit = self.dimensions['下广'][1]
#         depth_unit = self.dimensions['高'][1]
#         mao_unit = self.dimensions['袤'][1]

#         top_base_in_target_unit = self.convert_unit(top_base, top_base_unit, target_unit)
#         bottom_base_in_target_unit = self.convert_unit(bottom_base, bottom_base_unit, target_unit)
#         depth_in_target_unit = self.convert_unit(depth, depth_unit, target_unit)
#         mao_in_target_unit = self.convert_unit(mao, mao_unit, target_unit)

#         value = (top_base_in_target_unit + bottom_base_in_target_unit) / 2 * depth_in_target_unit * mao_in_target_unit
#         return value, target_unit

#     def __str__(self, target_unit='步'):
#         """
#         返回梯形田地的详细字符串描述，包括面积信息。

#         参数:
#             target_unit (str): 面积描述使用的单位（默认为'步'）。

#         返回:
#             str: 包括名称、尺寸和面积的详细描述。
#         """
#         area_in_target_unit = self.value(target_unit)[0]
#         return f"{self.name}，上广（上底）: {self.dimensions['上广'][0]}{self.dimensions['上广'][1]}，下广（下底）: {self.dimensions['下广'][0]}{self.dimensions['下广'][1]}，高（梯形的高）: {self.dimensions['高'][0]}{self.dimensions['高'][1]}，袤（四棱柱的高）: {self.dimensions['袤'][0]}{self.dimensions['袤'][1]}，体积: {area_in_target_unit}{target_unit}³"


# class 堑(Structure):
#     def value(self, target_unit='步'):
#         """
#         计算城的体积，并以指定单位返回。

#         参数:
#             target_unit (str): 面积计算使用的目标单位，默认为'步'。

#         返回:
#             float: 目标单位下的体积。
#         """

#         top_base = self.dimensions['上广'][0]
#         bottom_base = self.dimensions['下广'][0]
#         depth = self.dimensions['深'][0]
#         mao = self.dimensions['袤'][0]

#         top_base_unit = self.dimensions['上广'][1]
#         bottom_base_unit = self.dimensions['下广'][1]
#         depth_unit = self.dimensions['高'][1]
#         mao_unit = self.dimensions['袤'][1]

#         top_base_in_target_unit = self.convert_unit(top_base, top_base_unit, target_unit)
#         bottom_base_in_target_unit = self.convert_unit(bottom_base, bottom_base_unit, target_unit)
#         depth_in_target_unit = self.convert_unit(depth, depth_unit, target_unit)
#         mao_in_target_unit = self.convert_unit(mao, mao_unit, target_unit)

#         value = (top_base_in_target_unit + bottom_base_in_target_unit) / 2 * depth_in_target_unit * mao_in_target_unit
#         return value, target_unit

#     def __str__(self, target_unit='步'):
#         """
#         返回梯形田地的详细字符串描述，包括面积信息。

#         参数:
#             target_unit (str): 面积描述使用的单位（默认为'步'）。

#         返回:
#             str: 包括名称、尺寸和面积的详细描述。
#         """
#         area_in_target_unit = self.value(target_unit)[0]
#         return f"{self.name}，上广（上底）: {self.dimensions['上广'][0]}{self.dimensions['上广'][1]}，下广（下底）: {self.dimensions['下广'][0]}{self.dimensions['下广'][1]}，高（梯形的高）: {self.dimensions['高'][0]}{self.dimensions['高'][1]}，袤（四棱柱的高）: {self.dimensions['袤'][0]}{self.dimensions['袤'][1]}，体积: {area_in_target_unit}{target_unit}³"


# class 方堡嶹(Structure):
#     def value(self, target_unit='步'):
#         """
#         计算圆亭的体积，并以指定单位返回。

#         参数:
#             target_unit (str): 面积计算使用的目标单位，默认为'步'。

#         返回:
#             float: 目标单位下的体积。
#         """

#         base = self.dimensions['方'][0]
#         height = self.dimensions['高'][0]

#         base_unit = self.dimensions['方'][1]
#         height_unit = self.dimensions['高'][1]

#         base_in_target_unit = self.convert_unit(base, base_unit, target_unit)
#         height_in_target_unit = self.convert_unit(height, height_unit, target_unit)

#         value = base_in_target_unit * base_in_target_unit * height_in_target_unit
#         return value, target_unit

#     def __str__(self, target_unit='步'):
#         """
#         返回梯形田地的详细字符串描述，包括面积信息。

#         参数:
#             target_unit (str): 面积描述使用的单位（默认为'步'）。

#         返回:
#             str: 包括名称、尺寸和面积的详细描述。
#         """
#         area_in_target_unit = self.value(target_unit)[0]
#         return f"{self.name}，方: {self.dimensions['方'][0]}{self.dimensions['方'][1]}，高: {self.dimensions['高'][0]}{self.dimensions['高'][1]}，体积: {area_in_target_unit}{target_unit}³"


# class 圆堡嶹(Structure):
#     def value(self, target_unit='步'):
#         """
#         计算圆亭的体积，并以指定单位返回。

#         参数:
#             target_unit (str): 面积计算使用的目标单位，默认为'步'。

#         返回:
#             float: 目标单位下的体积。
#         """

#         perimeter = self.dimensions['周'][0]
#         height = self.dimensions['高'][0]

#         perimeter_unit = self.dimensions['周'][1]
#         height_unit = self.dimensions['高'][1]

#         perimeter_in_target_unit = self.convert_unit(perimeter, perimeter_unit, target_unit)
#         height_in_target_unit = self.convert_unit(height, height_unit, target_unit)

#         value = perimeter_in_target_unit * perimeter_in_target_unit * height_in_target_unit / 12
#         return value, target_unit

#     def __str__(self, target_unit='步'):
#         """
#         返回梯形田地的详细字符串描述，包括面积信息。

#         参数:
#             target_unit (str): 面积描述使用的单位（默认为'步'）。

#         返回:
#             str: 包括名称、尺寸和面积的详细描述。
#         """
#         area_in_target_unit = self.value(target_unit)[0]
#         return f"{self.name}，周: {self.dimensions['周'][0]}{self.dimensions['周'][1]}，高: {self.dimensions['高'][0]}{self.dimensions['高'][1]}，体积: {area_in_target_unit}{target_unit}³"


# class 方亭(Structure):
#     def value(self, target_unit='步'):
#         """
#         计算圆亭的体积，并以指定单位返回。

#         参数:
#             target_unit (str): 面积计算使用的目标单位，默认为'步'。

#         返回:
#             float: 目标单位下的体积。
#         """

#         top_base = self.dimensions['上方'][0]
#         bottom_base = self.dimensions['下方'][0]
#         height = self.dimensions['高'][0]

#         top_base_unit = self.dimensions['上方'][1]
#         bottom_base_unit = self.dimensions['下方'][1]
#         height_unit = self.dimensions['高'][1]

#         top_base_in_target_unit = self.convert_unit(top_base, top_base_unit, target_unit)
#         bottom_base_in_target_unit = self.convert_unit(bottom_base, bottom_base_unit, target_unit)
#         height_in_target_unit = self.convert_unit(height, height_unit, target_unit)

#         value = (
#                             top_base_in_target_unit * bottom_base_in_target_unit + bottom_base_in_target_unit * bottom_base_in_target_unit + top_base_in_target_unit * top_base_in_target_unit) * height_in_target_unit / 3
#         return value, target_unit

#     def __str__(self, target_unit='步'):
#         """
#         返回梯形田地的详细字符串描述，包括面积信息。

#         参数:
#             target_unit (str): 面积描述使用的单位（默认为'步'）。

#         返回:
#             str: 包括名称、尺寸和面积的详细描述。
#         """
#         area_in_target_unit = self.value(target_unit)[0]
#         return f"{self.name}，上广（上底）: {self.dimensions['上广'][0]}{self.dimensions['上广'][1]}，下广（下底）: {self.dimensions['下广'][0]}{self.dimensions['下广'][1]}，高: {self.dimensions['高'][0]}{self.dimensions['高'][1]}，体积: {area_in_target_unit}{target_unit}³"


# # 圆台
# class 圆亭(Structure):
#     def value(self, target_unit='步'):
#         """
#         计算圆亭的体积，并以指定单位返回。

#         参数:
#             target_unit (str): 面积计算使用的目标单位，默认为'步'。

#         返回:
#             float: 目标单位下的体积。
#         """

#         top_perimeter = self.dimensions['上周'][0]
#         bottom_perimeter = self.dimensions['下周'][0]
#         height = self.dimensions['高'][0]

#         top_perimeter_unit = self.dimensions['上周'][1]
#         bottom_perimeter_unit = self.dimensions['下周'][1]
#         height_unit = self.dimensions['高'][1]

#         top_perimeter_in_target_unit = self.convert_unit(top_perimeter, top_perimeter_unit, target_unit)
#         bottom_perimeter_in_target_unit = self.convert_unit(bottom_perimeter, bottom_perimeter_unit, target_unit)
#         height_in_target_unit = self.convert_unit(height, height_unit, target_unit)

#         value = (
#                             top_perimeter_in_target_unit * bottom_perimeter_in_target_unit + bottom_perimeter_in_target_unit * bottom_perimeter_in_target_unit + top_perimeter_in_target_unit * top_perimeter_in_target_unit) * height_in_target_unit / 36
#         return value, target_unit

#     def __str__(self, target_unit='步'):
#         """
#         返回梯形田地的详细字符串描述，包括面积信息。

#         参数:
#             target_unit (str): 面积描述使用的单位（默认为'步'）。

#         返回:
#             str: 包括名称、尺寸和面积的详细描述。
#         """
#         area_in_target_unit = self.value(target_unit)[0]
#         return f"{self.name}，上周: {self.dimensions['上周'][0]}{self.dimensions['上周'][1]}，下周: {self.dimensions['下周'][0]}{self.dimensions['下周'][1]}，高: {self.dimensions['高'][0]}{self.dimensions['高'][1]}，体积: {area_in_target_unit}{target_unit}³"


# class 圆锥(Structure):
#     def value(self, target_unit='步'):
#         """
#         计算圆锥的体积，并以指定单位返回。

#         参数:
#             target_unit (str): 面积计算使用的目标单位，默认为'步'。

#         返回:
#             float: 目标单位下的体积。
#         """

#         perimeter = self.dimensions['下周'][0]
#         height = self.dimensions['高'][0]

#         perimeter_unit = self.dimensions['下周'][1]
#         height_unit = self.dimensions['高'][1]

#         perimeter_in_target_unit = self.convert_unit(perimeter, perimeter_unit, target_unit)
#         height_in_target_unit = self.convert_unit(height, height_unit, target_unit)

#         value = (perimeter_in_target_unit * perimeter_in_target_unit) * height_in_target_unit / 36
#         return value, target_unit

#     def __str__(self, target_unit='步'):
#         """
#         返回梯形田地的详细字符串描述，包括面积信息。

#         参数:
#             target_unit (str): 面积描述使用的单位（默认为'步'）。

#         返回:
#             str: 包括名称、尺寸和面积的详细描述。
#         """
#         area_in_target_unit = self.value(target_unit)[0]
#         return f"{self.name}，下周: {self.dimensions['下周'][0]}{self.dimensions['下周'][1]}，高: {self.dimensions['高'][0]}{self.dimensions['高'][1]}，体积: {area_in_target_unit}{target_unit}³"


# # 四棱锥
# class 方锥(Structure):
#     def value(self, target_unit='步'):
#         """
#         计算方锥的体积，并以指定单位返回。

#         参数:
#             target_unit (str): 面积计算使用的目标单位，默认为'步'。

#         返回:
#             float: 目标单位下的体积。
#         """

#         bottom_base = self.dimensions['下方'][0]
#         height = self.dimensions['高'][0]

#         bottom_base_unit = self.dimensions['下方'][1]
#         height_unit = self.dimensions['高'][1]

#         bottom_base_in_target_unit = self.convert_unit(bottom_base, bottom_base_unit, target_unit)
#         height_in_target_unit = self.convert_unit(height, height_unit, target_unit)

#         value = (bottom_base_in_target_unit * bottom_base_in_target_unit) * height_in_target_unit / 3
#         return value, target_unit

#     def __str__(self, target_unit='步'):
#         """
#         返回梯形田地的详细字符串描述，包括面积信息。

#         参数:
#             target_unit (str): 面积描述使用的单位（默认为'步'）。

#         返回:
#             str: 包括名称、尺寸和面积的详细描述。
#         """
#         area_in_target_unit = self.value(target_unit)[0]
#         return f"{self.name}，下方: {self.dimensions['下方'][0]}{self.dimensions['下方'][1]}，高: {self.dimensions['高'][0]}{self.dimensions['高'][1]}，体积: {area_in_target_unit}{target_unit}³"


# # 底面为直角三角形的直棱柱
# class 堑堵(Structure):
#     def value(self, target_unit='步'):
#         """
#         计算堑堵的体积，并以指定单位返回。

#         参数:
#             target_unit (str): 面积计算使用的目标单位，默认为'步'。

#         返回:
#             float: 目标单位下的体积。
#         """

#         bottom_base = self.dimensions['下广'][0]
#         height = self.dimensions['高'][0]
#         mao = self.dimensions['袤'][0]

#         bottom_base_unit = self.dimensions['下广'][1]
#         height_unit = self.dimensions['高'][1]
#         mao_unit = self.dimensions['袤'][1]

#         bottom_base_in_target_unit = self.convert_unit(bottom_base, bottom_base_unit, target_unit)
#         height_in_target_unit = self.convert_unit(height, height_unit, target_unit)
#         mao_in_target_unit = self.convert_unit(mao, mao_unit, target_unit)

#         value = bottom_base_in_target_unit * height_in_target_unit * mao_in_target_unit / 2
#         return value, target_unit

#     def __str__(self, target_unit='步'):
#         """
#         返回梯形田地的详细字符串描述，包括面积信息。

#         参数:
#             target_unit (str): 面积描述使用的单位（默认为'步'）。

#         返回:
#             str: 包括名称、尺寸和面积的详细描述。
#         """
#         area_in_target_unit = self.value(target_unit)[0]
#         return f"{self.name}，下广（下底）: {self.dimensions['下广'][0]}{self.dimensions['下广'][1]}，高: {self.dimensions['高'][0]}{self.dimensions['高'][1]}，袤（棱柱的高）: {self.dimensions['袤'][0]}{self.dimensions['袤'][1]}，体积: {area_in_target_unit}{target_unit}³"


# class 馀1(Structure):
#     def value(self, target_unit=None):
#         """
#         计算列表中所有数值的总和。
#
#         返回:
#             float: 列表中所有数值的总和。
#         """
#         first = self.dimensions['量纲量'][0]
#         second = self.dimensions['无量纲量'][0]
#
#         return first - second, target_unit
#
#     def __str__(self):
#         """
#         返回一个描述此类及其计算的总和的详细字符串。
#
#         返回:
#             str: 包含初始化的数值列表和计算的总和的详细描述。
#         """
#         # 调用求和方法，获取总和
#         different = self.value()
#         # 格式化字符串，展示类的内容
#         return f"{self.name}，第一个数: {self.dimensions['无量纲量'][0]}，第二个数: {self.dimensions['无量纲量1'][0]}，馀（差）: {different}"


# 通过名字找对应的计算函数
total_types = {
    '田': 田,
    '圭田': 圭田,
    '邪田': 邪田,
    '箕田': 箕田,
    '圆田': 圆田,
    '宛田': 宛田,
    '弧田': 弧田,
    '环田': 环田,
    # '合之': 合之,
    # '馀': 馀,
    "城": 城,
    "垣": 垣,
    "堤": 堤,
    "沟": 沟,
    "聢": 聢,
    "渠": 渠,
    "堑": 堑,
    "仓": 仓,
    "方堡壔": 方堡壔,
    "圆堡壔": 圆堡壔,
    "方亭": 方亭,
    "圆亭": 圆亭,
    "圆锥": 圆锥,
    "方锥": 方锥,
    "堑堵": 堑堵,
    "穿渠": 穿渠,
    "曲池": 曲池,
    "冥谷": 冥谷,
    "盘池": 盘池,
    "刍童": 刍童,
    "阳马": 阳马,
    "鳖臑": 鳖臑,
    "羡除": 羡除,
    "刍甍": 刍甍,
    "圆困": 圆困,
    "委粟平地": 委粟平地,
    "委菽依垣": 委菽依垣,
    "委米依垣内角": 委米依垣内角,

    # '馀1': 馀1,
}

texts = [
    # "今有圭田广十二步，正从二十一步。问为田几何？",
    # "又有九分之八，七分之六。问孰多，多几何？",
    # "今有堑堵下广二丈，袤一十八丈，高二丈。问积几何？",
    # "今有城下广四丈，上广二丈，高五丈，袤一百二十六丈。问积几何？",
    # "今有田广九亿零八百七十六万五千四百三十二步，从八亿八千万零一千零三步。问为田几何？",
    # "又有田广十二步，从十四步。问为田几何？",
    # "今有田广一里，从六百步。问为田几何？",
    # "又有三步，减其二。问馀几何？",
    # "又有三步，减其二。问合之得几何？",
    # "又有田广二里，从三里。问为田几何？",
    # "今有十八分之十二。问约之得几何？",
    # "又有九十一分之四十九。问约之得几何？",
    # "今有三分之一，五分之二。问合之得几何？",
    # "又有三分之二，七分之四，九分之五。问合之得几何？",
    # "又有二分之一，三分之二，四分之三，五分之四。问合之得几何？",
    # "今有九分之八，减其五分之一。问馀几何？",
    # "又有四分之三，减其三分之一。问馀几何？",
    # "今有八分之五，二十五分之十六。问孰多？多几何？",
    # "又有九分之八，七分之六。问孰多？多几何？",
    # "又有二十一分之八，五十分之十七。问孰多？几何？",
    # "今有三分之一，三分之二，四分之三。问减多益少，各几何而平？",
    # "又有二分之一，三分之二，四分之三。问减多益少，各几何而平？",
    # "今有七人，分八钱三分钱之一。问人得几何？",
    # "又有三人，三分人之一，分六钱三分钱之一，四分钱之三。问人得几何？",
    # "今有田广七分步之四，从五分步之三。问为田几何？",
    # "又有田广九分步之七，从十一分步之九。问为田几何？",
    # "又有田广五分步之四，从九分步之五，问为田几何？",
    # "今有田广三步、三分步之一，从五步、五分步之二。问为田几何？",
    # "又有田广七步、四分步之三，从十五步、九分步之五。问为田几何？",
    # "又有田广十八步、七分步之五，从二十三步、十一分步之六。问为田几何？",
    # "今有圭田广十二步，正从二十一步。问为田几何？",
    # "又有圭田广五步、二分步之一，从八步、三分步之二。问为田几何？",
    # "今有宛田，下周三十步，径十六步。问为田几何？",
    # "又有宛田，下周九十九步，径五十一步。问为田几何？",
    # "今有邪田，一头广三十步，一头广四十二步，正从六十四步。问为田几何？",
    # "又有邪田，正广六十五步，一畔从一百步，一畔从七十二步。问为田几何？",
    # "今有箕田，舌广二十步，踵广五步，正从三十步。问为田几何？",
    # "又有箕田，舌广一百一十七步，踵广五十步，正从一百三十五步。问为田几何？",
    # "今有圆田，周三十步，径十步。问为田几何？",
    # "今有弧田，弦三十步，矢十五步。问为田几何？",
    # "又有弧田，弦七十八步、二分步之一，矢十三步、九分步之七。问为田几何？",
    # "今有环田，中周九十二步，外周一百二十二步，径五步。问为田几何？"
]

# 对象初始化
lexer = Lexer()

# Call the function to tokenize the provided texts
# Processing all provided texts类中调用，文本处理
results = lexer.tokenize_texts(texts)

# 输出token结果
lexer.format_and_display_results(results)
# token对象的打印
print(results)

# 打印传递给parser的列表，字符type传递
token_types = lexer.extract_token_types(results)
print("token_types = ", token_types)

# 打印传递给parser的列表，value的传递
token_value = lexer.extract_values(results)
print("token_value = ", token_value)

lexer.add_tokens_to_symbol_table(results)

# 调用 print_symbols 方法来打印符号表中的所有符号及其详细信息
lexer.symbol_table.print_symbols()

# tem1 = lexer.symbol_table.get_symbol('广')
# tem2 = lexer.symbol_table.get_symbol('从')
# print(tem1)
# print(tem2)
print("-----------------")
# rect_field = 田("田", {lexer.symbol_table.get_symbol('广')['type']: [lexer.symbol_table.get_symbol('广')['value'], lexer.symbol_table.get_symbol('广')['unit']], lexer.symbol_table.get_symbol('从')['type']: [lexer.symbol_table.get_symbol('从')['value'], lexer.symbol_table.get_symbol('从')['unit']]})
# rect_field = 圭田("圭田", {lexer.symbol_table.get_symbol('广')['type']: [lexer.symbol_table.get_symbol('广')['value'], lexer.symbol_table.get_symbol('广')['unit']], lexer.symbol_table.get_symbol('正从')['type']: [lexer.symbol_table.get_symbol('正从')['value'], lexer.symbol_table.get_symbol('正从')['unit']]})
# rect_field = 邪田("邪田", {lexer.symbol_table.get_symbol('头广')['type']: [lexer.symbol_table.get_symbol('头广')['value'], lexer.symbol_table.get_symbol('头广')['unit']], lexer.symbol_table.get_symbol('头广1')['type']: [lexer.symbol_table.get_symbol('头广1')['value'], lexer.symbol_table.get_symbol('头广1')['unit']], lexer.symbol_table.get_symbol('正从')['type']: [lexer.symbol_table.get_symbol('正从')['value'], lexer.symbol_table.get_symbol('正从')['unit']]})
# rect_field = 箕田("箕田", {lexer.symbol_table.get_symbol('舌广')['type']: [lexer.symbol_table.get_symbol('舌广')['value'], lexer.symbol_table.get_symbol('舌广')['unit']], lexer.symbol_table.get_symbol('踵广')['type']: [lexer.symbol_table.get_symbol('踵广')['value'], lexer.symbol_table.get_symbol('踵广')['unit']], lexer.symbol_table.get_symbol('正从')['type']: [lexer.symbol_table.get_symbol('正从')['value'], lexer.symbol_table.get_symbol('正从')['unit']]})
# rect_field = 圆田("圆田", {lexer.symbol_table.get_symbol('周')['type']: [lexer.symbol_table.get_symbol('周')['value'], lexer.symbol_table.get_symbol('周')['unit']], lexer.symbol_table.get_symbol('径')['type']: [lexer.symbol_table.get_symbol('径')['value'], lexer.symbol_table.get_symbol('径')['unit']]})
# rect_field = 宛田("宛田", {lexer.symbol_table.get_symbol('下周')['type']: [lexer.symbol_table.get_symbol('下周')['value'], lexer.symbol_table.get_symbol('下周')['unit']], lexer.symbol_table.get_symbol('径')['type']: [lexer.symbol_table.get_symbol('径')['value'], lexer.symbol_table.get_symbol('径')['unit']]})
# rect_field = 弧田("弧田", {lexer.symbol_table.get_symbol('弦')['type']: [lexer.symbol_table.get_symbol('弦')['value'], lexer.symbol_table.get_symbol('弦')['unit']], lexer.symbol_table.get_symbol('矢')['type']: [lexer.symbol_table.get_symbol('矢')['value'], lexer.symbol_table.get_symbol('矢')['unit']]})
# rect_field = 环田("环田", {lexer.symbol_table.get_symbol('中周')['type']: [lexer.symbol_table.get_symbol('中周')['value'], lexer.symbol_table.get_symbol('中周')['unit']], lexer.symbol_table.get_symbol('外周')['type']: [lexer.symbol_table.get_symbol('外周')['value'], lexer.symbol_table.get_symbol('外周')['unit']], lexer.symbol_table.get_symbol('径')['type']: [lexer.symbol_table.get_symbol('径')['value'], lexer.symbol_table.get_symbol('径')['unit']]})

# 查symbol_table对构造类型的type进行计算
process_symbols_based_on_type(lexer)

# area_result = lexer.symbol_table.execute_function_by_type("邪田")
# if area_result:
#     area, unit = area_result
#     print(f"计算的面积: {area} {unit}²")
#     # 更新符号表中的数据
#     lexer.symbol_table.update_symbol('田', area, unit)
# else:
#     print("没有找到类型对应的符号或函数。")


# print(rect_field.area('尺'))  # Output area in '尺'
# print(rect_field.area('步'))  # Output area in '步'
# print(rect_field.area('里'))  # Output area in '里'

# print(rect_field.__str__('步'))  # String representation with area in '里'
# a,b=rect_field.area('步')
# print(a,b)


# 更新type的值和单位
# lexer.symbol_table.get_symbol('田')['value'], lexer.symbol_table.get_symbol('田')['unit'] = rect_field.area('步')
lexer.symbol_table.print_symbols()

# 获取最后的symbol的代码调用
last_symbol = lexer.symbol_table.get_last_symbol()
print("last_symbol = ", last_symbol)

# 接入前端代码
# 初始化 Flask 应用
app = Flask(__name__)

from flask import g


# Flask 路由，用于接收问题并返回处理后的答案
@app.route('/process_question', methods=['POST'])
def process_question():
    # 获取请求中的问题文本
    question_text = request.json.get('question_text')
    if not question_text:
        return jsonify({'error': 'No question provided'}), 400

    # 处理问题文本，存储结果
    get_question(question_text)

    # 生成并返回答案
    answer = push_lexer_result()
    return jsonify({'answer': answer})


def get_question(question_text):
    # 使用 Lexer 实例的 tokenize 方法处理文本，并将结果存储在 g 对象中
    tokens = lexer.tokenize(question_text)
    token_types = lexer.extract_token_types(tokens)
    token_values = lexer.extract_values(tokens)
    g.tokens = tokens
    return token_types, token_values


def push_lexer_result():
    # 从 g 对象获取处理结果
    tokens = getattr(g, 'tokens', None)
    if tokens:
        i = 1
        formatted_answer = '\n'
        for token in tokens:
            s = '%d:  类型: %s, 值: %s\n' % (i, token.type, token.value)
            formatted_answer = formatted_answer + s
            i += 1
        # 格式化处理结果，以字符串的形式返回
        # formatted_answer = ''.join([f"类别='{token.type}',     值='{token.value}'\n" for token in tokens])
    else:
        formatted_answer = "No question processed."
    print(formatted_answer)
    return formatted_answer
