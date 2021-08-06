"""
Compiler program to convert Jack program into VM code.
We can run the program in following ways
    python3 compiler.py jack_file.jack
    python3 compiler.py jack_file1.jack,jack_file2.jack
    python3 compiler.py directory_of_jack_file

By
    Naresh Joshi
"""

import os
import re
import sys

import parser
import tokenizer


def run():
    file_path = 'Main.jack'
    if len(sys.argv) > 1:
        file_path = sys.argv[1]

    jack_file_names = get_jack_file_names(file_path)

    for jack_file_name in jack_file_names:
        tokens = tokenizer.tokenize(jack_file_name)

        xml_file_name = jack_file_name.replace('.jack', '.xml')
        vm_file_name = jack_file_name.replace('.jack', '.vm')

        class_name = jack_file_name.replace('.jack', '').split('/')[-1]
        with open(xml_file_name, 'w') as xml_file, open(vm_file_name, 'w') as vm_file:
            compiler = parser.Compiler(tokens, class_name, xml_file, vm_file)
            compiler.compile_class()


def get_jack_file_names(file_path):
    if '.jack' in file_path:
        if "," in file_path or " " in file_path:
            jack_file_names = re.split(r"[, ]", file_path)
        else:
            jack_file_names = [file_path]
    else:
        file_path = file_path[:-1] if file_path[-1] == '/' else file_path
        path_elements = file_path.split('/')
        path = '/'.join(path_elements)

        dir_path, dir_names, file_names = next(os.walk(file_path), [[], [], []])
        jack_file_names = filter(lambda x: '.jack' in x, file_names)
        jack_file_names = [path + '/' + jack_file for jack_file in jack_file_names]
    return jack_file_names


run()
