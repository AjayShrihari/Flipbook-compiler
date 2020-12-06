import copy
import sys
import lex

class ParseError(SyntaxError):
    def __init__(self, tokenizer, msg, info=None):
        self.tokenizer = tokenizer
        self.msg = msg
        self.info = info
    def print(self):
        info = self.info or self.tokenizer.get_next_info()
        source_info = '%s(%s): ' % (info.filename, info.lineno) if info.filename else ''
        print('%sparse error: %s' % (source_info, self.msg), file=sys.stderr)
        line = self.tokenizer.get_source_line(info)
        if line.strip():
            print(line, file=sys.stderr)
            print(' ' * info.column + '^' * info.length, file=sys.stderr)

def merge_info_list(info):
    first = last = info
    while isinstance(first, list):
        for item in first:
            if item:
                first = item
                break
        else:
            return None
    while isinstance(last, list):
        for i in reversed(last):
            if i:
                last = i
                break
        else:
            assert False
    info = copy.copy(first)
    info.length = last.length + (last.textpos - first.textpos)
    return info


class ParseResult:
    def __init__(self, ctx, items, info):
        self._ctx = ctx
        self.user_context = ctx.user_context
        self.items = items
        self.info = info
    def __getitem__(self, n):
        return self.items[n]
    def get_info(self, *indices):
        info = self.info
        for index in indices:
            info = info[index]
        if isinstance(info, list):
            info = merge_info_list(info)
        return info
    def set_token_list(self, tokens):
        self._ctx.tokenizer.set_token_list(tokens)
    def error(self, msg, *indices):
        raise ParseError(self._ctx.tokenizer, msg, self.get_info(*indices))
    def clone(self, items=None, info=None):
        return ParseResult(self._ctx, items or self.items, info or self.info)

class Context:
    def __init__(self, rule_table, tokenizer, user_context=None):
        self.rule_table = rule_table
        self.tokenizer = tokenizer
        self.user_context = user_context

def unzip(results):
    return [[r[i] for r in results] for i in range(2)]

# Classes to represent grammar structure. These are hierarchically nested, and
# operate through the parse method, usually calling other rules' parse methods.

# Parse either a token or a nonterminal of the grammar
class Identifier:
    '''
    For parsing for grammar structure
    Class for parsing either token or non terminal
    '''
    def __init__(self, name):
        self.name = name
    def parse(self, ctx):
        if self.name in ctx.rule_table:
            return ctx.rule_table[self.name].parse(ctx)
        # XXX check token name validity
        token = ctx.tokenizer.accept(self.name)
        if token:
            return (token.value, token.info)
        return None
    def __str__(self):
        return '"%s"' % self.name

# Parse a rule repeated at least <min> number of times (used for * and + in EBNF)
class Repeat:
    '''
    Parse a particular rule a repeated number of times
    '''
    def __init__(self, item, min_reps=0):
        self.item = item
        self.min_reps = min_reps
    def parse(self, ctx):
        results = []
        item = self.item.parse(ctx)
        state = ctx.tokenizer.get_state()
        while item:
            results.append(item)
            item = self.item.parse(ctx)
        if len(results) >= self.min_reps:
            return unzip(results)
        ctx.tokenizer.restore_state(state)
        return None
    def __str__(self):
        return 'rep(%s)' % self.item

class Sequence:
    '''
    Parse a sequence, when there are multiple rules for the given expression/command 
    '''
    def __init__(self, items):
        self.items = items
    def parse(self, ctx):
        results = []
        state = ctx.tokenizer.get_state()
        for item in self.items:
            result = item.parse(ctx)
            if not result:
                ctx.tokenizer.restore_state(state)
                return None
            results.append(result)
        return unzip(results)
    def __str__(self):
        return 'seq(%s)' % ','.join(map(str, self.items))


class Alternation:
    '''
    Parse an alternate rule
    '''
    def __init__(self, items):
        self.items = items
    def parse(self, ctx):
        for item in self.items:
            result = item.parse(ctx)
            if result:
                return result
        return None
    def __str__(self):
        return 'alt(%s)' % ','.join(map(str, self.items))


class Optional:
    '''
    Parse an optional rule in the rule table
    '''
    def __init__(self, item):
        self.item = item
    def parse(self, ctx):
        return self.item.parse(ctx) or (None, None)
    def __str__(self):
        return 'opt(%s)' % self.item


class FnWrapper:
    def __init__(self, rule, fn):
        '''
        Parse rule, and based on rule table, call a user defined function
        '''
        if not isinstance(rule, Sequence):
            rule = Sequence([rule])
        self.rule = rule
        self.fn = fn
    def parse(self, ctx):
        result = self.rule.parse(ctx)
        if result:
            result, info = result
            result = self.fn(ParseResult(ctx, result, info))
            if isinstance(result, ParseResult):
                result, info = result.items, result.info
            else:
                info = merge_info_list(info)
            return (result, info)
        return None
    def __str__(self):
        return str(self.rule)


def parse_repeat(tokenizer, repeated):
    '''
    Parser for EBNF language
    For repeating operations, like * and + 
    '''
    if tokenizer.accept('STAR'):
        return Repeat(repeated)
    elif tokenizer.accept('PLUS'):
        return Repeat(repeated, min_reps=1)
    return repeated

def parse_rule_atom(tokenizer):
    '''
    Rules for paranthesis
    '''
    if tokenizer.accept('LPAREN'):
        result = parse_rule_expr(tokenizer)
        tokenizer.expect('RPAREN')
        result = parse_repeat(tokenizer, result)
    
    elif tokenizer.accept('LBRACKET'):
        result = Optional(parse_rule_expr(tokenizer))
        tokenizer.expect('RBRACKET')
    
    else:
        token = tokenizer.expect('IDENTIFIER')
        result = parse_repeat(tokenizer, Identifier(token.value))
    return result


def parse_rule_seq(tokenizer):
    '''
    Parse a sequence using rules given specifically for sequences
    '''
    items = []
    token = tokenizer.peek()
    while (token and token.type != 'RBRACKET' and token.type != 'RPAREN' and
            token.type != 'PIPE'):
        items.append(parse_rule_atom(tokenizer))
        token = tokenizer.peek()
    
    if len(items) > 1:
        return Sequence(items)
    return items[0] if items else None


def parse_rule_expr(tokenizer):
    '''
    For Piping operation: alternation in the expression
    '''
    items = [parse_rule_seq(tokenizer)]
    while tokenizer.accept('PIPE'):
        items.append(parse_rule_seq(tokenizer))
    if len(items) > 1:
        return Alternation(items)
    return items[0]



rule_tokens = {
    'IDENTIFIER': r'[a-zA-Z_]+',
    'LBRACKET':   r'\[',
    'LPAREN':     r'\(',
    'PIPE':       r'\|',
    'RBRACKET':   r'\]',
    'RPAREN':     r'\)',
    'STAR':       r'\*',
    'PLUS':       r'\+',
    'WHITESPACE': (r' ', lambda t: None),
}
rule_lexer = lex.Lexer(rule_tokens)


def rule_fn(rule_table, name, rule):
    '''
    Use the function wrapper instead of PLY package for functions that we define explicitly
    '''
    def wrapper(fn):
        rule_table.append((name, (rule, fn)))
        return fn
    return wrapper

class Parser:
    '''
    Add user given rules to rule table 
    '''
    def __init__(self, rule_table, start):
        self.rule_table = {}
        for [name, *rules] in rule_table:
            for rule in rules:
                fn = None
                if isinstance(rule, tuple):
                    rule, fn = rule
                self.create_rule(name, rule, fn)
        
        for name, rule in self.rule_table.items():
            if isinstance(rule, Alternation) and len(rule.items) == 1:
                self.rule_table[name] = rule.items[0]
        self.start = start

    def create_rule(self, name, rule, fn):
        '''
        Parse table and create rules based on the programmer requirement
        '''
        rule = parse_rule_expr(rule_lexer.input(rule))

        
        rule = FnWrapper(rule, fn) if fn else rule

       
        if name not in self.rule_table:
            self.rule_table[name] = Alternation([])
        self.rule_table[name].items.append(rule)

    def parse(self, tokenizer, start=None, user_context=None, lazy=False):
        rule = self.rule_table[start or self.start]
        ctx = Context(self.rule_table, tokenizer, user_context=user_context)
        try:
            result = rule.parse(ctx)
        except lex.LexError as e:
            '''
            Error handling
            '''
            raise ParseError(tokenizer, e.msg, e.info)

        fail = (not result or tokenizer.peek() is not None)

        
        if lazy and fail and tokenizer.got_to_end():
            return None

        if fail:
            message = ('bad token, expected one of the following: %s' %
                    ' '.join(sorted(tokenizer.max_expected_tokens)))
            raise ParseError(tokenizer, message, info=tokenizer.max_info)

        result, info = result
        return result
