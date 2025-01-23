#
#   IPP - projekt 1
#   
#   Adam Juliš
#
import xml.etree.ElementTree as ET
from enum import Enum
import sys
import re

#
#   This class hold the "ENUM" of Name of error, error-code and error message.
#   Next, only method exit_error print message to stderr and exit the program with correct error-code
#
class ErrorCode(Enum):

    PARAM_ERR = (10, "Wrong arguments, try --help\n")
    OPEN_IN_ERR = (11, "Problem with opening input file\n")
    OPEN_OUT_ERR = (12, "Problem with opening output file\n")
    HEADER_ERR = (21, "Missing header or something wrong with it\n")
    UNKNOW_OPCODE_ERR = (22, "Unknow opcode\n")
    LEX_SYNTAX_ERR = (23,"Lexical or Syntax error\n")
    INTERNAL_ERR = (99,"Internal error of parser.py. At least some bonus points for HONEST for this poor code :)\n")

    def __init__(self, code, err_message):
        self.code = code
        self.message = err_message

    def exit_error(self):
        print(f"{self.message}",file=sys.stderr)
        sys.exit(self.code)
        
#
#   This class hold whole input text and is used by parser for goin throught the whole input data. It generates XML data to ET structure
#   Additionally, before call the Parser itself (so when this class loading the data), it start ET.Element for possible XML generating 
#   and mainly, it could (and may) trim the input code from white spaces and comments ('#')
#
class Context:

    def __init__(self, text):
        self.current_line = 0
        self.file = self.trim_white_space(text)
        self.xml_root = ET.Element("program", language="IPPcode24")

    def trim_white_space(self, text):

        #delete comments
        text = re.sub('#.*', "", text)

        #split by line
        text = text.split('\n')

        #get lines with commands
        nasty_commands = []
        for line in text:
            #if not only white spaces on line
            if line.strip():
                nasty_commands.append(line)

        #if commands has any white spaces, just strip it
        commands = []
        for line in nasty_commands:
            command = re.sub(r'\s+', ' ', line).strip()
            commands.append(command)

        return commands

    def get_file(self):
        return self.file

    def increment_line(self):
        self.current_line += 1

    def get_number_line(self):
        return self.current_line
    
    def get_current_line(self):
        return self.file[self.current_line]

    def add_instruction(self, opcode, args = []): 

        #order requiered string
        number_of_command = str(self.current_line)
        instruction = ET.SubElement(self.xml_root, "instruction", order=number_of_command, opcode = opcode)
        
        #every argument requieres new line
        for arg in args:
            ET.SubElement(instruction, f"arg{arg['order']}", type =arg['type']).text = arg['value']

    def get_next_line(self):
        if self.current_line < len(self.file):
            line = self.file[self.current_line]
            #self.current_line += 1      ##mozna az pak, zalezi
            return line
        else:
            #eof detected
            return None
#
#   Parent class for all Opcodes
#   Contain methods which are used for the most of the child-Opcodes
#   Pretty simple, better read the code then my "English" comments trying explain it :)
#
class Opcode:

    def __init__(self, args_number):
        self._args_number = args_number

    def syntax_check(self, context, line):
        raise NotImplemented("ERR, SYNTAX_CHECK IS NOT IMPLEMENT")

    #number of operands for each operand is specific, so always check first as you can see lately 
    def args_check(self, line):
        if len(line.split()) != self._args_number:
            ErrorCode.LEX_SYNTAX_ERR.exit_error()

    def var_check(self, line):
        if not re.match(regex_enum.get("VAR"), line):
            ErrorCode.LEX_SYNTAX_ERR.exit_error()
    
    #should be merged with var_check only with flags or smth 
    def label_check(self, line):    
        if not re.match(regex_enum.get("LABEL"), line):
            ErrorCode.LEX_SYNTAX_ERR.exit_error()
    
    #do not check syntax!! has to be done before use
    def what_type_is_it(self, line):
        typee, value = line.split("@")
        if re.match(regex_enum.get("NOT_VAR"),typee):
            return typee, value
        typee = "var"
        return typee, line


    def string_retype(self, line):
        return line

    def symb_check(self, line):
        
        # First check symb without sring, if not passed then check string
        if not re.match(regex_enum.get("SYMB_NO_STRING"), line):
            if not re.match(regex_enum.get("STRING"), line):
                ErrorCode.LEX_SYNTAX_ERR.exit_error()
            else:

                return self.what_type_is_it(line)

        else:
            return self.what_type_is_it(line)    

#
#   Child classes, pretty similar and easy for understanding, just call correct methods from Opcode and then add instruction via Context
#
class DefvarOpcode(Opcode):
    
    def __init__(self):
        super().__init__(args_number=1)
    
    def syntax_check(self,context, line):
        
        self.args_check(line)
        self.var_check(line)
        var, value = line.split("@")

        context.add_instruction("DEFVAR", [{"order": 1, "type": "var", "value": line}] )
        return None
    
class MoveOpcode(Opcode):

    def __init__(self):
        super().__init__(args_number=2)
        
    def syntax_check(self,context, line):

        self.args_check(line)

        var, symb = line.split()
        self.var_check(var)
        typee, line = self.symb_check(symb)

        context.add_instruction("MOVE", [{"order": 1, "type": "var", "value": var},
                                         {"order": 2, "type": typee, "value": line}])

class CreateframeOpcode(Opcode):

    def __init__(self):
        super().__init__(args_number=0)
        
    def syntax_check(self,context, line):

        self.args_check(line)

        context.add_instruction("CREATEFRAME", [])

class PushframeOpcode(Opcode):
    
    def __init__(self):
        super().__init__(args_number=0)
        
    def syntax_check(self,context, line):

        self.args_check(line)

        context.add_instruction("PUSHFRAME", [])

class PopframeOpcode(Opcode):
    def __init__(self):
        super().__init__(args_number=0)
        
    def syntax_check(self,context, line):

        self.args_check(line)
    
        context.add_instruction("POPFRAME", [])

class CallOpcode(Opcode):

    def __init__(self):
        super().__init__(args_number=1)
        
    def syntax_check(self,context, line):

        self.args_check(line)
        self.label_check(line)

        context.add_instruction("CALL", [{"order": 1, "type": "label", "value": line}])

class ReturnOpcode(Opcode):

    def __init__(self):
        super().__init__(args_number=0)
        
    def syntax_check(self,context, line):

        self.args_check(line)

        context.add_instruction("RETURN", [])

class PushsOpcode(Opcode):
    
    def __init__(self):
        super().__init__(args_number=1)
        
    def syntax_check(self,context, line):

        self.args_check(line)
        typee, line = self.symb_check(line)

        context.add_instruction("PUSHS", [{"order": 1, "type": typee, "value": line}])

class PopsOpcode(Opcode):
    
    def __init__(self):
        super().__init__(args_number=1)
        
    def syntax_check(self,context, line):

        self.args_check(line)
        self.var_check(line) 

        context.add_instruction("POPS", [{"order": 1, "type": "var", "value": line}])

class AddOpcode(Opcode):

    def __init__(self):
        super().__init__(args_number=3)
        
    def syntax_check(self,context, line):

        self.args_check(line)

        var, symb, symb2 = line.split()
        self.var_check(var)
        typee, line = self.symb_check(symb)
        typee2, line2 = self.symb_check(symb2)

        context.add_instruction("ADD", [{"order": 1, "type": "var", "value": var},
                                         {"order": 2, "type": typee, "value": line},
                                         {"order": 3, "type": typee2, "value": line2}])

class SubOpcode(Opcode):

    def __init__(self):
        super().__init__(args_number=3)
        
    def syntax_check(self,context, line):

        self.args_check(line)

        var, symb, symb2 = line.split()
        self.var_check(var)
        typee, line = self.symb_check(symb)
        typee2, line2 = self.symb_check(symb2)

        context.add_instruction("SUB", [{"order": 1, "type": "var", "value": var},
                                         {"order": 2, "type": typee, "value": line},
                                         {"order": 3, "type": typee2, "value": line2}])
        
class MulOpcode(Opcode):

    def __init__(self):
        super().__init__(args_number=3)
        
    def syntax_check(self,context, line):

        self.args_check(line)

        var, symb, symb2 = line.split()
        self.var_check(var)
        typee, line = self.symb_check(symb)
        typee2, line2 = self.symb_check(symb2)

        context.add_instruction("MUL", [{"order": 1, "type": "var", "value": var},
                                         {"order": 2, "type": typee, "value": line},
                                         {"order": 3, "type": typee2, "value": line2}])

class IdivOpcode(Opcode):

    def __init__(self):
        super().__init__(args_number=3)
        
    def syntax_check(self,context, line):

        self.args_check(line)

        var, symb, symb2 = line.split()
        self.var_check(var)
        typee, line = self.symb_check(symb)
        typee2, line2 = self.symb_check(symb2)

        context.add_instruction("IDIV", [{"order": 1, "type": "var", "value": var},
                                         {"order": 2, "type": typee, "value": line},
                                         {"order": 3, "type": typee2, "value": line2}])
        
class LtOpcode(Opcode):

    def __init__(self):
        super().__init__(args_number=3)
        
    def syntax_check(self,context, line):

        self.args_check(line)

        var, symb, symb2 = line.split()
        self.var_check(var)
        typee, line = self.symb_check(symb)
        typee2, line2 = self.symb_check(symb2)

        context.add_instruction("LT", [{"order": 1, "type": "var", "value": var},
                                         {"order": 2, "type": typee, "value": line},
                                         {"order": 3, "type": typee2, "value": line2}])
        
class GtOpcode(Opcode):

    def __init__(self):
        super().__init__(args_number=3)
        
    def syntax_check(self,context, line):

        self.args_check(line)

        var, symb, symb2 = line.split()
        self.var_check(var)
        typee, line = self.symb_check(symb)
        typee2, line2 = self.symb_check(symb2)

        context.add_instruction("GT", [{"order": 1, "type": "var", "value": var},
                                         {"order": 2, "type": typee, "value": line},
                                         {"order": 3, "type": typee2, "value": line2}])
        
class EqOpcode(Opcode):

    def __init__(self):
        super().__init__(args_number=3)
        
    def syntax_check(self,context, line):

        self.args_check(line)

        var, symb, symb2 = line.split()
        self.var_check(var)
        typee, line = self.symb_check(symb)
        typee2, line2 = self.symb_check(symb2)

        context.add_instruction("EQ", [{"order": 1, "type": "var", "value": var},
                                         {"order": 2, "type": typee, "value": line},
                                         {"order": 3, "type": typee2, "value": line2}])
        
class AndOpcode(Opcode):

    def __init__(self):
        super().__init__(args_number=3)
    
    def syntax_check(self,context, line):

        self.args_check(line)

        var, symb, symb2 = line.split()
        self.var_check(var)
        typee, line = self.symb_check(symb)
        typee2, line2 = self.symb_check(symb2)

        context.add_instruction("AND", [{"order": 1, "type": "var", "value": var},
                                            {"order": 2, "type": typee, "value": line},
                                            {"order": 3, "type": typee2, "value": line2}])
            
class OrOpcode(Opcode):

    def __init__(self):
        super().__init__(args_number=3)
        
    def syntax_check(self,context, line):

        self.args_check(line)

        var, symb, symb2 = line.split()
        self.var_check(var)
        typee, line = self.symb_check(symb)
        typee2, line2 = self.symb_check(symb2)

        context.add_instruction("OR", [{"order": 1, "type": "var", "value": var},
                                         {"order": 2, "type": typee, "value": line},
                                         {"order": 3, "type": typee2, "value": line2}])
        
class NotOpcode(Opcode):

    def __init__(self):
        super().__init__(args_number=2)
        
    def syntax_check(self,context, line):

        self.args_check(line)

        var, symb = line.split()
        self.var_check(var)
        typee, line = self.symb_check(symb)
        context.add_instruction("NOT", [{"order": 1, "type": "var", "value": var},
                                        {"order": 2, "type": typee, "value": line}])

class Int2charOpcode(Opcode):

    def __init__(self):
        super().__init__(args_number=2)
        
    def syntax_check(self,context, line):

        self.args_check(line)

        var, symb = line.split()
        self.var_check(var)
        typee, line = self.symb_check(symb)

        context.add_instruction("INT2CHAR", [{"order": 1, "type": "var", "value": var},
                                            {"order": 2, "type": typee, "value": line}])
        
class Stri2intOpcode(Opcode):

    def __init__(self):
        super().__init__(args_number=3)
        
    def syntax_check(self,context, line):

        self.args_check(line)

        var, symb, symb2 = line.split()
        self.var_check(var)
        typee, line = self.symb_check(symb)
        typee2, line2 = self.symb_check(symb2)

        context.add_instruction("STRI2INT", [{"order": 1, "type": "var", "value": var},
                                        {"order": 2, "type": typee, "value": line},
                                         {"order": 3, "type": typee2, "value": line2}])
        
class ReadOpcode(Opcode):

    def __init__(self):
        super().__init__(args_number=2)
        
    def syntax_check(self,context, line):

        self.args_check(line)

        var, type = line.split()
        self.var_check(var)

        if not re.match(regex_enum.get("TYPE"), type):
            ErrorCode.LEX_SYNTAX_ERR.exit_error()

        context.add_instruction("READ", [{"order": 1, "type": "var", "value": var},
                                            {"order": 2, "type": "type", "value": type}])
        
class WriteOpcode(Opcode):
    
    def __init__(self):
        super().__init__(args_number=1)
        
    def syntax_check(self,context, line):

        self.args_check(line)
        var, value = self.symb_check(line)
        

        context.add_instruction("WRITE", [{"order": 1, "type": var, "value": value}])

class ConcatOpcode(Opcode):

    def __init__(self):
        super().__init__(args_number=3)
        
    def syntax_check(self,context, line):

        self.args_check(line)

        var, symb, symb2 = line.split()
        self.var_check(var)
        typee, line = self.symb_check(symb)
        typee2, line2 = self.symb_check(symb2)

        context.add_instruction("CONCAT", [{"order": 1, "type": "var", "value": var},
                                        {"order": 2, "type": typee, "value": line},
                                         {"order": 3, "type": typee2, "value": line2}])
       
class StrlenOpcode(Opcode):

    def __init__(self):
        super().__init__(args_number=2)
        
    def syntax_check(self,context, line):

        self.args_check(line)

        var, symb = line.split()
        self.var_check(var)
        typee, line = self.symb_check(symb)

        context.add_instruction("STRLEN", [{"order": 1, "type": "var", "value": var},
                                            {"order": 2, "type": typee, "value": line}])
        
class GetcharOpcode(Opcode):

    def __init__(self):
        super().__init__(args_number=3)
        
    def syntax_check(self,context, line):

        self.args_check(line)

        var, symb, symb2 = line.split()
        self.var_check(var)
        typee, line = self.symb_check(symb)
        typee2, line2 = self.symb_check(symb2)

        context.add_instruction("GETCHAR", [{"order": 1, "type": "var", "value": var},
                                        {"order": 2, "type": typee, "value": line},
                                         {"order": 3, "type": typee2, "value": line2}])

class SetcharOpcode(Opcode):

    def __init__(self):
        super().__init__(args_number=3)
        
    def syntax_check(self,context, line):

        self.args_check(line)

        var, symb, symb2 = line.split()
        self.var_check(var)
        typee, line = self.symb_check(symb)
        typee2, line2 = self.symb_check(symb2)

        context.add_instruction("SETCHAR", [{"order": 1, "type": "var", "value": var},
                                        {"order": 2, "type": typee, "value": line},
                                         {"order": 3, "type": typee2, "value": line2}])
class TypeOpcode(Opcode):

    def __init__(self):
        super().__init__(args_number=2)
        
    def syntax_check(self,context, line):

        self.args_check(line)

        var, symb = line.split()
        self.var_check(var)
        typee, line = self.symb_check(symb)

        context.add_instruction("TYPE", [{"order": 1, "type": "var", "value": var},
                                        {"order": 2, "type": typee, "value": line}])

class LabelOpcode(Opcode):

    def __init__(self):
        super().__init__(args_number=1)
        
    def syntax_check(self,context, line):

        self.args_check(line)
        self.label_check(line)

        context.add_instruction("LABEL", [{"order": 1, "type": "label", "value": line}])

class JumpOpcode(Opcode):

    def __init__(self):
        super().__init__(args_number=1)
        
    def syntax_check(self,context, line):

        self.args_check(line)
        self.label_check(line)

        context.add_instruction("JUMP", [{"order": 1, "type": "label", "value": line}])

class JumpifeqOpcode(Opcode):

    def __init__(self):
        super().__init__(args_number=3)
        
    def syntax_check(self,context, line):

        self.args_check(line)

        label, symb, symb2 = line.split()
        self.label_check(label)
        typee, line = self.symb_check(symb)
        typee2, line2 = self.symb_check(symb2)

        context.add_instruction("JUMPIFEQ", [{"order": 1, "type": "label", "value": label},
                                        {"order": 2, "type": typee, "value": line},
                                         {"order": 3, "type": typee2, "value": line2}])
        
class JumpifneqOpcode(Opcode):

    def __init__(self):
        super().__init__(args_number=3)
        
    def syntax_check(self,context, line):

        self.args_check(line)

        label, symb, symb2 = line.split()
        self.label_check(label)
        typee, line = self.symb_check(symb)
        typee2, line2 = self.symb_check(symb2)

        context.add_instruction("JUMPIFNEQ", [{"order": 1, "type": "label", "value": label},
                                        {"order": 2, "type": typee, "value": line},
                                         {"order": 3, "type": typee2, "value": line2}])
        
class ExitOpcode(Opcode):

    def __init__(self):
        super().__init__(args_number=1)
        
    def syntax_check(self,context, line):

        self.args_check(line)
        typee, line = self.symb_check(line)

        context.add_instruction("EXIT", [{"order": 1, "type": typee, "value": line}])

class DprintOpcode(Opcode):

    def __init__(self):
        super().__init__(args_number=1)
        
    def syntax_check(self,context, line):

        self.args_check(line)
        typee, line = self.symb_check(line)

        context.add_instruction("DPRINT", [{"order": 1, "type": typee, "value": line}])

class BreakOpcode(Opcode):

    def __init__(self):
        super().__init__(args_number=0)
        
    def syntax_check(self,context, line):

        self.args_check(line)

        context.add_instruction("BREAK", [])

#
#   This class load the Context and then, line by line check requiered things for check the syntax and lexical errors from input data 
#
        
class Parser:

    def __init__(self, context):
        self.context = context

    def parse(self):

        #check header, case not sensitive
        if (Context.get_next_line(self.context).upper() != ".IPPCODE24"):
            ErrorCode.HEADER_ERR.exit_error()

        self.context.increment_line()
        
        #Needed for correct detect commands like "Return", without that parser detect it as error
        short_command = 0

        #MAIN CYCLE FOR parse whole code
        while True:    
            line = self.context.get_next_line()

            #EOF detect
            if line is None:
                break

            #if commmand has 0 arguments, its go wrong
            try:
                opcode, rest_line = line.split(maxsplit = 1)

            #possible 0 argument opcode detected
            except:
                opcode = line
                short_command = 1

            opcode = opcode.upper()

            command = opcode_enum.get(opcode)

            #pretty complicated if because author want fast-fix the problem with wrong error code when double header comes
            if command:
                if short_command:
                    command.syntax_check(self.context, "")
                else:
                    command.syntax_check(self.context, rest_line)
            elif self.context.get_number_line() == 1:
                if opcode == ".IPPCODE24":
                    ErrorCode.LEX_SYNTAX_ERR.exit_error()
                else:
                    ErrorCode.UNKNOW_OPCODE_ERR.exit_error()
            else:        
                ErrorCode.UNKNOW_OPCODE_ERR.exit_error()
            
            #every loop we need reset the short_command detection
            short_command = 0
            #get new_line didnt increment the line counter 
            self.context.increment_line()

#
#   Dictionary for better orientation in code 
#
regex_enum = {
    "VAR" : r"^(GF|LF|TF)@[a-zA-Z_\-$&%*!?][a-zA-Z0-9_\-$&%*!?]*$",
    "SYMB_NO_STRING" : r"^(GF|LF|TF)@[a-zA-Z_\-$&%*!?][a-zA-Z0-9_\-$&%*!?]*$|^(bool@true|bool@false|nil@nil|int@[+-]?[0-9]+)",
    "STRING"    :   r"^string@[^\s#]*" ,    #
    "LABEL" : r"^[a-zA-Z_\-$&%*!?][a-zA-Z0-9_\-$&%*?!]*$",
    "TYPE"  : r"^(string|bool|int)$",
    "NOT_VAR" : r"^(int|string|bool|nil)"
}

#
#   Dictionary for elegant choosing class in the main loop of parser
#
opcode_enum = {
    "MOVE": MoveOpcode(),
    "CREATEFRAME": CreateframeOpcode(),
    "PUSHFRAME": PushframeOpcode(),
    "POPFRAME": PopframeOpcode(),
    "DEFVAR": DefvarOpcode(),
     "CALL": CallOpcode(),
    "RETURN": ReturnOpcode(),
    "PUSHS": PushsOpcode(),
    "POPS": PopsOpcode(),
    "ADD": AddOpcode(),
    "SUB": SubOpcode(),
    "MUL": MulOpcode(),
    "IDIV": IdivOpcode(),
    "LT": LtOpcode(),
    "GT": GtOpcode(),
    "EQ": EqOpcode(),
    "AND": AndOpcode(),
    "OR": OrOpcode(),
    "NOT": NotOpcode(),
    "INT2CHAR": Int2charOpcode(),
    "STRI2INT": Stri2intOpcode(),
    "READ": ReadOpcode(),
    "WRITE": WriteOpcode(),
    "CONCAT": ConcatOpcode(),
    "STRLEN": StrlenOpcode(),
    "GETCHAR": GetcharOpcode(),
    "SETCHAR": SetcharOpcode(),
    "TYPE": TypeOpcode(),
    "LABEL": LabelOpcode(),
    "JUMP": JumpOpcode(),
    "JUMPIFEQ": JumpifeqOpcode(),
    "JUMPIFNEQ": JumpifneqOpcode(),
    "EXIT": ExitOpcode(),
    "DPRINT": DprintOpcode(),
    "BREAK": BreakOpcode(),

}

#
#   This is the first and last function on code for check 0 arguments or print help
#
def check_args():

    if "--help" in sys.argv:
        if (len(sys.argv) == 2):
            print("HELP MESSAGE, check the documentation, simply use is: python3.x parse.py < \"name_of_file_with_.IPPcode24_code\"\nHAPPY TESTING!")
            sys.exit(0)
        else:
            ErrorCode.PARAM_ERR.exit_error()
    elif len(sys.argv) > 1:
        ErrorCode.PARAM_ERR.exit_error()

def main():

    check_args()
    context = Context(sys.stdin.read())
    parser = Parser(context)

    #whole parser
    parser.parse()

    #generating of xml
    tree = ET.ElementTree(context.xml_root)
    ET.indent(tree, space="  ")
    
    #print the results on stdout, header is print mannualy
    print('<?xml version="1.0" encoding="UTF-8"?>')
    ET.dump(tree)

if __name__ == '__main__':
    main()
    sys.exit(0)
