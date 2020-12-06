
import decimal
import os
import lex
import parse
from fpdf import FPDF
num_type = decimal.Decimal
def dump_pdf(pydf, image_dict, image_path = "../images/", output_file = "../pdf/output_pdf.pdf"):
    start = image_dict['start']
    end = image_dict['end']
    for page_number in range(start, end + 1):
        pydf.add_page()
        pydf.image(os.path.join(image_path, image_dict['name1']), x = image_dict['x1'], y = image_dict['y1'], w = 396, h = 484)
        pydf.image(os.path.join(image_path, image_dict['name2']), x = image_dict['x2'], y = image_dict['y2'], w = 112, h = 112)
    return pydf


table = {
    "NUM" : r"[0-9]+",
    "SPACE" : (r'[ \t\n]+', lambda t: None),
    "ID" : r"[a-z.]+"
}
lexer = lex.Lexer(table)

rules = [["expr", ("NUM NUM ID NUM NUM ID NUM NUM", lambda p: {'start' : int(p[0]), 'end' : int(p[1]), 'name1' : p[2], 'x1' : int(p[3]), 'y1' : int(p[4]), 'name2' : p[5], 'x2' : int(p[6]), 'y2' : int(p[7])})]]

input_files_dir = "../input/"
output_file = "../pdf/output_pdf.pdf"
input_file = open(os.path.join(input_files_dir, "input.flip"), "r")
width, height = 800, 1000
pydf = FPDF(format = [width, height])
for line in input_file.readlines():
    parser = parse.Parser(rules, 'expr')
    result = parser.parse(lexer.input(line))
    
    pydf = dump_pdf(pydf, result)
pydf.output(output_file)