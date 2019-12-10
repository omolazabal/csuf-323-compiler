
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
        self.symbol_table = [['Identifier', 'Memory Location']]
        self.jump_stack = []
        self.code_listing = []
        self.address_start = 5000

    def table_insert(self, identifier):
        self.symbol_table.append([identifier, len(self.symbol_table) + self.address_start - 1])

    def in_table(self, identifier):
        return identifier in [row[0] for row in self.symbol_table]

    def gen_instruction(self, operation, operand):
        self.code_listing.append({
            'address': len(self.code_listing) + 1,
            'operation': operation,
            'operand': operand
        })

    def get_address(self, identifier):
        return self.symbol_table[[row[0] for row in self.symbol_table].index(identifier)][1]

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
            self.next()
            if self.term():
                self.gen_instruction("ADD", None)
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
            self.next()
            if self.factor():
                self.gen_instruction("MUL", None)
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
        if self.compound() or self.assign():
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
            if self.ID():
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

    def ID(self):
        if self.current['token'] == 'identifier':
            self.table_insert(self.current['lexeme'])
            self.next()
            if self.current['lexeme'] == ',':
                self.next()
                if not self.ID():
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

    def scan(self):
        if self.current['lexeme'] == 'get':
            self.next()
            if self.current['lexeme'] == '(':
                self.next()
                if self.ID():
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
                self.E()
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
                raise SyntaxError('Expected separator ( instead of {} {} on line {}'.format(
                        self.current['token'], 
                        self.current['lexeme'],
                        self.current['line_num']))
        else:
            return False

    def empty(self):
        return


