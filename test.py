
#!/usr/bin/env python3

from rat19f import Lexer

a = Lexer()
with open('input.rat', 'r') as f:
    content = f.read()
a.run(content)
