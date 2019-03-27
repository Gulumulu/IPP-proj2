import re
import sys

frame = "G"
globalFrame = {}
tempFrame = None
localFrame = [{}]
dataStack = []
labels = {}

'''
TODO
local and temporary dictionaries
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
            if args[x].name is None:
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


# prints the data to a defined output media
def print_out(text, out):
    # if the DPRINT instruction is called print to stderr
    if out == "err":
        file = sys.stderr
    # if the WRITE instruction is called print to stdout
    else:
        file = sys.stdout

    # if the text to print is a digit without any escape sequences
    if text.isdigit() and not re.match(r"\\", text):
        print(int(text), end='', file=file)
    # if the text to print is a bool
    elif re.match(r"^(true|TRUE|false|FALSE)$", text):
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
    global globalFrame, tempFrame, localFrame

    if interpret == 0:
        check_num(len(instruct.args), 2)
        vars = ['var', 'symb']
        check_vars(vars, instruct.args)
        check_data(instruct.args)
    elif interpret == 1:
        # if the variable is in the global frame
        if re.match(r"^(GF@).*$", instruct.args[0].name[0:3]) and instruct.args[0].name[3:] in globalFrame:
            # if the symbol is a variable in the global frame
            if instruct.args[1].type == "var" and re.match(r"^(GF@).*$", instruct.args[1].name[0:3]) \
                    and instruct.args[1].name[3:] in globalFrame:
                globalFrame.update({instruct.args[0].name[3:]: globalFrame[instruct.args[1].name[3:]]})
            # if the symbol is a variable in the temporary frame
            elif instruct.args[1].type == "var" and re.match(r"^(TF@).*$", instruct.args[1].name[0:3]) \
                    and instruct.args[1].name[3:] in tempFrame:
                globalFrame.update({instruct.args[0].name[3:]: tempFrame[instruct.args[1].name[3:]]})
            # if the symbol is a variable in the local frame
            elif instruct.args[1].type == "var" and re.match(r"^(LF@).*$", instruct.args[1].name[0:3]) \
                    and instruct.args[1].name[3:] in localFrame[-1]:
                globalFrame.update({instruct.args[0].name[3:]: localFrame[-1][instruct.args[1].name[3:]]})
            # if the symbol is a variable but isn't in the correct frame
            elif instruct.args[1].type == "var":
                quit(54)
            # if the symbol is not a variable
            else:
                globalFrame.update({instruct.args[0].name[3:]: instruct.args[1].name})
        # if the variable is in the temporary frame
        elif re.match(r"^(TF@).*$", instruct.args[0].name[0:3]) and instruct.args[0].name[3:] in tempFrame:
            # if the symbol is a variable in the global frame
            if instruct.args[1].type == "var" and re.match(r"^(GF@).*$", instruct.args[1].name[0:3]) \
                    and instruct.args[1].name[3:] in globalFrame:
                tempFrame.update({instruct.args[0].name[3:]: globalFrame[instruct.args[1].name[3:]]})
            # if the symbol is a variable in the temporary frame
            elif instruct.args[1].type == "var" and re.match(r"^(TF@).*$", instruct.args[1].name[0:3]) \
                    and instruct.args[1].name[3:] in tempFrame:
                tempFrame.update({instruct.args[0].name[3:]: tempFrame[instruct.args[1].name[3:]]})
            # if the symbol is a variable in the local frame
            elif instruct.args[1].type == "var" and re.match(r"^(LF@).*$", instruct.args[1].name[0:3]) \
                    and instruct.args[1].name[3:] in localFrame[-1]:
                tempFrame.update({instruct.args[0].name[3:]: localFrame[-1][instruct.args[1].name[3:]]})
            # if the symbol is a variable but isn't in the correct frame
            elif instruct.args[1].type == "var":
                quit(54)
            # if the symbol is not a variable
            else:
                tempFrame.update({instruct.args[0].name[3:]: instruct.args[1].name})
        # if the variable is in the local frame
        elif re.match(r"^(LF@).*$", instruct.args[0].name[0:3]) and instruct.args[1].name[3:] in localFrame[-1]:
            # if the symbol is a variable in the global frame
            if instruct.args[1].type == "var" and re.match(r"^(GF@).*$", instruct.args[1].name[0:3]) \
                    and instruct.args[1].name[3:] in globalFrame:
                localFrame[-1].update({instruct.args[0].name[3:]: globalFrame[instruct.args[1].name[3:]]})
            # if the symbol is a variable in the temporary frame
            elif instruct.args[1].type == "var" and re.match(r"^(TF@).*$", instruct.args[1].name[0:3]) \
                    and instruct.args[1].name[3:] in tempFrame:
                localFrame[-1].update({instruct.args[0].name[3:]: tempFrame[instruct.args[1].name[3:]]})
            # if the symbol is a variable in the local frame
            elif instruct.args[1].type == "var" and re.match(r"^(LF@).*$", instruct.args[1].name[0:3]) \
                    and instruct.args[1].name[3:] in localFrame[-1]:
                localFrame[-1].update({instruct.args[0].name[3:]: localFrame[-1][instruct.args[1].name[3:]]})
            # if the symbol is a variable but isn't in the correct frame
            elif instruct.args[1].type == "var":
                quit(54)
            # if the symbol is not a variable
            else:
                localFrame[-1].update({instruct.args[0].name[3:]: instruct.args[1].name})


def createframe(instruct, interpret):
    global tempFrame

    if interpret == 0:
        check_num(len(instruct.args), 0)
    elif interpret == 1:
        # if the temporary frame is not initialised
        if tempFrame is None:
            tempFrame = {}
        # if it was already initialised
        else:
            tempFrame.clear()


def pushframe(instruct, interpret):
    global tempFrame, localFrame

    if interpret == 0:
        check_num(len(instruct.args), 0)
    elif interpret == 1:
        # if the temporary frame wan't initialised
        if tempFrame is None:
            quit(55)
        # add the current temporary frame to the top of the local frame stack and destroy the temporary frame
        localFrame.append(tempFrame)
        tempFrame.clear()
        tempFrame = None


def popframe(instruct, interpret):
    global tempFrame, localFrame

    if interpret == 0:
        check_num(len(instruct.args), 0)
    elif interpret == 1:
        # if the local frame isn't initialised
        if localFrame is None or not localFrame or tempFrame is None:
            quit(55)
        # pop the top frame from the local frame stack into the temporary frame
        tempFrame = localFrame.pop()


def defvar(instruct, interpret):
    global globalFrame, tempFrame, localFrame

    if interpret == 0:
        check_num(len(instruct.args), 1)
        vars = ['var']
        check_vars(vars, instruct.args)
        check_data(instruct.args)
    elif interpret == 1:
        # if the variable is supposed to be in the global frame
        if re.match(r"^(GF@).*$", instruct.args[0].name):
            globalFrame.update({instruct.args[0].name[3:]: None})
        # if the variable is supposed to be in the local stack frame
        elif re.match(r"^(LF@).*$", instruct.args[0].name):
            localFrame[-1].update({instruct.args[0].name[3:]: None})
        # if the variable is supposed to be in the temporary frame and the current frame is temporary
        elif re.match(r"^(TF@).*$", instruct.args[0].name):
            tempFrame.update({instruct.args[0].name[3:]: None})
        # if the variable is badly defined
        else:
            quit(55)


def call(instruct, interpret):
    if interpret == 0:
        check_num(len(instruct.args), 1)
        vars = ['label']
        check_vars(vars, instruct.args)
        check_data(instruct.args)


def _return(instruct, interpret):
    if interpret == 0:
        check_num(len(instruct.args), 0)


def pushs(instruct, interpret):
    global dataStack, globalFrame, tempFrame, localFrame

    if interpret == 0:
        check_num(len(instruct.args), 1)
        vars = ['symb']
        check_vars(vars, instruct.args)
        check_data(instruct.args)
    elif interpret == 1:
        # if the symbol is a variable in the global frame
        if instruct.args[0].type == "var" and re.match(r"^(GF@).*$", instruct.args[0].name[0:3]) \
                and instruct.args[0].name[3:] in globalFrame:
            dataStack.append(globalFrame[instruct.args[0].name[3:]])
        # if the symbol is a variable in the temporary frame
        elif instruct.args[0].type == "var" and re.match(r"^(TF@).*$", instruct.args[0].name[0:3]) \
                and instruct.args[0].name[3:] in tempFrame:
            dataStack.append(tempFrame[instruct.args[0].name[3:]])
        # if the symbol is a variable in the local frame
        elif instruct.args[0].type == "var" and re.match(r"^(LF@).*$", instruct.args[0].name[0:3]) \
                and instruct.args[0].name[3:] in localFrame[-1]:
            dataStack.append(localFrame[-1][instruct.args[0].name[3:]])
        # if the symbol is a variable but isn't in the correct frame
        elif instruct.args[0].type == "var":
            quit(54)
        # if the symbol isn't a variable
        else:
            dataStack.append(instruct.args[0].name)


def pops(instruct, interpret):
    global dataStack, globalFrame, tempFrame, localFrame

    if interpret == 0:
        check_num(len(instruct.args), 1)
        vars = ['var']
        check_vars(vars, instruct.args)
        check_data(instruct.args)
    elif interpret == 1:
        # if the data stack is empty
        if not dataStack:
            quit(56)
        else:
            # if the variable in the global frame
            if re.match(r"^(GF@).*$", instruct.args[0].name[0:3]) and instruct.args[0].name[3:] in globalFrame:
                globalFrame.update({instruct.args[0].name[3:]: dataStack.pop()})
            # if the variable in the temporary frame
            elif re.match(r"^(TF@).*$", instruct.args[0].name[0:3]) and instruct.args[0].name[3:] in tempFrame:
                tempFrame.update({instruct.args[0].name[3:]: dataStack.pop()})
            # if the variable in the local frame
            elif re.match(r"^(LF@).*$", instruct.args[0].name[0:3]) and instruct.args[0].name[3:] in localFrame[-1]:
                localFrame[-1].update({instruct.args[0].name[3:]: dataStack.pop()})
            # if there is no such variable defined in any frame
            else:
                quit(54)


def add(instruct, interpret):
    global globalFrame, tempFrame, localFrame

    if interpret == 0:
        check_num(len(instruct.args), 3)
        vars = ['var', 'symb', 'symb']
        check_vars(vars, instruct.args)
        check_data(instruct.args)
    elif interpret == 1:
        symb1 = None
        symb2 = None
        # if the first symbol is a variable in the global frame
        if instruct.args[1].type == "var" and re.match(r"^(GF@).*$", instruct.args[1].name[0:3]) \
                and instruct.args[1].name[3:] in globalFrame:
            # if the symbol is an integer
            if globalFrame[instruct.args[1].name[3:]].isdigit():
                symb1 = globalFrame[instruct.args[1].name[3:]]
            else:
                quit(53)
        # if the first symbol is a variable in the temporary frame
        elif instruct.args[1].type == "var" and re.match(r"^(TF@).*$", instruct.args[1].name[0:3]) \
                and instruct.args[1].name[3:] in tempFrame:
            # if the symbol is an integer
            if tempFrame[instruct.args[1].name[3:]].isdigit():
                symb1 = tempFrame[instruct.args[1].name[3:]]
            else:
                quit(53)
        # if the first symbol is a variable in the local frame
        elif instruct.args[1].type == "var" and re.match(r"^(LF@).*$", instruct.args[1].name[0:3]) \
                and instruct.args[1].name[3:] in localFrame[-1]:
            # if the symbol is an integer
            if localFrame[-1][instruct.args[1].name[3:]].isdigit():
                symb1 = localFrame[-1][instruct.args[1].name[3:]]
            else:
                quit(53)
        # if the first symbol is a variable but isn't in the correct frame
        elif instruct.args[1].type == "var":
            quit(54)
        # if the first symbol is an integer
        elif instruct.args[1].type == "int" and instruct.args[1].name.isdigit:
            symb1 = instruct.args[1].name
        # if the first symbol isn't an integer
        else:
            quit(53)
        # if the second symbol is a variable in the global frame
        if instruct.args[2].type == "var" and re.match(r"^(GF@).*$", instruct.args[2].name[0:3]) \
                and instruct.args[2].name[3:] in globalFrame:
            # if the symbol is an integer
            if globalFrame[instruct.args[2].name[3:]].isdigit():
                symb2 = globalFrame[instruct.args[2].name[3:]]
            else:
                quit(53)
        # if the second symbol is a variable in the local frame
        elif instruct.args[2].type == "var" and re.match(r"^(LF@).*$", instruct.args[2].name[0:3]) \
                and instruct.args[2].name[3:] in localFrame[-1]:
            # if the symbol is an integer
            if localFrame[-1][instruct.args[2].name[3:]].isdigit():
                symb1 = localFrame[-1][instruct.args[2].name[3:]]
            else:
                quit(53)
        # if the second symbol is a variable in the temporary frame
        elif instruct.args[2].type == "var" and re.match(r"^(TF@).*$", instruct.args[2].name[0:3]) \
                and instruct.args[2].name[3:] in tempFrame:
            # if the symbol is an integer
            if tempFrame[instruct.args[2].name[3:]].isdigit():
                symb1 = tempFrame[instruct.args[2].name[3:]]
            else:
                quit(53)
        # if the second symbol is a variable but isn't in the correct frame
        elif instruct.args[2].type == "var":
            quit(54)
        # if the second symbol is an integer
        elif instruct.args[2].type == "int" and instruct.args[1].name.isdigit:
            symb2 = instruct.args[2].name
        # if the second symbol isn't an integer
        else:
            quit(53)
        # performing the ADD operation
        # if the variable in the global frame
        if re.match(r"^(GF@).*$", instruct.args[0].name[0:3]) and instruct.args[0].name[3:] in globalFrame:
            globalFrame.update({instruct.args[0].name[3:]: str(int(symb1) + int(symb2))})
            return
        # if the variable in the temporary frame
        if re.match(r"^(TF@).*$", instruct.args[0].name[0:3]) and instruct.args[0].name[3:] in tempFrame:
            tempFrame.update({instruct.args[0].name[3:]: str(int(symb1) + int(symb2))})
            return
        # if the temporary frame doesn't exist
        elif re.match(r"^(TF@).*$", instruct.args[0].name[0:3]) and not tempFrame:
            quit(55)
        # if the temporary frame exists but the variable isn't in it
        elif re.match(r"^(TF@).*$", instruct.args[0].name[0:3]) and not instruct.args[0].name[3:] in tempFrame:
            quit(54)
        # if the variable in the local frame
        if re.match(r"^(LF@).*$", instruct.args[0].name[0:3]) and instruct.args[0].name[3:] in localFrame[-1]:
            localFrame[-1].update({instruct.args[0].name[3:]: str(int(symb1) + int(symb2))})
            return
        # if the local frame doesn't exist
        elif re.match(r"^(LF@).*$", instruct.args[0].name[0:3]) and not localFrame:
            quit(55)
        # if the local frame exists but the variable isn't in it
        elif re.match(r"^(TF@).*$", instruct.args[0].name[0:3]) and not instruct.args[0].name[3:] in tempFrame:
            quit(54)


def sub(instruct, interpret):
    global globalFrame, tempFrame, localFrame

    if interpret == 0:
        check_num(len(instruct.args), 3)
        vars = ['var', 'symb', 'symb']
        check_vars(vars, instruct.args)
        check_data(instruct.args)
    elif interpret == 1:
        symb1 = None
        symb2 = None
        # if the first symbol is a variable in the global frame
        if instruct.args[1].type == "var" and re.match(r"^(GF@).*$", instruct.args[1].name[0:3]) \
                and instruct.args[1].name[3:] in globalFrame:
            # if the symbol is an integer
            if globalFrame[instruct.args[1].name[3:]].isdigit():
                symb1 = globalFrame[instruct.args[1].name[3:]]
            else:
                quit(53)
        # if the first symbol is a variable in the temporary frame
        elif instruct.args[1].type == "var" and re.match(r"^(TF@).*$", instruct.args[1].name[0:3]) \
                and instruct.args[1].name[3:] in tempFrame:
            # if the symbol is an integer
            if tempFrame[instruct.args[1].name[3:]].isdigit():
                symb1 = tempFrame[instruct.args[1].name[3:]]
            else:
                quit(53)
        # if the first symbol is a variable in the local frame
        elif instruct.args[1].type == "var" and re.match(r"^(LF@).*$", instruct.args[1].name[0:3]) \
                and instruct.args[1].name[3:] in localFrame[-1]:
            # if the symbol is an integer
            if localFrame[-1][instruct.args[1].name[3:]].isdigit():
                symb1 = localFrame[-1][instruct.args[1].name[3:]]
            else:
                quit(53)
        # if the first symbol is a variable but isn't in the correct frame
        elif instruct.args[1].type == "var":
            quit(54)
        # if the first symbol is an integer
        elif instruct.args[1].type == "int" and instruct.args[1].name.isdigit:
            symb1 = instruct.args[1].name
        # if the first symbol isn't an integer
        else:
            quit(53)
        # if the second symbol is a variable in the global frame
        if instruct.args[2].type == "var" and re.match(r"^(GF@).*$", instruct.args[2].name[0:3]) \
                and instruct.args[2].name[3:] in globalFrame:
            # if the symbol is an integer
            if globalFrame[instruct.args[2].name[3:]].isdigit():
                symb2 = globalFrame[instruct.args[2].name[3:]]
            else:
                quit(53)
        # if the second symbol is a variable in the local frame
        elif instruct.args[2].type == "var" and re.match(r"^(LF@).*$", instruct.args[2].name[0:3]) \
                and instruct.args[2].name[3:] in localFrame[-1]:
            # if the symbol is an integer
            if localFrame[-1][instruct.args[2].name[3:]].isdigit():
                symb1 = localFrame[-1][instruct.args[2].name[3:]]
            else:
                quit(53)
        # if the second symbol is a variable in the temporary frame
        elif instruct.args[2].type == "var" and re.match(r"^(TF@).*$", instruct.args[2].name[0:3]) \
                and instruct.args[2].name[3:] in tempFrame:
            # if the symbol is an integer
            if tempFrame[instruct.args[2].name[3:]].isdigit():
                symb1 = tempFrame[instruct.args[2].name[3:]]
            else:
                quit(53)
        # if the second symbol is a variable but isn't in the correct frame
        elif instruct.args[2].type == "var":
            quit(54)
        # if the second symbol is an integer
        elif instruct.args[2].type == "int" and instruct.args[1].name.isdigit:
            symb2 = instruct.args[2].name
        # if the second symbol isn't an integer
        else:
            quit(53)
        # performing the SUB operation
        # if the variable in the global frame
        if re.match(r"^(GF@).*$", instruct.args[0].name[0:3]) and instruct.args[0].name[3:] in globalFrame:
            globalFrame.update({instruct.args[0].name[3:]: str(int(symb1) - int(symb2))})
            return
        # if the variable in the temporary frame
        if re.match(r"^(TF@).*$", instruct.args[0].name[0:3]) and instruct.args[0].name[3:] in tempFrame:
            tempFrame.update({instruct.args[0].name[3:]: str(int(symb1) - int(symb2))})
            return
        # if the temporary frame doesn't exist
        elif re.match(r"^(TF@).*$", instruct.args[0].name[0:3]) and not tempFrame:
            quit(55)
        # if the temporary frame exists but the variable isn't in it
        elif re.match(r"^(TF@).*$", instruct.args[0].name[0:3]) and not instruct.args[0].name[3:] in tempFrame:
            quit(54)
        # if the variable in the local frame
        if re.match(r"^(LF@).*$", instruct.args[0].name[0:3]) and instruct.args[0].name[3:] in localFrame[-1]:
            localFrame[-1].update({instruct.args[0].name[3:]: str(int(symb1) - int(symb2))})
            return
        # if the local frame doesn't exist
        elif re.match(r"^(LF@).*$", instruct.args[0].name[0:3]) and not localFrame:
            quit(55)
        # if the local frame exists but the variable isn't in it
        elif re.match(r"^(TF@).*$", instruct.args[0].name[0:3]) and not instruct.args[0].name[3:] in tempFrame:
            quit(54)


def mul(instruct, interpret):
    global globalFrame, tempFrame, localFrame

    if interpret == 0:
        check_num(len(instruct.args), 3)
        vars = ['var', 'symb', 'symb']
        check_vars(vars, instruct.args)
        check_data(instruct.args)
    elif interpret == 1:
        symb1 = None
        symb2 = None
        # if the first symbol is a variable in the global frame
        if instruct.args[1].type == "var" and re.match(r"^(GF@).*$", instruct.args[1].name[0:3]) \
                and instruct.args[1].name[3:] in globalFrame:
            # if the symbol is an integer
            if globalFrame[instruct.args[1].name[3:]].isdigit():
                symb1 = globalFrame[instruct.args[1].name[3:]]
            else:
                quit(53)
        # if the first symbol is a variable in the temporary frame
        elif instruct.args[1].type == "var" and re.match(r"^(TF@).*$", instruct.args[1].name[0:3]) \
                and instruct.args[1].name[3:] in tempFrame:
            # if the symbol is an integer
            if tempFrame[instruct.args[1].name[3:]].isdigit():
                symb1 = tempFrame[instruct.args[1].name[3:]]
            else:
                quit(53)
        # if the first symbol is a variable in the local frame
        elif instruct.args[1].type == "var" and re.match(r"^(LF@).*$", instruct.args[1].name[0:3]) \
                and instruct.args[1].name[3:] in localFrame[-1]:
            # if the symbol is an integer
            if localFrame[-1][instruct.args[1].name[3:]].isdigit():
                symb1 = localFrame[-1][instruct.args[1].name[3:]]
            else:
                quit(53)
        # if the first symbol is a variable but isn't in the correct frame
        elif instruct.args[1].type == "var":
            quit(54)
        # if the first symbol is an integer
        elif instruct.args[1].type == "int" and instruct.args[1].name.isdigit:
            symb1 = instruct.args[1].name
        # if the first symbol isn't an integer
        else:
            quit(53)
        # if the second symbol is a variable in the global frame
        if instruct.args[2].type == "var" and re.match(r"^(GF@).*$", instruct.args[2].name[0:3]) \
                and instruct.args[2].name[3:] in globalFrame:
            # if the symbol is an integer
            if globalFrame[instruct.args[2].name[3:]].isdigit():
                symb2 = globalFrame[instruct.args[2].name[3:]]
            else:
                quit(53)
        # if the second symbol is a variable in the local frame
        elif instruct.args[2].type == "var" and re.match(r"^(LF@).*$", instruct.args[2].name[0:3]) \
                and instruct.args[2].name[3:] in localFrame[-1]:
            # if the symbol is an integer
            if localFrame[-1][instruct.args[2].name[3:]].isdigit():
                symb1 = localFrame[-1][instruct.args[2].name[3:]]
            else:
                quit(53)
        # if the second symbol is a variable in the temporary frame
        elif instruct.args[2].type == "var" and re.match(r"^(TF@).*$", instruct.args[2].name[0:3]) \
                and instruct.args[2].name[3:] in tempFrame:
            # if the symbol is an integer
            if tempFrame[instruct.args[2].name[3:]].isdigit():
                symb1 = tempFrame[instruct.args[2].name[3:]]
            else:
                quit(53)
        # if the second symbol is a variable but isn't in the correct frame
        elif instruct.args[2].type == "var":
            quit(54)
        # if the second symbol is an integer
        elif instruct.args[2].type == "int" and instruct.args[1].name.isdigit:
            symb2 = instruct.args[2].name
        # if the second symbol isn't an integer
        else:
            quit(53)
        # performing the MUL operation
        # if the variable in the global frame
        if re.match(r"^(GF@).*$", instruct.args[0].name[0:3]) and instruct.args[0].name[3:] in globalFrame:
            globalFrame.update({instruct.args[0].name[3:]: str(int(symb1) * int(symb2))})
            return
        # if the variable in the temporary frame
        if re.match(r"^(TF@).*$", instruct.args[0].name[0:3]) and instruct.args[0].name[3:] in tempFrame:
            tempFrame.update({instruct.args[0].name[3:]: str(int(symb1) * int(symb2))})
            return
        # if the temporary frame doesn't exist
        elif re.match(r"^(TF@).*$", instruct.args[0].name[0:3]) and not tempFrame:
            quit(55)
        # if the temporary frame exists but the variable isn't in it
        elif re.match(r"^(TF@).*$", instruct.args[0].name[0:3]) and not instruct.args[0].name[3:] in tempFrame:
            quit(54)
        # if the variable in the local frame
        if re.match(r"^(LF@).*$", instruct.args[0].name[0:3]) and instruct.args[0].name[3:] in localFrame[-1]:
            localFrame[-1].update({instruct.args[0].name[3:]: str(int(symb1) * int(symb2))})
            return
        # if the local frame doesn't exist
        elif re.match(r"^(LF@).*$", instruct.args[0].name[0:3]) and not localFrame:
            quit(55)
        # if the local frame exists but the variable isn't in it
        elif re.match(r"^(TF@).*$", instruct.args[0].name[0:3]) and not instruct.args[0].name[3:] in tempFrame:
            quit(54)


def idiv(instruct, interpret):
    global globalFrame, tempFrame, localFrame

    if interpret == 0:
        check_num(len(instruct.args), 3)
        vars = ['var', 'symb', 'symb']
        check_vars(vars, instruct.args)
        check_data(instruct.args)
    elif interpret == 1:
        symb1 = None
        symb2 = None
        # if the first symbol is a variable in the global frame
        if instruct.args[1].type == "var" and re.match(r"^(GF@).*$", instruct.args[1].name[0:3]) \
                and instruct.args[1].name[3:] in globalFrame:
            # if the symbol is an integer
            if globalFrame[instruct.args[1].name[3:]].isdigit():
                symb1 = globalFrame[instruct.args[1].name[3:]]
            else:
                quit(53)
        # if the first symbol is a variable in the temporary frame
        elif instruct.args[1].type == "var" and re.match(r"^(TF@).*$", instruct.args[1].name[0:3]) \
                and instruct.args[1].name[3:] in tempFrame:
            # if the symbol is an integer
            if tempFrame[instruct.args[1].name[3:]].isdigit():
                symb1 = tempFrame[instruct.args[1].name[3:]]
            else:
                quit(53)
        # if the first symbol is a variable in the local frame
        elif instruct.args[1].type == "var" and re.match(r"^(LF@).*$", instruct.args[1].name[0:3]) \
                and instruct.args[1].name[3:] in localFrame[-1]:
            # if the symbol is an integer
            if localFrame[-1][instruct.args[1].name[3:]].isdigit():
                symb1 = localFrame[-1][instruct.args[1].name[3:]]
            else:
                quit(53)
        # if the first symbol is a variable but isn't in the correct frame
        elif instruct.args[1].type == "var":
            quit(54)
        # if the first symbol is an integer
        elif instruct.args[1].type == "int" and instruct.args[1].name.isdigit:
            symb1 = instruct.args[1].name
        # if the first symbol isn't an integer
        else:
            quit(53)
        # if the second symbol is a variable in the global frame
        if instruct.args[2].type == "var" and re.match(r"^(GF@).*$", instruct.args[2].name[0:3]) \
                and instruct.args[2].name[3:] in globalFrame:
            # if the symbol is an integer
            if globalFrame[instruct.args[2].name[3:]].isdigit():
                symb2 = globalFrame[instruct.args[2].name[3:]]
            else:
                quit(53)
        # if the second symbol is a variable in the local frame
        elif instruct.args[2].type == "var" and re.match(r"^(LF@).*$", instruct.args[2].name[0:3]) \
                and instruct.args[2].name[3:] in localFrame[-1]:
            # if the symbol is an integer
            if localFrame[-1][instruct.args[2].name[3:]].isdigit():
                symb1 = localFrame[-1][instruct.args[2].name[3:]]
            else:
                quit(53)
        # if the second symbol is a variable in the temporary frame
        elif instruct.args[2].type == "var" and re.match(r"^(TF@).*$", instruct.args[2].name[0:3]) \
                and instruct.args[2].name[3:] in tempFrame:
            # if the symbol is an integer
            if tempFrame[instruct.args[2].name[3:]].isdigit():
                symb1 = tempFrame[instruct.args[2].name[3:]]
            else:
                quit(53)
        # if the second symbol is a variable but isn't in the correct frame
        elif instruct.args[2].type == "var":
            quit(54)
        # if the second symbol is an integer
        elif instruct.args[2].type == "int" and instruct.args[1].name.isdigit:
            symb2 = instruct.args[2].name
        # if the second symbol isn't an integer
        else:
            quit(53)
        # performing the IDIV operation
        # if the denominator is 0
        if int(symb2) == 0:
            quit(57)
        # if the variable in the global frame
        if re.match(r"^(GF@).*$", instruct.args[0].name[0:3]) and instruct.args[0].name[3:] in globalFrame:
            globalFrame.update({instruct.args[0].name[3:]: str(int(symb1) // int(symb2))})
            return
        # if the variable in the temporary frame
        if re.match(r"^(TF@).*$", instruct.args[0].name[0:3]) and instruct.args[0].name[3:] in tempFrame:
            tempFrame.update({instruct.args[0].name[3:]: str(int(symb1) // int(symb2))})
            return
        # if the temporary frame doesn't exist
        elif re.match(r"^(TF@).*$", instruct.args[0].name[0:3]) and not tempFrame:
            quit(55)
        # if the temporary frame exists but the variable isn't in it
        elif re.match(r"^(TF@).*$", instruct.args[0].name[0:3]) and not instruct.args[0].name[3:] in tempFrame:
            quit(54)
        # if the variable in the local frame
        if re.match(r"^(LF@).*$", instruct.args[0].name[0:3]) and instruct.args[0].name[3:] in localFrame[-1]:
            localFrame[-1].update({instruct.args[0].name[3:]: str(int(symb1) // int(symb2))})
            return
        # if the local frame doesn't exist
        elif re.match(r"^(LF@).*$", instruct.args[0].name[0:3]) and not localFrame:
            quit(55)
        # if the local frame exists but the variable isn't in it
        elif re.match(r"^(TF@).*$", instruct.args[0].name[0:3]) and not instruct.args[0].name[3:] in tempFrame:
            quit(54)


def lt(instruct, interpret):
    global globalFrame, tempFrame, localFrame

    if interpret == 0:
        check_num(len(instruct.args), 3)
        vars = ['var', 'symb', 'symb']
        check_vars(vars, instruct.args)
        check_data(instruct.args)
    elif interpret == 1:
        symb1 = None
        symb2 = None
        # if the first symbol is a variable in the correct frame
        if instruct.args[1].type == "var" and instruct.args[1].name[3:] in globalFrame:
            symb1 = globalFrame[instruct.args[1].name[3:]]
        # if the first symbol is a variable but isn't in the correct frame
        elif instruct.args[1].type == "var":
            quit(54)
        # if the first symbol isn't a variable
        else:
            symb1 = instruct.args[1].name
        # if the second symbol is a variable in the correct frame
        if instruct.args[2].type == "var" and instruct.args[2].name[3:] in globalFrame:
            symb2 = globalFrame[instruct.args[2].name[3:]]
        # if the second symbol is a variable but isn't in the correct frame
        elif instruct.args[2].type == "var":
            quit(54)
        # if the second symbol isn't a variable
        else:
            symb2 = instruct.args[1].name
        # if the destination variable is in the correct frame
        if frame == "G" and instruct.args[0].name[3:] in globalFrame:
            # if both symbols are int
            if symb1.isdigit() and symb2.isdigit():
                # if the comparison is true
                if symb1 < symb2:
                    globalFrame.update({instruct.args[0].name[3:]: "true"})
                else:
                    globalFrame.update({instruct.args[0].name[3:]: "false"})
            # if both symbols are bool
            elif re.match(r"^(true|TRUE|false|FALSE)$", symb1) and re.match(r"^(true|TRUE|false|FALSE)$", symb2):
                # if the comparison is true
                if re.match(r"^(true|TRUE)$", symb1) and re.match(r"^(false|FALSE)$", symb2):
                    globalFrame.update({instruct.args[0].name[3:]: "true"})
                else:
                    globalFrame.update({instruct.args[0].name[3:]: "false"})


def gt(instruct, interpret):
    global globalFrame, tempFrame, localFrame

    if interpret == 0:
        check_num(len(instruct.args), 3)
        vars = ['var', 'symb', 'symb']
        check_vars(vars, instruct.args)
        check_data(instruct.args)
    elif interpret == 1:
        symb1 = None
        symb2 = None
        # if the first symbol is a variable in the correct frame
        if instruct.args[1].type == "var" and instruct.args[1].name[3:] in globalFrame:
            symb1 = globalFrame[instruct.args[1].name[3:]]
        # if the first symbol is a variable but isn't in the correct frame
        elif instruct.args[1].type == "var":
            quit(54)
        # if the first symbol isn't a variable
        else:
            symb1 = instruct.args[1].name
        # if the second symbol is a variable in the correct frame
        if instruct.args[2].type == "var" and instruct.args[2].name[3:] in globalFrame:
            symb2 = globalFrame[instruct.args[2].name[3:]]
        # if the second symbol is a variable but isn't in the correct frame
        elif instruct.args[2].type == "var":
            quit(54)
        # if the second symbol isn't a variable
        else:
            symb2 = instruct.args[1].name
        # if the destination variable is in the correct frame
        if frame == "G" and instruct.args[0].name[3:] in globalFrame:
            # if both symbols are int
            if symb1.isdigit() and symb2.isdigit():
                # if the comparison is true
                if symb1 > symb2:
                    globalFrame.update({instruct.args[0].name[3:]: "true"})
                else:
                    globalFrame.update({instruct.args[0].name[3:]: "false"})
            # if both symbols are bool
            elif re.match(r"^(true|TRUE|false|FALSE)$", symb1) and re.match(r"^(true|TRUE|false|FALSE)$", symb2):
                # if the comparison is true
                if re.match(r"^(false|FALSE)$", symb1) and re.match(r"^(true|TRUE)$", symb2):
                    globalFrame.update({instruct.args[0].name[3:]: "true"})
                else:
                    globalFrame.update({instruct.args[0].name[3:]: "false"})


def eq(instruct, interpret):
    global globalFrame, tempFrame, localFrame

    if interpret == 0:
        check_num(len(instruct.args), 3)
        vars = ['var', 'symb', 'symb']
        check_vars(vars, instruct.args)
        check_data(instruct.args)
    elif interpret == 1:
        symb1 = None
        symb2 = None
        # if the first symbol is a variable in the correct frame
        if instruct.args[1].type == "var" and instruct.args[1].name[3:] in globalFrame:
            symb1 = globalFrame[instruct.args[1].name[3:]]
        # if the first symbol is a variable but isn't in the correct frame
        elif instruct.args[1].type == "var":
            quit(54)
        # if the first symbol isn't a variable
        else:
            symb1 = instruct.args[1].name
        # if the second symbol is a variable in the correct frame
        if instruct.args[2].type == "var" and instruct.args[2].name[3:] in globalFrame:
            symb2 = globalFrame[instruct.args[2].name[3:]]
        # if the second symbol is a variable but isn't in the correct frame
        elif instruct.args[2].type == "var":
            quit(54)
        # if the second symbol isn't a variable
        else:
            symb2 = instruct.args[1].name
        # if the destination variable is in the correct frame
        if frame == "G" and instruct.args[0].name[3:] in globalFrame:
            # if both symbols are int
            if symb1.isdigit() and symb2.isdigit():
                # if the comparison is true
                if symb1 == symb2:
                    globalFrame.update({instruct.args[0].name[3:]: "true"})
                else:
                    globalFrame.update({instruct.args[0].name[3:]: "false"})
            # if both symbols are bool
            elif re.match(r"^(true|TRUE|false|FALSE)$", symb1) and re.match(r"^(true|TRUE|false|FALSE)$", symb2):
                # if the comparison is true
                if (re.match(r"^(true|TRUE)$", symb1) and re.match(r"^(true|TRUE)$", symb2)) or (re.match(r"^(false|FALSE)$", symb1) and re.match(r"^(false|FALSE)$", symb2)):
                    globalFrame.update({instruct.args[0].name[3:]: "true"})
                else:
                    globalFrame.update({instruct.args[0].name[3:]: "false"})


def _and(instruct, interpret):
    global globalFrame, tempFrame, localFrame

    if interpret == 0:
        check_num(len(instruct.args), 3)
        vars = ['var', 'symb', 'symb']
        check_vars(vars, instruct.args)
        check_data(instruct.args)
    elif interpret == 1:
        symb1 = None
        symb2 = None
        if frame == "G" and instruct.args[0].name[3:] in globalFrame:
            # if the first symbol is a variable in the correct frame
            if instruct.args[1].type == "var" and instruct.args[1].name[3:] in globalFrame:
                # if the variable is the correct type
                if re.match(r"^(true|TRUE|false|FALSE)$", globalFrame[instruct.args[1].name[3:]]):
                    symb1 = globalFrame[instruct.args[1].name[3:]]
                # if the variable isn't the correct type
                else:
                    quit(53)
            # if the first symbol is a variable but isn't in the correct frame
            elif instruct.args[1].type == "var":
                quit(54)
            # if the first symbol is a bool
            elif instruct.args[1].type == "bool" and re.match(r"^(true|TRUE|false|FALSE)$", instruct.args[1].name):
                symb1 = instruct.args[1].name
            # if the type of the first symbol is incorrect
            else:
                quit(53)
            # if the second symbol is a variable in the correct frame
            if instruct.args[2].type == "var" and instruct.args[2].name[3:] in globalFrame:
                # if the variable is the correct type
                if re.match(r"^(true|TRUE|false|FALSE)$", globalFrame[instruct.args[2].name[3:]]):
                    symb2 = globalFrame[instruct.args[2].name[3:]]
                # if the variable isn't the correct type
                else:
                    quit(53)
            # if the second symbol is a variable but isn't in the correct frame
            elif instruct.args[2].type == "var":
                quit(54)
            # if the second symbol is a bool
            elif instruct.args[2].type == "bool" and re.match(r"^(true|TRUE|false|FALSE)$", instruct.args[2].name):
                symb2 = instruct.args[2].name
            # if the type of the second symbol is incorrect
            else:
                quit(53)
            # applying the AND operation
            if re.match(r"^(true|TRUE)$", symb1) and re.match(r"^(true|TRUE)$", symb2):
                globalFrame.update({instruct.args[0].name[3:]: "true"})
            else:
                globalFrame.update({instruct.args[0].name[3:]: "false"})


def _or(instruct, interpret):
    global globalFrame, tempFrame, localFrame

    if interpret == 0:
        check_num(len(instruct.args), 3)
        vars = ['var', 'symb', 'symb']
        check_vars(vars, instruct.args)
        check_data(instruct.args)
    elif interpret == 1:
        symb1 = None
        symb2 = None
        if frame == "G" and instruct.args[0].name[3:] in globalFrame:
            # if the first symbol is a variable in the correct frame
            if instruct.args[1].type == "var" and instruct.args[1].name[3:] in globalFrame:
                # if the variable is the correct type
                if re.match(r"^(true|TRUE|false|FALSE)$", globalFrame[instruct.args[1].name[3:]]):
                    symb1 = globalFrame[instruct.args[1].name[3:]]
                # if the variable isn't the correct type
                else:
                    quit(53)
            # if the first symbol is a variable but isn't in the correct frame
            elif instruct.args[1].type == "var":
                quit(54)
            # if the first symbol is a bool
            elif instruct.args[1].type == "bool" and re.match(r"^(true|TRUE|false|FALSE)$", instruct.args[1].name):
                symb1 = instruct.args[1].name
            # if the type of the first symbol is incorrect
            else:
                quit(53)
            # if the second symbol is a variable in the correct frame
            if instruct.args[2].type == "var" and instruct.args[2].name[3:] in globalFrame:
                # if the variable is the correct type
                if re.match(r"^(true|TRUE|false|FALSE)$", globalFrame[instruct.args[2].name[3:]]):
                    symb2 = globalFrame[instruct.args[2].name[3:]]
                # if the variable isn't the correct type
                else:
                    quit(53)
            # if the second symbol is a variable but isn't in the correct frame
            elif instruct.args[2].type == "var":
                quit(54)
            # if the second symbol is a bool
            elif instruct.args[2].type == "bool" and re.match(r"^(true|TRUE|false|FALSE)$", instruct.args[2].name):
                symb2 = instruct.args[2].name
            # if the type of the second symbol is incorrect
            else:
                quit(53)
            # applying the OR operation
            if re.match(r"^(true|TRUE)$", symb1) or re.match(r"^(true|TRUE)$", symb2):
                globalFrame.update({instruct.args[0].name[3:]: "true"})
            else:
                globalFrame.update({instruct.args[0].name[3:]: "false"})


def _not(instruct, interpret):
    global globalFrame, tempFrame, localFrame

    if interpret == 0:
        check_num(len(instruct.args), 3)
        vars = ['var', 'symb', 'symb']
        check_vars(vars, instruct.args)
        check_data(instruct.args)
    elif interpret == 1:
        symb1 = None
        if frame == "G" and instruct.args[0].name[3:] in globalFrame:
            # if the first symbol is a variable in the correct frame
            if instruct.args[1].type == "var" and instruct.args[1].name[3:] in globalFrame:
                # if the variable is the correct type
                if re.match(r"^(true|TRUE|false|FALSE)$", globalFrame[instruct.args[1].name[3:]]):
                    symb1 = globalFrame[instruct.args[1].name[3:]]
                # if the variable isn't the correct type
                else:
                    quit(53)
            # if the first symbol is a variable but isn't in the correct frame
            elif instruct.args[1].type == "var":
                quit(54)
            # if the first symbol is a bool
            elif instruct.args[1].type == "bool" and re.match(r"^(true|TRUE|false|FALSE)$", instruct.args[1].name):
                symb1 = instruct.args[1].name
            # if the type of the first symbol is incorrect
            else:
                quit(53)
            # applying the NOT operation
            if re.match(r"^(true|TRUE)$", symb1):
                globalFrame.update({instruct.args[0].name[3:]: "false"})
            else:
                globalFrame.update({instruct.args[0].name[3:]: "true"})


def int2char(instruct, interpret):
    global globalFrame, tempFrame, localFrame

    if interpret == 0:
        check_num(len(instruct.args), 2)
        vars = ['var', 'symb']
        check_vars(vars, instruct.args)
        check_data(instruct.args)
    elif interpret == 1:
        int = None
        if frame == "G" and instruct.args[0].name[3:] in globalFrame:
            # if the symbol is a variable in the correct frame
            if instruct.args[1].type == "var" and instruct.args[1].name[3:] in globalFrame:
                # if the variable is the correct type
                if globalFrame[instruct.args[1].name[3:]].isdigit():
                    int = globalFrame[instruct.args[1].name[3:]]
                # if the variable isn't the correct type
                else:
                    quit(53)
            # if the symbol is a variable but isn't in the correct frame
            elif instruct.args[1].type == "var":
                quit(54)
            # if the symbol is an integer
            elif instruct.args[1].type == "int" and instruct.args[1].name.isdigit():
                int = instruct.args[1].name
            # if the type of the symbol is incorrect
            else:
                quit(53)
            # if the symbol is in the correct value range
            if int(int) >= 0 and int(int) <= 1114111:
                globalFrame.update({instruct.args[0].name[3:]: chr(int(int))})
            # if the symbol isn't in the correct range
            else:
                quit(58)


def stri2int(instruct, interpret):
    global globalFrame, tempFrame, localFrame

    if interpret == 0:
        check_num(len(instruct.args), 3)
        vars = ['var', 'symb', 'symb']
        check_vars(vars, instruct.args)
        check_data(instruct.args)
    elif interpret == 1:
        if frame == "G" and instruct.args[0].name[3:] in globalFrame:
            # if the first symbol is a variable in the correct frame
            if instruct.args[1].type == "var" and instruct.args[1].name[3:] in globalFrame:
                string = globalFrame[instruct.args[1].name[3:]]
            # if the first symbol is a variable but isn't in the correct frame
            elif instruct.args[1].type == "var":
                quit(54)
            # if the first symbol is a string
            elif instruct.args[1].type == "string":
                string = instruct.args[1].name
            # if the type of the first symbol is incorrect
            else:
                quit(53)
            # if the second symbol is a variable in the correct frame
            if instruct.args[2].type == "var" and instruct.args[2].name[3:] in globalFrame:
                integer = globalFrame[instruct.args[2].name[3:]]
            # if the second symbol is a variable but isn't in the correct frame
            elif instruct.args[2].type == "var":
                quit(54)
            elif instruct.args[2].type == "int" and (int(instruct.args[2].name) < 0 or int(instruct.args[2].name) >= len(string)):
                quit(58)
            # if the second symbol is an integer
            elif instruct.args[2].type == "int" and instruct.args[2].name.isdigit():
                integer = instruct.args[2].name
            # if the type of the second symbol is incorrect
            else:
                quit(53)
            globalFrame.update({instruct.args[0].name[3:]: ord(string[integer:integer + 1])})
        else:
            quit(54)


def read(instruct, interpret):
    if interpret == 0:
        check_num(len(instruct.args), 2)
        vars = ['var', 'type']
        check_vars(vars, instruct.args)
        check_data(instruct.args)


def write(instruct, interpret):
    global globalFrame, tempFrame, localFrame

    if interpret == 0:
        check_num(len(instruct.args), 1)
        vars = ['symb']
        check_vars(vars, instruct.args)
        check_data(instruct.args)
    elif interpret == 1:
        value = None
        # if the symbol is a variable in the global frame
        if instruct.args[0].type == "var" and re.match(r"^(GF@).*$", instruct.args[0].name[0:3]) \
                and instruct.args[0].name[3:] in globalFrame:
            value = globalFrame[instruct.args[0].name[3:]]
        # if the symbol is a variable in the temporary frame
        elif instruct.args[0].type == "var" and re.match(r"^(TF@).*$", instruct.args[0].name[0:3]) \
                and instruct.args[0].name[3:] in tempFrame:
            value = tempFrame[instruct.args[0].name[3:]]
        # if the symbol is a variable in the local frame
        elif instruct.args[0].type == "var" and re.match(r"^(LF@).*$", instruct.args[0].name[0:3]) \
                and instruct.args[0].name[3:] in localFrame[-1]:
            value = localFrame[-1][instruct.args[0].name[3:]]
        # if the symbol is a variable but isn't in the global frame
        elif re.match(r"^(GF@).*$", instruct.args[0].name[0:3]) and not instruct.args[0].name[3:] in globalFrame:
            quit(54)
        # if the symbol is a variable but isn't in the temporary frame
        elif re.match(r"^(TF@).*$", instruct.args[0].name[0:3]) and not instruct.args[0].name[3:] in tempFrame:
            quit(54)
        # if the temporary frame doesn't exist
        elif re.match(r"^(TF@).*$", instruct.args[0].name[0:3]) and not tempFrame:
            quit(55)
        # if the symbol is a variable but isn't in the local frame
        elif re.match(r"^(LF@).*$", instruct.args[0].name[0:3]) and not instruct.args[0].name[3:] in localFrame[-1]:
            quit(54)
        # if the local frame doesn't exist
        elif re.match(r"^(LF@).*$", instruct.args[0].name[0:3]) and not localFrame:
            quit(55)
        # if the symbol isn't a variable
        else:
            value = instruct.args[0].name
        # performing the PRINT operation
        print_out(value, "std")


def concat(instruct, interpret):
    global globalFrame, tempFrame, localFrame

    if interpret == 0:
        check_num(len(instruct.args), 3)
        vars = ['var', 'symb', 'symb']
        check_vars(vars, instruct.args)
        check_data(instruct.args)
    elif interpret == 1:
        symb1 = None
        symb2 = None
        if frame == "G" and instruct.args[0].name[3:] in globalFrame:
            # if the first symbol is a variable in the correct frame
            if instruct.args[1].type == "var" and instruct.args[1].name[3:] in globalFrame:
                symb1 = globalFrame[instruct.args[1].name[3:]]
            # if the first symbol is a variable but isn't in the correct frame
            elif instruct.args[1].type == "var":
                quit(54)
            # if the first symbol is a string
            elif instruct.args[1].type == "string":
                symb1 = instruct.args[1].name
            # if the type of the first symbol is incorrect
            else:
                quit(53)
            # if the second symbol is a variable in the correct frame
            if instruct.args[2].type == "var" and instruct.args[2].name[3:] in globalFrame:
                symb2 = globalFrame[instruct.args[2].name[3:]]
            # if the second symbol is a variable but isn't in the correct frame
            elif instruct.args[2].type == "var":
                quit(54)
            # if the second symbol is a string
            elif instruct.args[1].type == "string":
                symb2 = instruct.args[1].name
            # if the type of the second symbol is incorrect
            else:
                quit(53)
            # performing the CONCAT operation
            globalFrame.update({instruct.args[0].name[3:]: symb1 + symb2})


def strlen(instruct, interpret):
    global globalFrame, tempFrame, localFrame

    if interpret == 0:
        check_num(len(instruct.args), 2)
        vars = ['var', 'symb']
        check_vars(vars, instruct.args)
        check_data(instruct.args)
    elif interpret == 1:
        symb = None
        dest = None
        # if the symbol is a variable in the global frame
        if instruct.args[1].type == "var" and re.match(r"^(GF@).*$", instruct.args[1].name[0:3]) \
                and instruct.args[1].name[3:] in globalFrame:
            symb = globalFrame[instruct.args[1].name[3:]]
        # if the symbol is a variable in the temporary frame
        elif instruct.args[1].type == "var" and re.match(r"^(TF@).*$", instruct.args[1].name[0:3]) \
                and instruct.args[1].name[3:] in tempFrame:
            symb = tempFrame[instruct.args[1].name[3:]]
        # if the symbol is a variable in the local frame
        elif instruct.args[1].type == "var" and re.match(r"^(LF@).*$", instruct.args[1].name[0:3]) \
                and instruct.args[1].name[3:] in localFrame[-1]:
            symb = localFrame[-1][instruct.args[1].name[3:]]
        # if the symbol is a variable but isn't in the temporary frame
        elif re.match(r"^(TF@).*$", instruct.args[1].name[0:3]) and not instruct.args[1].name[3:] in tempFrame:
            quit(54)
        # if the temporary frame doesn't exist
        elif re.match(r"^(TF@).*$", instruct.args[1].name[0:3]) and not tempFrame:
            quit(55)
        # if the symbol is a variable but isn't in the local frame
        elif re.match(r"^(LF@).*$", instruct.args[1].name[0:3]) and not instruct.args[1].name[3:] in localFrame[-1]:
            quit(54)
        # if the local frame doesn't exist
        elif re.match(r"^(LF@).*$", instruct.args[1].name[0:3]) and not localFrame:
            quit(55)
        # if the first symbol is a string
        elif instruct.args[1].type == "string":
            symb = instruct.args[1].name
        # if the type of the first symbol is incorrect
        else:
            quit(53)
        # if the variable is in the global frame
        if re.match(r"^(GF@).*$", instruct.args[0].name[0:3]) and instruct.args[0].name[3:] in globalFrame:
            dest = globalFrame
        # if the variable isn't in the global frame
        elif re.match(r"^(GF@).*$", instruct.args[0].name[0:3]) and not instruct.args[0].name[3:] in globalFrame:
            quit(54)
        # if the variable is in the temporary frame
        elif re.match(r"^(TF@).*$", instruct.args[0].name[0:3]) and instruct.args[0].name[3:] in tempFrame:
            dest = tempFrame
        # if the temporary frame doesn't exist
        elif re.match(r"^(TF@).*$", instruct.args[0].name[0:3]) and not tempFrame:
            quit(55)
        # if the variable isn't in the temporary frame
        elif re.match(r"^(TF@).*$", instruct.args[0].name[0:3]) and not instruct.args[0].name[3:] in tempFrame:
            quit(54)
        # if the variable is in the local frame
        elif re.match(r"^(LF@).*$", instruct.args[0].name[0:3]) and instruct.args[0].name[3:] in localFrame[-1]:
            dest = localFrame[-1]
        # if the local frame doesn't exist
        elif re.match(r"^(LF@).*$", instruct.args[0].name[0:3]) and not localFrame:
            quit(55)
        # if the variable isn't in the local frame
        elif re.match(r"^(LF@).*$", instruct.args[0].name[0:3]) and not instruct.args[0].name[3:] in localFrame[-1]:
            quit(54)
        # performs the STRLEN function
        else:
            dest.update({instruct.args[0].name[3:]: len(symb)})


def getchar(instruct, interpret):
    global globalFrame, tempFrame, localFrame

    if interpret == 0:
        check_num(len(instruct.args), 3)
        vars = ['var', 'symb', 'symb']
        check_vars(vars, instruct.args)
        check_data(instruct.args)
    elif interpret == 1:
        symb1 = None
        symb2 = None
        dest = None
        # if the symbol is a variable in the global frame
        if instruct.args[1].type == "var" and re.match(r"^(GF@).*$", instruct.args[1].name[0:3]) \
                and instruct.args[1].name[3:] in globalFrame:
            symb1 = globalFrame[instruct.args[1].name[3:]]
        # if the symbol is a variable in the temporary frame
        elif instruct.args[1].type == "var" and re.match(r"^(TF@).*$", instruct.args[1].name[0:3]) \
                and instruct.args[1].name[3:] in tempFrame:
            symb1 = tempFrame[instruct.args[1].name[3:]]
        # if the symbol is a variable in the local frame
        elif instruct.args[1].type == "var" and re.match(r"^(LF@).*$", instruct.args[1].name[0:3]) \
                and instruct.args[1].name[3:] in localFrame[-1]:
            symb1 = localFrame[-1][instruct.args[1].name[3:]]
        # if the symbol is a variable but isn't in the temporary frame
        elif re.match(r"^(TF@).*$", instruct.args[1].name[0:3]) and not instruct.args[1].name[3:] in tempFrame:
            quit(54)
        # if the temporary frame doesn't exist
        elif re.match(r"^(TF@).*$", instruct.args[1].name[0:3]) and not tempFrame:
            quit(55)
        # if the symbol is a variable but isn't in the local frame
        elif re.match(r"^(LF@).*$", instruct.args[1].name[0:3]) and not instruct.args[1].name[3:] in localFrame[-1]:
            quit(54)
        # if the local frame doesn't exist
        elif re.match(r"^(LF@).*$", instruct.args[1].name[0:3]) and not localFrame:
            quit(55)
        # if the first symbol is a string
        elif instruct.args[1].type == "string":
            symb1 = instruct.args[1].name
        # if the type of the first symbol is incorrect
        else:
            quit(53)
        # if the second symbol is a variable in the global frame
        if instruct.args[2].type == "var" and re.match(r"^(GF@).*$", instruct.args[2].name[0:3]) \
                and instruct.args[2].name[3:] in globalFrame:
            # if the variable is an integer
            if globalFrame[instruct.args[2].name[3:]].isdigit():
                symb2 = globalFrame[instruct.args[2].name[3:]]
            else:
                quit(53)
        # if the second symbol is a variable in the temporary frame
        elif instruct.args[2].type == "var" and re.match(r"^(TF@).*$", instruct.args[2].name[0:3]) \
                and instruct.args[2].name[3:] in tempFrame:
            # if the variable is an integer
            if tempFrame[instruct.args[2].name[3:]].isdigit():
                symb2 = tempFrame[instruct.args[2].name[3:]]
            else:
                quit(53)
        # if the second symbol is a variable in the local frame
        elif instruct.args[2].type == "var" and re.match(r"^(LF@).*$", instruct.args[2].name[0:3]) \
                and instruct.args[2].name[3:] in localFrame[-1]:
            # if the variable is an integer
            if localFrame[-1][instruct.args[2].name[3:]].isdigit():
                symb2 = localFrame[-1][instruct.args[2].name[3:]]
            else:
                quit(53)
        # if the symbol is a variable but isn't in the temporary frame
        elif re.match(r"^(TF@).*$", instruct.args[2].name[0:3]) and not instruct.args[2].name[3:] in tempFrame:
            quit(54)
        # if the temporary frame doesn't exist
        elif re.match(r"^(TF@).*$", instruct.args[2].name[0:3]) and not tempFrame:
            quit(55)
        # if the symbol is a variable but isn't in the local frame
        elif re.match(r"^(LF@).*$", instruct.args[2].name[0:3]) and not instruct.args[2].name[3:] in localFrame[-1]:
            quit(54)
        # if the local frame doesn't exist
        elif re.match(r"^(LF@).*$", instruct.args[2].name[0:3]) and not localFrame:
            quit(55)
        # if the second symbol is an integer
        elif instruct.args[2].type == "int" and instruct.args[2].name.isdigit():
            symb2 = instruct.args[2].name
        # if the type of the second symbol is incorrect
        else:
            quit(53)
        # if the variable is in the global frame
        if re.match(r"^(GF@).*$", instruct.args[0].name[0:3]) and instruct.args[0].name[3:] in globalFrame:
            dest = globalFrame
        # if the variable isn't in the global frame
        elif re.match(r"^(GF@).*$", instruct.args[0].name[0:3]) and not instruct.args[0].name[3:] in globalFrame:
            quit(54)
        # if the variable is in the temporary frame
        elif re.match(r"^(TF@).*$", instruct.args[0].name[0:3]) and instruct.args[0].name[3:] in tempFrame:
            dest = tempFrame
        # if the temporary frame doesn't exist
        elif re.match(r"^(TF@).*$", instruct.args[0].name[0:3]) and not tempFrame:
            quit(55)
        # if the variable isn't in the temporary frame
        elif re.match(r"^(TF@).*$", instruct.args[0].name[0:3]) and not instruct.args[0].name[3:] in tempFrame:
            quit(54)
        # if the variable is in the local frame
        elif re.match(r"^(LF@).*$", instruct.args[0].name[0:3]) and instruct.args[0].name[3:] in localFrame[-1]:
            dest = localFrame[-1]
        # if the local frame doesn't exist
        elif re.match(r"^(LF@).*$", instruct.args[0].name[0:3]) and not localFrame:
            quit(55)
        # if the variable isn't in the local frame
        elif re.match(r"^(LF@).*$", instruct.args[0].name[0:3]) and not instruct.args[0].name[3:] in localFrame[-1]:
            quit(54)
        # if the index isn't outside of the string performs the GETCHAR operation
        if int(symb2) >= 0 and int(symb2) < len(symb1):
            dest.update({instruct.args[0].name[3:]: symb1[int(symb2):int(symb2) + 1]})
        # if the index is outside of the string
        else:
            quit(58)


def setchar(instruct, interpret):
    global globalFrame, tempFrame, localFrame

    if interpret == 0:
        check_num(len(instruct.args), 3)
        vars = ['var', 'symb', 'symb']
        check_vars(vars, instruct.args)
        check_data(instruct.args)
    elif interpret == 1:
        symb1 = None
        symb2 = None
        dest = None
        # if the symbol is a variable in the global frame
        if instruct.args[1].type == "var" and re.match(r"^(GF@).*$", instruct.args[1].name[0:3]) \
                and instruct.args[1].name[3:] in globalFrame:
            # if the variable is an integer
            if globalFrame[instruct.args[1].name[3:]].isdigit():
                symb1 = globalFrame[instruct.args[1].name[3:]]
            else:
                quit(53)
        # if the symbol is a variable in the temporary frame
        elif instruct.args[1].type == "var" and re.match(r"^(TF@).*$", instruct.args[1].name[0:3]) \
                and instruct.args[1].name[3:] in tempFrame:
            # if the variable is an integer
            if tempFrame[instruct.args[1].name[3:]].isdigit():
                symb1 = tempFrame[instruct.args[1].name[3:]]
            else:
                quit(53)
        # if the symbol is a variable in the local frame
        elif instruct.args[1].type == "var" and re.match(r"^(LF@).*$", instruct.args[1].name[0:3]) \
                and instruct.args[1].name[3:] in localFrame[-1]:
            # if the variable is an integer
            if localFrame[-1][instruct.args[1].name[3:]].isdigit():
                symb1 = localFrame[-1][instruct.args[1].name[3:]]
            else:
                quit(53)
        # if the symbol is a variable but isn't in the temporary frame
        elif re.match(r"^(TF@).*$", instruct.args[1].name[0:3]) and not instruct.args[1].name[3:] in tempFrame:
            quit(54)
        # if the temporary frame doesn't exist
        elif re.match(r"^(TF@).*$", instruct.args[1].name[0:3]) and not tempFrame:
            quit(55)
        # if the symbol is a variable but isn't in the local frame
        elif re.match(r"^(LF@).*$", instruct.args[1].name[0:3]) and not instruct.args[1].name[3:] in localFrame[-1]:
            quit(54)
        # if the local frame doesn't exist
        elif re.match(r"^(LF@).*$", instruct.args[1].name[0:3]) and not localFrame:
            quit(55)
        # if the first symbol is a string
        elif instruct.args[1].type == "int" and instruct.args[1].name.isdigit():
            symb1 = instruct.args[1].name
        # if the type of the first symbol is incorrect
        else:
            quit(53)
        # if the second symbol is a variable in the global frame
        if instruct.args[2].type == "var" and re.match(r"^(GF@).*$", instruct.args[2].name[0:3]) \
                and instruct.args[2].name[3:] in globalFrame:
            symb2 = globalFrame[instruct.args[2].name[3:]]
        # if the second symbol is a variable in the temporary frame
        elif instruct.args[2].type == "var" and re.match(r"^(TF@).*$", instruct.args[2].name[0:3]) \
                and instruct.args[2].name[3:] in tempFrame:
            symb2 = tempFrame[instruct.args[2].name[3:]]
        # if the second symbol is a variable in the local frame
        elif instruct.args[2].type == "var" and re.match(r"^(LF@).*$", instruct.args[2].name[0:3]) \
                and instruct.args[2].name[3:] in localFrame[-1]:
            symb2 = localFrame[-1][instruct.args[2].name[3:]]
        # if the symbol is a variable but isn't in the temporary frame
        elif re.match(r"^(TF@).*$", instruct.args[2].name[0:3]) and not instruct.args[2].name[3:] in tempFrame:
            quit(54)
        # if the temporary frame doesn't exist
        elif re.match(r"^(TF@).*$", instruct.args[2].name[0:3]) and not tempFrame:
            quit(55)
        # if the symbol is a variable but isn't in the local frame
        elif re.match(r"^(LF@).*$", instruct.args[2].name[0:3]) and not instruct.args[2].name[3:] in localFrame[-1]:
            quit(54)
        # if the local frame doesn't exist
        elif re.match(r"^(LF@).*$", instruct.args[2].name[0:3]) and not localFrame:
            quit(55)
        # if the second symbol is an integer
        elif instruct.args[2].type == "string":
            symb2 = instruct.args[2].name
        # if the type of the second symbol is incorrect
        else:
            quit(53)
        # if the variable is in the global frame
        if re.match(r"^(GF@).*$", instruct.args[0].name[0:3]) and instruct.args[0].name[3:] in globalFrame:
            dest = globalFrame
        # if the variable isn't in the global frame
        elif re.match(r"^(GF@).*$", instruct.args[0].name[0:3]) and not instruct.args[0].name[3:] in globalFrame:
            quit(54)
        # if the variable is in the temporary frame
        elif re.match(r"^(TF@).*$", instruct.args[0].name[0:3]) and instruct.args[0].name[3:] in tempFrame:
            dest = tempFrame
        # if the temporary frame doesn't exist
        elif re.match(r"^(TF@).*$", instruct.args[0].name[0:3]) and not tempFrame:
            quit(55)
        # if the variable isn't in the temporary frame
        elif re.match(r"^(TF@).*$", instruct.args[0].name[0:3]) and not instruct.args[0].name[3:] in tempFrame:
            quit(54)
        # if the variable is in the local frame
        elif re.match(r"^(LF@).*$", instruct.args[0].name[0:3]) and instruct.args[0].name[3:] in localFrame[-1]:
            dest = localFrame[-1]
        # if the local frame doesn't exist
        elif re.match(r"^(LF@).*$", instruct.args[0].name[0:3]) and not localFrame:
            quit(55)
        # if the variable isn't in the local frame
        elif re.match(r"^(LF@).*$", instruct.args[0].name[0:3]) and not instruct.args[0].name[3:] in localFrame[-1]:
            quit(54)
        # if the index isn't outside of the string performs the SETCHAR operation
        if int(symb1) >= 0 and int(symb1) < len(dest[instruct.args[0].name[3:]]):
            tmp = dest[instruct.args[0].name[3:]]
            new = "".join((tmp[int(symb1)], symb2[0:1], tmp[int(symb1)]))
            dest.update({instruct.args[0].name[3:]: new})
        # if the index is outside of the string
        else:
            quit(58)


def type(instruct, interpret):
    global globalFrame, tempFrame, localFrame

    if interpret == 0:
        check_num(len(instruct.args), 2)
        vars = ['var', 'symb']
        check_vars(vars, instruct.args)
        check_data(instruct.args)
    elif interpret == 1:
        symb = None
        dest = None
        # if the symbol is a variable in the global frame
        if instruct.args[1].type == "var" and re.match(r"^(GF@).*$", instruct.args[1].name[0:3]) \
                and instruct.args[1].name[3:] in globalFrame:
            symb = globalFrame[instruct.args[1].name[3:]]
        # if the symbol is a variable in the temporary frame
        elif instruct.args[1].type == "var" and re.match(r"^(TF@).*$", instruct.args[1].name[0:3]) \
                and instruct.args[1].name[3:] in tempFrame:
            symb = tempFrame[instruct.args[1].name[3:]]
        # if the symbol is a variable in the local frame
        elif instruct.args[1].type == "var" and re.match(r"^(LF@).*$", instruct.args[1].name[0:3]) \
                and instruct.args[1].name[3:] in localFrame[-1]:
            symb = localFrame[-1][instruct.args[1].name[3:]]
        # if the symbol is a variable but isn't in the temporary frame
        elif re.match(r"^(TF@).*$", instruct.args[1].name[0:3]) and not instruct.args[1].name[3:] in tempFrame:
            quit(54)
        # if the temporary frame doesn't exist
        elif re.match(r"^(TF@).*$", instruct.args[1].name[0:3]) and not tempFrame:
            quit(55)
        # if the symbol is a variable but isn't in the local frame
        elif re.match(r"^(LF@).*$", instruct.args[1].name[0:3]) and not instruct.args[1].name[3:] in localFrame[-1]:
            quit(54)
        # if the local frame doesn't exist
        elif re.match(r"^(LF@).*$", instruct.args[1].name[0:3]) and not localFrame:
            quit(55)
        # if the symbol isn't a variable
        else:
            symb = instruct.args[1].name
        # if the variable is in the global frame
        if re.match(r"^(GF@).*$", instruct.args[0].name[0:3]) and instruct.args[0].name[3:] in globalFrame:
            dest = globalFrame
        # if the variable isn't in the global frame
        elif re.match(r"^(GF@).*$", instruct.args[0].name[0:3]) and not instruct.args[0].name[3:] in globalFrame:
            quit(54)
        # if the variable is in the temporary frame
        elif re.match(r"^(TF@).*$", instruct.args[0].name[0:3]) and instruct.args[0].name[3:] in tempFrame:
            dest = tempFrame
        # if the temporary frame doesn't exist
        elif re.match(r"^(TF@).*$", instruct.args[0].name[0:3]) and not tempFrame:
            quit(55)
        # if the variable isn't in the temporary frame
        elif re.match(r"^(TF@).*$", instruct.args[0].name[0:3]) and not instruct.args[0].name[3:] in tempFrame:
            quit(54)
        # if the variable is in the local frame
        elif re.match(r"^(LF@).*$", instruct.args[0].name[0:3]) and instruct.args[0].name[3:] in localFrame[-1]:
            dest = localFrame[-1]
        # if the local frame doesn't exist
        elif re.match(r"^(LF@).*$", instruct.args[0].name[0:3]) and not localFrame:
            quit(55)
        # if the variable isn't in the local frame
        elif re.match(r"^(LF@).*$", instruct.args[0].name[0:3]) and not instruct.args[0].name[3:] in localFrame[-1]:
            quit(54)
        else:
            # if the symbol is None
            if instruct.args[1].name is None:
                dest.update({instruct.args[0].name[3:]: ""})
            # if the symbol is type nil
            elif instruct.args[1].type == "nil" and re.match(r"^(nil)$", symb):
                dest.update({instruct.args[0].name[3:]: "nil"})
            # if the symbol is an integer
            elif instruct.args[1].type == "int" and re.match(r"^([-|+]?\d+)$", symb):
                dest.update({instruct.args[0].name[3:]: "int"})
            # if the symbol is a bool
            elif instruct.args[1].type == "bool" and re.match(r"^(true|false|TRUE|FALSE)$", symb):
                dest.update({instruct.args[0].name[3:]: "bool"})
            # if the symbol is a string
            elif instruct.args[1].type == "string" and re.match(r"^(([\w]*(\\\\[0-9]{3})*)*)\S*$", symb, flags=re.UNICODE):
                dest.update({instruct.args[0].name[3:]: "string"})


def label(instruct, counter):
    global globalFrame, tempFrame, localFrame

    check_num(len(instruct.args), 1)
    vars = ['label']
    check_vars(vars, instruct.args)
    check_data(instruct.args)

    if not instruct.args[0].name in labels:
        labels.update({instruct.args[0].name: counter})
    else:
        quit(52)


def jump(instruct, interpret):
    if interpret == 0:
        check_num(len(instruct.args), 1)
        vars = ['label']
        check_vars(vars, instruct.args)
        check_data(instruct.args)
    if interpret == 1:
        if instruct.args[0].name in labels:
            print("its here")


def jumpifeq(instruct, interpret):
    if interpret == 0:
        check_num(len(instruct.args), 3)
        vars = ['label', 'symb', 'symb']
        check_vars(vars, instruct.args)
        check_data(instruct.args)


def jumpifnoteq(instruct, interpret):
    if interpret == 0:
        check_num(len(instruct.args), 3)
        vars = ['label', 'symb', 'symb']
        check_vars(vars, instruct.args)
        check_data(instruct.args)


def exit(instruct, interpret):
    global globalFrame, tempFrame, localFrame

    if interpret == 0:
        check_num(len(instruct.args), 1)
        vars = ['symb']
        check_vars(vars, instruct.args)
        check_data(instruct.args)
    elif interpret == 1:
        code = None
        # if the symbol is a variable in the global frame
        if instruct.args[0].type == "var" and re.match(r"^(GF@).*$", instruct.args[0].name[0:3]) \
                and instruct.args[0].name[3:] in globalFrame:
            code = globalFrame[instruct.args[0].name[3:]]
        # if the symbol is a variable in the temporary frame
        elif instruct.args[0].type == "var" and re.match(r"^(TF@).*$", instruct.args[0].name[0:3]) \
                and instruct.args[0].name[3:] in tempFrame:
            code = tempFrame[instruct.args[0].name[3:]]
        # if the symbol is a variable in the local frame
        elif instruct.args[0].type == "var" and re.match(r"^(LF@).*$", instruct.args[0].name[0:3]) \
                and instruct.args[0].name[3:] in localFrame[-1]:
            code = localFrame[-1][instruct.args[0].name[3:]]
        # if the symbol is a variable but isn't in the global frame
        elif re.match(r"^(GF@).*$", instruct.args[0].name[0:3]) and not instruct.args[0].name[3:] in globalFrame:
            quit(54)
        # if the symbol is a variable but isn't in the temporary frame
        elif re.match(r"^(TF@).*$", instruct.args[0].name[0:3]) and not instruct.args[0].name[3:] in tempFrame:
            quit(54)
        # if the temporary frame doesn't exist
        elif re.match(r"^(TF@).*$", instruct.args[0].name[0:3]) and not tempFrame:
            quit(55)
        # if the symbol is a variable but isn't in the local frame
        elif re.match(r"^(LF@).*$", instruct.args[0].name[0:3]) and not instruct.args[0].name[3:] in localFrame[-1]:
            quit(54)
        # if the local frame doesn't exist
        elif re.match(r"^(LF@).*$", instruct.args[0].name[0:3]) and not localFrame:
            quit(55)
        # if the symbol isn't a variable
        else:
            code = instruct.args[0].name
        # if the symbol is an integer
        if code.isdigit():
            # if the symbol is in the correct range
            if int(code) <= 49 and int(code) >= 0:
                quit(int(code))
            else:
                quit(57)
        else:
            quit(53)


def dprint(instruct, interpret):
    global globalFrame, tempFrame, localFrame

    if interpret == 0:
        check_num(len(instruct.args), 1)
        vars = ['symb']
        check_vars(vars, instruct.args)
        check_data(instruct.args)
    elif interpret == 1:
        value = None
        # if the symbol is a variable in the global frame
        if instruct.args[0].type == "var" and re.match(r"^(GF@).*$", instruct.args[0].name[0:3]) \
                and instruct.args[0].name[3:] in globalFrame:
            value = globalFrame[instruct.args[0].name[3:]]
        # if the symbol is a variable in the temporary frame
        elif instruct.args[0].type == "var" and re.match(r"^(TF@).*$", instruct.args[0].name[0:3]) \
                and instruct.args[0].name[3:] in tempFrame:
            value = tempFrame[instruct.args[0].name[3:]]
        # if the symbol is a variable in the local frame
        elif instruct.args[0].type == "var" and re.match(r"^(LF@).*$", instruct.args[0].name[0:3]) \
                and instruct.args[0].name[3:] in localFrame[-1]:
            value = localFrame[-1][instruct.args[0].name[3:]]
        # if the symbol is a variable but isn't in the global frame
        elif re.match(r"^(GF@).*$", instruct.args[0].name[0:3]) and not instruct.args[0].name[3:] in globalFrame:
            quit(54)
        # if the symbol is a variable but isn't in the temporary frame
        elif re.match(r"^(TF@).*$", instruct.args[0].name[0:3]) and not instruct.args[0].name[3:] in tempFrame:
            quit(54)
        # if the temporary frame doesn't exist
        elif re.match(r"^(TF@).*$", instruct.args[0].name[0:3]) and not tempFrame:
            quit(55)
        # if the symbol is a variable but isn't in the local frame
        elif re.match(r"^(LF@).*$", instruct.args[0].name[0:3]) and not instruct.args[0].name[3:] in localFrame[-1]:
            quit(54)
        # if the local frame doesn't exist
        elif re.match(r"^(LF@).*$", instruct.args[0].name[0:3]) and not localFrame:
            quit(55)
        # if the symbol isn't a variable
        else:
            value = instruct.args[0].name
        # performing the PRINT operation
        print_out(value, "err")


def _break(instruct, interpret):
    if interpret == 0:
        check_num(len(instruct.args), 0)
