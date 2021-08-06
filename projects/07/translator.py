"""
Translator program to convert vm instructions to assembly instructions.
We can run the translator in following ways
    python3 translator.py vm_file.vm
    python3 translator.py vm_file1.vm,vm_file2.vm
    python3 translator.py directory_of_vm_file

If present then Sys.vm file needs to be passed in as first file to the translator program to initiate the execution
By
    Naresh Joshi - CS19M506
    Shubham Sangal - CS19M521
"""
import os
import random
import re
import sys

segments = {
    "local": "LCL",
    "argument": "ARG",
    "this": "THIS",
    "that": "THAT"
}

ADD = [
    "@SP",
    "AM=M-1",
    "D=M",
    "M=0",
    "A=A-1",
    "M=D+M"
]

SUB = [
    "@SP",
    "AM=M-1",
    "D=M",
    "M=0",
    "A=A-1",
    "M=M-D"
]

NEG = [
    "@SP",
    "A=M-1",
    "M=-M"
]

AND = [
    "@SP",
    "AM=M-1",
    "D=M",
    "M=0",
    "A=A-1",
    "M=D&M"
]

OR = [
    "@SP",
    "AM=M-1",
    "D=M",
    "M=0",
    "A=A-1",
    "M=D|M"
]

NOT = [
    "@SP",
    "A=M-1",
    "M=!M"
]

PUSH = [
    "@SP",
    "A=M",
    "M=D",
    "@SP",
    "M=M+1"
]

POP = [
    "@R13",
    "M=D",
    "@SP",
    "AM=M-1",
    "D=M",
    "M=0",
    "@R13",
    "A=M",
    "M=D"
]

RETURN = [
    # frame = R14 = LCL
    "@LCL",
    "D=M",
    "@R14",
    "M=D",
    # RET = R13 = *(LCL - 5)
    "@5",
    "A=D-A",
    "D=M",
    "@R13",
    "M=D",
    # *ARG = *(SP - 1)
    "@SP",
    "A=M-1",
    "D=M",
    "@ARG",
    "A=M",
    "M=D ",
    # SP = ARG + 1
    "D=A+1",
    "@SP",
    "M=D",
    # THAT = *(frame - 1)
    "@R14",
    "AM=M-1",
    "D=M",
    "@THAT",
    "M=D",
    # THIS = *(frame - 1)
    "@R14",
    "AM=M-1",
    "D=M",
    "@THIS",
    "M=D",
    # ARG = *(frame - 1)
    "@R14",
    "AM=M-1",
    "D=M",
    "@ARG",
    "M=D",
    # LCL = *(frame - 1)
    "@R14",
    "AM=M-1",
    "D=M",
    "@LCL",
    "M=D",
    # goto RET R13
    "@R13",
    "A=M",
    "0;JMP"
]


def run():
    file_path = 'input.vm'
    if len(sys.argv) > 1:
        file_path = sys.argv[1]

    if '.vm' in file_path:
        if "," in file_path or " " in file_path:
            vm_files = re.split(r"[, ]", file_path)
            path_elements = vm_files[0].split('/')
            path_elements = path_elements[0:-1]

            asm_file = '/'.join(path_elements) + '/' + path_elements[-1] + '.asm'
        else:
            asm_file = file_path.replace('.vm', '.asm')
            vm_files = [file_path]
    else:
        file_path = file_path[:-1] if file_path[-1] == '/' else file_path
        path_elements = file_path.split('/')
        path = '/'.join(path_elements)

        asm_file = path + '/' + path_elements[-1] + '.asm'

        dirpath, dirnames, filenames = next(os.walk(file_path), [[], [], []])
        vm_files = filter(lambda x: '.vm' in x, filenames)
        vm_files = [path + '/' + vm_file for vm_file in vm_files]

    asm_instructions = []
    for vm_file in vm_files:
        asm_instructions.append(f"// {vm_file}")

        print(f"Reading input file {vm_file}")
        vm_instructions = de_comment(vm_file)

        program = vm_file.replace('.vm', '').split("/")[-1]

        asm_instructions += parse_vm_instructions(program, vm_instructions)

        print(f'VM Instructions : {[line for line in vm_instructions if line]}')
        print(f'Asm Instructions : {asm_instructions}')

    print(f"Writing to output file {asm_file}")
    generate_asm(asm_file, asm_instructions)


def de_comment(vm_file):
    instructions = []
    with open(vm_file) as file:
        instruction = file.readline()
        is_comment = False
        while instruction:
            instruction = instruction.strip()
            instruction = re.sub(r'//.*', '', instruction)
            instruction = re.sub(r'/\*.*\*/', '', instruction)

            if instruction.startswith('/*'):
                is_comment = True
                instruction = ''
            elif instruction.endswith('*/'):
                is_comment = False
                instruction = ''

            if is_comment:
                instructions.append('')
            else:
                instructions.append(instruction.strip())

            instruction = file.readline()
    return instructions


def parse_vm_instructions(program, vm_instructions):
    line_count = 0
    asm_instructions = []

    if program == "Sys":
        asm_instructions += sys_init(program)

    for instruction in vm_instructions:
        line_count += 1
        if instruction:
            asm_instructions.append(f"// {instruction}")
            asm_instructions += parse_vm_instruction(program, line_count, instruction)
    return asm_instructions


def parse_vm_instruction(program, line_count, instruction):
    if instruction == "add":
        return ADD
    elif instruction == "sub":
        return SUB
    elif instruction == "neg":
        return NEG
    elif instruction == "eq":
        return equality(program, line_count, instruction)
    elif instruction == "gt":
        return equality(program, line_count, instruction)
    elif instruction == "lt":
        return equality(program, line_count, instruction)
    elif instruction == "and":
        return AND
    elif instruction == "or":
        return OR
    elif instruction == "not":
        return NOT
    else:
        tokens = instruction.split(" ")
        if len(tokens) <= 0 or len(tokens) > 3:
            raise Exception(f'Error at line {line_count}, {instruction} is not a valid instruction')
        elif tokens[0] == "push":
            return parse_push(program, tokens[1], tokens[2])
        elif tokens[0] == "pop":
            return parse_pop(program, tokens[1], tokens[2])
        elif tokens[0] == "label":
            return [f"({program}_{tokens[1]})"]
        elif tokens[0] == "goto":
            return goto(program, tokens[1])
        elif tokens[0] == "if-goto":
            return if_goto(program, tokens[1])
        elif tokens[0] == "function":
            return function(tokens[1], tokens[2])
        elif tokens[0] == "call":
            return call(program, tokens[1], tokens[2])
        elif tokens[0] == "return":
            return RETURN
        else:
            raise Exception(f'Error at line {line_count}, {instruction} is not a valid instruction')


def equality(program, line_count, operation):
    operations = {
        "eq": "JNE",
        "gt": "JLE",
        "lt": "JGE"
    }
    return [
        "@SP",
        "AM=M-1",
        "D=M",
        "M=0",
        "A=A-1",
        "D=M-D",
        "M=0",
        f"@{operation}_{program}_{line_count}",
        f"D;{operations[operation]}",
        "@SP",
        "A=M",
        "A=A-1",
        "M=-1",
        f"({operation}_{program}_{line_count})",
    ]


def parse_push(program, segment, index):
    if segment in ["local", "argument", "this", "that"]:
        return [
                   f"@{segments[segment]}",
                   "D=M",
                   f"@{index}",
                   "A=D+A",
                   "D=M",
               ] + PUSH
    elif segment == "pointer":
        if index in ["0", "1"]:
            return [
                       "@THIS" if index == "0" else "@THAT",
                       "D=M",
                   ] + PUSH
        else:
            raise Exception(f'Error at - push {segment} {index} is not a valid instruction')
    elif segment == "constant":
        return [
                   f"@{index}",
                   "D=A",
               ] + PUSH
    elif segment == "static":
        return [
                   f"@{program}_{index}",
                   "D=M",
               ] + PUSH
    elif segment == "temp":
        return [
                   "@R5",
                   "D=A",
                   f"@{index}",
                   "A=D+A",
                   "D=M",
               ] + PUSH
    else:
        raise Exception(f'Error at - push {segment} {index} is not a valid instruction')


def parse_pop(program, segment, index):
    if segment in ["local", "argument", "this", "that"]:
        return [
                   f"@{segments[segment]}",
                   "D=M",
                   f"@{index}",
                   "D=D+A"
               ] + POP
    elif segment == "pointer":
        if index in ["0", "1"]:
            return [
                "@SP",
                "AM=M-1",
                "D=M",
                "M=0",
                "@THIS" if index == "0" else "@THAT",
                "M=D"
            ]
        else:
            raise Exception(f'Error at - pop {segment} {index} is not a valid instruction')
    elif segment == "static":
        return [
            "@SP",
            "AM=M-1",
            "D=M",
            "M=0",
            f"@{program}_{index}",
            "M=D"
        ]
    elif segment == "temp":
        return [
                   "@R5",
                   "D=A",
                   f"@{index}",
                   "D=D+A"
               ] + POP
    else:
        raise Exception(f'Error at - pop {segment} {index} is not a valid instruction')


def goto(program, label):
    return [
        f"@{program}_{label}",
        "0;JMP"
    ]


def if_goto(program, label):
    return [
        "@SP",
        "AM=M-1",
        "D=M",
        "M=0",
        f"@{program}_{label}",
        "D;JNE"
    ]


def function(f, k):
    instructions = [
        f"({f})",
        "@SP",
        "A=M"
    ]

    for i in range(int(k)):
        instructions += [
            "M=0",
            "A=A+1"
        ]

    return instructions + [
        "D=A",
        "@SP",
        "M=D"
    ]


def call(program, f, n):
    count = random.randint(1, 100)
    return [
        # Push return address
        f"@ret_{program}_{count}",
        "D=A",
        "@SP",
        "A=M",
        "M=D",
        "@SP",
        "M=M+1",
        # Push LCL
        "@LCL",
        "D=M",
        "@SP",
        "A=M",
        "M=D",
        "@SP",
        "M=M+1",
        # Push ARG
        "@ARG",
        "D=M",
        "@SP",
        "A=M",
        "M=D",
        "@SP",
        "M=M+1",
        # Push THIS
        "@THIS",
        "D=M",
        "@SP",
        "A=M",
        "M=D",
        "@SP",
        "M=M+1",
        # Push THAT
        "@THAT",
        "D=M",
        "@SP",
        "A=M",
        "M=D",
        "@SP",
        "M=M+1",
        # ARG = SP - n - 5
        f"@{str(int(n) + 5)}",
        "D=A",
        "@SP",
        "D=M-D",
        "@ARG",
        "M=D",
        # LCL = SP
        "@SP",
        "D=M",
        "@LCL",
        "M=D",
        # goto f
        f"@{f}",
        "0;JMP",
        # (ret)
        f"(ret_{program}_{count})"
    ]


def sys_init(program):
    return [
               "@256",
               "D=A",
               "@SP",
               "M=D",
           ] + call(program, "Sys.init", "0") + ["0;JMP"]


def generate_asm(asm_file, asm_instructions):
    with open(asm_file, 'w') as file:
        for instruction in asm_instructions:
            file.write(instruction + '\n')


run()
