import collections

def Parser(grammar):
    # Map the name of each grammar rule to a list of its alternatives.
    rules = collections.defaultdict(list)
    lines = [line for line in grammar.splitlines() if line.strip()]
    for line in lines:
        tokens = line.split()
        if tokens: rules[tokens[0]].append(tokens[1:])

    def comp():
        yield 'import re'
        for rule, alternatives in rules.items():
            for line in comp_rule(rule, alternatives):
                yield line

    def comp_rule(rule, alternatives):
        yield 'def rule_%s(text, far, i):' % rule
        for a, alternative in enumerate(alternatives):
            yield '    def alt_%s(text, far, i):' % a
            for line in comp_alternative(alternative):
                yield '        ' + line
        yield ('    return '
               + ' or '.join('alt_%d(text, far, i)' % a
                             for a, _ in enumerate(alternatives)))

    def comp_alternative(alternative):
        yield 'vals = ()'
        for token in alternative:
            for line in comp_token(token):
                yield line
        yield 'return i, vals'

    def comp_token(token):
        if token.startswith('::'):
            yield 'st = %s({}, text, far, (i, vals))' % token[2:]
            yield 'if st is None: return None'
            yield 'i, vals = st'
        elif token.startswith(':'):
            yield 'vals = (%s(*vals),)' % token[1:]
        elif token.startswith('!'):
            yield 'def inverted(text, far, i, vals):'
            for line in comp_token(token[1:]):
                yield '    ' + line
            yield '    return i, vals'
            yield 'if inverted(text, far, i, vals): return None'
        elif token in rules:
            yield 'st = rule_%s(text, far, i)' % token
            yield 'if st is None: return None'
            yield 'i, vals = st[0], vals + st[1]'
        else:
            yield 'm = re.match(%r, text[i:])' % token
            yield 'if not m: return None'
            yield 'i += m.end()'
            yield 'far[0] = max(far[0], i)'
            yield 'vals += m.groups()'

    return '\n'.join(comp())

## exec(nums_grammar)
## rule_num('42,123 hag', [0], 0)
#. (2, (42,))
## rule_nums('42,123 hag', [0], 0)
#. (6, (42, 123))
## rule_allnums('42,123', [0], 0)
#. (6, (42, 123))
## rule_allnums('42,123 hag', [0], 0)

## print nums_grammar
#. import re
#. def rule_num(text, far, i):
#.     def alt_0(text, far, i):
#.         vals = ()
#.         m = re.match('([0-9]+)', text[i:])
#.         if not m: return None
#.         i += m.end()
#.         far[0] = max(far[0], i)
#.         vals += m.groups()
#.         vals = (int(*vals),)
#.         return i, vals
#.     return alt_0(text, far, i)
#. def rule_allnums(text, far, i):
#.     def alt_0(text, far, i):
#.         vals = ()
#.         st = rule_nums(text, far, i)
#.         if st is None: return None
#.         i, vals = st[0], vals + st[1]
#.         def inverted(text, far, i, vals):
#.             m = re.match('.', text[i:])
#.             if not m: return None
#.             i += m.end()
#.             far[0] = max(far[0], i)
#.             vals += m.groups()
#.             return i, vals
#.         if inverted(text, far, i, vals): return None
#.         return i, vals
#.     return alt_0(text, far, i)
#. def rule_nums(text, far, i):
#.     def alt_0(text, far, i):
#.         vals = ()
#.         st = rule_num(text, far, i)
#.         if st is None: return None
#.         i, vals = st[0], vals + st[1]
#.         m = re.match(',', text[i:])
#.         if not m: return None
#.         i += m.end()
#.         far[0] = max(far[0], i)
#.         vals += m.groups()
#.         st = rule_nums(text, far, i)
#.         if st is None: return None
#.         i, vals = st[0], vals + st[1]
#.         return i, vals
#.     def alt_1(text, far, i):
#.         vals = ()
#.         st = rule_num(text, far, i)
#.         if st is None: return None
#.         i, vals = st[0], vals + st[1]
#.         return i, vals
#.     def alt_2(text, far, i):
#.         vals = ()
#.         return i, vals
#.     return alt_0(text, far, i) or alt_1(text, far, i) or alt_2(text, far, i)
#. 

nums_grammar = Parser(r"""
allnums   nums !.

nums   num , nums
nums   num
nums   

num    ([0-9]+) :int
""")