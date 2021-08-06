"""
Compiler program to convert Jack program into VM code.
We can run the program in following ways
    python3 compiler.py jack_file.jack
    python3 compiler.py jack_file1.jack,jack_file2.jack
    python3 compiler.py directory_of_jack_file

By
    Naresh Joshi
"""

from collections import namedtuple

JackSymbol = namedtuple('Symbol', ['kind', 'type', 'index'])

JACK_TO_VM_OP = {
    '+': 'add',
    '-': 'sub',
    '*': 'call Math.multiply 2',
    '/': 'call Math.divide 2',
    '&': 'and',
    '|': 'or',
    '<': 'lt',
    '>': 'gt',
    '=': 'eq'
}

JACK_TO_XML_OP = {
    '&': '&amp;',
    '<': '&lt;',
    '>': '&gt;',
}


class Compiler:
    def __init__(self, tokens, class_name, xml_file, vm_file):
        self.tokens = tokens
        self.class_name = class_name
        self.xml_file = xml_file
        self.vm_file = vm_file

        self.label_count = 0

    def current_token(self):
        return self.tokens[0] if self.tokens else None

    def pop_token(self, indent, expected=None):
        token = self.tokens.pop(0) if self.tokens else None

        if expected is not None and token.value not in expected:
            expected_values = ' or '.join(expected)
            raise Exception(
                f'Error in - {self.class_name}.jack: Expected `{expected_values}` but found : `{token.value}`'
            )

        token_value = JACK_TO_XML_OP.get(token.value, token.value.replace('"', ''))
        self.xml_file.write(f'{" " * indent}<{token.type}> {token_value} </{token.type}>\n')
        return token

    def get_label(self):
        label = f'{self.class_name}.L{self.label_count}'
        self.label_count += 1
        return label

    def compile_class(self):
        self.xml_file.write(f'<class>\n')

        indent = 2

        self.pop_token(indent, expected={'class'})

        try:
            jack_class = JackClass(self.pop_token(indent, expected={self.class_name}).value)
        except:
            raise Exception(f"Error in - {self.class_name}.jack: The class name doesn't match the file name")

        self.pop_token(indent, expected={'{'})

        self.compile_class_var_dec(jack_class, indent)
        self.compile_subroutine(jack_class, indent)

        self.pop_token(indent, expected={'}'})

        self.xml_file.write(f'</class>\n')

    def compile_class_var_dec(self, jack_class, indent):
        token = self.current_token()

        while token is not None and token.type == 'keyword' and token.value in ['static', 'field']:
            self.xml_file.write(f'{" " * indent}<classVarDec>\n')

            internal_indent = indent + 2

            self.pop_token(internal_indent)

            is_static_var = (token.value == 'static')

            var_type = self.pop_token(internal_indent).value

            var_exists = True
            while var_exists:
                var_name = self.pop_token(internal_indent).value

                if is_static_var:
                    jack_class.add_static_var(var_name, var_type)
                else:
                    jack_class.add_field_var(var_name, var_type)

                token = self.pop_token(internal_indent, expected={',', ';'})
                var_exists = (token == ('symbol', ','))

            self.xml_file.write(f'{" " * indent}</classVarDec>\n')
            token = self.current_token()

    def compile_subroutine(self, jack_class, indent):
        token = self.current_token()
        while token is not None and token.type == 'keyword' and token.value in ['constructor', 'function', 'method']:
            self.xml_file.write(f'{" " * indent}<subroutineDec>\n')

            internal_indent = indent + 2

            subroutine_type = self.pop_token(internal_indent).value
            return_type = self.pop_token(internal_indent).value
            name = self.pop_token(internal_indent).value

            jack_subroutine = JackSubroutine(name, subroutine_type, return_type, jack_class)

            self.pop_token(internal_indent, expected={'('})

            self.compile_parameter_list(jack_subroutine, internal_indent)

            self.pop_token(internal_indent, expected={')'})

            self.compile_subroutine_body(jack_subroutine, internal_indent)

            self.xml_file.write(f'{" " * indent}</subroutineDec>\n')

            token = self.current_token()

    def compile_parameter_list(self, jack_subroutine, indent):
        self.xml_file.write(f'{" " * indent}<parameterList>\n')

        internal_indent = indent + 2

        token = self.current_token()
        parameter_exists = token is not None and token.type in ['keyword', 'identifier']
        while parameter_exists:
            parameter_type = self.pop_token(internal_indent).value
            parameter_name = self.pop_token(internal_indent).value

            jack_subroutine.add_argument(parameter_name, parameter_type)

            token = self.current_token()
            if token == ('symbol', ','):
                self.pop_token(internal_indent)  # Pop ',' from tokens
                token = self.current_token()
                parameter_exists = token is not None and token.type in ['keyword', 'identifier']
            else:
                parameter_exists = False
        self.xml_file.write(f'{" " * indent}</parameterList>\n')

    def compile_subroutine_body(self, jack_subroutine, indent):

        self.xml_file.write(f'{" " * indent}<subroutineBody>\n')

        internal_indent = indent + 2

        self.pop_token(internal_indent, expected={'{'})

        self.compile_var_dec(jack_subroutine, internal_indent)

        self.write_function(jack_subroutine)

        if jack_subroutine.subroutine_type == 'constructor':
            field_count = jack_subroutine.jack_class.field_var_count
            self.write_push('constant', field_count)
            self.write_call('Memory', 'alloc', 1)
            self.write_pop('pointer', 0)
        elif jack_subroutine.subroutine_type == 'method':
            self.write_push('argument', 0)
            self.write_pop('pointer', 0)

        self.compile_statements(jack_subroutine, internal_indent)

        self.pop_token(internal_indent, expected={'}'})

        self.xml_file.write(f'{" " * indent}</subroutineBody>\n')

    def compile_var_dec(self, jack_subroutine, indent):
        internal_indent = indent + 2
        token = self.current_token()
        while token is not None and token == ('keyword', 'var'):
            self.xml_file.write(f'{" " * indent}<varDec>\n')

            self.pop_token(internal_indent)

            var_type = self.pop_token(internal_indent).value
            var_name = self.pop_token(internal_indent).value

            jack_subroutine.add_local_var(var_name, var_type)

            while self.pop_token(internal_indent, expected={',', ';'}) == ('symbol', ','):
                var_name = self.pop_token(internal_indent).value
                jack_subroutine.add_local_var(var_name, var_type)

            token = self.current_token()

            self.xml_file.write(f'{" " * indent}</varDec>\n')

    def compile_statements(self, jack_subroutine, indent):
        self.xml_file.write(f'{" " * indent}<statements>\n')

        internal_indent = indent + 2

        statements_exists = True
        while statements_exists:
            token = self.current_token()

            if token == ('keyword', 'let'):
                self.compile_let_statement(jack_subroutine, internal_indent)
            elif token == ('keyword', 'if'):
                self.compile_if_statement(jack_subroutine, internal_indent)
            elif token == ('keyword', 'while'):
                self.compile_while_statement(jack_subroutine, internal_indent)
            elif token == ('keyword', 'do'):
                self.compile_do_statement(jack_subroutine, internal_indent)
            elif token == ('keyword', 'return'):
                self.compile_return_statement(jack_subroutine, internal_indent)
            else:
                statements_exists = False

        self.xml_file.write(f'{" " * indent}</statements>\n')

    def compile_let_statement(self, jack_subroutine, indent):
        self.xml_file.write(f'{" " * indent}<letStatement>\n')

        internal_indent = indent + 2

        self.pop_token(internal_indent)

        var_name = self.pop_token(internal_indent).value

        jack_symbol = jack_subroutine.get_symbol(var_name)

        is_array = self.current_token().value == '['
        if is_array:
            self.pop_token(internal_indent, expected={'['})
            self.compile_expression(jack_subroutine, internal_indent)
            self.pop_token(internal_indent, expected={']'})

            self.pop_token(internal_indent, expected={'='})

            self.write_push_symbol(jack_symbol)
            self.write('add')

            self.compile_expression(jack_subroutine, internal_indent)
            self.write_pop('temp', 0)
            self.write_pop('pointer', 1)
            self.write_push('temp', 0)
            self.write_pop('that', 0)
        else:
            self.pop_token(internal_indent, expected={'='})
            self.compile_expression(jack_subroutine, internal_indent)
            self.write_pop_symbol(jack_symbol)

        self.pop_token(internal_indent, expected={';'})

        self.xml_file.write(f'{" " * indent}</letStatement>\n')

    def compile_if_statement(self, jack_subroutine, indent):
        self.xml_file.write(f'{" " * indent}<ifStatement>\n')

        internal_indent = indent + 2

        self.pop_token(internal_indent)
        self.pop_token(internal_indent, expected={'('})
        self.compile_expression(jack_subroutine, internal_indent)
        self.pop_token(internal_indent, expected={')'})
        self.pop_token(internal_indent, expected={'{'})

        if_false_label = self.get_label()
        if_true_label = self.get_label()

        self.write_if(if_false_label)

        self.compile_statements(jack_subroutine, internal_indent)

        self.write_goto(if_true_label)
        self.write_label(if_false_label)

        self.pop_token(internal_indent, expected={'}'})

        token = self.current_token()
        if token == ('keyword', 'else'):
            self.pop_token(internal_indent)
            self.pop_token(internal_indent, expected={'{'})
            self.compile_statements(jack_subroutine, internal_indent)
            self.pop_token(internal_indent, expected={'}'})

        self.write_label(if_true_label)

        self.xml_file.write(f'{" " * indent}</ifStatement>\n')

    def compile_while_statement(self, jack_subroutine, indent):
        self.xml_file.write(f'{" " * indent}<whileStatement>\n')

        internal_indent = indent + 2

        self.pop_token(internal_indent)
        self.pop_token(internal_indent, expected={'('})

        while_true_label = self.get_label()
        while_false_label = self.get_label()

        self.write_label(while_true_label)
        self.compile_expression(jack_subroutine, internal_indent)

        self.pop_token(internal_indent, expected={')'})
        self.pop_token(internal_indent, expected={'{'})

        self.write_if(while_false_label)

        self.compile_statements(jack_subroutine, internal_indent)

        self.write_goto(while_true_label)
        self.write_label(while_false_label)

        self.pop_token(internal_indent, expected={'}'})

        self.xml_file.write(f'{" " * indent}</whileStatement>\n')

    def compile_do_statement(self, jack_subroutine, indent):
        self.xml_file.write(f'{" " * indent}<doStatement>\n')

        internal_indent = indent + 2

        self.pop_token(internal_indent)

        token = self.pop_token(internal_indent)

        token_value = token.value
        token_var_name = jack_subroutine.get_symbol(token_value)

        token = self.current_token()

        self.compile_subroutine_call(jack_subroutine, internal_indent, token, token_value, token_var_name)

        self.write_pop('temp', 0)

        self.pop_token(internal_indent, expected={';'})

        self.xml_file.write(f'{" " * indent}</doStatement>\n')

    def compile_return_statement(self, jack_subroutine, indent):
        self.xml_file.write(f'{" " * indent}<returnStatement>\n')

        internal_indent = indent + 2

        self.pop_token(internal_indent)

        token = self.current_token()
        if token == ('symbol', ';'):
            self.write_int(0)
        else:
            self.compile_expression(jack_subroutine, internal_indent)

        self.write_return()
        self.pop_token(internal_indent, expected={';'})

        self.xml_file.write(f'{" " * indent}</returnStatement>\n')

    def compile_expression_list(self, jack_subroutine, indent):

        self.xml_file.write(f'{" " * indent}<expressionList>\n')

        internal_indent = indent + 2

        count = 0
        token = self.current_token()
        while token != ('symbol', ')'):

            if token == ('symbol', ','):
                self.pop_token(internal_indent)

            count += 1
            self.compile_expression(jack_subroutine, internal_indent)
            token = self.current_token()

        self.xml_file.write(f'{" " * indent}</expressionList>\n')

        return count

    def compile_expression(self, jack_subroutine, indent):
        self.xml_file.write(f'{" " * indent}<expression>\n')

        internal_indent = indent + 2

        self.compile_term(jack_subroutine, internal_indent)

        token = self.current_token()
        while token.value in '+-*/&|<>=':
            binary_op = self.pop_token(internal_indent).value

            self.compile_term(jack_subroutine, internal_indent)
            self.write(JACK_TO_VM_OP[binary_op])

            token = self.current_token()

        self.xml_file.write(f'{" " * indent}</expression>\n')

    def compile_term(self, jack_subroutine, indent):
        self.xml_file.write(f'{" " * indent}<term>\n')

        internal_indent = indent + 2

        token = self.pop_token(internal_indent)

        if token.type == 'integerConstant':
            self.write_int(token.value)
        elif token.type == 'stringConstant':
            self.write_string(token.value)
        elif token.type == 'keyword':
            if token.value == 'this':
                self.write_push('pointer', 0)
            else:
                self.write_int(0)
                if token.value == 'true':
                    self.write('not')
        elif token.type == 'identifier':
            token_value = token.value
            token_var_name = jack_subroutine.get_symbol(token_value)

            token = self.current_token()
            if token.value == '[':
                self.pop_token(internal_indent, expected={'['})
                self.compile_expression(jack_subroutine, internal_indent)
                self.write_push_symbol(token_var_name)
                self.write('add')

                self.write_pop('pointer', 1)
                self.write_push('that', 0)
                self.pop_token(internal_indent, expected={']'})
            else:
                self.compile_subroutine_call(jack_subroutine, internal_indent, token, token_value, token_var_name)
        elif token.value == '(':
            self.compile_expression(jack_subroutine, internal_indent)
            self.pop_token(internal_indent, expected={')'})
        elif token.value in ['-', '~']:
            self.compile_term(jack_subroutine, internal_indent)
            if token.value == '-':
                self.write('neg')
            elif token.value == '~':
                self.write('not')

        self.xml_file.write(f'{" " * indent}</term>\n')

    def compile_subroutine_call(self, jack_subroutine, internal_indent, token, token_value, token_var_name):
        subroutine_name = token_value
        subroutine_class = jack_subroutine.jack_class.class_name

        argument_count = 0
        call_without_instance = True

        if token.value == '.':
            call_without_instance = False
            self.pop_token(internal_indent)

            subroutine_instance = jack_subroutine.get_symbol(token_value)
            subroutine_name = self.pop_token(internal_indent).value

            if subroutine_instance:
                subroutine_class = token_var_name.type
                argument_count = 1
                self.write_push_symbol(token_var_name)
            else:
                subroutine_class = token_value
            token = self.current_token()

        if token.value == '(':
            if call_without_instance:
                argument_count = 1
                self.write_push('pointer', 0)

            self.pop_token(internal_indent, expected={'('})
            argument_count += self.compile_expression_list(jack_subroutine, internal_indent)
            self.write_call(subroutine_class, subroutine_name, argument_count)
            self.pop_token(internal_indent, expected={')'})
        elif token_var_name:
            self.write_push_symbol(token_var_name)

    def write_if(self, label):
        self.vm_file.write('not\n')
        self.vm_file.write(f'if-goto {label}\n')

    def write_goto(self, label):
        self.vm_file.write(f'goto {label}\n')

    def write_label(self, label):
        self.vm_file.write(f'label {label}\n')

    def write_function(self, jack_subroutine):
        class_name = jack_subroutine.jack_class.class_name
        subroutine_name = jack_subroutine.subroutine_name
        local_var_count = jack_subroutine.local_var_count

        self.vm_file.write(f'function {class_name}.{subroutine_name} {local_var_count}\n')

    def write_return(self):
        self.vm_file.write('return\n')

    def write_call(self, class_name, func_name, arg_count):
        self.vm_file.write(f'call {class_name}.{func_name} {arg_count}\n')  # call function_name arg_count

    def write_pop_symbol(self, jack_symbol):
        self.write_pop(jack_symbol.kind, jack_symbol.index)  # TOS -> segment + index

    def write_push_symbol(self, jack_symbol):
        self.write_push(jack_symbol.kind, jack_symbol.index)  # TOS <- segment + index

    def write_pop(self, segment, index):
        self.vm_file.write(f'pop {segment} {index}\n')  # pop segment index (TOS -> segment + index)

    def write_push(self, segment, index):
        self.vm_file.write(f'push {segment} {index}\n')  # push segment index (TOS <- segment + index)

    def write(self, action):
        self.vm_file.write(f'{action}\n')

    def write_int(self, n):
        self.write_push('constant', n)  # push constant n (TOS <- constant + n)

    def write_string(self, string):
        # Creating a new string object by appends all the chars one-by-one
        string = string[1:-1]
        self.write_int(len(string))
        self.write_call('String', 'new', 1)
        for char in string:
            self.write_int(ord(char))
            self.write_call('String', 'appendChar', 2)


class JackClass:
    def __init__(self, class_name):
        self.class_name = class_name
        self.class_symbol_table = dict()

        self.static_var_count = 0
        self.field_var_count = 0

    def add_field_var(self, name, var_type):
        self.class_symbol_table[name] = JackSymbol('this', var_type, self.field_var_count)
        self.field_var_count += 1

    def add_static_var(self, name, var_type):
        self.class_symbol_table[name] = JackSymbol('static', var_type, self.static_var_count)
        self.static_var_count += 1

    def get_symbol(self, name):
        return self.class_symbol_table.get(name)


class JackSubroutine:
    def __init__(self, subroutine_name, subroutine_type, return_type, jack_class):
        self.subroutine_name = subroutine_name
        self.subroutine_type = subroutine_type
        self.return_type = return_type

        self.jack_class = jack_class

        self.subroutine_symbol_table = dict()
        self.argument_count = 0
        self.local_var_count = 0

        if subroutine_type == 'method':
            self.add_argument('this', self.jack_class.class_name)

    def add_argument(self, name, var_type):
        self.subroutine_symbol_table[name] = JackSymbol('argument', var_type, self.argument_count)
        self.argument_count += 1

    def add_local_var(self, name, var_type):
        self.subroutine_symbol_table[name] = JackSymbol('local', var_type, self.local_var_count)
        self.local_var_count += 1

    def get_symbol(self, name):
        symbol = self.subroutine_symbol_table.get(name)
        return symbol if symbol is not None else self.jack_class.get_symbol(name)
