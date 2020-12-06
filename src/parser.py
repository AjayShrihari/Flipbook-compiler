from rply import ParserGenerator
class Parser:
    def __init__(self, list_token):
        self.list_token = list_token
        self.parse_gen = ParserGenerator('NUMBER', 'ID', 'END', 'ASSIGN', 'NEWLINE')


    def parse()