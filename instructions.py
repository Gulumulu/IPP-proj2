import re
import sys


tempFrame = {}
frame = "G"
globalFrame = {}
labels = {}


'''
TODO
local and temporary dictionaries
writing the escape sequences
'''

# checks the number of arguments of an instruction
def check_num(args, num):
    if args != num:
        quit(32)


# checks the variable types used in the instruction
def check_vars(vars, args):
    x = 0
    while x < len(args):
        if vars[x] == 'var':
            if not re.match(r"^var$", args[x].type):
                quit(32)
        elif vars[x] == 'symb':
            if not re.match(r"^(string|var|bool|nil|int)$", args[x].type):
                quit(32)
        elif vars[x] == 'label':
            if not re.match(r"^label$", args[x].type):
                quit(32)
        elif vars[x] == 'type':
            if not re.match(r"^type$", args[x].type):
                quit(32)
        x += 1


# checks the data stored in the variables
def check_data(args):
    x = 0
    while x < len(args):
        if args[x].type == 'string':
            if args[x].name == None:
                x += 1
                continue
                # !!!!! mozno bude treba zmenit regex !!!!!
            elif not re.match(r"^(([\w]*(\\\\[0-9]{3})*)*)\S*$", args[x].name, flags=re.UNICODE):
                quit(32)
        elif args[x].type == 'int':
            if not re.match(r"^([-|+]?\d+)$", args[x].name):
                quit(32)
        elif args[x].type == 'bool':
            if not re.match(r"^(bool@(true|false|TRUE|FALSE))$", args[x].name):
                quit(32)
        elif args[x].type == 'var':
            if not re.match(r"^([G|L|T]F@)[\w|_|-|$|&|%|*|!|?][\w|_|-|$|&|%|*|!|?]+$", args[x].name, flags=re.UNICODE):
                quit(32)
        elif args[x].type == 'nil':
            if not re.match(r"^(nil@nil)$", args[x].name):
                quit(32)
        elif args[x].type == 'label':
            if not re.match(r"^([\w]*(\\\\[0-9]{3})*)*$", args[x].name, flags=re.UNICODE):
                quit(32)
        elif args[x].type == 'type':
            if not re.match(r"^(string|int|bool)$", args[x].name):
                quit(32)
        x += 1


def print_out(text, out):
    if out == 'err':
        file = sys.stderr
    else:
        file = sys.stdout

    if text.isdigit() and not re.match(r"\\", text):
        print(text, end='', file=file)
    else:
        i = 0
        while i < len(text):
            if text[i] == "\\":
                print(chr(int(text[i+2:i+4])), end='', file=file)
                i += 4
            else:
                print(text[i], end='', file=file)
                i += 1


def move(instruct, interpret):
    global globalFrame, tempFrame, frame

    if interpret == 0:
        check_num(len(instruct.args), 2)
        vars = ['var', 'symb']
        check_vars(vars, instruct.args)
        check_data(instruct.args)
    elif interpret == 1 and frame == "G":
        if instruct.args[0].name[3:] in globalFrame:
            if instruct.args[1].type == 'var' and not instruct.args[1].name[3:] in globalFrame:
                quit(54)
            elif instruct.args[1].name == None:
                globalFrame.update({instruct.args[0].name[3:]: ""})
            else:
                globalFrame.update({instruct.args[0].name[3:]: instruct.args[1].name})
        else:
            quit(54)
    elif interpret == 1 and frame == "L":
        print("local")
    elif interpret == 1 and frame == "T":
        print("temp")


def createframe(instruct, interpret):
    check_num(len(instruct.args), 0)


def pushframe(instruct, interpret):
    check_num(len(instruct.args), 0)


def popframe(instruct, interpret):
    check_num(len(instruct.args), 0)


def defvar(instruct, interpret):
    global globalFrame, tempFrame, frame

    if interpret == 0:
        check_num(len(instruct.args), 1)
        vars = ['var']
        check_vars(vars, instruct.args)
        check_data(instruct.args)
        return {}
    elif interpret == 1:
        if re.match(r"GF@", instruct.args[0].name):
            globalFrame.update({instruct.args[0].name[3:]: None})
            return globalFrame
        elif re.match(r"LF@", instruct.args[0].name) and frame == "L":
            print("LF")
        elif re.match(r"TF@", instruct.args[0].name) and frame == "T":
            tempFrame.update({instruct.args[0].name[3:]: None})
            return tempFrame
        else:
            quit(55)


def call(instruct, interpret):
    check_num(len(instruct.args), 1)
    vars = ['label']
    check_vars(vars, instruct.args)
    check_data(instruct.args)


def _return(instruct, interpret):
    check_num(len(instruct.args), 0)


def pushs(instruct, interpret):
    check_num(len(instruct.args), 1)
    vars = ['symb']
    check_vars(vars, instruct.args)
    check_data(instruct.args)


def pops(instruct, interpret):
    check_num(len(instruct.args), 1)
    vars = ['var']
    check_vars(vars, instruct.args)
    check_data(instruct.args)


def add(instruct, interpret):
    if interpret == 0:
        check_num(len(instruct.args), 3)
        vars = ['var', 'symb', 'symb']
        check_vars(vars, instruct.args)
        check_data(instruct.args)
    elif interpret == 1:
        if frame == "G" and instruct.args[0].name[3:] in globalFrame:
            if not instruct.args[1].type == "int" or not instruct.args[2].type == "int":
                quit(53)
            else:
                globalFrame.update({instruct.args[0].name[3:]: str(int(instruct.args[1].name) + int(instruct.args[2].name))})
        elif frame == "T" and (instruct.args[0].name[3:] in globalFrame or instruct.args[0].name[3:] in tempFrame):
            if not instruct.args[1].type == "int" or not instruct.args[2].type == "int":
                quit(53)
            else:
                tempFrame.update({instruct.args[0].name[3:]: str(int(instruct.args[1].name) + int(instruct.args[2].name))})


def sub(instruct, interpret):
    if interpret == 0:
        check_num(len(instruct.args), 3)
        vars = ['var', 'symb', 'symb']
        check_vars(vars, instruct.args)
        check_data(instruct.args)
    elif interpret == 1:
        if frame == "G" and instruct.args[0].name[3:] in globalFrame:
            if not instruct.args[1].type == "int" or not instruct.args[2].type == "int":
                quit(53)
            else:
                globalFrame.update({instruct.args[0].name[3:]: str(int(instruct.args[1].name) - int(instruct.args[2].name))})
        elif frame == "T" and (instruct.args[0].name[3:] in globalFrame or instruct.args[0].name[3:] in tempFrame):
            if not instruct.args[1].type == "int" or not instruct.args[2].type == "int":
                quit(53)
            else:
                tempFrame.update({instruct.args[0].name[3:]: str(int(instruct.args[1].name) - int(instruct.args[2].name))})



def mul(instruct, interpret):
    if interpret == 0:
        check_num(len(instruct.args), 3)
        vars = ['var', 'symb', 'symb']
        check_vars(vars, instruct.args)
        check_data(instruct.args)
    elif interpret == 1:
        if frame == "G" and instruct.args[0].name[3:] in globalFrame:
            if not instruct.args[1].type == "int" or not instruct.args[2].type == "int":
                quit(53)
            else:
                globalFrame.update({instruct.args[0].name[3:]: str(int(instruct.args[1].name) * int(instruct.args[2].name))})
        elif frame == "T" and (instruct.args[0].name[3:] in globalFrame or instruct.args[0].name[3:] in tempFrame):
            if not instruct.args[1].type == "int" or not instruct.args[2].type == "int":
                quit(53)
            else:
                tempFrame.update({instruct.args[0].name[3:]: str(int(instruct.args[1].name) * int(instruct.args[2].name))})


def idiv(instruct, interpret):
    if interpret == 0:
        check_num(len(instruct.args), 3)
        vars = ['var', 'symb', 'symb']
        check_vars(vars, instruct.args)
        check_data(instruct.args)
    elif interpret == 1:
        if frame == "G" and instruct.args[0].name[3:] in globalFrame:
            if not instruct.args[1].type == "int" or not instruct.args[2].type == "int":
                quit(53)
            elif int(instruct.args[2].name) == 0:
                quit(57)
            else:
                globalFrame.update({instruct.args[0].name[3:]: str(int(instruct.args[1].name) // int(instruct.args[2].name))})
        elif frame == "T" and (instruct.args[0].name[3:] in globalFrame or instruct.args[0].name[3:] in tempFrame):
            if not instruct.args[1].type == "int" or not instruct.args[2].type == "int":
                quit(53)
            elif int(instruct.args[2].name) == 0:
                quit(57)
            else:
                tempFrame.update({instruct.args[0].name[3:]: str(int(instruct.args[1].name) // int(instruct.args[2].name))})
        else:
            quit(54)


def lt(instruct, interpret):
    check_num(len(instruct.args), 3)
    vars = ['var', 'symb', 'symb']
    check_vars(vars, instruct.args)
    check_data(instruct.args)


def gt(instruct, interpret):
    check_num(len(instruct.args), 3)
    vars = ['var', 'symb', 'symb']
    check_vars(vars, instruct.args)
    check_data(instruct.args)


def eq(instruct, interpret):
    check_num(len(instruct.args), 3)
    vars = ['var', 'symb', 'symb']
    check_vars(vars, instruct.args)
    check_data(instruct.args)


def _and(instruct, interpret):
    check_num(len(instruct.args), 3)
    vars = ['var', 'symb', 'symb']
    check_vars(vars, instruct.args)
    check_data(instruct.args)


def _or(instruct, interpret):
    check_num(len(instruct.args), 3)
    vars = ['var', 'symb', 'symb']
    check_vars(vars, instruct.args)
    check_data(instruct.args)


def _not(instruct, interpret):
    check_num(len(instruct.args), 3)
    vars = ['var', 'symb', 'symb']
    check_vars(vars, instruct.args)
    check_data(instruct.args)


def int2char(instruct, interpret):
    check_num(len(instruct.args), 2)
    vars = ['var', 'symb']
    check_vars(vars, instruct.args)
    check_data(instruct.args)


def stri2int(instruct, interpret):
    if interpret == 0:
        check_num(len(instruct.args), 3)
        vars = ['var', 'symb', 'symb']
        check_vars(vars, instruct.args)
        check_data(instruct.args)
    elif interpret == 1:
        if instruct.args[0].name[3:] in globalFrame and frame == "G":
            if instruct.args[1].name[3:] in globalFrame and instruct.args[1].type == "var":
                string = globalFrame[instruct.args[1].name[3:]]
            elif instruct.args[1].type == "var":
                quit(54)
            elif instruct.args[1].type == "string":
                string = instruct.args[1].name
            else:
                quit(53)
            if instruct.args[2].name[3:] in globalFrame and instruct.args[2].type == "var":
                integer = globalFrame[instruct.args[2].name[3:]]
            elif instruct.args[2].type == "var":
                quit(54)
            elif instruct.args[2].type == "int" and (int(instruct.args[2].name) < 0 or int(instruct.args[2].name) >= len(string)):
                quit(58)
            elif instruct.args[2].type == "int":
                integer = instruct.args[2].name
            else:
                quit(53)
            globalFrame.update({instruct.args[0].name[3:]: ord(string[integer:integer + 1])})
        else:
            quit(54)


def read(instruct, interpret):
    check_num(len(instruct.args), 2)
    vars = ['var', 'type']
    check_vars(vars, instruct.args)
    check_data(instruct.args)


def write(instruct, interpret):
    global globalFrame, tempFrame, frame

    if interpret == 0:
        check_num(len(instruct.args), 1)
        vars = ['symb']
        check_vars(vars, instruct.args)
        check_data(instruct.args)
    elif interpret == 1:
        if instruct.args[0].type == 'var':
            if instruct.args[0].name[3:] in globalFrame and frame == "G":
                print_out(globalFrame[instruct.args[0].name[3:]], 'std')
            elif frame == "L":
                print("local")
            elif instruct.args[0].name[3:] in tempFrame and frame == "T":
                print_out(tempFrame[instruct.args[0].name[3:]], 'std')
            elif instruct.args[0].name[3:] in globalFrame and frame == "T":
                print_out(globalFrame[instruct.args[0].name[3:]], 'std')
            else:
                quit(54)
        else:
            print_out(instruct.args[0].name, 'std')


def concat(instruct, interpret):
    if interpret == 0:
        check_num(len(instruct.args), 3)
        vars = ['var', 'symb', 'symb']
        check_vars(vars, instruct.args)
        check_data(instruct.args)
    elif interpret == 1:
        if (instruct.args[1].type == "string" or instruct.args[1].type == "var") and (instruct.args[2].type == "string" or instruct.args[2].type == "var"):
            if instruct.args[0].name[3:] in globalFrame and frame == "G":
                str1 = instruct.args[1].name
                str2 = instruct.args[2].name
                if str1[3:] in globalFrame and instruct.args[1].type == "var":
                    str1 = globalFrame[instruct.args[1].name[3:]]
                elif instruct.args[1].type == "var":
                    quit(54)
                if str2[3:] in globalFrame and instruct.args[2].type == "var":
                    str2 = globalFrame[instruct.args[2].name[3:]]
                elif instruct.args[2].type == "var":
                    quit(54)
                globalFrame.update({instruct.args[0].name[3:]: str1 + str2})
            elif instruct.args[0].name[3:] in tempFrame and frame == "T":
                tempFrame.update({instruct.args[0].name[3:]: instruct.args[1].name + instruct.args[2].name})
            else:
                quit(54)
        else:
            quit(53)


def strlen(instruct, interpret):
    if interpret == 0:
        check_num(len(instruct.args), 2)
        vars = ['var', 'symb']
        check_vars(vars, instruct.args)
        check_data(instruct.args)
    elif interpret == 1:
        if instruct.args[0].name[3:] in globalFrame and frame == "G":
            globalFrame.update({instruct.args[0].name[3:]: len(instruct.args[1].name)})
        elif instruct.args[0].name[3:] in tempFrame and frame == "T":
            tempFrame.update({instruct.args[0].name[3:]: len(instruct.args[1].name)})
        else:
            quit(54)


def getchar(instruct, interpret):
    if interpret == 0:
        check_num(len(instruct.args), 3)
        vars = ['var', 'symb', 'symb']
        check_vars(vars, instruct.args)
        check_data(instruct.args)
    elif interpret == 1:
        if int(instruct.args[2].name) >= 0 and int(instruct.args[2].name) < len(instruct.args[1].name):
            if instruct.args[2].type == "int":
                if instruct.args[0].name[3:] in globalFrame and (frame == "G" or frame == "T"):
                    globalFrame.update({instruct.args[0].name[3:]: instruct.args[1].name[int(instruct.args[2].name):int(instruct.args[2].name) + 1]})
                elif instruct.args[0].name[3:] in globalFrame and frame == "T":
                    tempFrame.update({instruct.args[0].name[3:]: instruct.args[1].name[int(instruct.args[2].name):int(instruct.args[2].name) + 1]})
                else:
                    quit(54)
            else:
                quit(53)
        else:
            quit(58)


def setchar(instruct, interpret):
    if interpret == 0:
        check_num(len(instruct.args), 3)
        vars = ['var', 'symb', 'symb']
        check_vars(vars, instruct.args)
        check_data(instruct.args)
    elif interpret == 1:
        if not instruct.args[2].name and int(instruct.args[1].name) >= 0 and int(instruct.args[1].name) < len(instruct.args[2].name):
            if instruct.args[1].type == "int":
                if instruct.args[0].name[3:] in globalFrame and (frame == "G" or frame == "T"):
                    tmp = globalFrame[instruct.args[0].name[3:]]
                    new = "".join((tmp[int(instruct.args[1].name)], instruct.args[2].name[0:1], tmp[int(instruct.args[1].name)]))
                    globalFrame.update({instruct.args[0].name[3:]: new})
                elif instruct.args[0].name[3:] in globalFrame and frame == "T":
                    tmp = globalFrame[instruct.args[0].name[3:]]
                    new = "".join((tmp[int(instruct.args[1].name)], instruct.args[2].name[0:1], tmp[int(instruct.args[1].name)]))
                    tempFrame.update({instruct.args[0].name[3:]: new})
                else:
                    quit(54)
            else:
                quit(53)
        else:
            quit(58)


def type(instruct, interpret):
    if interpret == 0:
        check_num(len(instruct.args), 2)
        vars = ['var', 'symb']
        check_vars(vars, instruct.args)
        check_data(instruct.args)
    elif interpret == 1:
        if frame == "G" and instruct.args[0].name[3:] in globalFrame:
            if instruct.args[1].name is None:
                globalFrame.update({instruct.args[0].name[3:]: ""})
            elif instruct.args[1].type == "nil":
                globalFrame.update({instruct.args[0].name[3:]: "nil"})
            elif instruct.args[1].type == "int":
                globalFrame.update({instruct.args[0].name[3:]: "int"})
            elif instruct.args[1].type == "bool":
                globalFrame.update({instruct.args[0].name[3:]: "bool"})
            elif instruct.args[1].type == "string":
                globalFrame.update({instruct.args[0].name[3:]: "string"})
        else:
            quit(54)


def label(instruct, interpret):
    if interpret == 0:
        check_num(len(instruct.args), 1)
        vars = ['label']
        check_vars(vars, instruct.args)
        check_data(instruct.args)
    elif interpret == 1:
        if not bool(labels):
            labels.update({1: instruct.args[0].name})
        elif not instruct.args[0].name in labels:
            labels.update({len(labels) + 1: instruct.args[0].name})
        else:
            quit(52)


def jump(instruct, interpret):
    if interpret == 0:
        check_num(len(instruct.args), 1)
        vars = ['label']
        check_vars(vars, instruct.args)
        check_data(instruct.args)


def jumpifeq(instruct, interpret):
    check_num(len(instruct.args), 3)
    vars = ['label', 'symb', 'symb']
    check_vars(vars, instruct.args)
    check_data(instruct.args)


def jumpifnoteq(instruct, interpret):
    check_num(len(instruct.args), 3)
    vars = ['label', 'symb', 'symb']
    check_vars(vars, instruct.args)
    check_data(instruct.args)


def exit(instruct, interpret):
    if interpret == 0:
        check_num(len(instruct.args), 1)
        vars = ['symb']
        check_vars(vars, instruct.args)
        check_data(instruct.args)
    elif interpret == 1:
        if not instruct.args[0].name.isdigit() or not int(instruct.args[0].name) <= 49 or not int(instruct.args[0].name) >= 0:
            quit(57)
        else:
            quit(int(instruct.args[0].name))


def dprint(instruct, interpret):
    if interpret == 0:
        check_num(len(instruct.args), 1)
        vars = ['symb']
        check_vars(vars, instruct.args)
        check_data(instruct.args)
    elif interpret == 1:
        if instruct.args[0].type == "var" and frame == "G":
            if instruct.args[0].name[3:] in globalFrame:
                print_out(globalFrame[instruct.args[0].name[3:]], 'err')
            else:
                quit(54)
        elif not instruct.args[0].type == "var":
            print_out(instruct.args[0].name, 'err')


def _break(instruct, interpret):
    check_num(len(instruct.args), 0)
