
#!/usr/bin/env python3

from rat19f import Lexer

a = Lexer()
with open('input.rat', 'r') as f:
    content = f.read()

symbol_table = a.run(content)
symbol_table.insert(0, ['Tokens', 'Lexemes'])
symbol_table.insert(1, ['------', '-------'])

col_width = max(len(val) for row in symbol_table for val in row) + 5  # padding
for row in symbol_table:
    print("".join(val.ljust(col_width) for val in row))
