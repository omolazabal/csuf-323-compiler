
class CodeGenerator:
    lexer   = None
    current = None
    symbol_table = None
    code_listing = None
    addr = 0
    jump_stack = None

    def __init__(self, lexer):
        self.lexer = lexer
        self.current = {'token': '', 'lexeme': '', 'line_num': '', 'line': ''}
        self.symbol_table = []
        self.jump_stack = []
        self.code_listing = []
        self.address_start = 5000

    def table_insert(self, identifier):
        self.symbol_table.append([identifier, len(self.symbol_table) + self.address_start])

    def in_table(self, identifier):
        return identifier in [row[0] for row in self.symbol_table]

    def gen_instruction(self, operation, operand):
        self.code_listing.append({
            'address': len(self.code_listing) + 1,
            'operation': operation,
            'operand': operand
        })

    def instruction_address(self):
        return len(self.code_listing) + 1

    def get_address(self, identifier):
        if self.in_table(identifier):
            return self.symbol_table[[row[0] for row in self.symbol_table].index(identifier)][1]
        else:
            raise SyntaxError(f'{identifier} is undefined')

    def back_patch(self, jump_address):
        addr = self.jump_stack.pop()
        self.code_listing[addr - 1]['operand'] = jump_address
        self.gen_instruction("LABEL", None)

    def next(self):
        self.current = next(self.lexer)

    def rat19f(self):
        self.next()
        if self.current['lexeme'] == '%%':
            self.next()
            self.opt_declaration_list()
            self.statement_list()
        else:
            raise SyntaxError('Expected %% instead of {} {} on line {}'.format(
                    self.current['token'], 
                    self.current['lexeme'],
                    self.current['line_num']))
        # Check if program ends
        if self.current['lexeme'] == '%%':
            try:
                self.next()
                raise SyntaxError('Expected EOF instead of {} {} on line {}'.format(
                        self.current['token'], 
                        self.current['lexeme'],
                        self.current['line_num']))
            except StopIteration:
                pass # End of Program
        else:
            raise SyntaxError('Expected %% instead of {} {} on line {}'.format(
                    self.current['token'], 
                    self.current['lexeme'],
                    self.current['line_num']))

    def assign(self):
        if self.current['token'] == 'identifier':
            save = self.current['lexeme']
            self.next()
            if self.current['lexeme'] == '=':
                self.next()
                if self.expression():
                    if self.current['lexeme'] == ';':
                        self.gen_instruction('POPM', self.get_address(save))
                        self.next()
                        return True
                    else:
                        raise SyntaxError('Expected separator ; instead of {} {} on line {}'.format(
                                self.current['token'], 
                                self.current['lexeme'],
                                self.current['line_num']))
                else:
                    raise SyntaxError('Expected expression after = instead of {} {} on line {}'.format(
                            self.current['token'], 
                            self.current['lexeme'],
                            self.current['line_num']))
            else:
                raise SyntaxError('Expected operator = instead of {} {} on line {}'.format(
                        self.current['token'], 
                        self.current['lexeme'],
                        self.current['line_num']))
        else:
            return False

    def expression(self):
        if self.term():
            self.expression_prime()
            return True
        else:
            raise SyntaxError('Expected term on line {}'.format(
                    self.current['line_num']))
            
    def expression_prime(self):
        if self.current['lexeme'] == '+' or self.current['lexeme'] == '-':
            op = self.current['lexeme']
            self.next()
            if self.term():
                if op == '+':
                    self.gen_instruction("ADD", None)
                if op == '-':
                    self.gen_instruction("SUB", None)
                self.expression_prime()
            else:
                raise SyntaxError('Expected term on line {}'.format(
                        self.current['line_num']))
        else:
            self.empty()

    def term(self):
        if self.factor():
            self.term_prime()
            return True
        else:
            return False

    def term_prime(self):
        if self.current['lexeme'] == '*' or self.current['lexeme'] == '/':
            op = self.current['lexeme']
            self.next()
            if self.factor():
                if op == '*':
                    self.gen_instruction("MUL", None)
                elif op == '/':
                    self.gen_instruction("DIV", None)
                self.term_prime()
            else:
                raise SyntaxError('Expected factor on line {}'.format(
                        self.current['line_num']))
        else:
            self.empty()

    def factor(self):
        if self.current['lexeme'] == '-':
            self.next()
        if self.primary():
            return True
        raise SyntaxError('Expected identifier on line {}'.format(
                self.current['line_num']))

    def primary(self):
        if self.current['token'] in ['integer'] or self.current['lexeme'] in ['true', 'false']:
            self.gen_instruction("PUSHI", self.current['lexeme'])
            self.next()
            return True
        elif self.current['token'] == 'identifier':
            self.gen_instruction("PUSHM", self.get_address(self.current['lexeme']))
            self.next()
            if self.current['lexeme'] == '(':
                self.next()
                if self.ID():
                    if self.current['lexeme'] == ')':
                        self.next()
                        return True
                    else:
                        raise SyntaxError('Expected separator ) instead of {} {} on line {}'.format(
                                self.current['token'], 
                                self.current['lexeme'],
                                self.current['line_num']))
                else:
                    raise SyntaxError('Expected id on line {}'.format(
                            self.current['line_num']))
            else:
                return True
        elif self.current['lexeme'] == '(':
            self.next()
            if self.expression():
                if self.current['lexeme'] == ')':
                    self.next()
                    return True
                else:
                    raise SyntaxError('Expected separator ) instead of {} {} on line {}'.format(
                            self.current['token'], 
                            self.current['lexeme'],
                            self.current['line_num']))
            else:
                raise SyntaxError('Expected expression on line {}'.format(
                        self.current['line_num']))
        else:
            return False


    def statement_list(self):
        if self.statement():
            if not self.statement_list():
                self.empty()
                return True
            else:
                return True
        else:
            return False

    def statement(self):
        if self.compound() or self.assign() or self.while_() or self.if_() or self.scan() or self.print_():
            return True
        else:
            return False

    def qualifier(self):
        if self.current['lexeme'] in ['int', 'boolean']:
            self.next()
            return True
        else:
            return False

    def opt_declaration_list(self):
        if self.declaration_list():
            return
        else:
            self.empty()

    def declaration_list(self):
        if self.declaration():
            if self.current['lexeme'] == ';':
                self.next()
                if not self.declaration_list():
                    self.empty()
                    return True
                else:
                    return True
            else:
                raise SyntaxError('Expected separator ; instead of {} {} on line {}'.format(
                        self.current['token'], 
                        self.current['lexeme'],
                        self.current['line_num']))
        else:
            return False

    def declaration(self):
        if self.qualifier():
            if self.ID(from_declaration=True):
                return True
        return False

    def compound(self):
        if self.current['lexeme'] == '{':
            self.next()
            if self.statement_list():
                if self.current['lexeme'] == '}':
                    self.next()
                    return True
                else:
                    raise SyntaxError('Expected separator }} instead of {} {} on line {}'.format(
                            self.current['token'], 
                            self.current['lexeme'],
                            self.current['line_num']))
            else:
                raise SyntaxError('Expected separator {{ instead of {} {} on line {}'.format(
                        self.current['token'], 
                        self.current['lexeme'],
                        self.current['line_num']))
        else:
            return False

    def ID(self, from_declaration=False, from_scan=False):
        if self.current['token'] == 'identifier':
            if from_scan:
                if not self.in_table(self.current['lexeme']):
                    raise SyntaxError(f'{self.current["lexeme"]} is undefined')
                self.gen_instruction("STDIN", None)
                self.gen_instruction('POPM', self.get_address(self.current['lexeme']))
            if from_declaration:
                if self.in_table(self.current['lexeme']):
                    raise SyntaxError(f'{self.current["lexeme"]} already declared')
                self.table_insert(self.current['lexeme'])
            self.next()
            if self.current['lexeme'] == ',':
                self.next()
                if not self.ID(from_declaration):
                    raise SyntaxError('Expected identifier instead of {} {} on line {}'.format(
                            self.current['token'], 
                            self.current['lexeme'],
                            self.current['line_num']))
                else:
                    return True
            else:
                self.empty()
                return True
        else:
            return False

    def while_(self):
        if self.current['lexeme'] == 'while':
            addr = self.instruction_address()
            self.gen_instruction("LABEL", None)
            self.next()
            if self.current['lexeme'] == '(':
                self.next()
                if self.condition():
                    if self.current['lexeme'] == ')':
                        self.next()
                        if self.statement():
                            self.gen_instruction("JUMP", addr)
                            self.back_patch(self.instruction_address())
                            return True
                        else:
                            raise SyntaxError('Expected statement on line {}'.format(
                                    self.current['token'], 
                                    self.current['lexeme'],
                                    self.current['line_num']))
                    else:
                        raise SyntaxError('Expected separator ) instead of {} {} on line {}'.format(
                                self.current['token'], 
                                self.current['lexeme'],
                                self.current['line_num']))
                else:
                    raise SyntaxError('Expected condition on line {}'.format(
                            self.current['line_num']))
            else:
                raise SyntaxError('Expected separator ( instead of {} {} on line {}'.format(
                        self.current['token'], 
                        self.current['lexeme'],
                        self.current['line_num']))
        else:
            return False

    def condition(self):
        if self.expression():
            if self.relop():
                op = self.current['lexeme']
                self.next()
                if self.expression():
                    if op == '<':
                        self.gen_instruction("LES", None)
                    elif op == '>':
                        self.gen_instruction("GRT", None)
                    elif op == '==':
                        self.gen_instruction("EQU", None)
                    elif op == '/=':
                        self.gen_instruction("NEQ", None)
                    elif op == '=>':
                        self.gen_instruction("GEQ", None)
                    elif op == '<=':
                        self.gen_instruction("LEQ", None)
                    self.jump_stack.append(self.instruction_address())
                    self.gen_instruction("JUMPZ", None)
                    return True
                else:
                    raise SyntaxError('Expected expression on line {}'.format(
                            self.current['line_num']))
            else:
                raise SyntaxError('Expected replop on line {}'.format(
                        self.current['line_num']))
        else:
            return False

    def relop(self):
        if self.current['lexeme'] in ['==', '/=', '>', '<', '=>', '<=']:
            return True
        else:
            return False

    def if_(self):
        if self.current['lexeme'] == 'if':
            addr = self.instruction_address()
            self.next()
            if self.current['lexeme'] == '(':
                self.next()
                if self.condition():
                    if self.current['lexeme'] == ')':
                        self.next()
                        if self.statement():
                            self.back_patch(self.instruction_address())
                            if self.current['lexeme'] == 'otherwise':
                                self.next()
                                if self.statement():
                                    if self.current['lexeme'] == 'fi':
                                        self.next()
                                        return True
                                    else:
                                        raise SyntaxError('Expected separator fi instead of {} {} on line {}'.format(
                                                self.current['token'], 
                                                self.current['lexeme'],
                                                self.current['line_num']))
                                else:
                                    raise SyntaxError('Expected statement on line {}'.format(
                                            self.current['line_num']))
                            else:
                                if self.current['lexeme'] == 'fi':
                                    self.next()
                                    return True
                                else:
                                    raise SyntaxError('Expected fi instead of {} {} on line {}'.format(
                                            self.current['token'], 
                                            self.current['lexeme'],
                                            self.current['line_num']))
                        else:
                            raise SyntaxError('Expected statement on line {}'.format(
                                    self.current['line_num']))
                    else:
                        raise SyntaxError('Expected ) instead of {} {} on line {}'.format(
                                self.current['token'], 
                                self.current['lexeme'],
                                self.current['line_num']))
                else:
                    raise SyntaxError('Expected condition on line {}'.format(
                            self.current['line_num']))
            else:
                raise SyntaxError('Expected separator ( instead of {} {} on line {}'.format(
                        self.current['token'], 
                        self.current['lexeme'],
                        self.current['line_num']))
        else:
            return False

    def scan(self):
        if self.current['lexeme'] == 'get':
            self.next()
            if self.current['lexeme'] == '(':
                self.next()
                if self.ID(from_scan=True):
                    if self.current['lexeme'] == ')':
                        self.next()
                        if self.current['lexeme'] == ';':
                            self.next()
                            return True
                        else:
                            raise SyntaxError('Expected separator ; instead of {} {} on line {}'.format(
                                    self.current['token'], 
                                    self.current['lexeme'],
                                    self.current['line_num']))
                    else:
                        raise SyntaxError('Expected separator ) instead of {} {} on line {}'.format(
                                self.current['token'], 
                                self.current['lexeme'],
                                self.current['line_num']))
                else:
                    raise SyntaxError('Expected identifier on line {}'.format(
                            self.current['line_num']))
            else:
                raise SyntaxError('Expected separator ( instead of {} {} on line {}'.format(
                        self.current['token'], 
                        self.current['lexeme'],
                        self.current['line_num']))
        else:
            return False

    def print_(self):
        if self.current['lexeme'] == 'put':
            self.next()
            if self.current['lexeme'] == '(':
                self.next()
                self.expression()
                if self.current['lexeme'] == ')':
                    self.next()
                    if self.current['lexeme'] == ';':
                        self.gen_instruction("STDOUT", None)
                        self.next()
                        return True
                    else:
                        raise SyntaxError('Expected separator ; instead of {} {} on line {}'.format(
                                self.current['token'], 
                                self.current['lexeme'],
                                self.current['line_num']))
                else:
                    raise SyntaxError('Expected separator ) instead of {} {} on line {}'.format(
                            self.current['token'], 
                            self.current['lexeme'],
                            self.current['line_num']))
            else:
                raise SyntaxError('Expected separator ( instead of {} {} on line {}'.format(
                        self.current['token'], 
                        self.current['lexeme'],
                        self.current['line_num']))
        else:
            return False

    def empty(self):
        return


