
class Lexer:
    state    = None   # State table
    colstr   = None   # Determine state table column
    keywords = None   # List of keywords

    def __init__(self):
        self.state = [
        #    0  1  2  3  4 
            [1, 2, 5, 5, 5], # 0
            [1, 1, 1, 5, 5], # 1  Identifier
            [5, 2, 5, 3, 5], # 2  Integer
            [5, 4, 5, 5, 5], # 3
            [5, 4, 5, 5, 5], # 4  Real
            [5, 5, 5, 5, 5], # 5  
        ]
        self.colstr = [
            'abcdefghijklmnopqrstuvwxyz',
            '0123456789',
            '_',
            '.'
        ]
        self.keywords = [
            'function', 'int', 'boolean', 'real', 'if', 'fi', 'otherwise',
            'return', 'put', 'get', 'while', 'true', 'false'
        ]
        self.operators = [ '=', '>', '<', '+', '-', '*', '/']
        self.seperators = ['(', ')', '{', '}', ',', ';']
        self.combination_operators = ['==', '\=', '=>', '<=']
        self.combination_seperators = ['%%', '[*', '*]']
        self.whitespaces = [' ', '\t', '\n']

    def position(self, char):
        for i, col in enumerate(self.colstr):
            if char.lower() in col: return i
        return len(self.state[0]) - 1

    def run(self, text):
        lexemes = []
        comments = []
        symbol_table = lexemes

        lex_state = 0  # Row of state table
        currentp = 0  # Pointer to current character
        startp = 0  # Token start pointer
        token_class = ''
        while currentp < len(text):
            currentc = text[currentp]  # Current character
            col = self.position(currentc)  # Column of state table
            lex_state = self.state[lex_state][col]
            if lex_state == 1:  # Potential identifier
                token = text[startp:currentp+1]
                token_class = 'keyword' if token in self.keywords else 'identifier'
            elif lex_state == 2:  # Potential integer
                token = text[startp:currentp+1]
                token_class = 'integer'
            elif lex_state == 4:  # Potential real
                token = text[startp:currentp+1]
                token_class = 'real'
            elif lex_state == 5:
                selection = \
                    'operator' if currentc in self.operators else \
                    'seperator' if currentc in self.seperators else \
                    ''
                # Combination seperators
                if len(symbol_table) and (symbol_table[-1][1] + currentc) in self.combination_seperators:
                    token = symbol_table[-1][1] + currentc
                    if token == '[*':
                        symbol_table.pop()
                        symbol_table = comments
                    elif token == '*]':
                        symbol_table[-1] = ['seperator', token]
                        symbol_table = lexemes
                    else:
                        symbol_table[-1] = ['seperator', token]
                # Combination operators
                elif selection is 'operator' and (symbol_table[-1][1] + currentc) in self.combination_operators:
                    symbol_table[-1][1] = symbol_table[-1][1] + currentc
                # Single operators
                elif selection:
                    if token_class:
                        symbol_table.append([token_class, token])
                    token = currentc
                    token_class = selection
                    symbol_table.append([token_class, token])
                # Empty state
                elif token_class:
                    symbol_table.append([token_class, token])
                # Unknown symbols
                elif currentc not in self.whitespaces:
                    token = currentc
                    token_class = 'unknown'
                    symbol_table.append([token_class, token])
                token_class = ''
                lex_state = 0
            else:
                token_class = ''
            currentp += 1
            if lex_state == 0:
                startp = currentp

        if token_class:
            symbol_table.append((token_class, token))
        symbol_table = lexemes

        for row in symbol_table:
            print(row)






