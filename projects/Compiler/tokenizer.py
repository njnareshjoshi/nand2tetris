"""
Compiler program to convert Jack program into VM code.
We can run the program in following ways
    python3 compiler.py jack_file.jack
    python3 compiler.py jack_file1.jack,jack_file2.jack
    python3 compiler.py directory_of_jack_file

By
    Naresh Joshi
"""

import re
from collections import namedtuple

KEYWORDS = [
    'class', 'constructor', 'function', 'method', 'field', 'static',
    'var', 'int', 'char', 'boolean', 'void', 'true', 'false', 'null', 'this',
    'let', 'do', 'if', 'else', 'while', 'return'
]

KEYWORD_REGEX = '|'.join([f'{keyword}' for keyword in KEYWORDS])
SYMBOL_REGEX = r'\{|\}|\(|\)|\[|\]|\.|,|;|\+|-|\*|/|&|\||\<|\>|=|~'
INTEGER_CONSTANT_REGEX = r'\d+'
STRING_CONSTANT_REGEX = r'"[^"]*"'
IDENTIFIER_REGEX = r'[A-z_][A-z_\d]*'
SPACE_REGEX = r'\s+'

# A list regex and its lexical element type in there precedence
TOKEN_TYPES = [
    (KEYWORD_REGEX, 'keyword'),
    (SYMBOL_REGEX, 'symbol'),
    (INTEGER_CONSTANT_REGEX, 'integerConstant'),
    (STRING_CONSTANT_REGEX, 'stringConstant'),
    (IDENTIFIER_REGEX, 'identifier')
]

JACK_TO_XML_OP = {
    '&': '&amp;',
    '<': '&lt;',
    '>': '&gt;',
}

Token = namedtuple('Token', ('type', 'value'))


def tokenize(jack_file_name):
    jack_file = de_comment(jack_file_name)

    code_segments = re.split(f'({SYMBOL_REGEX}|{STRING_CONSTANT_REGEX})|{SPACE_REGEX}', jack_file)

    tokens = []
    for token in code_segments:
        if not token:
            continue

        for expr, token_type in TOKEN_TYPES:
            if re.match(expr, token):
                tokens.append(Token(token_type, token))
                break
        else:
            raise Exception(f'Error at - {token} is not a valid instruction')

    lex_file_name = jack_file_name.replace('.jack', 'T.xml')
    print(f"Generating token file {lex_file_name}")
    with open(lex_file_name, 'w') as lex_file:
        lex_file.write('<tokens>\n')

        for token in tokens:
            token_value = JACK_TO_XML_OP.get(token.value, token.value.replace('"', ''))
            lex_file.write(f'<{token.type}> {token_value} </{token.type}>\n')

        lex_file.write('</tokens>\n')

    return tokens


def de_comment(jack_file_name):
    instructions = []

    print(f"Reading jack file {jack_file_name}")

    with open(jack_file_name) as jack_file:
        instruction = jack_file.readline()
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

            instruction = instruction.strip()
            if instruction and not is_comment:
                instructions.append(instruction)

            instruction = jack_file.readline()

    return '\n'.join(instructions)
