#!/usr/bin/env python3

# Simple calculator program written using SPRDPL

# Make the local package importable by futzing with weird variables.
# Python packaging kinda sucks
if __name__ == '__main__' and __package__ is None:
    import sys
    __package__ = 'sprdpl'
    sys.path.append('%s/..' % sys.path[0])

import decimal

from . import lex
from . import parse

num_type = decimal.Decimal

# Lexer tokens. These tokens define all valid input to the parser.
# Whitespace is ignored
# table = {
#     'PLUS':       r'\+',
#     'MINUS':      r'-',
#     'TIMES':      r'\*',
#     'DIVIDE':     r'/',
#     'POWER':      r'\^',
#     'NUMBER':     (r'[0-9]+(\.[0-9]*)?|\.[0-9]+',
#         lambda t: t.copy(value=num_type(t.value))),
#     'LPAREN':     r'\(',
#     'RPAREN':     r'\)',
#     'WHITESPACE': (r'[ \t\n]+', lambda t: None),
# }
def dump_pdf(image_dict, output_file = "../pdf/output_pdf.pdf"):
    pydf = FPDF()
    
        # print (image_info)
    start = image_dict['start']
    end = image_dict['end']
    for page_number in range(start, end + 1):
        pydf.add_page()
        pydf.image(image_dict['name'], x = image_dict['x'], y = image_dict['y'], w = 100)
    pydf.output(output_file)

def dump_pdf_token(p):
    # print (p)
    print (p[0])
    print (p[1])
    image_dict = {'name' : p[2], 'start' : p[0], 'end' : p[1], 'x' : p[3], 'y' : p[4]}
    dump_pdf(image_dict)

table = {
    "NUM" : r"[0-9]+",
    "SPACE" : (r'[ \t\n]+', lambda t: None),
    "ID" : r"[a-z.]+"
}
lexer = lex.Lexer(table)

def reduce_binop(p):
    r = p[0]
    for item in p[1]:
        if   item[0] == '+': r = r + item[1]
        elif item[0] == '-': r = r - item[1]
        elif item[0] == '*': r = r * item[1]
        elif item[0] == '/': r = r / item[1]
    return r

# Parse rules. Each rule is a list, with the first element being the
# rule name, and each item after one of the p
# rules = [
#     ['atom', 'NUMBER', ('LPAREN expr RPAREN', lambda p: p[1])],
#     ['factor', ('atom POWER factor', lambda p: p[0] ** p[2]), 'atom',
#         ('MINUS factor', lambda p: -p[1])],
#     ['term', ('factor ((TIMES|DIVIDE) factor)*', reduce_binop)],
#     ['expr', ('term ((PLUS|MINUS) term)*', reduce_binop)],
# ]
rules = [["expr", ("NUM NUM ID NUM NUM", lambda p: "start = {}, end = {}, id = {}, x = {}, y = {}".format(p[0], p[1], p[2], p[3], p[4]))]]
# rules = [[]]
line = '''1 4 child.png 50 50'''
parser = parse.Parser(rules, 'expr')
result = parser.parse(lexer.input(line))
print (result)
# try:
    
#     parser = parser.parse(rules, 'expr')
# except parse.ParseError as e:
#     e.print()
#     raise

# try:
#     while True:
#         # Read lines until the parser hits an error or has parsed a full
#         # statement.  We use the "lazy" feature of the parser, that will
#         # return None if the input could be the first part of a valid parse,
#         # rather than throwing an error.
#         line = ''
#         while True:
#             prompt = '>>> ' if not line else '... '
#             line = line + input(prompt) + '\n'
#             tokens = lexer.input(line, filename='<stdin>')

#             try:
#                 result = parser.parse(tokens, lazy=True)
#             except parse.ParseError as e:
#                 e.print()
#                 break
#             if result is not None:
#                 print('%s' % result)
#                 break
# except EOFError:
#     print()
