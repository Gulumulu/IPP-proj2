import sys
import getopt
import re
import xml.etree.ElementTree as ET
from xml.etree.ElementTree import ParseError
import instructions as INSTR


# class for storing the information about an instruction
class Instruction:
    def __init__(self, order, opcode, Argument):
        self.order = int(order)
        self.opcode = opcode.upper()
        self.args = Argument


# class for storing the information about the arguments of an instruction
class Argument:
    def __init__(self, num, type, name=None):
        self.num = num
        self.type = type
        if name is None:
            name = ""
        self.name = name.replace("\n", "")


# global variables
source = "stdin"
input = "stdin"
source_file = ''
input_file = []
instruction_list = []
argument_list = []
count_vars = 0
count_insts = 0
insts_num = 0
vars_num = 0
stats = None


# function for parsing the arguments
def check_argv():
    global source, input, count_insts, count_vars, stats

    # get the command line arguments
    options, remainder = getopt.getopt(sys.argv[1:], '', ["help", "source=", "input=", "stats=", "insts", "vars"])

    # deal with each argument
    for opt, arg in options:
        # if the help argument is present show the help message and exit
        if opt == "--help":
            print('This script interprets IPPcode19 from an xml format.')
            print('You can use these arguments:')
            print('     --source=file to set the input XML to file,')
            print('     --input=file to set the the source for the READ and WRITE IPPcode19 instructions to file,')
            print('     --help to show this message.')
            print('At least one of the input/source arguments has to be present. If only one is present,')
            print('the other information will be gathered from stdin.')
            exit(0)
        # if vars argument is present store true for counting vars
        if opt == "--vars":
            count_vars = 1
        # if insts argument is present store true for counting insts
        if opt == "--insts":
            count_insts = 1
        # if stats argument is present store the file name
        if opt == "--stats":
            stats = arg
        # if source argument is present store the file name
        if opt == "--source":
            source = arg
        # if input argument is present store the file name
        if opt == "--input":
            input = arg

    # checks if the stats argument was present when vars or insts arguments were
    if (count_vars == 1 or count_insts == 1) and stats is None:
        exit(10)

    # check whether at least one of the files needed as input is present
    if source == "stdin" and input == "stdin":
        # error when checking the input parameters
        exit(10)


def check_xml():
    global source_file, instruction_list, argument_list

    # getting the root (upper most) element of the xml
    root = source_file.getroot()

    # check if xml starts with the program element
    if not re.match(r"^program$", root.tag):
        exit(31)

    # checks if the program element has the language attribute with the IPPcode19 value
    for name, value in root.attrib.items():
        if re.match(r"^language$", name) and re.match(r"^IPPcode19$", value):
            continue
        else:
            if re.match(r"^name$", name) or re.match(r"^description$", name):
                continue
            else:
                exit(32)

    # checking if the elements have correct name = instruction
    for instruct in root:
        if not re.match(r"^instruction$", instruct.tag):
            exit(32)
        # checking if the attributes of the instruction elements have correct names
        for name, value in instruct.attrib.items():
            if (not re.match(r"^order$", name) or not value.isnumeric()) and (not re.match(r"^opcode$", name)):
                exit(32)

    # creating classes of instruction elements and their arguments
    for instruct in root.findall('instruction'):
        # checking if there are any elements other than arg within the instriction element
        for argument in instruct:
            if not re.match("^arg[1|2|3]$", argument.tag):
                exit(32)
        x = 0
        arg1 = instruct.findall('arg1')
        arg2 = instruct.findall('arg2')
        arg3 = instruct.findall('arg3')

        # if arg elements have incorrect numbers
        if len(arg1) == 0 and (len(arg2) != 0 or len(arg3) != 0):
            exit(32)
        elif len(arg2) == 0 and len(arg3) != 0:
            exit(32)

        for arg in arg1 + arg2 + arg3:
            # checking for unwanted elements within the arg element
            for anything in arg:
                exit(32)
            # checking if the attribute of the arg elements has the correct name
            for name, value in arg.attrib.items():
                if not re.match(r"^type$", name):
                    exit(32)
            x += 1
            argument_list.append(Argument(x, arg.get('type'), arg.text))
        instruction_list.append(Instruction(instruct.get('order'), instruct.get('opcode'), argument_list))
        argument_list = []

    instruction_list.sort(key=lambda x: x.order, reverse=False)

    order = 1
    for instruct in instruction_list:
        if instruct.order != order:
            exit(32)
        order += 1


# checks instructions for errors
def parse_instruction(mode):
    global instruction_list, argument_list, input_file, insts_num, vars_num

    counter = 0
    read_count = 0
    helper = [mode, 0, 0]

    # calling the instruction checker based on the instruction name
    # if instruction name is not found exits
    while counter < len(instruction_list):
        instruct = instruction_list[counter]
        if re.match(r"^MOVE$", instruct.opcode):
            INSTR.move(instruct, helper)
        elif re.match(r"^CREATEFRAME$", instruct.opcode):
            INSTR.createframe(instruct, helper)
        elif re.match(r"^PUSHFRAME$", instruct.opcode):
            INSTR.pushframe(instruct, helper)
        elif re.match(r"^POPFRAME$", instruct.opcode):
            INSTR.popframe(instruct, helper)
        elif re.match(r"^DEFVAR$", instruct.opcode):
            INSTR.defvar(instruct, helper)
        elif re.match(r"^CALL$", instruct.opcode):
            counter = INSTR.call(instruct, helper, counter)
        elif re.match(r"^RETURN$", instruct.opcode):
            counter = INSTR._return(instruct, helper, counter)
        elif re.match(r"^PUSHS$", instruct.opcode):
            INSTR.pushs(instruct, helper)
        elif re.match(r"^POPS$", instruct.opcode):
            INSTR.pops(instruct, helper)
        elif re.match(r"^ADD$", instruct.opcode):
            INSTR.add(instruct, helper)
        elif re.match(r"^SUB$", instruct.opcode):
            INSTR.sub(instruct, helper)
        elif re.match(r"^MUL$", instruct.opcode):
            INSTR.mul(instruct, helper)
        elif re.match(r"^IDIV$", instruct.opcode):
            INSTR.idiv(instruct, helper)
        elif re.match(r"^DIV$", instruct.opcode):
            INSTR.div(instruct, helper)
        elif re.match(r"^LT$", instruct.opcode):
            INSTR.lt(instruct, helper)
        elif re.match(r"^GT$", instruct.opcode):
            INSTR.gt(instruct, helper)
        elif re.match(r"^EQ$", instruct.opcode):
            INSTR.eq(instruct, helper)
        elif re.match(r"^AND$", instruct.opcode):
            INSTR._and(instruct, helper)
        elif re.match(r"^OR$", instruct.opcode):
            INSTR._or(instruct, helper)
        elif re.match(r"^NOT$", instruct.opcode):
            INSTR._not(instruct, helper)
        elif re.match(r"^INT2CHAR$", instruct.opcode):
            INSTR.int2char(instruct, helper)
        elif re.match(r"^STRI2INT$", instruct.opcode):
            INSTR.stri2int(instruct, helper)
        elif re.match(r"^INT2FLOAT$", instruct.opcode):
            INSTR.int2float(instruct, helper)
        elif re.match(r"^FLOAT2INT$", instruct.opcode):
            INSTR.float2int(instruct, helper)
        elif re.match(r"^READ$", instruct.opcode):
            INSTR.read(instruct, helper, input_file, read_count)
            read_count += 1
        elif re.match(r"^WRITE$", instruct.opcode):
            INSTR.write(instruct, helper)
        elif re.match(r"^CONCAT$", instruct.opcode):
            INSTR.concat(instruct, helper)
        elif re.match(r"^STRLEN$", instruct.opcode):
            INSTR.strlen(instruct, helper)
        elif re.match(r"^GETCHAR$", instruct.opcode):
            INSTR.getchar(instruct, helper)
        elif re.match(r"^SETCHAR$", instruct.opcode):
            INSTR.setchar(instruct, helper)
        elif re.match(r"^TYPE$", instruct.opcode):
            INSTR.type(instruct, helper)
        elif re.match(r"^LABEL$", instruct.opcode):
            INSTR.label(instruct, helper, counter)
        elif re.match(r"^JUMP$", instruct.opcode):
            counter = INSTR.jump(instruct, helper, counter)
        elif re.match(r"^JUMPIFEQ$", instruct.opcode):
            counter = INSTR.jumpifeq(instruct, helper, counter)
        elif re.match(r"^JUMPIFNEQ$", instruct.opcode):
            counter = INSTR.jumpifnoteq(instruct, helper, counter)
        elif re.match(r"^EXIT$", instruct.opcode):
            INSTR._exit(instruct, helper)
        elif re.match(r"^DPRINT$", instruct.opcode):
            INSTR.dprint(instruct, helper)
        elif re.match(r"^BREAK$", instruct.opcode):
            INSTR._break(instruct, helper, counter)
        elif re.match(r"^CLEARS$", instruct.opcode):
            INSTR.clears(instruct, helper)
        elif re.match(r"^ADDS$", instruct.opcode):
            INSTR.adds(instruct, helper)
        elif re.match(r"^SUBS$", instruct.opcode):
            INSTR.subs(instruct, helper)
        elif re.match(r"^MULS$", instruct.opcode):
            INSTR.muls(instruct, helper)
        elif re.match(r"^IDIVS$", instruct.opcode):
            INSTR.idivs(instruct, helper)
        elif re.match(r"^LTS$", instruct.opcode):
            INSTR.lts(instruct, helper)
        elif re.match(r"^GTS$", instruct.opcode):
            INSTR.gts(instruct, helper)
        elif re.match(r"^EQS$", instruct.opcode):
            INSTR.eqs(instruct, helper)
        elif re.match(r"^ANDS$", instruct.opcode):
            INSTR.ands(instruct, helper)
        elif re.match(r"^ORS$", instruct.opcode):
            INSTR.ors(instruct, helper)
        elif re.match(r"^NOTS$", instruct.opcode):
            INSTR.nots(instruct, helper)
        elif re.match(r"^INT2CHARS$", instruct.opcode):
            INSTR.int2chars(instruct, helper)
        elif re.match(r"^STRI2INTS$", instruct.opcode):
            INSTR.stri2ints(instruct, helper)
        elif re.match(r"^JUMPIFEQS$", instruct.opcode):
            counter = INSTR.jumpifeqs(instruct, helper, counter)
        elif re.match(r"^JUMPIFNEQS$", instruct.opcode):
            counter = INSTR.jumpifnoteqs(instruct, helper, counter)
        else:
            # mistake in instruction name
            exit(32)
        counter += 1

    insts_num = helper[1]
    vars_num = helper[2]


# function for parsing the xml input
def interpret():
    global source, input, source_file, input_file, stats, count_insts, count_vars, insts_num, vars_num

    # read the xml source from stdin
    if source == "stdin":
        source_file = sys.stdin.readline()
    # read the xml source from an xml file
    else:
        try:
            source_file = ET.parse(source)
        # error while parsing the file
        except ParseError:
            exit(11)

    # read the READ instruction input from stdin
    if input == "stdin":
        input_file = sys.stdin.readline()
    # read the READ instruction input from a file
    else:
        try:
            file = open(input, "r")
            for line in file:
                input_file.append(line)
        # error while parsing the file
        except IOError:
            exit(11)

    # calling the function to check the xml file for mistakes
    check_xml()
    # calling the function to check the instructions for mistakes
    parse_instruction(0)
    # calling the function to interpret the instructions
    parse_instruction(1)

    if stats is not None:
        stats_file = open(stats, "w")
        if count_insts == 1:
            stats_file.write(str(insts_num) + "\n")
        if count_vars == 1:
            stats_file.write(str(vars_num) + "\n")
        stats_file.close()

# calling the function to parse the input arguments
check_argv()
# calling the function to parse the xml code
interpret()
