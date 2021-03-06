from code import InteractiveConsole
from pyparsing import srange, Word, quotedString
import re
import sys
import traceback

关键字词典 = {
    "如果":"if",
    "否则":"else",
    "定义":"def",
    "尝试":"try",
    "善后":"finally",
    "提出":"raise",
    "捕获":"except",
    "返回":"return",
    "打印":"print"
}

def 关键字替换(原字符串, 位置, token):
    字段 = token[0]
    if 字段 in 关键字词典:
        return 关键字词典[字段]
    else:
        return 字段

中文字符 = srange(r"[\0x0080-\0xfe00]")
中文词汇 = Word(中文字符)
中文词汇.setParseAction(关键字替换)

python词 = quotedString | 中文词汇

class 中文报错控制台(InteractiveConsole):
    """
    封装Python控制台, 对输出进行转换
    """
    字典 = {
        r"Traceback \(most recent call last\):": r"回溯 (最近的调用在最后):",
        r"AttributeError: '(.*)' object has no attribute '(.*)'": r"属性错误: '\1'个体没有'\2'属性",
        r"NameError: name '(.*)' is not defined": r"命名错误: 命名'\1'未定义",
        r"NameError: free variable '(.*)' referenced before assignment in enclosing scope": r"命名错误: 在闭合作用域中, 自由变量'\1'在引用之前未被赋值",
        r"SyntaxError: invalid syntax": r"语法错误: 不正确的语法",
        r"TypeError: unsupported operand type\(s\) for /: '(.*)' and '(.*)'": r"类型错误: 不支持/的操作数: '\1'和'\2'",
        r"TypeError: unsupported operand type\(s\) for \*\* or pow\(\): '(.*)' and '(.*)'": r"类型错误: 不支持**或pow()的操作数: '\1'和'\2'",
        r"TypeError: can't multiply sequence by non-int of type '(.*)'": r"类型错误: 不能用非整数的类型--'\1'对序列进行累乘",
        r'TypeError: can only concatenate list \(not "(.*)"\) to list': r'类型错误: 只能将list(而非"\1")联结到list',
        r"TypeError: must be str, not int": r"类型错误: 不能将整数自动转换为字符串",
        r"UnboundLocalError: local variable '(.*)' referenced before assignment": r"本地变量未定义错误: 本地变量'\1'在引用之前未被赋值",
        r"ZeroDivisionError: division by zero": r"除零错误: 不能被0除",
        }

    # 由InteractiveConsole.showsyntaxerror源码改写
    def showsyntaxerror(self, filename=None):
        type, value, tb = sys.exc_info()
        sys.last_type = type
        sys.last_value = value
        sys.last_traceback = tb
        if filename and type is SyntaxError:
            # Work hard to stuff the correct filename in the exception
            try:
                msg, (dummy_filename, lineno, offset, line) = value.args
            except ValueError:
                # Not the format we expect; leave it alone
                pass
            else:
                # Stuff in the right filename
                value = SyntaxError(msg, (filename, lineno, offset, line))
                sys.last_value = value
        if sys.excepthook is sys.__excepthook__:
            行 = traceback.format_exception_only(type, value)
            汉化行 = []
            for 某行 in 行:
                汉化行.append(self.中文化(某行))
            self.write(''.join(汉化行))
        else:
            # If someone has set sys.excepthook, we let that take precedence
            # over self.write
            sys.excepthook(type, value, tb)

    # 由InteractiveConsole.showtraceback源码改写
    def showtraceback(self):
        sys.last_type, sys.last_value, 回溯信息 = 运行信息 = sys.exc_info()
        sys.last_traceback = 回溯信息
        try:
            行 = traceback.format_exception(运行信息[0], 运行信息[1], 回溯信息.tb_next)
            汉化行 = []
            if sys.excepthook is sys.__excepthook__:
                for 某行 in 行:
                    汉化行.append(self.中文化(某行))
                self.write(''.join(汉化行))
            else:
                # If someone has set sys.excepthook, we let that take precedence
                # over self.write
                sys.excepthook(运行信息[0], 运行信息[1], 回溯信息)
        finally:
            回溯信息 = 运行信息 = None

    # 参考: https://docs.python.org/3/library/re.html#re.sub
    def 中文化(self, 原始信息):
        for 英文模式 in self.字典:
            if re.match(英文模式, 原始信息):
                return re.sub(英文模式, self.字典[英文模式], 原始信息)
        return 原始信息

    def 转换(self, 中文代码):
        return python词.transformString(中文代码)

    def push(self, 行):
        self.buffer.append(行)
        源码 = "\n".join(self.buffer)
        #windows patch
        编码 = sys.stdout.encoding
        if 编码 == 'cp950':
            编码 = ''

        more = self.runsource(self.转换(源码), self.filename)
        if not more:
            self.resetbuffer()
        return more

def 解释器(lang=None):
    """
    zhpy解释器
    """
    控制台 = 中文报错控制台()
    控制台.interact()

if __name__=="__main__":
    解释器()