import re
import sys

globalFrame = {}
tempFrame = None
localFrame = [{}]
dataStack = []
labels = {}
returnJump = []


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
            if not re.match(r"^(true|false|TRUE|FALSE)$", args[x].name):
                quit(32)
        elif args[x].type == 'var':
            if not re.match(r"^([G|L|T]F@)[\w|\d|_|-|$|&|%|*|!|?]+$", args[x].name, flags=re.UNICODE):
                quit(32)
        elif args[x].type == 'nil':
            if not re.match(r"^(nil)$", args[x].name):
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
    # if the DPRINT or BREAK instruction is called print to stderr
    if out == "err":
        file = sys.stderr
    # if the WRITE instruction is called print to stdout
    else:
        file = sys.stdout

    # if the text to print is a dictionary or a list
    if isinstance(text, dict) or isinstance(text, list):
        for elem in text:
            print(elem, end='', file=file)
    # if the text to print is a bool
    elif isinstance(text, bool):
        print(text, end='', file=file)
    # if the text to print is an integer
    elif isinstance(text, int):
        print(text, end='', file=file)
    # if the text to print is a string
    else:
        i = 0
        while i < len(text):
            if text[i] == "\\":
                print(chr(int(text[i+2:i+4])), end='', file=file)
                i += 4
            else:
                print(text[i], end='', file=file)
                i += 1


def check_symb(symbol):
    global globalFrame, tempFrame, localFrame

    if symbol.name is None:
        return set_type("")
    # if the symbol is a GF variable in the global frame return it
    elif symbol.type == "var" and re.match(r"^(GF@).*$", symbol.name[0:3]) \
            and symbol.name[3:] in globalFrame:
        return globalFrame[symbol.name[3:]]
    # if the symbol is a TF variable in the temporary frame return it
    elif symbol.type == "var" and re.match(r"^(TF@).*$", symbol.name[0:3]) \
            and symbol.name[3:] in tempFrame:
        return tempFrame[symbol.name[3:]]
    # if the symbol is an LF variable in the local frame return it
    elif symbol.type == "var" and re.match(r"^(LF@).*$", symbol.name[0:3]) \
            and symbol.name[3:] in localFrame[-1]:
        return localFrame[-1][symbol.name[3:]]
    # if the symbol is a GF variable but isn't in the global frame
    elif re.match(r"^(GF@).*$", symbol.name[0:3]) and not symbol.name[3:] in globalFrame:
        quit(54)
    # if the symbol is a TF variable but isn't in the temporary frame
    elif re.match(r"^(TF@).*$", symbol.name[0:3]) and not symbol.name[3:] in tempFrame:
        quit(54)
    # if the symbol is a TF variable but the temporary frame doesn't exist
    elif re.match(r"^(TF@).*$", symbol.name[0:3]) and not tempFrame:
        quit(55)
    # if the symbol is an LF variable but isn't in the local frame
    elif re.match(r"^(LF@).*$", symbol.name[0:3]) and not symbol.name[3:] in localFrame[-1]:
        quit(54)
    # if the symbol is an LF variable but the local frame doesn't exist
    elif re.match(r"^(LF@).*$", symbol.name[0:3]) and not localFrame:
        quit(55)
    # if the symbol isn't a variable return it with the correct type
    else:
        return set_type(symbol.name)


def check_dest(variable):
    global globalFrame, tempFrame, localFrame

    # if the variable is in the global frame
    if re.match(r"^(GF@).*$", variable.name[0:3]) and variable.name[3:] in globalFrame:
        return globalFrame
    # if the variable isn't in the global frame
    elif re.match(r"^(GF@).*$", variable.name[0:3]) and not variable.name[3:] in globalFrame:
        quit(54)
    # if the variable is in the temporary frame
    elif re.match(r"^(TF@).*$", variable.name[0:3]) and variable.name[3:] in tempFrame:
        return tempFrame
    # if the variable isn't in the temporary frame
    elif re.match(r"^(TF@).*$", variable.name[0:3]) and not variable.name[3:] in tempFrame:
        quit(54)
    # if the temporary frame doesn't exist
    elif re.match(r"^(TF@).*$", variable.name[0:3]) and not tempFrame:
        quit(55)
    # if the variable is in the local frame
    elif re.match(r"^(LF@).*$", variable.name[0:3]) and variable.name[3:] in localFrame[-1]:
        return localFrame[-1]
    # if the variable isn't in the local frame
    elif re.match(r"^(LF@).*$", variable.name[0:3]) and not variable.name[3:] in localFrame[-1]:
        quit(54)
    # if the local frame doesn't exist
    elif re.match(r"^(LF@).*$", variable.name[0:3]) and not localFrame:
        quit(55)


def set_type(string):
    if string is None:
        return string
    elif re.match(r"^(true)$", string.lower()):
        return True
    elif re.match(r"^(false)$", string.lower()):
        return False
    elif re.match(r"^([-|+]?\d+)$", string):
        return int(string)
    elif re.match(r"^(nil)$", string.lower()):
        return string.lower()
    elif re.match(r"^(([\w]*(\\\\[0-9]{3})*)*)\S*$", string, flags=re.UNICODE):
        return string


def get_type(symbol):
    if isinstance(symbol, bool):
        return "bool"
    elif isinstance(symbol, int):
        return "int"
    elif re.match(r"^(nil)$", symbol):
        return "nil"
    elif isinstance(symbol, str):
        return "string"
    elif symbol is None:
        return None


def move(instruct, interpret):
    global globalFrame, tempFrame, localFrame

    if interpret == 0:
        check_num(len(instruct.args), 2)
        vars = ['var', 'symb']
        check_vars(vars, instruct.args)
        check_data(instruct.args)
    elif interpret == 1:
        # loading the symbol
        symb = check_symb(instruct.args[1])
        # loading the destination variable
        dest = check_dest(instruct.args[0])
        dest.update({instruct.args[0].name[3:]: symb})


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
        # add the current temporary frame to the top of the local frame stack and destroy the temporary frame
        if not bool(tempFrame) or tempFrame:
            localFrame.append(tempFrame)
            tempFrame.clear()
            tempFrame = None
        # if the temporary frame wan't initialised
        else:
            quit(55)


def popframe(instruct, interpret):
    global tempFrame, localFrame

    if interpret == 0:
        check_num(len(instruct.args), 0)
    elif interpret == 1:
        # pop the top frame from the local frame stack into the temporary frame
        if localFrame or not bool(tempFrame) or tempFrame:
            tempFrame = localFrame.pop()
        # if the local frame isn't initialised
        else:
            quit(55)


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


def call(instruct, interpret, counter):
    global labels, returnJump

    if interpret == 0:
        check_num(len(instruct.args), 1)
        vars = ['label']
        check_vars(vars, instruct.args)
        check_data(instruct.args)
        return counter
    if interpret == 1:
        # store the position
        returnJump.append(counter)
        # if the label exists jump to it
        if instruct.args[0].name in labels:
            return labels[instruct.args[0].name]
        # if the label doesn't exist
        else:
            quit(56)


def _return(instruct, interpret, counter):
    global returnJump

    if interpret == 0:
        check_num(len(instruct.args), 0)
        return counter
    elif interpret == 1:
        # if the jump point was previously defined
        if returnJump:
            return returnJump.pop()
        # if it wasn't defined
        else:
            quit(54)


def pushs(instruct, interpret):
    global dataStack, globalFrame, tempFrame, localFrame

    if interpret == 0:
        check_num(len(instruct.args), 1)
        vars = ['symb']
        check_vars(vars, instruct.args)
        check_data(instruct.args)
    elif interpret == 1:
        # loading the symbol
        symb = check_symb(instruct.args[0])
        # pushing the symbol into the data stack
        dataStack.append(symb)


def pops(instruct, interpret):
    global dataStack, globalFrame, tempFrame, localFrame

    if interpret == 0:
        check_num(len(instruct.args), 1)
        vars = ['var']
        check_vars(vars, instruct.args)
        check_data(instruct.args)
    elif interpret == 1:
        if not bool(dataStack) or dataStack:
            # loading the destination variable
            dest = check_dest(instruct.args[0])
            # poping the data from the data stack into the variable
            dest.update({instruct.args[0].name[3:]: dataStack.pop()})
        # if the data stack is empty
        else:
            quit(56)


def add(instruct, interpret):
    global globalFrame, tempFrame, localFrame

    if interpret == 0:
        check_num(len(instruct.args), 3)
        vars = ['var', 'symb', 'symb']
        check_vars(vars, instruct.args)
        check_data(instruct.args)
    elif interpret == 1:
        # loading the first symbol
        symb1 = check_symb(instruct.args[1])
        # loading the second symbol
        symb2 = check_symb(instruct.args[2])
        # loading the destination variable
        dest = check_dest(instruct.args[0])
        # performing the ADD operation
        # if both of the variables are integers
        if get_type(symb1) == "int" and get_type(symb2) == "int":
            # performing the MUL operation
            dest.update({instruct.args[0].name[3:]: symb1 + symb2})
        else:
            quit(53)


def sub(instruct, interpret):
    global globalFrame, tempFrame, localFrame

    if interpret == 0:
        check_num(len(instruct.args), 3)
        vars = ['var', 'symb', 'symb']
        check_vars(vars, instruct.args)
        check_data(instruct.args)
    elif interpret == 1:
        # loading the first symbol
        symb1 = check_symb(instruct.args[1])
        # loading the second symbol
        symb2 = check_symb(instruct.args[2])
        # loading the destination variable
        dest = check_dest(instruct.args[0])
        # performing the SUB operation
        # if both of the variables are integers
        if get_type(symb1) == "int" and get_type(symb2) == "int":
            # performing the MUL operation
            dest.update({instruct.args[0].name[3:]: symb1 - symb2})
        else:
            quit(53)


def mul(instruct, interpret):
    global globalFrame, tempFrame, localFrame

    if interpret == 0:
        check_num(len(instruct.args), 3)
        vars = ['var', 'symb', 'symb']
        check_vars(vars, instruct.args)
        check_data(instruct.args)
    elif interpret == 1:
        # loading the first symbol
        symb1 = check_symb(instruct.args[1])
        # loading the second symbol
        symb2 = check_symb(instruct.args[2])
        # loading the destination variable
        dest = check_dest(instruct.args[0])
        # if both of the variables are integers
        if get_type(symb1) == "int" and get_type(symb2) == "int":
            # performing the MUL operation
            dest.update({instruct.args[0].name[3:]: symb1 * symb2})
        else:
            quit(53)


def idiv(instruct, interpret):
    global globalFrame, tempFrame, localFrame

    if interpret == 0:
        check_num(len(instruct.args), 3)
        vars = ['var', 'symb', 'symb']
        check_vars(vars, instruct.args)
        check_data(instruct.args)
    elif interpret == 1:
        # loading the first symbol
        symb1 = check_symb(instruct.args[1])
        # loading the second symbol
        symb2 = check_symb(instruct.args[2])
        # loading the destination variable
        dest = check_dest(instruct.args[0])
        # if both of the variables are integers
        if get_type(symb1) == "int" and get_type(symb2) == "int":
            # if the denominator is 0
            if symb2 == 0:
                quit(57)
            # performing the IDIV operation
            else:
                dest.update({instruct.args[0].name[3:]: symb1 // symb2})
        else:
            quit(53)


def lt(instruct, interpret):
    global globalFrame, tempFrame, localFrame

    if interpret == 0:
        check_num(len(instruct.args), 3)
        vars = ['var', 'symb', 'symb']
        check_vars(vars, instruct.args)
        check_data(instruct.args)
    elif interpret == 1:
        # loading the first symbol
        symb1 = check_symb(instruct.args[1])
        # loading the second symbol
        symb2 = check_symb(instruct.args[2])
        # loading the destination variable
        dest = check_dest(instruct.args[0])
        # if both symbols are integers
        if get_type(symb1) == "int" and get_type(symb2) == "int":
            # if the comparison is true
            if symb1 < symb2:
                dest.update({instruct.args[0].name[3:]: True})
            else:
                dest.update({instruct.args[0].name[3:]: False})
        # if both symbols are strings
        elif get_type(symb1) == "string" and get_type(symb2) == "string":
            # if the comparison is true
            if symb1 < symb2:
                dest.update({instruct.args[0].name[3:]: True})
            else:
                dest.update({instruct.args[0].name[3:]: False})
        # if both symbols are bool
        elif get_type(symb1) == "bool" and get_type(symb2) == "bool":
            # if the comparison is true
            if symb1 < symb2:
                dest.update({instruct.args[0].name[3:]: True})
            else:
                dest.update({instruct.args[0].name[3:]: False})
        else:
            quit(53)


def gt(instruct, interpret):
    global globalFrame, tempFrame, localFrame

    if interpret == 0:
        check_num(len(instruct.args), 3)
        vars = ['var', 'symb', 'symb']
        check_vars(vars, instruct.args)
        check_data(instruct.args)
    elif interpret == 1:
        # loading the first symbol
        symb1 = check_symb(instruct.args[1])
        # loading the second symbol
        symb2 = check_symb(instruct.args[2])
        # loading the destination variable
        dest = check_dest(instruct.args[0])
        # if both symbols are integers
        if get_type(symb1) == "int" and get_type(symb2) == "int":
            # if the comparison is true
            if symb1 > symb2:
                dest.update({instruct.args[0].name[3:]: True})
            else:
                dest.update({instruct.args[0].name[3:]: False})
        # if both symbols are strings
        elif get_type(symb1) == "string" and get_type(symb2) == "string":
            # if the comparison is true
            if symb1 > symb2:
                dest.update({instruct.args[0].name[3:]: True})
            else:
                dest.update({instruct.args[0].name[3:]: False})
        # if both symbols are bool
        elif get_type(symb1) == "bool" and get_type(symb2) == "bool":
            # if the comparison is true
            if symb1 > symb2:
                dest.update({instruct.args[0].name[3:]: True})
            else:
                dest.update({instruct.args[0].name[3:]: False})
        else:
            quit(53)


def eq(instruct, interpret):
    global globalFrame, tempFrame, localFrame

    if interpret == 0:
        check_num(len(instruct.args), 3)
        vars = ['var', 'symb', 'symb']
        check_vars(vars, instruct.args)
        check_data(instruct.args)
    elif interpret == 1:
        # loading the first symbol
        symb1 = check_symb(instruct.args[1])
        # loading the second symbol
        symb2 = check_symb(instruct.args[2])
        # loading the destination variable
        dest = check_dest(instruct.args[0])
        # if both symbols are integers
        if get_type(symb1) == "int" and get_type(symb2) == "int":
            # if the comparison is true
            if symb1 == symb2:
                dest.update({instruct.args[0].name[3:]: True})
            else:
                dest.update({instruct.args[0].name[3:]: False})
        # if both symbols are strings
        elif get_type(symb1) == "string" and get_type(symb2) == "string":
            # if the comparison is true
            if symb1 == symb2:
                dest.update({instruct.args[0].name[3:]: True})
            else:
                dest.update({instruct.args[0].name[3:]: False})
        # if both symbols are bool
        elif get_type(symb1) == "bool" and get_type(symb2) == "bool":
            # if the comparison is true
            if symb1 == symb2:
                dest.update({instruct.args[0].name[3:]: True})
            else:
                dest.update({instruct.args[0].name[3:]: False})
        else:
            quit(53)


def _and(instruct, interpret):
    global globalFrame, tempFrame, localFrame

    if interpret == 0:
        check_num(len(instruct.args), 3)
        vars = ['var', 'symb', 'symb']
        check_vars(vars, instruct.args)
        check_data(instruct.args)
    elif interpret == 1:
        # loading the first symbol
        symb1 = check_symb(instruct.args[1])
        # loading the second symbol
        symb2 = check_symb(instruct.args[2])
        # loading the destination variable
        dest = check_dest(instruct.args[0])
        # if both symbols are bool
        if get_type(symb1) == "bool" and get_type(symb2) == "bool":
            # if the comparison is true
            if symb1 and symb2:
                dest.update({instruct.args[0].name[3:]: True})
            else:
                dest.update({instruct.args[0].name[3:]: False})
        else:
            quit(53)


def _or(instruct, interpret):
    global globalFrame, tempFrame, localFrame

    if interpret == 0:
        check_num(len(instruct.args), 3)
        vars = ['var', 'symb', 'symb']
        check_vars(vars, instruct.args)
        check_data(instruct.args)
    elif interpret == 1:
        # loading the first symbol
        symb1 = check_symb(instruct.args[1])
        # loading the second symbol
        symb2 = check_symb(instruct.args[2])
        # loading the destination variable
        dest = check_dest(instruct.args[0])
        # if both symbols are bool
        if get_type(symb1) == "bool" and get_type(symb2) == "bool":
            # if the comparison is true
            if symb1 or symb2:
                dest.update({instruct.args[0].name[3:]: True})
            else:
                dest.update({instruct.args[0].name[3:]: False})
        else:
            quit(53)


def _not(instruct, interpret):
    global globalFrame, tempFrame, localFrame

    if interpret == 0:
        check_num(len(instruct.args), 2)
        vars = ['var', 'symb']
        check_vars(vars, instruct.args)
        check_data(instruct.args)
    elif interpret == 1:
        # loading the symbol
        symb = check_symb(instruct.args[1])
        # loading the destination variable
        dest = check_dest(instruct.args[0])
        # if both symbols are bool
        if get_type(symb) == "bool":
            # negate the bool value
            dest.update({instruct.args[0].name[3:]: not symb})
        else:
            quit(53)


def int2char(instruct, interpret):
    global globalFrame, tempFrame, localFrame

    if interpret == 0:
        check_num(len(instruct.args), 2)
        vars = ['var', 'symb']
        check_vars(vars, instruct.args)
        check_data(instruct.args)
    elif interpret == 1:
        # loading the symbol
        symb = check_symb(instruct.args[1])
        # loading the destination variable
        dest = check_dest(instruct.args[0])
        # if the symbol is an integer
        if get_type(symb) == "int":
            # if the symbol is in the correct range
            if 0 <= symb <= 1114111:
                dest.update({instruct.args[0].name[3:]: chr(symb)})
            # if the symbol isn't in the correct range
            else:
                quit(58)
        else:
            quit(53)


def stri2int(instruct, interpret):
    global globalFrame, tempFrame, localFrame

    if interpret == 0:
        check_num(len(instruct.args), 3)
        vars = ['var', 'symb', 'symb']
        check_vars(vars, instruct.args)
        check_data(instruct.args)
    elif interpret == 1:
        # loading the first symbol
        symb1 = check_symb(instruct.args[1])
        # loading the second symbol
        symb2 = check_symb(instruct.args[2])
        # loading the destination variable
        dest = check_dest(instruct.args[0])
        # if the first symbol is string and the second one is integer
        if get_type(symb1) == "string" and get_type(symb2) == "int":
            # if the integer is in the correct range
            if 0 <= int(symb2) <= len(symb1):
                dest.update({instruct.args[0].name[3:]: ord(symb1[symb2:symb2 + 1])})
            else:
                quit(58)
        else:
            quit(53)


def read(instruct, interpret, input, count):
    global globalFrame, tempFrame, localFrame

    if interpret == 0:
        check_num(len(instruct.args), 2)
        vars = ['var', 'type']
        check_vars(vars, instruct.args)
        check_data(instruct.args)
    elif interpret == 1:
        dest = check_dest(instruct.args[0])
        dest.update({instruct.args[0].name[3:]: set_type(input[count].rstrip())})


def write(instruct, interpret):
    global globalFrame, tempFrame, localFrame

    if interpret == 0:
        check_num(len(instruct.args), 1)
        vars = ['symb']
        check_vars(vars, instruct.args)
        check_data(instruct.args)
    elif interpret == 1:
        # loading the symbol
        value = check_symb(instruct.args[0])
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
        # loading the first symbol
        symb1 = check_symb(instruct.args[1])
        # loading the second symbol
        symb2 = check_symb(instruct.args[2])
        # loading the destination variable
        dest = check_dest(instruct.args[0])
        # performing the CONCAT operation
        dest.update({instruct.args[0].name[3:]: symb1 + symb2})


def strlen(instruct, interpret):
    global globalFrame, tempFrame, localFrame

    if interpret == 0:
        check_num(len(instruct.args), 2)
        vars = ['var', 'symb']
        check_vars(vars, instruct.args)
        check_data(instruct.args)
    elif interpret == 1:
        # loading the symbol
        symb = check_symb(instruct.args[1])
        # loading the destination variable
        dest = check_dest(instruct.args[0])
        # performs the STRLEN function
        dest.update({instruct.args[0].name[3:]: len(symb)})


def getchar(instruct, interpret):
    global globalFrame, tempFrame, localFrame

    if interpret == 0:
        check_num(len(instruct.args), 3)
        vars = ['var', 'symb', 'symb']
        check_vars(vars, instruct.args)
        check_data(instruct.args)
    elif interpret == 1:
        # loading the first symbol
        symb1 = check_symb(instruct.args[1])
        # loading the second symbol
        symb2 = check_symb(instruct.args[2])
        # loading the destination variable
        dest = check_dest(instruct.args[0])
        # if the first symbol is a string and the second symbol is an integer
        if get_type(symb1) == "string" and get_type(symb2) == "int":
            # if the index isn't outside of the string performs the GETCHAR operation
            if 0 <= symb2 < len(symb1):
                dest.update({instruct.args[0].name[3:]: symb1[symb2:symb2 + 1]})
            else:
                quit(58)
        else:
            quit(53)


def setchar(instruct, interpret):
    global globalFrame, tempFrame, localFrame

    if interpret == 0:
        check_num(len(instruct.args), 3)
        vars = ['var', 'symb', 'symb']
        check_vars(vars, instruct.args)
        check_data(instruct.args)
    elif interpret == 1:
        # loading the first symbol
        symb1 = check_symb(instruct.args[1])
        # loading the second symbol
        symb2 = check_symb(instruct.args[2])
        # loading the destination variable
        dest = check_dest(instruct.args[0])
        # if the first symbol is a string and the second symbol is an integer
        if get_type(symb1) == "int" and get_type(symb2) == "string":
            # if the index isn't outside of the string performs the SETCHAR operation
            if 0 <= int(symb1) < len(dest[instruct.args[0].name[3:]]):
                tmp = dest[instruct.args[0].name[3:]]
                new = "".join((tmp[int(symb1)], symb2[0:1], tmp[int(symb1)]))
                dest.update({instruct.args[0].name[3:]: new})
            else:
                quit(58)
        else:
            quit(53)


def type(instruct, interpret):
    global globalFrame, tempFrame, localFrame

    if interpret == 0:
        check_num(len(instruct.args), 2)
        vars = ['var', 'symb']
        check_vars(vars, instruct.args)
        check_data(instruct.args)
    elif interpret == 1:
        # loading the first symbol
        symb = check_symb(instruct.args[1])
        # loading the destination variable
        dest = check_dest(instruct.args[0])
        # if the type of the symbol is None set the variable to empty string
        if get_type(symb) is None:
            dest.update({instruct.args[0].name[3:]: ""})
        # set the variable to the name of the type of the symbol
        else:
            dest.update({instruct.args[0].name[3:]: get_type(symb)})


def label(instruct, interpret, counter):
    global globalFrame, tempFrame, localFrame, labels

    if interpret == 0:
        check_num(len(instruct.args), 1)
        vars = ['label']
        check_vars(vars, instruct.args)
        check_data(instruct.args)
        # if the label is not already stored
        if not instruct.args[0].name in labels:
            labels.update({instruct.args[0].name: counter})
        # if the label was stored before
        else:
            quit(52)
    elif interpret == 1:
        return


def jump(instruct, interpret, counter):
    if interpret == 0:
        check_num(len(instruct.args), 1)
        vars = ['label']
        check_vars(vars, instruct.args)
        check_data(instruct.args)
        return counter
    if interpret == 1:
        # if the label exists jump to it
        if instruct.args[0].name in labels:
            return labels[instruct.args[0].name]
        # if the label doesn't exist
        else:
            quit(56)


def jumpifeq(instruct, interpret, counter):
    if interpret == 0:
        check_num(len(instruct.args), 3)
        vars = ['label', 'symb', 'symb']
        check_vars(vars, instruct.args)
        check_data(instruct.args)
        return counter
    elif interpret == 1:
        # loading the first symbol
        symb1 = check_symb(instruct.args[1])
        # loading the second symbol
        symb2 = check_symb(instruct.args[2])
        # if the symbols are both strings
        if get_type(symb1) == "string" and get_type(symb2) == "string":
            # if the label exists and equality is satisfied jump to it
            if instruct.args[0].name in labels and symb1 == symb2:
                return labels[instruct.args[0].name]
            # if the equality is not satisfied
            elif symb1 != symb2:
                return counter
            # if the label doesn't exist
            else:
                quit(56)
        # if the symbols are both integers
        elif get_type(symb1) == "int" and get_type(symb2) == "int":
            # if the label exists and equality is satisfied jump to it
            if instruct.args[0].name in labels and symb1 == symb2:
                return labels[instruct.args[0].name]
            # if the equality is not satisfied
            elif symb1 != symb2:
                return counter
            # if the label doesn't exist
            else:
                quit(56)
        # if the symbols are both bools
        elif get_type(symb1) == "bool" and get_type(symb2) == "bool":
            # if the label exists and equality is satisfied jump to it
            if instruct.args[0].name in labels and symb1 == symb2:
                return labels[instruct.args[0].name]
            # if the equality is not satisfied
            elif symb1 != symb2:
                return counter
            # if the label doesn't exist
            else:
                quit(56)
        # if the symbols are both nils
        elif get_type(symb1) == "nil" and get_type(symb2) == "nil":
            # if the label exists and equality is satisfied jump to it
            if instruct.args[0].name in labels:
                return labels[instruct.args[0].name]
            # if the label doesn't exist
            else:
                quit(56)
        # if the symbols are different types
        else:
            quit(53)


def jumpifnoteq(instruct, interpret, counter):
    if interpret == 0:
        check_num(len(instruct.args), 3)
        vars = ['label', 'symb', 'symb']
        check_vars(vars, instruct.args)
        check_data(instruct.args)
        return counter
    elif interpret == 1:
        # loading the first symbol
        symb1 = check_symb(instruct.args[1])
        # loading the second symbol
        symb2 = check_symb(instruct.args[2])
        # if the symbols are both strings
        if get_type(symb1) == "string" and get_type(symb2) == "string":
            # if the label exists and equality is satisfied jump to it
            if instruct.args[0].name in labels and symb1 != symb2:
                return labels[instruct.args[0].name]
            # if the equality is not satisfied
            elif symb1 == symb2:
                return counter
            # if the label doesn't exist
            else:
                quit(56)
        # if the symbols are both integers
        elif get_type(symb1) == "int" and get_type(symb2) == "int":
            # if the label exists and equality is satisfied jump to it
            if instruct.args[0].name in labels and symb1 != symb2:
                return labels[instruct.args[0].name]
            # if the equality is not satisfied
            elif symb1 == symb2:
                return counter
            # if the label doesn't exist
            else:
                quit(56)
        # if the symbols are both bools
        elif get_type(symb1) == "bool" and get_type(symb2) == "bool":
            # if the label exists and equality is satisfied jump to it
            if instruct.args[0].name in labels and symb1 != symb2:
                return labels[instruct.args[0].name]
            # if the equality is not satisfied
            elif symb1 == symb2:
                return counter
            # if the label doesn't exist
            else:
                quit(56)
        # if the symbols are both nils
        elif get_type(symb1) == "nil" and get_type(symb2) == "nil":
            # if the label exists and equality is satisfied jump to it
            if instruct.args[0].name in labels:
                return counter
            # if the label doesn't exist
            else:
                quit(56)
        # if the symbols are different types
        else:
            quit(53)


def _exit(instruct, interpret):
    global globalFrame, tempFrame, localFrame

    if interpret == 0:
        check_num(len(instruct.args), 1)
        vars = ['symb']
        check_vars(vars, instruct.args)
        check_data(instruct.args)
    elif interpret == 1:
        # loading the exit code
        code = check_symb(instruct.args[0])
        # if the symbol is an integer
        if get_type(code) == "int":
            # if the symbol is in the correct range
            if 0 <= code <= 49:
                quit(code)
            else:
                quit(57)
        # if the symbol is a different type
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
        # loading the symbol
        symb = check_symb(instruct.args[0])
        # performing the PRINT operation
        print_out(symb, "err")


def _break(instruct, interpret, counter):
    global globalFrame, tempFrame, localFrame

    if interpret == 0:
        check_num(len(instruct.args), 0)
    elif interpret == 1:
        print_out("Position in code: " + str(counter), "err")
        print_out("GLOBAL FRAME: \n", "err")
        print_out(globalFrame, "err")
        print_out("LOCAL FRAME: \n", "err")
        print_out(localFrame[-1], "err")
        print_out("TEMPORARY FRAME: \n", "err")
        print_out(tempFrame, "err")
