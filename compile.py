#!/bin/python

from functools import reduce
import itertools
import logging
import sys

_logger = logging.getLogger(__name__)

if len(sys.argv) < 2:
    print('./compile.py {yu source file}')
    sys.exit(0)

with open(sys.argv[1]) as f:
    content = f.read()

functions = {
    '#': lambda *args: (print(*args), list(args))[1],
    'reduce': lambda *args: [reduce(args[0], args[1:])],
}

operations = {
    '+': '__add__', '*': '__mul__', '-': '__sub__', '/': '__div__',
    '**': '__pow__', '//': '__floordiv__', '%': '__mod__',
}

def add_reducer(op, func):
    functions[op] = lambda *args: C('reduce', [lambda x, y: getattr(x, func)(y)] + list(args))

for op, func in operations.items():
    add_reducer(op, func)

def C(function, arguments):
    if function not in functions:
        return expand([function])
    return functions[function](*arguments)

def expand(args):
    for index, arg in reversed(list(enumerate(args))):
        if '..' in arg:
            first, _, after = arg.partition('..')
            second, _, after = after.partition('..')
            args[index:index+1] = list(range(int(first), int(second)+1))
        if arg.isdigit():
            args[index] = int(arg)
    return args

for script in content.split('\n\n'):
    script = script.strip()
    if not script:
        continue
    ret = None
    for code in script.split('|'):
        if code.startswith('> '):
            code = code[2:]
            divide = True
        else:
            divide = False
        tokens = code.split()
        args = expand(tokens[1:])
        if divide and ret:
            ret = list(itertools.chain(*list(C(tokens[0], [re] + args) for re in ret)))
        else:
            if ret is not None:
                args = ret + args
            ret = C(tokens[0], args)
