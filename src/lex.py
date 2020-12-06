import copy
import re

class LexError(SyntaxError):
    def __init__(self, msg, info=None):
        self.msg = msg
        self.info = info


class Info:
    def __init__(self, filename, lineno=1, textpos=0, column=0, length=0):
        self.filename = filename
        self.lineno = lineno
        self.textpos = textpos
        self.column = column
        self.length = length
    def __str__(self):
        return 'Info("%s", %s, %s, %s)' % (self.filename, self.lineno, self.column, self.length)

class Token:
    def __init__(self, type, value, info=None):
        self.type = type
        self.value = value
        self.info = info
    def copy(self, type=None, value=None, info=None):
        c = copy.copy(self)
        if type is not None:  c.type = type
        if value is not None: c.value = value
        if info is not None:  c.info = info
        return c
    def __repr__(self):
        return 'Token(%s, %r, info=%s)' % (self.type, self.value, self.info)

class Lexer:
    def __init__(self, token_list):
        self._set_token_list(token_list)

    
    def _set_token_list(self, token_list):
        self.token_fns = {}
        if isinstance(token_list, dict):
            token_list = sorted(token_list.items(), key=lambda item: -len(item[1]))
        sorted_tokens = []
        for k, v in token_list:
            if isinstance(v, tuple):
                v, fn = v
                self.token_fns[k] = fn
            sorted_tokens.append([k, v])
        regex = '|'.join('(?P<%s>%s)' % (k, v) for k, v in sorted_tokens)
        self.matcher = re.compile(regex, re.MULTILINE).match

    def lex_input(self, text, filename):
        match = self.matcher(text)
        lineno = 1
        last_newline = 0
        end = 0
        while match is not None:
            type = match.lastgroup
            value = match.group(type)
            start, end = match.start(), match.end()

            token = Token(type, value)
            if type in self.token_fns:
                token = self.token_fns[type](token)
            if token:
                token.info = Info(filename, lineno, start, start - last_newline, end - start)
                
                new_token_list = (yield token)
                if new_token_list:
                    self._set_token_list(new_token_list)

            
            if '\n' in value:
                lineno += value.count('\n')
                last_newline = end - value.rfind('\n')
            match = self.matcher(text, end)

        
        if end != len(text):
            info = Info(filename, lineno, end, end - last_newline, 1)
            raise LexError('tokenizing error, invalid input', info=info)

    def input(self, text, filename=None):
        return LexerContext(text, self.lex_input(text, filename), filename)

class LexerContext:
    def __init__(self, text, token_stream, filename):
        self.text = text
        self.pos = 0
        self.token_stream = iter(token_stream)
        self.token_cache = []

        
        self.max_pos = 0
        self.max_info = None
        self.max_expected_tokens = set()

        self.filename = filename

    def get_source_line(self, info):
        start = self.text.rfind('\n', 0, info.textpos) + 1
        end = self.text.find('\n', info.textpos)
        if end == -1:
            end = None
        return self.text[start:end]

    def token_at(self, pos):
        while self.token_stream and pos >= len(self.token_cache):
            try:
                self.token_cache.append(next(self.token_stream))
            except StopIteration:
                self.token_stream = None
        if pos >= len(self.token_cache):
            return None
        return self.token_cache[pos]

    def set_token_list(self, tokens):
        try:
            self.token_cache.append(self.token_stream.send(tokens))
        except StopIteration:
            self.token_stream = None

    def get_next_info(self):
        token = self.peek()
        if token:
            return token.info
        return Info(self.filename)
    def get_state(self):
        return self.pos

    def restore_state(self, state):
        self.pos = state

    def peek(self):
        return self.token_at(self.pos)

    def got_to_end(self):
        return self.token_stream is None and self.max_pos == len(self.token_cache)

    def accept(self, token_type):
        token = self.peek()
        if self.pos >= self.max_pos:
            if self.pos > self.max_pos:
                self.max_pos = self.pos
                self.max_info = token and token.info
                if self.max_expected_tokens:
                    self.max_expected_tokens = set()
            if token_type != None:
                self.max_expected_tokens.add(token_type)
        if token and token.type == token_type:
            self.pos += 1
            return token
        return None
    def next(self):
        token = self.peek()
        return token and self.accept(token.type)

    def expect(self, token_type):
        token = self.accept(token_type)
        if not token:
            raise RuntimeError('got %s instead of %s' % (self.peek(), t))
        return token
