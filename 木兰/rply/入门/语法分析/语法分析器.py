from rply import ParserGenerator

### 分词器部分
from rply import LexerGenerator

分词器母机 = LexerGenerator()

分词器母机.add('数', r'\d+')
分词器母机.add('加', r'\+')
分词器母机.add('减', r'-')
分词器母机.add('乘', r'\*')
分词器母机.add('除', r'/')
分词器母机.add('左括号', r'\(')
分词器母机.add('右括号', r'\)')

分词器母机.ignore(r'\s+')

分词器 = 分词器母机.build()

### 语法树部分

from rply.token import BaseBox

class 数(BaseBox):
    def __init__(self, 值):
        self.值 = 值

    def 求值(self):
        return self.值

class 二元运算符(BaseBox):
    def __init__(self, 左, 右):
        self.左 = 左
        self.右 = 右

class 加(二元运算符):
    def 求值(self):
        return self.左.求值() + self.右.求值()

class 减(二元运算符):
    def 求值(self):
        return self.左.求值() - self.右.求值()

class 乘(二元运算符):
    def 求值(self):
        return self.左.求值() * self.右.求值()

class 除(二元运算符):
    def 求值(self):
        return self.左.求值() / self.右.求值()

### 语法分析器部分

分析器母机 = ParserGenerator(
    # 所有词名
    ['数', '左括号', '右括号',
     '加', '减', '乘', '除'
    ],
    # A list of precedence rules with ascending precedence, to
    # disambiguate ambiguous production rules.
    precedence=[
        ('left', ['加', '减']),
        ('left', ['乘', '除'])
    ]
)

@分析器母机.production('表达式 : 数')
def 数表达式(片段):
    # 匹配规则右部的片段列表
    return 数(int(片段[0].getstr()))

@分析器母机.production('表达式 : 左括号 表达式 右括号')
def 括号表达式(片段):
    return 片段[1]

@分析器母机.production('表达式 : 表达式 加 表达式')
@分析器母机.production('表达式 : 表达式 减 表达式')
@分析器母机.production('表达式 : 表达式 乘 表达式')
@分析器母机.production('表达式 : 表达式 除 表达式')
def 二元运算表达式(片段):
    左 = 片段[0]
    右 = 片段[2]
    运算符 = 片段[1]
    if 运算符.gettokentype() == '加':
        return 加(左, 右)
    elif 运算符.gettokentype() == '减':
        return 减(左, 右)
    elif 运算符.gettokentype() == '乘':
        return 乘(左, 右)
    elif 运算符.gettokentype() == '除':
        return 除(左, 右)
    else:
        raise AssertionError('不应出现')

分析器 = 分析器母机.build()

print(分析器.parse(分词器.lex('1 + 1')).求值())

print(分析器.parse(分词器.lex('(1 + 2) * 3 - 4')).求值())