import sys
import getopt
import re
import xml.etree.ElementTree as ET
import instructions as INSTR

'''
!!!TODO!!!
treba zoradit pole instrukcii podla ich order-u (mozu byt prehadzane)
'''

'''
!!!DONE!!!
argumenty skriptu
? format XML ?
nazvy instrukcii
nazvy argumentov
'''


# class for storing the information about an instruction
class Instruction:
    def __init__(self, order, opcode, Argument):
        self.order = order
        self.opcode = opcode
        self.args = Argument


# class for storing the information about the arguments of an instruction
class Argument:
    def __init__(self, num, type, name=None):
        self.num = num
        self.type = type
        self.name = name


# global variables
source = "stdin"
input = "stdin"
source_file = ''
input_file = ''
instruction_list = []
argument_list = []
count_vars = 0
count_insts = 0
stats = None
global_frame = {}
temp_frame = {}


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
    if (count_vars == 1 or count_insts == 1) and stats == None:
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
        if not re.match(r"^language$", name) or not re.match(r"^IPPcode19$", value):
            exit(31)

    # checking if the elements have correct name = instruction
    for instruct in root:
        if not re.match(r"^instruction$", instruct.tag):
            exit(31)
        # checking if the attributes of the instruction elements have correct names
        for name, value in instruct.attrib.items():
            if (not re.match(r"^order$", name) or not value.isnumeric()) and (not re.match(r"^opcode$", name)):
                exit(31)

    # creating classes of instruction elements and their arguments
    for instruct in root.findall('instruction'):
        x = 0
        arg1 = instruct.findall('arg1')
        arg2 = instruct.findall('arg2')
        arg3 = instruct.findall('arg3')
        for arg in arg1 + arg2 + arg3:
            # checking if the attribute of the arg elements has the correct name
            for name, value in arg.attrib.items():
                if not re.match(r"^type$", name):
                    exit(31)
            x += 1
            argument_list.append(Argument(x, arg.get('type'), arg.text))
        instruction_list.append(Instruction(instruct.get('order'), instruct.get('opcode'), argument_list))
        argument_list = []


# checks instructions for errors
def parse_instruction(interpret):
    global instruction_list, argument_list, global_frame, temp_frame

    counter = 0

    # calling the instruction checker based on the instruction name
    # if instruction name is not found exits
    # for instruct in instruction_list:
    while counter < len(instruction_list):
        instruct = instruction_list[counter]
        if re.match(r"^MOVE$", instruct.opcode):
            INSTR.move(instruct, interpret)
        elif re.match(r"^CREATEFRAME$", instruct.opcode):
            INSTR.createframe(instruct, interpret)
        elif re.match(r"^PUSHFRAME$", instruct.opcode):
            INSTR.pushframe(instruct, interpret)
        elif re.match(r"^POPFRAME$", instruct.opcode):
            INSTR.popframe(instruct, interpret)
        elif re.match(r"^DEFVAR$", instruct.opcode):
            INSTR.defvar(instruct, interpret)
        elif re.match(r"^CALL$", instruct.opcode):
            INSTR.call(instruct, interpret)
        elif re.match(r"^RETURN$", instruct.opcode):
            INSTR._return(instruct, interpret)
        elif re.match(r"^PUSHS^", instruct.opcode):
            INSTR.pushs(instruct, interpret)
        elif re.match(r"^POPS$", instruct.opcode):
            INSTR.pops(instruct, interpret)
        elif re.match(r"^ADD$", instruct.opcode):
            INSTR.add(instruct, interpret)
        elif re.match(r"^SUB$", instruct.opcode):
            INSTR.sub(instruct, interpret)
        elif re.match(r"^MUL$", instruct.opcode):
            INSTR.mul(instruct, interpret)
        elif re.match(r"^IDIV$", instruct.opcode):
            INSTR.idiv(instruct, interpret)
        elif re.match(r"^LT$", instruct.opcode):
            INSTR.lt(instruct, interpret)
        elif re.match(r"^GT$", instruct.opcode):
            INSTR.gt(instruct, interpret)
        elif re.match(r"^EQ$", instruct.opcode):
            INSTR.eq(instruct, interpret)
        elif re.match(r"^AND$", instruct.opcode):
            INSTR._and(instruct, interpret)
        elif re.match(r"^OR$", instruct.opcode):
            INSTR._or(instruct, interpret)
        elif re.match(r"^NOT$", instruct.opcode):
            INSTR._not(instruct, interpret)
        elif re.match(r"^INT2CHAR$", instruct.opcode):
            INSTR.int2char(instruct, interpret)
        elif re.match(r"^STRI2INT$", instruct.opcode):
            INSTR.stri2int(instruct, interpret)
        elif re.match(r"^READ$", instruct.opcode):
            INSTR.read(instruct, interpret)
        elif re.match(r"^WRITE$", instruct.opcode):
            INSTR.write(instruct, interpret)
        elif re.match(r"^CONCAT$", instruct.opcode):
            INSTR.concat(instruct, interpret)
        elif re.match(r"^STRLEN$", instruct.opcode):
            INSTR.strlen(instruct, interpret)
        elif re.match(r"^GETCHAR$", instruct.opcode):
            INSTR.getchar(instruct, interpret)
        elif re.match(r"^SETCHAR$", instruct.opcode):
            INSTR.setchar(instruct, interpret)
        elif re.match(r"^TYPE$", instruct.opcode):
            INSTR.type(instruct, interpret)
        elif re.match(r"^LABEL$", instruct.opcode):
            INSTR.label(instruct, counter)
        elif re.match(r"^JUMP$", instruct.opcode):
            INSTR.jump(instruct, interpret)
        elif re.match(r"^JUMPIFEQ$", instruct.opcode):
            INSTR.jumpifeq(instruct, interpret)
        elif re.match(r"^JUMPIFNOTEQ$", instruct.opcode):
            INSTR.jumpifnoteq(instruct, interpret)
        elif re.match(r"^EXIT$", instruct.opcode):
            INSTR.exit(instruct, interpret)
        elif re.match(r"^DPRINT$", instruct.opcode):
            INSTR.dprint(instruct, interpret)
        elif re.match(r"^BREAK$", instruct.opcode):
            INSTR._break(instruct, interpret)
        else:
            # mistake in instruction name
            exit(32)
        counter += 1


# function for parsing the xml input
def interpret():
    global source, input, source_file, input_file

    # read xml source from file or from stdin
    if source == "stdin":
        source_file = sys.stdin.readline()
    else:
        try:
            source_file = ET.parse(source)
        except:
            # error while opening input xml file
            exit(11)

    # read input from file or from stdin
    if input == "stdin":
        input_file = sys.stdin.readline()
    else:
        print("")
        #input_file = ET.parse(input)

    # calling the function to check the xml file for mistakes
    check_xml()
    # calling the function to check the instructions for mistakes
    parse_instruction(0)
    # calling the function to interpret the instructions
    parse_instruction(1)


# calling the function to parse the input arguments
check_argv()
# calling the function to parse the xml code
interpret()
