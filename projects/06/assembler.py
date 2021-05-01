"""
Naresh Joshi
Assembler program to convert HACK assembly to binary
"""
import re

import numpy as np
import sys

symbol_table = {
    'R0': 0, 'R1': 1, 'R2': 2, 'R3': 3,
    'R4': 4, 'R5': 5, 'R6': 6, 'R7': 7,
    'R8': 8, 'R9': 9, 'R10': 10, 'R11': 11,
    'R12': 12, 'R13': 13, 'R14': 14, 'R15': 15,
    'SCREEN': 16384, 'KBD': 24576,
    'SP': 0, 'LCL': 1, 'ARG': 2, 'THIS': 3, 'THAT': 4
}

computations = {
    '0': '0101010',
    '1': '0111111',
    '-1': '0111010',
    'D': '0001100',
    'A': '0110000', 'M': '1110000',
    '!D': '0001101',
    '!A': '0110001', '!M': '1110001',
    '-D': '0001111',
    '-A': '0110011', '-M': '1110011',
    'D+1': '0011111',
    'A+1': '0110111', 'M+1': '1110111',
    'D-1': '0001110',
    'A-1': '0110010', 'M-1': '1110010',
    'D+A': '0000010', 'D+M': '1000010',
    'D-A': '0010011', 'D-M': '1010011',
    'A-D': '0000111', 'M-D': '1000111',
    'D&A': '0000000', 'D&M': '1000000',
    'D|A': '0010101', 'D|M': '1010101'
}

destinations = {
    'null': '000',
    'M': '001',
    'D': '010',
    'MD': '011',
    'A': '100',
    'AM': '101',
    'AD': '110',
    'AMD': '111'
}

jumps = {
    'null': '000',
    'JGT': '001',
    'JEQ': '010',
    'JGE': '011',
    'JLT': '100',
    'JNE': '101',
    'JLE': '110',
    'JMP': '111'
}


def run():
    asm_file = 'input.asm'
    if len(sys.argv) > 1:
        asm_file = sys.argv[1]

    hack_file = asm_file.replace('.asm', '.hack')

    print(f"Reading input asm file {asm_file}")
    lines = de_comment(asm_file)

    lines = pass1(lines)

    binaries = pass2(lines)

    print(f'Assembly Instructions : {[line for line in lines if line]}')
    print(f'Symbol Table : {symbol_table}')
    print(f'Binary Instructions : {binaries}')

    print(f"Writing to output hack file {hack_file}")
    generate_hack(hack_file, binaries)


def de_comment(asm_file):
    lines = []
    with open(asm_file) as file:
        line = file.readline()
        is_comment = False
        while line:
            line = re.sub(' ', '', line).strip()
            line = re.sub(r'//.*', '', line)
            line = re.sub(r'/\*.*\*/', '', line)

            if line.startswith('/*'):
                is_comment = True
                line = ''
            elif line.endswith('*/'):
                is_comment = False
                line = ''

            if is_comment:
                lines.append('')
            else:
                lines.append(line)

            line = file.readline()
    return lines


def pass1(lines):
    inst_count = 0
    for line in lines:
        if line:
            if line.startswith('@'):
                symbol = re.sub('@', '', line)
                if not symbol.isdigit() and symbol not in symbol_table:
                    symbol_table[symbol] = -1
                inst_count += 1
            elif line.startswith('('):
                symbol = re.sub(r'[()]', '', line)
                symbol_table[symbol] = inst_count
                new_line = re.sub(r'.*\)', '', line)
                if new_line:
                    lines[lines.index(line)] = new_line
                else:
                    lines[lines.index(line)] = ''
            else:
                inst_count += 1

    ram = 16
    for symbol in symbol_table.keys():
        if symbol_table[symbol] == -1:
            symbol_table[symbol] = ram
            ram += 1
    return lines


def pass2(lines):
    binaries = []

    line_count = 0
    for line in lines:
        line_count += 1
        if line:
            if line.startswith('@'):
                inst = re.sub('@', '', line)
                inst = inst if inst.isdigit() else symbol_table[inst]
                binaries.append('0' + np.binary_repr(int(inst), 15))
            else:
                inst = line
                if '=' not in inst:
                    inst = f'null={inst}'
                if ';' not in inst:
                    inst = f'{inst};null'

                tokens = re.split(r'[=;]', inst)
                if len(tokens) < 3 or len(tokens) > 3:
                    raise Exception(f'Error at line {line_count}, {line} is not a valid instruction')

                dest = destinations.get(tokens[0], None)
                comp = computations.get(tokens[1], None)
                jump = jumps.get(tokens[2], None)

                if not dest or not comp or not jump:
                    raise Exception(f'Error at line {line_count}, {line} is not a valid instruction')

                binaries.append(f'111{comp}{dest}{jump}')
    return binaries


def generate_hack(hack_file, binaries):
    with open(hack_file, 'w') as file:
        for binary in binaries:
            file.write(binary + '\n')


run()
