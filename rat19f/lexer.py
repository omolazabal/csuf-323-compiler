
class Set:
    def __init__(self, comment=False):
        self.comment = comment

    def values(self, *args):
        if not self.comment:
            return tuple(args)
        else:
            return None


class Lexer:
    state                  = None   # State table
    colstr                 = None   # Determine state table column
    keywords               = None   # List of keywords
    operators              = None   # List of valid operators
    separators             = None   # List of valid separators
    combination_operators  = None   # List of valid combined operators
    combination_separators = None   # List of valid combined separators
    whitespaces            = None   # Types of whitespaces

    def __init__(self, filename):
        self.filename = filename
        self.state = [
        #    0  1  2  3  4 
            [1, 2, 5, 5, 5], # 0
            [1, 1, 1, 5, 5], # 1  Identifier end state
            [5, 2, 5, 3, 5], # 2  Integer end state
            [5, 4, 5, 5, 5], # 3
            [5, 4, 5, 5, 5], # 4  Real end state
            [5, 5, 5, 5, 5], # 5  
        ]
        self.colstr = [
            'abcdefghijklmnopqrstuvwxyz', # Alpha chars
            '0123456789',                 # Digits
            '_',                          # Underscores
            '.'                           # Decimal point
            # Last column is reserved if none of the above
        ]
        self.keywords = [
            'function', 'int', 'boolean', 'real', 'if', 'fi', 'otherwise',
            'return', 'put', 'get', 'while', 'true', 'false'
        ]
        self.operators = [ '=', '>', '<', '+', '-', '*', '/']
        self.separators = ['(', ')', '{', '}', ',', ';']
        self.combination_operators = ['==', '/=', '=>', '<=']
        self.combination_separators = ['%%', '[*', '*]']
        self.whitespaces = [' ', '\t', '\n']

    def position(self, char):
        '''Gets column position of char'''
        for i, col in enumerate(self.colstr):
            if char.lower() in col: return i
        return len(self.state[0]) - 1

    def is_in_combination(self, char, first=False, second=False):
        if first and second:
            return (char in [op[0] for op in self.combination_operators] and char in [op[1] for op in self.combination_operators]) or \
                   (char in [sp[0] for sp in self.combination_separators] and char in [sp[1] for sp in self.combination_separators])
        elif first:
            return (char in [op[0] for op in self.combination_operators]) or (char in [sp[0] for sp in self.combination_separators])
        elif second:
            return (char in [op[1] for op in self.combination_operators]) or (char in [sp[1] for sp in self.combination_separators])
        return False


    def scanner(self):
        '''Performs parsing, leveraging the state table'''
        prev_op_sep = False
        lex_state = 0          # Row of state table
        currentp = 0           # Pointer to current character
        token = ''
        token_class = ''
        current_token = []
        set_ = Set()

        with open(self.filename) as fileobj:
            for line in fileobj:
                for currentc in line:
                    col = self.position(currentc)
                    lex_state = self.state[lex_state][col]
                    current_token.append(currentc)

                    if not self.is_in_combination(currentc, second=True) and prev_op_sep:
                        # A single operator has been stored, and the combination instance does not exist
                        prev_op_sep = False
                        yield set_.values(selection, token)

                    # Check the States
                    if lex_state == 1:
                        # Potential identifier
                        token = ''.join(current_token)
                        token_class = 'keyword' if token in self.keywords else 'identifier'
                    elif lex_state == 2:
                        # Potential integer
                        token = ''.join(current_token)
                        token_class = 'integer'
                    elif lex_state == 4:
                        # Potential real
                        token = ''.join(current_token)
                        token_class = 'real'
                    elif lex_state == 5:
                        # Other cases (operator, separator, unknowns, comments, etc)
                        selection = \
                            'operator' if currentc in self.operators else \
                            'separator' if currentc in self.separators else \
                            ''
                        if token and (token + currentc) in self.combination_separators:
                            # Combination separators
                            prev_op_sep = False
                            token = token + currentc
                            if token == '[*':
                                # Ignore output
                                set_.comment = True
                            elif token == '*]':
                                yield set_.values('separator', token)
                                set_.comment =  False
                            else:
                                yield set_.values('separator', token)
                        elif token and selection is 'operator' and (token + currentc) in self.combination_operators:
                            # Combination operators
                            prev_op_sep = False
                            token = token + currentc
                            yield set_.values('operator', token)
                        elif selection:
                            # Single operators & separators
                            if token_class:
                                yield set_.values(token_class, token)
                            token = currentc
                            token_class = selection
                            prev_op_sep = True
                        # Empty state
                        elif token_class:
                            yield set_.values(token_class, token)
                        # Unknown symbols
                        elif currentc not in self.whitespaces:
                            token = currentc
                            token_class = 'unknown'
                            if not self.is_in_combination(token, first=True): 
                                yield set_.values(token_class, token)
                        # Reset the state if no potential ending state
                        token_class = ''
                        lex_state = 0
                    else:
                        token_class = ''
                    if lex_state == 0:
                        current_token.clear()

        if token_class:
            # Grab last remaining token
            yield set_.values(token_class, token)

