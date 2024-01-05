# 主程序

import sys
import os
import cgg_parser as p  # 导入语法分析器模块
import cgg_lex as l     # 导入词法分析器模块

# 当脚本作为主程序运行时
if __name__ == "__main__":

    # 检查命令行参数是否提供了源文件名
    if len(sys.argv) < 2:
        print("请提供源文件名！")
        sys.exit()  # 如果没有提供，则退出程序

    # 获取当前工作目录并构建源文件的完整路径
    srcPath = os.getcwd()
    srcPath += os.sep
    srcPath += sys.argv[1]

    # 从源文件获取内容
    l.getSrc(srcPath)

    # 启动词法分析器
    l.getRes()

    # 将词法分析的结果输出到文件，每个元素单独一行
    with open("lexical_analysis_result.txt", "w") as file:
        file.write("lexical_analysis_result:\n")
        for item in l.resList:
            file.write(str(item) + "\n")

    # 将词法分析的结果传递给语法分析器
    p.getSen()

    # 启动语法分析器
    p.openOut()  # 打开输出文件
    p.program()  # 开始语法分析并生成中间代码

    # 将符号表和四元式列表输出到文件
    with open("symbol_table_and_quater_list.txt", "w") as file:
        file.write("symbol_table:\n")
        for key, value in p.symbol_table.items():
            file.write(f"{key}: {value}\n")
        file.write("\nquater_list:\n")
        for item in p.quate_list:
            file.write(str(item) + "\n")

    # 输出四元式到文件
    p.outPutQuate()
    p.closeOut()  # 关闭输出文件
