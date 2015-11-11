# -*- coding:utf-8 -*-

import re
import pickle
import math

BLOCK_POSITION = 2
LOGARITHM_BASE = 2
ALPHABET = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789_'

def del_comments(code):
    is_str = False
    is_comment_two_sl = False # типа //
    is_comment_sl_ast = False # типа /**/
    comment_two_sl = []
    comment_sl_ast = []
    comments_list = [] # список с координатами начала и конца комментариев
    for i in range(len(code)):
        if not is_str and not is_comment_sl_ast and not is_comment_two_sl:
            if code[i] == "\"":
                is_str = True
            elif code[i] == "/" and code[i+1] == "/":
                is_comment_two_sl = True
                comment_two_sl.append(i)
            elif code[i] == "/" and code[i+1] == "*":
                is_comment_sl_ast = True
                comment_sl_ast.append(i)
        elif is_str:
            if code[i] == "\"" and code[i-1] != "\\":
                is_str = False
        elif is_comment_two_sl:
            if code[i] == "\n":
                is_comment_two_sl = False
                comment_two_sl.append(i)
                comments_list.append(comment_two_sl)
                comment_two_sl = []
        elif is_comment_sl_ast:
            if code[i:i+2] == "*/":
                is_comment_sl_ast = False
                comment_sl_ast.append(i+2)
                comments_list.append(comment_sl_ast)
                comment_sl_ast = []
    comments_list.reverse()
    for i in comments_list:
        code = code[:i[0]] + code[i[1]:]
    return code


def read_operators_list():
    try:
        f = open('operators.bin', 'rb')
        operator_list = pickle.load(f)
        f.close()
    except:
        operator_list = []
    return operator_list

def write_operators_list(operator_list):
    try:
        f = open('operators.bin', 'wb')
        pickle.dump(operator_list, f)
        f.close()
    except:
        print("Не удалось записать:)")


def make_holsted(code):
    print("_________________Метрика Холстеда_________________")
    n_operators = 0
    n_operands = 0
    n_unique_operands = 0
    n_unique_operators = 0
    #операторы из бд
    d_n_operators, d_n_unique_operators = count_std_operators(code)
    n_operators += d_n_operators
    n_unique_operators += d_n_unique_operators
    #поиск: переменные, именованные константы, функции и процедуры
    d_n_operators, d_n_unique_operators, d_n_operands, d_n_unique_operands, potentional_volume = count_vars_funcs_namedconsts_funcparams(code)
    n_operands += d_n_operands
    n_unique_operands += d_n_unique_operands
    n_operators += d_n_operators
    n_unique_operators += d_n_unique_operators
    #численные константы
    d_n_operands, d_n_unique_operands = count_number_const(code)
    n_operands += d_n_operands
    n_unique_operands += d_n_unique_operands
    #строковые константы и символьные
    d_n_operands, d_n_unique_operands = count_str_const(code)
    n_operands += d_n_operands
    n_unique_operands += d_n_unique_operands
    #-> ***************************************************
    calculate_values(n_operands, n_operators, n_unique_operands, n_unique_operators, potentional_volume)
#из списка
def count_std_operators(code):
    n_operators = 0
    n_unique_operators = 0
    operators_list = read_operators_list()
    #для операторов символьных
    for operator in operators_list:
         if operator[0] not in ALPHABET:
            print re.compile('\%s' % operator).findall(code)
            entries = len(re.compile('\%s' % operator).findall(code))
            n_operators += entries
            if entries != 0:
                n_unique_operators += 1
    #print '//////////////////////////////////////////'
    #для операторов (слова)
    for operator in operators_list:
        if operator[0] in ALPHABET:
            print re.compile('%s' % operator).findall(code)
            entries = len(re.compile('%s' %operator).findall(code))
            n_operators += entries
            if entries != 0:
                n_unique_operators += 1
    #operators_list = []
    return n_operators, n_unique_operators
#++++++++++
def count_var(code, operands_list):
    re_def_var = re.compile('((char|int|float|long|short|double|file){1}\*{0,2}\s+\*{0,2}(([_a-zA-Z]{1}[\w]*)(\[*[\w,\{\}"\'\* \t]*\]*)(\s*,*\s*)+={0,1}["\'{}\w\s]*);{1})')
    full_var_list = []
    for part in re_def_var.findall(code):
        #во втором списке нах-ся переменные
        list_var = part[BLOCK_POSITION].split(',')
        for var in list_var:
            i = len(var) - 1
            while (var[i] != ' 'or var[i] != '=') and i > 0:
                i -= 1
            if i > 0:
                var = var[i+1:]
            i = 0
            while (var[i] not in ALPHABET) and (i < len(var)):
                i += 1
            var = var[i:]
            i = 0
            while (var[i] in ALPHABET) and (i < len(var) - 1):
                i += 1
            if i == len(var)-1:
                var = var[:i+1]
            else:
                var = var[:i]
            if  var and (var not in full_var_list):
                full_var_list.append(var)
    print full_var_list
    for var in full_var_list:
        if  var != '' and var not in operands_list:
            operands_list.append(var)

def count_func_params(code, operands_list):
    re_param_of_func = re.compile('(\(((((char|int|float|long|short|double|file|void){1}\*{0,2})\s+([a-zA-Z_]{1}[\w]*\s*,*\s*)+)*)\)\s*\{)')
    full_func_params_list = []
    potentional_volume = 0
    print re_param_of_func.findall(code)
    for part in re_param_of_func.findall(code):
        #в первой блоке параметры
        func_params_list = part[1].split(",")
        print func_params_list
        potentional_volume += 1
        for param in func_params_list:
            if param:
                potentional_volume += 1
                i = len(param) - 1
                while param[i] != ' ':
                    i -= 1
                param = param[i+1:]
                for letter in param:
                    if letter not in ALPHABET:
                        param.replace(letter, "")
                if param not in full_func_params_list:
                    full_func_params_list.append(param)

                #potentional_volume += len(full_func_params_list) + 1
    #print full_func_params_list
    for func_param in full_func_params_list:
        if func_param not in operands_list:
            operands_list.append(func_param)

    potentional_volume = potentional_volume * math.log(potentional_volume, LOGARITHM_BASE)
    return potentional_volume


def count_func(code, operators_list):
    re_def_func = re.compile('((char|int|float|long|short|double|file|void){1}\*{0,2}\s+([a-zA-Z_]{1}\w*)\s*\({1}[\w,\{\}"\'\*\[\] \t]*\){1}\s*\{{1})')
    for part in re_def_func.findall(code):
        #print part[2]
        if part[BLOCK_POSITION] not in operators_list:
            operators_list.append(part[2])

def count_named_const(code, operands_list):
    re_def_named_const = re.compile('#define\s+([_a-zA-Z]{1}[\w]*)\s+"*\'*[\w+-/*\?\!\@.,]\'*"*;')
    for part in re_def_named_const.findall(code):
        #print part[2]
        if part[BLOCK_POSITION] not in operands_list:
            operands_list.append(part[2])

def count_number_const(code):
    operands_list = []
    n_operands = 0
    n_unique_operands = 0
    re_number_const = re.compile('[\(\*-/\+ =\[:\t\{\D]+((-?[\d]*)|(-?0(x|X)[\da-fA-F]*)|(-?0[0-7]*)|(-?\d.\d))[\D\)=\]\*-/\+ :\t\}]+')
    for operand in re_number_const.findall(code):
        if operand[0] and (operand[0] not in operands_list):
            operands_list.append(operand[0])
    for operand in operands_list:
        n_operands += len((re.compile('[\(\)\*-/\+ \[:\t\{]+(%s)[\)\(\]\*-/\+ :\t\;}]+' %operand)).findall(code))
    n_unique_operands += len(operands_list)
    return n_operands, n_unique_operands

def count_str_const(code):
    operands_list = []
    n_operands = 0
    n_unique_operands = 0
    re_str_const = re.compile('("{1}[\w\\\s\*/\-\+\[\]%:\{\}]*"{1}|\'{1}[\w\\\s\*/%:\-\+\[\]\{\}]{1}\'{1})')
    str_const_list = re_str_const.findall(code)
    n_operands += len(str_const_list)
    for operand in str_const_list:
        if operand:
            print operand
            if (operand not in operands_list):
                operands_list.append(operand[1:len(operand)-1])
    n_unique_operands += len(operands_list)
    print operands_list
    return n_operands, n_unique_operands

def count_vars_funcs_namedconsts_funcparams(code):
    n_operands = 0
    n_unique_operands = 0
    n_operators = 0
    n_unique_operators = 0
    operators_list = operands_list = []
    count_var(code, operands_list)
    count_func(code, operators_list)
    n_unique_operators += len(operators_list)
    for operator in operators_list:
        n_operators += len(re.compile('%s' %operator).findall(code))

    potential_volume = count_func_params(code, operands_list)
    n_unique_operands += len(operands_list) - 1

    for operand in operands_list:
        n_operands += len((re.compile('[\(\)\*-/\+ \[:\t\{]+(%s)[\)\(\]\*-/\+ :\t\;\}]+' %operand)).findall(code))
    return n_operators, n_unique_operators, n_operands, n_unique_operands, potential_volume

def calculate_values(n_operands, n_operators, n_unique_operands, n_unique_operators, potentional_volume):
    print("----------------------------Results----------------------------")
    print("Кол-во уникальных операторов: %d" %n_unique_operators)
    print("Общее кол-во операторов: %d" %n_operators)
    print("Кол-во уникальных операндов: %d" %n_unique_operands)
    print("Общее кол-во операндов: %d" %n_operands)
    prog_length = n_operands + n_operators
    prog_vocabulary = n_unique_operands + n_unique_operators
    prog_volume = prog_length * math.log(prog_vocabulary, 2)
    theory_length = n_operators * math.log(n_operands) + n_operands * math.log(n_operators)
    prog_level = float(potentional_volume/prog_volume)
    counter_fact_params = float(2.0 * n_unique_operands)/(n_unique_operators * n_operands)
    I = float(counter_fact_params * prog_volume)
    E = theory_length * float(math.log(2, prog_vocabulary/potentional_volume))
    E1 = prog_length * float(math.log(2, prog_vocabulary/potentional_volume))
    print("Длина: %d" %prog_length)
    print("Словарь: %d" %prog_vocabulary)
    print("Объём: %f" %prog_volume)
    print("Потенциальный объём: %f" %potentional_volume)
    print("Теоретическая длина программы: %f" %theory_length)
    print("Уровень качества программы: %f" %prog_level)
    #print("L*: %f" %counter_fact_params) только фактические параметры
    print("Интеллектуальность: %f" %I)
    print("Усилия: %f" %E)
    print("Усилия при реальной длине словаря: %f" %E1)


def openfile():
    filename = str(raw_input("Введите имя файла: "))
    try:
        f = open(filename, "r")
        code = f.read()
    except:
        f = None
        code = None
    if f:
        print("File is loaded!")
    return code

def main():
    choice = None
    code = None
    while choice != 0:
        print("""
        1 - Проанализировать (метрика Холстеда)
        2 - Открыть файл с кодом (язык C)
        3 - Показать код
        4 - Показать список операторов
        5 - Добавить оператор
        6 - Удалить оператор
        0 - Выйти
        """)
        try:
            choice = input("Ваш выбор: ")
        except:
            choice = None
        if choice == 1:
            if code:
                make_holsted(code)
            else:
                print("File with code is not loaded!")
        elif choice == 2:
            code = openfile()
            if code:
                code = del_comments(code)
        elif choice == 3:
            if code:
                print("-*-*-*-*-*-*-*-*-*code-*-*-*-*-*-*-*-*-*-*-*-")
                print(code)
            else:
                print("Код недоступен")
        elif choice == 4:
            operators_list = read_operators_list()
            print('Список операторов: \n')
            print(operators_list)
        elif choice == 5:
            new_operators = (str(raw_input("Новый(е) оператор(ы)(через пробел, если их несколько): "))).split()
            operators_list = read_operators_list()
            for new_operator in new_operators:
                if new_operator not in operators_list:
                    operators_list.append(new_operator)
            write_operators_list(operators_list)
        elif choice == 6:
            del_operators = (str(raw_input("Удаляемый(е) оператор(ы)(через пробел, если их несколько): "))).split()
            operators_list = read_operators_list()
            for del_operator in del_operators:
                if operators_list:
                    if del_operator in operators_list:
                        operators_list.remove(del_operator)
            write_operators_list(operators_list)
        elif choice == 0:
            print("Пока:)")
        else:
            print("Некорректный выбор!")
        print("-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-*-")

if __name__ == "__main__":
    print('max')
    main()
