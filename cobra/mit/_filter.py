# Copyright 2019 Cisco Systems, Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from builtins import object

import ply.lex as lex
import ply.yacc as yacc

from ._expr import MoPropExpr, And, Or, Not
from ._expr import eq, ne, gt, ge, lt, le, wcard


class LexerException(Exception):
    pass


class ParserException(Exception):
    pass


opTable = {
    'and': And,
    'or': Or,
    'not': Not,
    'eq': eq,
    'ne': ne,
    'lt': lt,
    'gt': gt,
    'ge': ge,
    'le': le,
    'wcard': wcard
}


class Lexer(object):
    tokens = (
        'COMP',
        'OP',
        'COMMA',
        'LPAREN',
        'RPAREN',
        'CLASS_PROP',
        'VALUE'
    )

    t_LPAREN = r'\('
    t_RPAREN = r'\)'
    t_COMMA = r','

    t_COMP = r'and|or|not'
    t_OP = r'eq|ne|gt|ge|le|lt|wcard'

    t_CLASS_PROP = r'(\w+)\.(\w+)'
    t_VALUE = r'"(.*?)"'

    t_ignore = ' \t\r\n'

    def __init__(self, **kwargs):
        self.lexer = lex.lex(module=self, **kwargs)

    def t_error(self, t):
        raise LexerException("Illegal character '{}' at pos {}".format(t.value[0], t.lexpos))
        # t.lexer.skip(1)


class Parser(object):
    tokens = Lexer.tokens

    def __init__(self, **kwargs):
        self.lexer = Lexer()
        self.parser = yacc.yacc(module=self, **kwargs)

    # get ast from a string expr
    def from_string(self, expressionStr):
        return self.parser.parse(expressionStr)

    # Grammar rules
    def p_head_expression(self, p):
        '''head_expression : expression'''
        p[0] = p[1]

    def p_expression(self, p):
        '''expression : COMP LPAREN expressions RPAREN'''
        comp = p[1]
        expressions = p[3]
        p[0] = opTable[comp](expressions)

    def p_expressions_list(self, p):
        '''expressions : expressions COMMA expression'''
        expressions = p[1]
        expression = p[3]
        p[0] = expressions + [expression]

    def p_expressions_one(self, p):
        '''expressions : expression'''
        expression = p[1]
        p[0] = [expression]

    def p_expression_op(self, p):
        '''expression : OP LPAREN CLASS_PROP COMMA VALUE RPAREN'''
        op = p[1]
        className, propName = p[3].split('.')
        value = p[5].strip('"')
        p[0] = MoPropExpr(className, propName, value, opTable[op])

    def p_error(self, t):
        raise ParserException("Syntax error: '{}'({}) at pos {}".format(t.value, t.type, t.lexpos))


filterParser = Parser()
