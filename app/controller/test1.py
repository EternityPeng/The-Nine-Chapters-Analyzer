class SymbolTable:
    def __init__(self):
        # 使用字典来存储符号及其属性
        self.symbols = {}

    def add_symbol(self, name, type, value, unit):
        """
        添加一个符号到符号表中，如果符号已存在，则修改名字使其唯一。

        参数:
            name (str): 单位的名称或标识符。
            unit (str): 单位的描述或类型。
            value (float): 与单位相关联的数值。
        """
        unique_name = self.generate_unique_name(type)
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

    def get_symbol(self, name):
        """
        从符号表中检索一个单位符号的信息。

        参数:
            name (str): 要检索的单位的名称或标识符。

        返回:
            dict: 检索到的单位符号的信息，如果不存在则返回 None。
        """
        return self.symbols.get(name)

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

    def print_symbols(self):
        """
        打印符号表中所有单位符号的详细信息。
        """
        if not self.symbols:
            print("Symbol table is empty.")
            return
        for name, info in self.symbols.items():
            print(f"Name: {info['name']}, Type: {info['type']}, Value: {info['value']}, Unit: {info['unit']}")

    def execute_function_by_type(self, type, unit='步'):
        """
        从function_type计算target这个结果
        """
        if type in total_types:
            print("获取类型:", type)
            # 假设每种类型都需要一组特定的维度键来实例化
            dimensions_needed = {
                '圭田': ['广', '正从', '田'],

                # '田': ['广', '从'],
                # '邪田': ['头广', '头广1', '正从'],
                # '箕田': ['舌广', '踵广', '正从'],
                # '圆田': ['周', '径'],
                # '宛田': ['下周', '径'],
                # '弧田': ['弦', '矢'],
                # '环田': ['中周', '外周', '径'],
                # '合之': ['无量纲量', '无量纲量1'],
                # '合之': ['量纲量', '无量纲量'],
                # '馀': ['无量纲量', '无量纲量1'],
                # '馀': ['量纲量', '无量纲量'],
                # '城': ['上广', '下广', '高', '袤'],
                # '垣': ['上广', '下广', '高', '袤'],
                # '堤': ['上广', '下广', '高', '袤'],
                # '沟': ['上广', '下广', '深', '袤'],
                # '聢': ['上广', '下广', '深', '袤'],
                # '穿渠': ['上广', '下广', '深', '袤'],
                # '渠': ['上广', '下广', '深', '袤'],
                # '堑': ['上广', '下广', '深', '袤'],
                # '方堡壔': ['方', '高'],
                # '圆堡壔': ['周', '高'],
                # '方亭': ['上方', '下方', '高'],
                # '圆亭': ['上周', '下周', '高'],
                # '圆锥': ['下周', '高'],
                # '方锥': ['下方', '高'],
                # '堑堵': ['下广', '袤', '高'],
                # '阳马': ['广', '袤', '高'],
                # '刍童': ['上广', '下广', '上袤', '下袤', '高'],
                # '曲池': ['上中周', '下中周', '外周', '上袤', '下袤', '上广', '下广', '高'],
                # '盘池': ['上广', '下广', '上袤', '下袤', '深'],
                # '冥谷': ['上广', '下广', '上袤', '下袤', '深'],
                # '鳖臑': ['下广', '上袤', '高'],
                # '羡除': ['上广', '下广', '末广', '深', '袤'],
                # '刍甍': ['下袤', '上袤', '下广', '高'],
                # '仓': ['广', '高', '袤'],
                # '圆困': ['周', '高'],
                # '委粟平地': ['下周', '高'],
                # '委菽依垣': ['下周', '高'],
                # '委米依垣内角': ['下周', '高'],
                # '''
                # '方': ['积'],# 面积 diifferent
                # '圆周':['积'],# 面积
                # '立方':['积'],# 体积
                # '立圆径':['积'],# 体积
                # '''
                # '弦': ['勾', '股', '弦'],
                # '勾': ['勾', '股', '弦'],
                # '股': ['勾', '股', '弦'],
                # # '穿地 坚 壤':[],'粟|粝米|粺米|绺米|御米|小䵂|大䵂|粝饭|粺饭|绺饭|御饭|菽|答|麻|麦|稻|豉|飧|熟菽|櫱|米'
                # # Add other mappings as needed
            }
            dimensions = {}
            # 检查该类型是否在所需维度的列表中
            if type in dimensions_needed:
                # 根据key和type对应，从列表中找到对应的元素
                for dimension in dimensions_needed[type]:
                    symbol = self.get_symbol(dimension)
                    print("symbol = ", symbol)
                    if symbol:
                        dimensions[dimension] = (symbol['value'], symbol['unit'])
                    else:
                        print(f"警告: 找不到必要的维度 '{dimension}'")
                        return None
                print("type = ", type)
                print("dimensions = ", dimensions)
                # 生成该类型的实例并计算面积
                instance = total_types[type](type, dimensions)
                print("instance = ", instance)
                # print(f"创建的 {type} 实例: {instance}")
                print("instance_value = ", instance.value(unit))
                return instance.value(unit)
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

class UnitConversion:
    # 单位转换率，基准单位为 '里'
    # 1 顷 = 100 亩
    # 1 亩 = 240（平方）步 = 6 ^ 2 * 240 （平方)）尺
    CONVERSION_RATES = {
        '里': 1 / 300 * 240,
        '匹': 45 / 300 * 240,
        '丈': 180 / 300 * 240,
        '步': 300 / 300 * 240, # 1 亩 = 240（平方）步 可以类比
        '尺': 1800 / 300 * 240,
        '寸': 18000 / 300 * 240,

        '顷': 1 / 100,
        '亩': 1,
        '平方里': 240 * (1 / 300) * (1 / 300),
        '平方匹': 240 * (45 / 300) * (45 / 300),
        '平方丈': 240 * (180 / 300) * (180 / 300),
        '平方步': 240,
        '平方尺': 240 * (1800 / 300) * (1800 / 300),
        '平方寸': 240 * (18000 / 300) * (18000 / 300),

        '立方里': (1 / 300) * (1 / 300) * (1 / 300),
        '立方匹': (45 / 300) * (45 / 300) * (45 / 300),
        '立方丈': (180 / 300) * (180 / 300) * (180 / 300),
        '立方步': 1,
        '立方尺': (1800 / 300) * (1800 / 300) * (1800 / 300),
        '立方寸': (18000 / 300) * (18000 / 300) * (18000 / 300),

        '斛': 1,
        '斗': 10,
        '升': 100,

        '石': 1,
        '钧': 4,
        '斤': 120,
        '两': 1920,
        '铢': 46080,
        # 可以添加更多的单位换算关系
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
    def find_smallest_unit_symbol(cls, symbols):
        """
        在给定的符号列表中找出具有最小转换率单位的符号。

        参数:
            symbols (list of dict): 包含符号信息的列表，每个符号字典至少包含 'unit' 键。

        返回:
            dict: 转换率最小的符号字典，如果列表为空或没有有效的单位，则返回 None。
        """
        smallest_symbol = None
        # 如果找最小的就需要把初始的变为0
        smallest_conversion_rate = 0

        for symbol in symbols:
            unit = symbol.get('unit')
            print("!!!unit!!! = ", unit)
            if unit in cls.CONVERSION_RATES:
                conversion_rate = cls.CONVERSION_RATES[unit]
                print("!!!conversion_rate!!! = ", conversion_rate)
                # 应该是数值取大的，因为一个数值小的换一个大的，单位就是相反
                if conversion_rate >= smallest_conversion_rate:
                    smallest_conversion_rate = conversion_rate
                    smallest_symbol = symbol
                    print("!!!smallest_symbol!!! = ", smallest_symbol)

        return smallest_symbol

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


class 圭田(Structure):
    def __init__(self, name, dimensions):
        super().__init__(name, dimensions)

    def value(self, target_unit='步'):
        """
        根据提供的参数计算缺失的尺寸或面积。

        参数:
            target_unit (str): 计算结果的单位，默认为'步'。

        返回:
            float: 缺失参数的计算值，以指定的单位返回。
        """
        # 检查哪个参数缺失，并计算它
        if self.dimensions['广'][0] is None and self.dimensions['广'][1] is None:
            # 缺少底，已知面积和高
            area = self.dimensions['田'][0]
            area_unit = self.dimensions['田'][1]
            height = self.dimensions['正从'][0]
            height_unit = self.dimensions['正从'][1]

            area_in_target_unit = self.convert_unit(area, area_unit, target_unit)
            height_in_target_unit = self.convert_unit(height, height_unit, target_unit)

            base = (2 * area_in_target_unit) / height_in_target_unit
            return base, target_unit  # 计算底的长度

        elif self.dimensions['正从'][0] is None and self.dimensions['正从'][1] is None:
            # 缺少高，已知面积和底
            area = self.dimensions['田'][0]
            area_unit = self.dimensions['田'][1]
            base = self.dimensions['广'][0]
            base_unit = self.dimensions['广'][1]

            area_in_target_unit = self.convert_unit(area, area_unit, target_unit)
            base_in_target_unit = self.convert_unit(base, base_unit, target_unit)

            height = (2 * area_in_target_unit) / base_in_target_unit

            return height, target_unit  # 计算高的长度

        elif self.dimensions['田'][0] is None and self.dimensions['田'][1] is None:
            # 缺少面积，已知底和高
            base = self.dimensions['广'][0]
            base_unit = self.dimensions['广'][1]
            height = self.dimensions['正从'][0]
            height_unit = self.dimensions['正从'][1]

            base_in_target_unit = self.convert_unit(base, base_unit, target_unit)
            height_in_target_unit = self.convert_unit(height, height_unit, target_unit)

            area = 0.5 * base_in_target_unit * height_in_target_unit
            return area, target_unit  # 计算面积

# 通过名字找对应的计算函数
total_types = {
    # '田': 田,
    '圭田': 圭田,
    # '邪田': 邪田,
    # '箕田': 箕田,
    # '圆田': 圆田,
    # '宛田': 宛田,
    # '弧田': 弧田,
    # '环田': 环田,
    # '合之': 合之,
    # '馀': 馀,
    # "垣": 垣,
    # "堤": 堤,
    # "沟": 沟,
    # "聢": 聢,
    # "渠": 渠,
    # "堑": 堑,
    # "方堡嶹": 方堡嶹,
    # "圆堡嶹": 圆堡嶹,
    # "方亭": 方亭,
    # "圆亭": 圆亭,
    # "圆锥": 圆锥,
    # "方锥": 方锥,
    # "堑堵": 堑堵
    # '馀1': 馀1,
}


# Example Usage
symbol_table = SymbolTable()

symbol_table.add_symbol("面积", "圭田", None, None)
symbol_table.add_symbol("长度", "广", 2, "步")
# symbol_table.add_symbol("长度", "广", 21, "步")
symbol_table.add_symbol("面积", "田", 20, "步")
symbol_table.add_symbol("长度", "正从", None, None)


# 当前自底向上的读到的值
target = "正从"

function_type = symbol_table.get_types_needing_processing()
print("function_type = ", function_type[0])

function_type = function_type[0]
function_symbol = symbol_table.get_symbol(str(function_type))

print()
for i,j in symbol_table.symbols.items():
    print(i,j)

print()
symbol_table.print_symbols()

print()
symbol_1 = symbol_table.get_symbol("广")
print("symbol_1 = ", symbol_1)

print()
# 从function_type计算target这个结果
symbol_table.execute_function_by_type(function_type, "步")