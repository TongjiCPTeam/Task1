# 词法分析
# 此模块提供一个函数，用于每次在解析器模块中被调用时从源代码中获取一个符号

import os
import string
import sys
import re

# 以下定义了保留字：
# 字典将保留的关键字/符号（在源代码中出现的）映射到程序的内部字符串类型
kwordDict = {
    "PROGRAM": "PROGRAM",
    "PROCEDURE": "PROCEDURE",
    "CALL": "CALL",
    "BEGIN": "BEGIN",
    "END": "END",
    "CONST": "CONST",
    "VAR": "VAR",
    "WHILE": "WHILE",
    "DO": "DO",
    "IF": "IF",
    "THEN": "THEN"
}

symDict = {
    "+": "+",
    "-": "-",
    "*": "*",
    "/": "/",
    ":=": ":=",
    "=": "=",
    "#": "#",
    ">": ">",
    ">=": ">=",
    "<": "<",
    "<=": "<=",
    "(": "(",
    ")": ")",
    ";": ";",
    ",": ",",
    ".": "."
}

srcList = []  # 源代码的内部表示形式，每个元素是源代码的一行
"""示例:

[ "VAR x, y",
  "PROCEDURE ",
  "\tBEGIN",
  "\t\tx:=x+1",
  ...
  ]

"""

resList = []  # 词法分析的结果列表
"""示例:

[ ("VAR", None),
  ("ident", "x"),
  (",", None)
  ...
  ]

"""

# 从磁盘读取源代码并将其转换为列表
def getSrc(srcPath):
    global srcList
    srcFile = open(srcPath, "r")
    srcList = srcFile.readlines()
    srcFile.close()

# 执行词法分析
def getRes():
    srcLen = len(srcList)
    lineNo = 0
    buf = ""  # 存储当前处理的行
    bufLen = 0
    now = 0  # buf中的光标位置
    errorFlag = False  # 错误标志
    strToken = ""  # 存储当前正在构建的标识符或常数

    # 主循环遍历所有行
    while True:
        if lineNo == srcLen:  # 检查是否已处理完所有行
            break
        line = srcList[lineNo]
        lineNo += 1
        if errorFlag == True:
            break

        line = line.strip()  # 去除行首尾的空白字符
        if line == "":
            continue  # 跳过空行

        buf += line
        now = 0
        bufLen = len(buf)

        # 遍历缓冲区中的字符
        while now < bufLen:
            if buf[now] == " ":  # 跳过空格
                now += 1
            elif IsLetter(buf[now]):  # 识别标识符或关键字
                strToken += buf[now]
                now += 1
                # 防止超出缓冲区
                if now == bufLen:
                    if strToken in kwordDict.keys():
                        resList.append((kwordDict[strToken], None))
                    else:
                        resList.append(("ident", strToken))
                else:
                    while IsLetter(buf[now]) or IsDigit(buf[now]):
                        strToken += buf[now]
                        now += 1
                        if now >= bufLen:
                            break # 光标超出缓冲区
                    # 判断是否为关键字
                    if strToken in kwordDict.keys():
                        resList.append((kwordDict[strToken], None))
                    else:#是一个标识符
                        resList.append(("ident", strToken))
                    strToken = "" # 在被识别后清理令牌
            elif IsDigit(buf[now]):  # 识别数字常量
                strToken += buf[now]
                now += 1
                # 防止超出缓冲区
                if now == bufLen:
                    resList.append(("const", int(strToken)))
                else:
                    while IsDigit(buf[now]):
                        strToken += buf[now]
                        now += 1
                        if now >= bufLen:
                            break # 光标超出缓冲区
                    resList.append(("const", int(strToken)))
                strToken = ""
            # 识别符号
            elif buf[now] == ":":  # since
                now += 1
                if buf[now] == "=":
                    resList.append((symDict[":="], None))
                    now += 1
                else:
                    print("LexicalError(%d): missing '=' after ':'" % lineNo)
                    errorFlag = True
            elif buf[now] == "+":
                resList.append((symDict["+"], None))
                now += 1
            elif buf[now] == "-":
                resList.append((symDict["-"], None))
                now += 1
            elif buf[now] == "*":
                resList.append((symDict["*"], None))
                now += 1
            elif buf[now] == "/":
                resList.append((symDict["/"], None))
                now += 1
            elif buf[now] == "=":
                resList.append((symDict["="], None))
                now += 1
            elif buf[now] == "#":
                resList.append((symDict["#"], None))
                now += 1
            elif buf[now] == ">":
                if now == bufLen - 1:  # ">" is at the end of buf
                    resList.append((symDict[">", None]))
                    now += 1
                else:
                    if buf[now + 1] == "=":
                        resList.append((symDict[">="], None))
                        now += 2
                    else:
                        resList.append((symDict[">"], None))
                        now += 1
            elif buf[now] == "<":
                if now == bufLen - 1:  # ">" is at the end of buf
                    resList.append((symDict["<", None]))
                    now += 1
                else:
                    if buf[now + 1] == "=":
                        resList.append((symDict["<="], None))
                        now += 2
                    else:
                        resList.append((symDict["<"], None))
                        now += 1
            elif buf[now] == "(":
                resList.append((symDict["("], None))
                now += 1
            elif buf[now] == ")":
                resList.append((symDict[")"], None))
                now += 1
            elif buf[now] == ";":
                resList.append((symDict[";"], None))
                now += 1
            elif buf[now] == ",":
                resList.append((symDict[","], None))
                now += 1
            elif buf[now] == ".":
                resList.append((symDict["."], None))
                now += 1
            # 未知字符或词法错误
            else:
                print(f"词法错误（行号：{lineNo}）")
                errorFlag = True
                break

        now = 0  # 重置缓冲区光标
        buf = ""  # 清空缓冲区

# 判断字符是否为字母
def IsLetter(ch):
	if re.match(r'[a-zA-Z]', ch):
		return True
	else:
		return False

# 判断字符是否为数字
def IsDigit(ch):
    return ch.isdigit()
