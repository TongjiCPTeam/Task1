# 语法分析和中间代码生成
# 实现了一个递归下降解析器，用于解析PL/0语法

import sys
import cgg_lex as l

# '指针'是从词法分析模块导入的句子的索引
# 从词法分析模块导入的句子的索引。调用 getSen()方法对其进行设置
# 全局变量定义：
sentence = []  # 从词法分析模块导入的语句
pointer = 0    # 语句中的索引
has_error = False  # 错误标志
cutoff = False     # 是否关闭调试功能的标志

symbol_table = {}  # 符号表
quate_list = []    # 四元式列表
output_fp = None   # 输出文件指针
used_temp_index = 0 # 用于生成临时变量名的索引（如T0, T1, T2...）
output_line_no = 1  # 输出行号
saved_line = 1      # 保存的行号，用于while循环
refill_line = 1     # 需要回填的行号

# 定义一些语义动作的函数：
def match(symName):
    """
    匹配刚读入的符号并打印成功消息。
    如果cutoff为True，则输出信息可以被封闭。
    """
    global pointer
    global cutoff
    pointer += 1
    if not cutoff:
        print("匹配 " + symName + "，指针移动到 %s" % sentence[pointer][0])

def during(funcName):
    """
    在执行特定函数时打印调试信息。
    """
    global pointer
    global cutoff
    if not cutoff:
        print("正在执行 " + funcName + "，指针位于 %s" % sentence[pointer][0])

def error(info):
    """
    输出语法错误信息并退出程序。
    """
    global has_error
    has_error = True
    print("语法错误: " + info)
    sys.exit()

def getSym():
    """
    获取当前指针指向的符号。
    """
    global pointer
    return sentence[pointer][0]

def getVal():
    """
    获取当前指针指向的符号的值。
    """
    global pointer
    return sentence[pointer][1]

# 从源文件获取整个语句
def getSen():
    global sentence
    sentence = l.resList
    sentence.append(("EOF", None))  # 防止索引越界

def append(name, value):
    """
    在符号表中添加一个条目。
    """
    symbol_table[name] = value

def entry(name):
    """
    返回给定名称在符号表中的索引。
    """
    return name

def openOut():
    """
    打开输出文件。
    """
    global output_fp
    output_fp = open("test.out", 'w')

def closeOut():
    """
    关闭输出文件。
    """
    global output_fp
    output_fp.close()

def save_point():
    """
    保存当前输出行号。
    """
    global output_line_no
    global saved_line
    saved_line = output_line_no

def getSavedPoint():
    """
    获取保存的行号。
    """
    global saved_line
    return saved_line

def save_refill():
    """
    保存需要回填的行号。
    """
    global output_line_no
    global refill_line
    refill_line = output_line_no

def refill():
    """
    使用当前行号回填之前保存的行号。
    """
    global output_line_no
    global refill_line
    temp = quate_list[refill_line-1]
    quate_list[refill_line-1] = (temp[0], temp[1], temp[2], temp[3], output_line_no)

# 生成新的临时变量名，并将其添加到符号表中
def newTemp():
    global used_temp_index
    used_temp_index += 1
    name = '#TEMP' + str(used_temp_index)
    append(name, None)
    return name

def gen(op, arg1, arg2, result):
    """
    生成四元式并添加到四元式列表中。
    """
    global output_line_no
    quate_list.append((output_line_no, op, arg1, arg2, result))
    output_line_no += 1

def gen2(op, arg1, arg2, offset):
    """
    生成具有跳转功能的四元式。
    """
    global output_line_no
    jump_to = output_line_no + offset
    quate_list.append((output_line_no, op, arg1, arg2, jump_to))
    output_line_no += 1

def outPutQuate():
    """
    将四元式列表输出到文件。
    """
    for line in quate_list:
        output_fp.write(str(line[0]) + ": (" + str(line[1]) + ", " + str(line[2]) + ", " + str(line[3]) + ", " + str(line[4]) + ")\n")

# PL/0语言的EBNF描述如下：
"""
program	= block "."

	block	= [ CONST "ident" = "number" { "," ident "=" "number" } ";" ]
			  [ VAR "ident" { "," "ident" ";"}
			  { PROCEDURE "ident" ";" block ";"}
			  statement
	
	statement = [ CALL "ident" |
				  BEGIN statement { ";" statement } END |
				  IF condition THEN statement |
				  WHILE condition DO statement |
				  "ident" ":=" expresssion ]
	
	condition = ODD expression | 
				expression ( "=" | "#" | "<" | "<=" | ">" | ">=" ) expression

	expression = [ "+" | "-" ] term { ( "+" | "-" ) term }

	term = factor { ( "*" | "/") factor }

	factor = "ident" | "number" | "(" expression ")"
"""

# 对PL/0语法中每个非终结符的具体处理函数
# program 函数：对应PL/0语法中的 "program" 非终结符
def program():
    during("program()")
    if getSym() == "PROGRAM":
        match("PROGRAM")  # 匹配并跳过 "PROGRAM" 关键字
        if getSym() == "ident":
            match("ident")    # 如果紧跟着的是标识符，则匹配并跳过程序名称
    block()             # 继续解析程序主体
    if getSym() == ".":
        match(".")       # 匹配程序末尾的 "."
        print("程序解析完成！")
    else:
        error("程序的末尾缺少 '.'。")

# block 函数：对应PL/0语法中的 "block" 非终结符
def block():
    during("block()")

    # 常量定义区域
    if getSym() == "CONST":
        match("CONST")
        if getSym() == "ident":
            id = getVal()
            match("ident")
            if getSym() == "=":
                match("=")
                if getSym() == "const":
                    val = getVal()
                    match("const")
                    append(id, val) # 将常量添加到符号表
                else:
                    error("在 '=' 之后缺少数字。")
                while getSym() == ",":
                    match(",")
                    if getSym() == "ident":
                        id = getVal()
                        match("ident")
                        if getSym() == "=":
                            match("=")
                            if getSym() == "const":
                                val = getVal()
                                match("const")
                                append(id, val) # 将常量添加到符号表
                            else:
                                error("在 '=' 之后缺少数字。")
                        else:
                            error("在常量声明中缺少 '='。")
                if getSym() == ";":
                    match(";")
                else:
                    error("在 CONST 声明后忘记了 ';'。")
            else:
                error("在常量声明中缺少 '='。")
        else:
            error("在 CONST 声明中缺少标识符。")

    # 变量定义区域
    if getSym() == "VAR":
        match("VAR")
        if getSym() == "ident":
            id = getVal()
            match("ident")
            append(id, 0) # 将变量添加到符号表
            while getSym() == ",":
                match(",")
                if getSym() == "ident":
                    id = getVal()
                    match("ident")
                    append(id, 0) # 将变量添加到符号表
                else:
                    error("在 VAR 声明中缺少标识符。")
            if getSym() == ";":
                match(";")
            else:
                error("在 VAR 声明后忘记了 ';'。")
        else:
            error("在 VAR 声明中缺少标识符。")

    # 过程定义区域
    while getSym() == "PROCEDURE":
        match("PROCEDURE")
        if getSym() == "ident":
            match("ident")
            if getSym() == ";":
                match(";")
                block()
                if getSym() == ";":
                    match(";")
                else:
                    error("在过程体后缺少 ';'。")
            else:
                error("在 PROCEDURE 声明后忘记了 ';'。")
        else:
            error("在定义 PROCEDURE 时缺少标识符。")

    # 语句区域
    statement()
    return

# statement 函数：对应PL/0语法中的 "statement" 非终结符
def statement():
    during("statement()")

    # 处理 CALL 语句
    if getSym() == "CALL":
        match("CALL")
        if getSym() == "ident":
            match("ident")
            return
        else:
            error("在 'CALL' 后缺少标识符。")

    # 处理 BEGIN...END 语句
    if getSym() == "BEGIN":
        match("BEGIN")
        statement()

        while getSym() == ";":
            match(";")
            statement()

        if getSym() == "END":
            match("END")
            return
        else:
            error("在 'BEGIN...END' 语句中缺少 'END'。")

    # 处理 IF...THEN... 语句
    if getSym() == "IF":
        match("IF")
        condition()
        if getSym() == "THEN":
            match("THEN")
            statement()
            return
        else:
            error("在 'IF...THEN' 语句中缺少 'THEN'。")

    # 处理 WHILE...DO... 语句
    if getSym() == "WHILE":
        match("WHILE")
        save_point()   # 保存条件位置，以便返回
        place1 = condition()  # 获取条件的结果：true/false
        save_refill() # 记住这一行，我们将在 while...do 的最后一行回填 0
        gen("je", place1, "_", "0") # 跳出 while...do
        if getSym() == "DO":
            match("DO")
            statement()
            # 循环结束后，跳回条件
            gen("jmp", '_', '_', getSavedPoint())
            refill()  # 在这里回填
            return
        else:
            error("在 'WHILE...DO' 语句中缺少 'DO'。")

    # 处理赋值语句
    if getSym() == "ident":
        i = getVal()
        match("ident")
        if getSym() == ":=":
            match(":=")
            place = expression()
            gen(":=", place, "_", entry(i)) # 生成四元式
            return
        else:
            error("缺少赋值符号。")

    # 其他情况，语句可能为空
    return

# condition 函数：对应PL/0语法中的 "condition" 非终结符
def condition():
    during("condition()")
    if getSym() == "ODD":
        match("ODD")
        expression()
        return
    else:
        place1 = expression()
        if getSym() == "=":
            op = getSym()
            match("=")
        elif getSym() == "#":
            op = getSym()
            match("#")
        elif getSym() == "<":
            op = getSym()
            match("<")
        elif getSym() == "<=":
            op = getSym()
            match("<=")
        elif getSym() == ">":
            op = getSym()
            match(">")
        elif getSym() == ">=":
            op = getSym()
            match(">=")
        else:
            error("在表达式中缺少操作符（'=', '#', '<', '<=', '>', '>='）。")
        place2 = expression()
        place = newTemp()
        gen2(op, place1, place2, 3)  # nextstart + 3
        gen(":=", 0, "_", place)
        gen2("jmp", "_", "_", 2)   # nextstart + 2
        gen(":=", 1, "_", place)
        return place

# expression 函数：对应PL/0语法中的 "expression" 非终结符
def expression():
    during("expression()")
    # 如果当前符号是"+"或"-"
    if getSym() == "+" or getSym() == "-":
        if getSym() == "+":
            match("+")  # 匹配"+"
            place1 = term()  # 处理第一个项
            # 处理表达式中的后续项
            while getSym() == "+" or getSym() == "-":
                if getSym() == "+":
                    match("+")
                    place2 = term()
                    place = newTemp()  # 创建新的临时变量
                    gen('+', place1, place2, place)  # 生成加法四元式
                    return place
                else:  # 当前符号是"-"
                    match("-")
                    place2 = term()
                    place = newTemp()  # 创建新的临时变量
                    gen('-', place1, place2, place)  # 生成减法四元式
                    return place
            else:
                return place1
        else:  # 当前符号是"-"
            match("-")
            place1 = term()  # 处理第一个项
            # 处理表达式中的后续项
            while getSym() == "+" or getSym() == "-":
                if getSym() == "+":
                    match("+")
                    place2 = term()
                    place = newTemp()  # 创建新的临时变量
                    gen('+', place1, place2, place)  # 生成加法四元式
                    place_new = newTemp()
                    gen('@', place, '_', place_new)
                    return place_new
                else:  # 当前符号是"-"
                    match("-")
                    place2 = term()
                    place = newTemp()  # 创建新的临时变量
                    gen('-', place1, place2, place)  # 生成减法四元式
                    place_new = newTemp()
                    gen('@', place, '_', place_new)
                    return place_new
            else:
                return place1
    else:  # 表达式不是以"+"或"-"开始
        place1 = term()
        # 处理表达式中的后续项
        while getSym() == "+" or getSym() == "-":
            if getSym() == "+":
                match("+")
                place2 = term()
                place = newTemp()  # 创建新的临时变量
                gen('+', place1, place2, place)  # 生成加法四元式
                return place
            else:  # 当前符号是"-"
                match("-")
                place2 = term()
                place = newTemp()  # 创建新的临时变量
                gen('-', place1, place2, place)  # 生成减法四元式
                return place
        return place1

# term 函数：对应PL/0语法中的 "term" 非终结符
def term():
    during("term()")
    place1 = factor()  # 处理第一个因子
    # 处理项中的后续因子
    while getSym() == "*" or getSym() == "/":
        if getSym() == "*":
            match("*")
            place2 = factor()
            place = newTemp()  # 创建新的临时变量
            gen('*', place1, place2, place)  # 生成乘法四元式
            return place
        else:  # 当前符号是"/"
            match("/")
            place2 = factor()
            place = newTemp()  # 创建新的临时变量
            gen('/', place1, place2, place)  # 生成除法四元式
            return place
    else:
        return place1

# factor 函数：对应PL/0语法中的 "factor" 非终结符
def factor():
    during("factor()")
    # 如果当前符号是标识符
    if getSym() == "ident":
        place = entry(getVal())  # 获取标识符的值
        match("ident")
        return place
    elif getSym() == "const":  # 如果当前符号是常数
        place = entry(getVal())
        match("const")
        return place
    elif getSym() == "(":  # 如果当前符号是左括号
        match("(")
        place = expression()
        if getSym() == ")":
            match(")")
            return place  # 不生成四元式，直接返回
        else:
            error("在这个句子中缺少右括号 ')'。")
    else:
        error("因子中的语法错误。")
