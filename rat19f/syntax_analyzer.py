
class SyntaxAnalyzer:
    lexer   = None
    current = None

    def __init__(self, lexer):
        self.lexer = lexer
        self.output = []
        self.current = {'token': '', 'lexeme': '', 'line_num': '', 'line': ''}

    def next(self):
        self.current = next(self.lexer)
        out = '\n{0:15}  {1}'.format(
            'Token: {}'.format(self.current['token']), 
            'Lexeme: {}'.format(self.current['lexeme']))
        self.output.append(out)

    def rat19f(self):
        self.output.append('<Rat19F>                     ::=        <Opt Function Definitions> %% <Opt Declaration List> <Statement List> %%')
        self.next()
        self.opt_function_definitions()
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
                self.output.append('\nEnd of Program')
        else:
            for out in self.output:
                print(out)
            raise SyntaxError('Expected %% instead of {} {} on line {}'.format(
                    self.current['token'], 
                    self.current['lexeme'],
                    self.current['line_num']))

    def opt_function_definitions(self):
        self.output.append('<Opt Function Definitions>   ::=        <Function Definitions>   |   <Empty>')
        if self.function_definitions():
            return
        else:
            self.empty()

    def function_definitions(self):
        self.output.append( "<Function Definitions>       ::=        <Function> <Function Definitions>'")
        self.output.append( "<Function Definitions>'      ::=        <Empty>   |   <Function Definitions>")
        if self.function():
            if not self.function_definitions():
                self.empty()
                return True
            else:
                return True
        else:
            return False

    def function(self):
        self.output.append('<Function>                   ::=        function <Identifier> ( <Opt Parameter List> ) <Opt Declaration List> <Body>')
        if self.current['lexeme'] == 'function':
            self.next()
            if self.current['token'] == 'identifier':
                self.next()
                if self.current['lexeme'] == '(':
                    self.next()
                    self.opt_parameter_list()
                    if self.current['lexeme'] == ')':
                        self.next()
                        self.opt_declaration_list()
                        self.body()
                        return True
                    else:
                        raise SyntaxError('Expected separator ")" instead of {} {} on line {}'.format(
                                self.current['token'], 
                                self.current['lexeme'],
                                self.current['line_num']))
                else:
                    raise SyntaxError('Expected separator "(" instead of {} {} on line {}'.format(
                            self.current['token'], 
                            self.current['lexeme'],
                            self.current['line_num']))
            else:
                raise SyntaxError('Expected identifier instead of {} {} on line {}'.format(
                        self.current['token'], 
                        self.current['lexeme'],
                        self.current['line_num']))
        else:
            return False

    def opt_parameter_list(self):
        self.output.append('<Opt Parameter List>         ::=        <Parameter List>   |   <Empty>')
        if self.parameter_list():
            return
        else:
            self.empty()

    def parameter_list(self):
        self.output.append("<Parameter List>             ::=        <Parameter> <Parameter List>'")
        self.output.append("<Parameter List>'            ::=        <Empty> | , <Parameter List>")
        if self.parameter():
            if self.current['lexeme'] == ',':
                self.next()
                if not self.parameter_list():
                    raise SyntaxError('Expected parameter instead of {} {} on line {}'.format(
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

    def parameter(self):
        self.output.append('<Parameter>                  ::=        <IDs> <Qualifier>')
        if self.ID():
            if self.qualifier():
                return True
        else:
            return False

    def ID(self):
        self.output.append("<IDs>                       ::=        <Identifier> <IDs>'")
        self.output.append("<IDs>'                      ::=        <Empty>   |   , <IDs>")
        if self.current['token'] == 'identifier':
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

    def qualifier(self):
        self.output.append('<Qualifier>                 ::=        int   |   boolean   |   real')
        if self.current['lexeme'] in ['int', 'boolean', 'real']:
            self.next()
            return True
        else:
            return False

    def opt_declaration_list(self):
        self.output.append('<Opt Declaration List>      ::=        <Declaration List>   |   <Empty>')
        if self.declaration_list():
            return
        else:
            self.empty()

    def declaration_list(self):
        self.output.append("<Declaration List>          ::=        <Declaration> ; <Declaration List>'")
        self.output.append("<Declaration List>'         ::=        <Empty>   |   <Declaration List>")
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
        self.output.append('<Declaration>               ::=        <Qualifier> <IDs>')
        if self.qualifier():
            if self.ID():
                return True
        return False

    def body(self):
        self.output.append('<Body>                      ::=        { <Statement List> }')
        if self.current['lexeme'] == '{':
            self.next()
            self.statement_list()
            if self.current['lexeme'] == '}':
                self.next()
                return
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

    def statement_list(self):
        self.output.append("<Statement List>            ::=        <Statement> <Statement List>'")
        self.output.append("<Statement List>'           ::=        <Empty>   |   <Statement List>")
        if self.statement():
            if not self.statement_list():
                self.empty()
                return True
            else:
                return True
        else:
            return False

    def statement(self):
        self.output.append('<Statement>                 ::=        <Compound>   |   <Assign>   |   <If>   |   <Return>   |   <Print>   |   <Scan>   |   <While>')
        if self.compound() or self.assign() or self.if_() or self.return_() or self.print_() or self.scan() or self.while_():
            return True
        else:
            return False

    def compound(self):
        self.output.append('<Compound>                  ::=        { <Statement List> }')
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

    def assign(self):
        self.output.append('<Assign>                    ::=        <Identifier> = <Expression>;')
        if self.current['token'] == 'identifier':
            self.next()
            if self.current['lexeme'] == '=':
                self.next()
                if self.expression():
                    if self.current['lexeme'] == ';':
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

    def if_(self):
        self.output.append("<If>                        ::=        if ( <Condition>  ) <Statement> <If>'")
        if self.current['lexeme'] == 'if':
            self.next()
            if self.current['lexeme'] == '(':
                self.next()
                if self.condition():
                    if self.current['lexeme'] == ')':
                        self.next()
                        if self.statement():
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


    def return_(self):
        self.output.append("<Return>                    ::=        return <Return>'")
        self.output.append("<Return>'                   ::=        ;   |   <Expression> ;")
        if self.current['lexeme'] == 'return':
            self.next()
            self.expression()
            if self.current['lexeme'] == ';':
                self.next()
                return True
            else:
                raise SyntaxError('Expected separator ; instead of {} {} on line {}'.format(
                        self.current['token'], 
                        self.current['lexeme'],
                        self.current['line_num']))
        else:
            return False

    def print_(self):
        self.output.append('<Print>                     ::=        put ( <Expression> );')
        if self.current['lexeme'] == 'put':
            self.next()
            if self.current['lexeme'] == '(':
                self.next()
                self.expression()
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

    def scan(self):
        self.output.append('<Scan>                      ::=        get ( <IDs> );')
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

    def while_(self):
        self.output.append('<While>                     ::=        while ( <Condition>  ) <Statement>')
        if self.current['lexeme'] == 'while':
            self.next()
            if self.current['lexeme'] == '(':
                self.next()
                if self.condition():
                    if self.current['lexeme'] == ')':
                        self.next()
                        if self.statement():
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
        self.output.append('<Condition>                 ::=        <Expression> <Relop> <Expression>')
        if self.expression():
            if self.relop():
                if self.expression():
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
        self.output.append('<Relop>                     ::=        ==   |   /=   |   >   |   <   |   =>   |   <=')
        if self.current['lexeme'] in ['==', '/=', '>', '<', '=>', '<=']:
            self.next()
            return True
        else:
            return False

    def expression(self):
        self.output.append("<Expression>                ::=        <Term> <Expression>'")
        if self.term():
            self.expression_prime()
            return True
        else:
            raise SyntaxError('Expected term on line {}'.format(
                    self.current['line_num']))


    def expression_prime(self):
        self.output.append("<Expression>'               ::=        + <Term> <Expression>'   |   - <Term> <Expression>'   |   epsilon")
        if self.current['lexeme'] == '+' or self.current['lexeme'] == '-':
            self.next()
            if self.term():
                self.expression_prime()
            else:
                raise SyntaxError('Expected term on line {}'.format(
                        self.current['line_num']))
        else:
            self.empty()

    def term(self):
        self.output.append("<Term>                      ::=        <Factor> <Term>'")
        if self.factor():
            self.term_prime()
            return True
        else:
            return False

    def term_prime(self):
        self.output.append("<Term>'                     ::=        * <Factor> <Term>'   |   / <Factor> <Term>'   |   epsilon")
        if self.current['lexeme'] == '*' or self.current['lexeme'] == '/':
            self.next()
            if self.factor():
                self.term_prime()
            else:
                raise SyntaxError('Expected factor on line {}'.format(
                        self.current['line_num']))
        else:
            self.empty()

    def factor(self):
        self.output.append('<Factor>                    ::=        - <Primary>   |   <Primary>')
        if self.current['lexeme'] == '-':
            self.next()
        elif self.primary():
            return True
        raise SyntaxError('Expected primary on line {}'.format(
                self.current['line_num']))

    def primary(self):
        self.output.append("<Primary>                   ::=        <Identifier>   |   <Integer>   |   <Identifier> ( <IDs> )   |   ( <Factor> <Term>' <Expression>' )   |   <Real>   |   true   |   false")
        if self.current['token'] in ['real', 'integer'] or self.current['lexeme'] in ['true', 'false']:
            self.next()
            return True
        elif self.current['token'] == 'identifier':
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

    def empty(self):
        self.output.append('<Empty>   ::=   epsilon')

