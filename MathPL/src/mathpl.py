# mathpl.py — MathPL Interpreter v0.2.0
# Теперь с 3D, клавишами WASD, moveLiB и твоим синтаксисом!
# Запуск: python mathpl.py

import sys
import math
import random
from enum import Enum, auto

# ====================== ТОКЕНЫ ======================

class TokenType(Enum):
    # Ключевые слова
    TASK = auto(); CLOSE = auto(); BASE = auto(); DEP = auto()
    SAY = auto(); FN = auto(); IF = auto(); ELSE = auto()
    FOR = auto(); IN = auto(); AND = auto()
    COOR = auto(); COOR3D = auto(); TO = auto(); BY = auto()
    YES = auto(); NO = auto(); NIL = auto()
    
    # Новые ключевые слова (твой синтаксис)
    LAUNCH = auto(); CENTRE = auto(); 
    REQUEST = auto(); ACCESS = auto(); KEYBOARD = auto()
    KEYS = auto(); KEY = auto()
    FUNCTION = auto(); WORK = auto(); UNWORK = auto()
    WAIT = auto(); MOVE = auto(); MOVELIB = auto()
    FORWARD = auto(); LEFT = auto(); BACK = auto(); RIGHT = auto()
    START = auto(); ERROR_MODE = auto()

    # Типы данных
    IDENTIFIER = auto(); NUMBER = auto(); STRING = auto()

    # Операторы
    ASSIGN = auto(); PLUS = auto(); MINUS = auto()
    MUL = auto(); DIV = auto(); POWER = auto()
    MATMUL = auto(); PIPE = auto()
    EQ = auto(); NEQ = auto(); GT = auto(); LT = auto()
    GTE = auto(); LTE = auto()

    # Разделители
    LPAREN = auto(); RPAREN = auto()
    LBRACKET = auto(); RBRACKET = auto()
    LBRACE = auto(); RBRACE = auto()
    COLON = auto(); SEMICOLON = auto(); COMMA = auto()
    DOT = auto(); ARROW = auto()
    NEWLINE = auto(); EOF = auto()


class Token:
    def __init__(self, type, value=None, line=0):
        self.type = type
        self.value = value
        self.line = line

    def __repr__(self):
        return f"Token({self.type.name}, {repr(self.value)}, line={self.line})"


# ====================== ЛЕКСЕР ======================

class Lexer:
    def __init__(self, code):
        self.code = code
        self.pos = 0
        self.line = 1
        self.tokens = []

    def peek(self, offset=0):
        if self.pos + offset < len(self.code):
            return self.code[self.pos + offset]
        return None

    def advance(self):
        char = self.code[self.pos]
        self.pos += 1
        if char == '\n':
            self.line += 1
        return char

    def skip_whitespace(self):
        while self.pos < len(self.code) and self.code[self.pos] in ' \t\r':
            self.advance()

    def skip_comment(self):
        while self.pos < len(self.code) and self.code[self.pos] != '\n':
            self.advance()

    def read_string(self):
        self.advance()
        start = self.pos
        while self.pos < len(self.code) and self.code[self.pos] != '"':
            self.advance()
        value = self.code[start:self.pos]
        self.advance()
        return value

    def read_number(self):
        start = self.pos
        while self.pos < len(self.code) and self.code[self.pos].isdigit():
            self.advance()
        if self.pos < len(self.code) and self.code[self.pos] == '.':
            self.advance()
            while self.pos < len(self.code) and self.code[self.pos].isdigit():
                self.advance()
        value = self.code[start:self.pos]
        return float(value) if '.' in value else int(value)

    def read_identifier(self):
        start = self.pos
        while self.pos < len(self.code) and (self.code[self.pos].isalnum() or self.code[self.pos] in '_-#'):
            self.advance()
        return self.code[start:self.pos]

    def tokenize(self):
        keywords = {
            # Старые
            'task': TokenType.TASK, 'task#': TokenType.TASK,
            'close': TokenType.CLOSE,
            'base': TokenType.BASE, 'dep': TokenType.DEP,
            'say': TokenType.SAY, 'fn': TokenType.FN,
            'if': TokenType.IF, 'else': TokenType.ELSE,
            'for': TokenType.FOR, 'in': TokenType.IN,
            'and': TokenType.AND, 'coor': TokenType.COOR,
            'to': TokenType.TO, 'by': TokenType.BY,
            'yes': TokenType.YES, 'no': TokenType.NO,
            'nil': TokenType.NIL,
            
            # Новые (твой синтаксис)
            'launch': TokenType.LAUNCH,
            'centre': TokenType.CENTRE,
            'request': TokenType.REQUEST,
            'access': TokenType.ACCESS,
            'keyboard': TokenType.KEYBOARD,
            'keys': TokenType.KEYS,
            'key': TokenType.KEY,
            'function': TokenType.FUNCTION,
            'work': TokenType.WORK,
            'unwork': TokenType.UNWORK,
            'wait': TokenType.WAIT,
            'move': TokenType.MOVE,
            'moveLiB': TokenType.MOVELIB,
            'forward': TokenType.FORWARD,
            'left': TokenType.LEFT,
            'back': TokenType.BACK,
            'right': TokenType.RIGHT,
            'start': TokenType.START,
            'error-mode': TokenType.ERROR_MODE,
        }

        while self.pos < len(self.code):
            char = self.code[self.pos]

            if char in ' \t\r':
                self.skip_whitespace()
                continue

            if char == '\n':
                self.tokens.append(Token(TokenType.NEWLINE, '\n', self.line))
                self.advance()
                continue

            if char == '/' and self.peek() == '/':
                self.skip_comment()
                continue

            if char == '"':
                value = self.read_string()
                self.tokens.append(Token(TokenType.STRING, value, self.line))
                continue

            if char.isdigit():
                value = self.read_number()
                self.tokens.append(Token(TokenType.NUMBER, value, self.line))
                continue

            if char.isalpha() or char == '_':
                word = self.read_identifier()
                # Обработка task# и error-mode
                if word == 'task#':
                    self.tokens.append(Token(TokenType.TASK, 'task#', self.line))
                elif word == 'error-mode':
                    self.tokens.append(Token(TokenType.ERROR_MODE, 'error-mode', self.line))
                else:
                    token_type = keywords.get(word, TokenType.IDENTIFIER)
                    self.tokens.append(Token(token_type, word, self.line))
                continue

            # Двухсимвольные операторы
            if char == '=':
                if self.peek() == '=':
                    self.advance()
                    self.tokens.append(Token(TokenType.EQ, '==', self.line))
                else:
                    self.tokens.append(Token(TokenType.ASSIGN, '=', self.line))
                self.advance()
                continue

            if char == '!':
                if self.peek() == '=':
                    self.advance()
                    self.tokens.append(Token(TokenType.NEQ, '!=', self.line))
                self.advance()
                continue

            if char == '>':
                if self.peek() == '=':
                    self.advance()
                    self.tokens.append(Token(TokenType.GTE, '>=', self.line))
                else:
                    self.tokens.append(Token(TokenType.GT, '>', self.line))
                self.advance()
                continue

            if char == '<':
                if self.peek() == '=':
                    self.advance()
                    self.tokens.append(Token(TokenType.LTE, '<=', self.line))
                else:
                    self.tokens.append(Token(TokenType.LT, '<', self.line))
                self.advance()
                continue

            if char == '|':
                if self.peek() == '>':
                    self.advance()
                    self.tokens.append(Token(TokenType.PIPE, '|>', self.line))
                    self.advance()
                continue

            if char == '-':
                if self.peek() == '>':
                    self.advance()
                    self.tokens.append(Token(TokenType.ARROW, '->', self.line))
                    self.advance()
                else:
                    self.tokens.append(Token(TokenType.MINUS, '-', self.line))
                    self.advance()
                continue

            # Односимвольные
            single = {
                '+': TokenType.PLUS, '*': TokenType.MUL,
                '/': TokenType.DIV, '^': TokenType.POWER,
                '@': TokenType.MATMUL, '(': TokenType.LPAREN,
                ')': TokenType.RPAREN, '[': TokenType.LBRACKET,
                ']': TokenType.RBRACKET, '{': TokenType.LBRACE,
                '}': TokenType.RBRACE, ':': TokenType.COLON,
                ';': TokenType.SEMICOLON, ',': TokenType.COMMA,
                '.': TokenType.DOT,
            }

            if char in single:
                self.tokens.append(Token(single[char], char, self.line))
                self.advance()
                continue

            raise SyntaxError(f"Неизвестный символ '{char}' на строке {self.line}")

        self.tokens.append(Token(TokenType.EOF, None, self.line))
        return self.tokens


# ====================== AST УЗЛЫ ======================

class ASTNode:
    pass

class Program(ASTNode):
    def __init__(self, tasks):
        self.tasks = tasks

class TaskNode(ASTNode):
    def __init__(self, name, body):
        self.name = name
        self.body = body

class BaseDecl(ASTNode):
    def __init__(self, variables, functions=None, libs=None):
        self.variables = variables or []
        self.functions = functions or []
        self.libs = libs or []

class Assignment(ASTNode):
    def __init__(self, name, expression, dep_list=None):
        self.name = name
        self.expression = expression
        self.dep_list = dep_list or []

class SayStatement(ASTNode):
    def __init__(self, expression, label=None):
        self.expression = expression
        self.label = label

class BinaryOp(ASTNode):
    def __init__(self, left, operator, right):
        self.left = left
        self.operator = operator
        self.right = right

class NumberLiteral(ASTNode):
    def __init__(self, value):
        self.value = value

class StringLiteral(ASTNode):
    def __init__(self, value):
        self.value = value

class BooleanLiteral(ASTNode):
    def __init__(self, value):
        self.value = value

class NilLiteral(ASTNode):
    pass

class VariableRef(ASTNode):
    def __init__(self, name):
        self.name = name

class FunctionCall(ASTNode):
    def __init__(self, name, args):
        self.name = name
        self.args = args

class Coord3DNode(ASTNode):
    def __init__(self, x, y, z):
        self.x = x
        self.y = y
        self.z = z

class Coord2DNode(ASTNode):
    def __init__(self, x, y):
        self.x = x
        self.y = y

class CoordToNode(ASTNode):
    def __init__(self, coord):
        self.coord = coord

class CoordByNode(ASTNode):
    def __init__(self, coord):
        self.coord = coord

class IfStatement(ASTNode):
    def __init__(self, condition, then_body, else_body=None):
        self.condition = condition
        self.then_body = then_body
        self.else_body = else_body

class LaunchCentreNode(ASTNode):
    def __init__(self, mode):
        self.mode = mode  # "3D" или "2D"

class RequestAccessNode(ASTNode):
    def __init__(self, device, var_name, keys_list):
        self.device = device  # "keyboard"
        self.var_name = var_name
        self.keys_list = keys_list  # ["W", "A", "S", "D"]

class KeyBindingNode(ASTNode):
    def __init__(self, key_name, direction, fallback_coord):
        self.key_name = key_name
        self.direction = direction  # "forward", "left", "back", "right"
        self.fallback_coord = fallback_coord

class WaitAccessNode(ASTNode):
    def __init__(self, target):
        self.target = target  # "keys"

class WorkCheckNode(ASTNode):
    def __init__(self, lib_name, action, negative=False):
        self.lib_name = lib_name
        self.action = action
        self.negative = negative  # True для unwork

class ErrorModeNode(ASTNode):
    def __init__(self, message=None):
        self.message = message

class StartFunctionNode(ASTNode):
    pass


# ====================== ПАРСЕР ======================

class Parser:
    def __init__(self, tokens):
        self.tokens = tokens
        self.pos = 0

    def peek(self):
        if self.pos < len(self.tokens):
            return self.tokens[self.pos]
        return self.tokens[-1]

    def advance(self):
        token = self.tokens[self.pos]
        self.pos += 1
        return token

    def skip_newlines(self):
        while self.peek().type == TokenType.NEWLINE:
            self.advance()

    def expect(self, token_type, error_msg=None):
        token = self.peek()
        if token.type != token_type:
            msg = error_msg or f"Ожидался {token_type.name}, получен {token.type.name} (строка {token.line})"
            raise SyntaxError(msg)
        return self.advance()

    def parse(self):
        self.skip_newlines()
        tasks = []
        while self.peek().type != TokenType.EOF:
            tasks.append(self.parse_task())
            self.skip_newlines()
        return Program(tasks)

    def parse_task(self):
        self.expect(TokenType.TASK)
        name = "main"
        if self.peek().type == TokenType.IDENTIFIER:
            name = self.advance().value
        if self.peek().type == TokenType.COLON:
            self.advance()
        self.skip_newlines()

        body = []
        while self.peek().type not in (TokenType.CLOSE, TokenType.EOF):
            if self.peek().type == TokenType.NEWLINE:
                self.skip_newlines()
                continue
            body.append(self.parse_statement())
            self.skip_newlines()

        self.expect(TokenType.CLOSE)
        return TaskNode(name, body)

    def parse_statement(self):
        token = self.peek()

        if token.type == TokenType.BASE:
            return self.parse_base_decl()
        elif token.type == TokenType.LAUNCH:
            return self.parse_launch()
        elif token.type == TokenType.REQUEST:
            return self.parse_request_access()
        elif token.type == TokenType.KEY:
            return self.parse_key_binding()
        elif token.type == TokenType.WAIT:
            return self.parse_wait_access()
        elif token.type == TokenType.IF:
            return self.parse_if()
        elif token.type == TokenType.START:
            return self.parse_start_function()
        elif token.type == TokenType.ERROR_MODE:
            return self.parse_error_mode()
        elif token.type == TokenType.IDENTIFIER:
            return self.parse_assignment_or_call()
        elif token.type == TokenType.SAY:
            return self.parse_say()
        else:
            return self.parse_expression()

    def parse_base_decl(self):
        self.advance()  # base
        if self.peek().type == TokenType.ASSIGN:
            self.advance()
        
        variables = []
        functions = []
        libs = []
        
        # objp = "Player"
        name = self.expect(TokenType.IDENTIFIER).value
        if self.peek().type == TokenType.ASSIGN:
            self.advance()  # =
            # Может быть строка, or функция, or библиотека
            if self.peek().type == TokenType.STRING:
                variables.append((name, self.advance().value))
            elif self.peek().type == TokenType.FUNCTION:
                functions.append(name)
                self.advance()
            elif self.peek().type == TokenType.MOVELIB:
                libs.append(name)
                self.advance()
            else:
                expr = self.parse_expression()
                return Assignment(name, expr)
        else:
            variables.append((name, None))
        
        # Обработка and ...
        while self.peek().type == TokenType.AND:
            self.advance()  # and
            word = self.peek()
            
            if word.type == TokenType.FUNCTION:
                functions.append("function")
                self.advance()
            elif word.type == TokenType.MOVE:
                self.advance()
                if self.peek().type == TokenType.IDENTIFIER:
                    libs.append("move" + self.advance().value)
                elif self.peek().type == TokenType.MOVELIB:
                    libs.append("moveLiB")
                    self.advance()
            elif word.type == TokenType.IDENTIFIER:
                var_name = self.advance().value
                if self.peek().type == TokenType.ASSIGN:
                    self.advance()
                    if self.peek().type == TokenType.STRING:
                        variables.append((var_name, self.advance().value))
                    elif self.peek().type == TokenType.MOVELIB:
                        libs.append(var_name)
                        self.advance()
                    else:
                        variables.append((var_name, None))
                else:
                    variables.append((var_name, None))
            elif word.type == TokenType.MOVELIB:
                libs.append("moveLiB")
                self.advance()
        
        return BaseDecl(variables, functions, libs)

    def parse_launch(self):
        self.advance()  # launch
        centre_token = self.peek()
        if centre_token.type == TokenType.CENTRE:
            self.advance()  # centre
        self.expect(TokenType.ASSIGN)
        mode = self.advance()  # 3D
        return LaunchCentreNode(mode.value)

    def parse_request_access(self):
        self.advance()  # request
        self.expect(TokenType.ACCESS)
        device = self.expect(TokenType.IDENTIFIER).value  # keyboard
        self.expect(TokenType.ASSIGN)
        var_name = self.expect(TokenType.IDENTIFIER).value  # keys
        # WASD
        keys_list = []
        if self.peek().type == TokenType.IDENTIFIER:
            keys_str = self.advance().value
            keys_list = list(keys_str.upper())
        return RequestAccessNode(device, var_name, keys_list)

    def parse_key_binding(self):
        self.advance()  # key
        key_name = self.expect(TokenType.IDENTIFIER).value.upper()  # W, A, S, D
        self.expect(TokenType.ASSIGN)
        self.expect(TokenType.FUNCTION)
        self.expect(TokenType.TO)
        direction = self.advance().value  # forward, left, back, right
        
        fallback_coord = None
        if self.peek().type == TokenType.ELSE:
            self.advance()  # else
            self.expect(TokenType.TO)
            # (x:y:z)
            if self.peek().type == TokenType.LPAREN:
                self.advance()
                x = self.parse_expression()
                self.expect(TokenType.COLON)
                y = self.parse_expression()
                self.expect(TokenType.COLON)
                z = self.parse_expression()
                self.expect(TokenType.RPAREN)
                fallback_coord = Coord3DNode(x, y, z)
        
        return KeyBindingNode(key_name, direction, fallback_coord)

    def parse_wait_access(self):
        self.advance()  # wait
        self.expect(TokenType.ASSIGN)
        self.expect(TokenType.ACCESS)
        target = self.expect(TokenType.IDENTIFIER).value  # keys
        return WaitAccessNode(target)

    def parse_start_function(self):
        self.advance()  # start
        self.expect(TokenType.FUNCTION)
        self.expect(TokenType.LPAREN)
        self.expect(TokenType.RPAREN)
        return StartFunctionNode()

    def parse_error_mode(self):
        self.advance()  # error-mode
        message = None
        if self.peek().type == TokenType.STRING:
            message = self.advance().value
        return ErrorModeNode(message)

    def parse_if(self):
        self.advance()  # if
        
        # Проверяем особый случай: if work function = start function()
        if self.peek().type == TokenType.WORK or self.peek().type == TokenType.UNWORK:
            is_negative = self.peek().type == TokenType.UNWORK
            self.advance()  # work или unwork
            self.expect(TokenType.FUNCTION)
            self.expect(TokenType.ASSIGN)
            action = self.parse_statement()
            return WorkCheckNode("function", action, is_negative)
        
        # Обычный if
        condition = self.parse_expression()
        if self.peek().type == TokenType.COLON:
            self.advance()
        self.skip_newlines()
        then_body = [self.parse_statement()]
        else_body = None
        self.skip_newlines()
        if self.peek().type == TokenType.ELSE:
            self.advance()
            self.skip_newlines()
            else_body = [self.parse_statement()]
        return IfStatement(condition, then_body, else_body)

    def parse_assignment_or_call(self):
        name = self.advance().value

        if name == 'coor' and self.peek().type in (TokenType.TO, TokenType.BY):
            op = self.advance()
            coord = self.parse_2d_coord()
            if op.type == TokenType.TO:
                return CoordToNode(coord)
            else:
                return CoordByNode(coord)

        if self.peek().type == TokenType.ASSIGN:
            self.advance()
            expr = self.parse_expression()
            if self.peek().type == TokenType.ASSIGN:
                self.advance()
                self.expect(TokenType.LPAREN)
                self.expect(TokenType.SAY)
                label = None
                if self.peek().type == TokenType.STRING:
                    label = self.advance().value
                self.expect(TokenType.RPAREN)
                return SayStatement(expr, label)
            return Assignment(name, expr)
        elif self.peek().type == TokenType.LPAREN:
            return self.parse_function_call(name)
        else:
            return VariableRef(name)

    def parse_say(self):
        self.advance()
        expr = self.parse_expression()
        return SayStatement(expr)

    def parse_function_call(self, name):
        self.advance()
        args = []
        if self.peek().type != TokenType.RPAREN:
            args.append(self.parse_expression())
            while self.peek().type == TokenType.COMMA:
                self.advance()
                args.append(self.parse_expression())
        self.expect(TokenType.RPAREN)
        return FunctionCall(name, args)

    def parse_2d_coord(self):
        if self.peek().type == TokenType.LPAREN:
            self.advance()
        x = self.parse_expression()
        # Поддержка и ; и :
        sep = self.peek()
        if sep.type in (TokenType.SEMICOLON, TokenType.COLON):
            self.advance()
        y = self.parse_expression()
        if self.peek().type == TokenType.RPAREN:
            self.advance()
        return Coord2DNode(x, y)

    def parse_3d_coord(self):
        if self.peek().type == TokenType.LPAREN:
            self.advance()
        x = self.parse_expression()
        self.expect(TokenType.COLON)
        y = self.parse_expression()
        self.expect(TokenType.COLON)
        z = self.parse_expression()
        if self.peek().type == TokenType.RPAREN:
            self.advance()
        return Coord3DNode(x, y, z)

    def parse_expression_with_left(self, left):
        return self.parse_comparison(left)

    def parse_expression(self):
        return self.parse_comparison()

    def parse_comparison(self, left=None):
        if left is None:
            left = self.parse_addition()
        while self.peek().type in (TokenType.EQ, TokenType.NEQ, TokenType.GT,
                                    TokenType.LT, TokenType.GTE, TokenType.LTE):
            op = self.advance().value
            right = self.parse_addition()
            left = BinaryOp(left, op, right)
        return left

    def parse_addition(self):
        left = self.parse_multiplication()
        while self.peek().type in (TokenType.PLUS, TokenType.MINUS):
            op = self.advance().value
            right = self.parse_multiplication()
            left = BinaryOp(left, op, right)
        return left

    def parse_multiplication(self):
        left = self.parse_power()
        while self.peek().type in (TokenType.MUL, TokenType.DIV, TokenType.MATMUL):
            op = self.advance().value
            right = self.parse_power()
            left = BinaryOp(left, op, right)
        return left

    def parse_power(self):
        left = self.parse_atom()
        while self.peek().type == TokenType.POWER:
            self.advance()
            right = self.parse_atom()
            left = BinaryOp(left, '^', right)
        return left

    def parse_atom(self):
        token = self.peek()

        if token.type == TokenType.NUMBER:
            self.advance()
            return NumberLiteral(token.value)

        if token.type == TokenType.STRING:
            self.advance()
            return StringLiteral(token.value)

        if token.type == TokenType.YES:
            self.advance()
            return BooleanLiteral(True)

        if token.type == TokenType.NO:
            self.advance()
            return BooleanLiteral(False)

        if token.type == TokenType.NIL:
            self.advance()
            return NilLiteral()

        if token.type == TokenType.IDENTIFIER:
            name = self.advance().value
            if self.peek().type == TokenType.LPAREN:
                return self.parse_function_call(name)
            return VariableRef(name)

        if token.type == TokenType.LPAREN:
            # Проверяем: 2D, 3D координата или выражение
            saved = self.pos
            self.advance()
            
            # Пробуем 3D
            if self.peek().type == TokenType.NUMBER:
                self.pos = saved
                try:
                    return self.parse_3d_coord()
                except:
                    pass
            
            self.pos = saved
            self.advance()
            expr = self.parse_expression()
            self.expect(TokenType.RPAREN)
            return expr

        raise SyntaxError(f"Неожиданный токен {token.type.name} на строке {token.line}")


# ====================== ОКРУЖЕНИЕ ======================

class Environment:
    def __init__(self, parent=None):
        self.variables = {}
        self.parent = parent

    def define(self, name, value):
        self.variables[name] = value

    def assign(self, name, value):
        if name in self.variables:
            self.variables[name] = value
        elif self.parent:
            self.parent.assign(name, value)
        else:
            self.variables[name] = value

    def get(self, name):
        if name in self.variables:
            return self.variables[name]
        if self.parent:
            return self.parent.get(name)
        raise NameError(f"Переменная '{name}' не найдена")


# ====================== ИНТЕРПРЕТАТОР ======================

class Interpreter:
    def __init__(self):
        self.global_env = Environment()
        self.libs_loaded = {}
        self.key_bindings = {}
        self.player_pos = {'x': 0, 'y': 0, 'z': 0}
        self._register_builtins()

    def _register_builtins(self):
        env = self.global_env
        env.define('sin', lambda args: math.sin(args[0]))
        env.define('cos', lambda args: math.cos(args[0]))
        env.define('sqrt', lambda args: math.sqrt(args[0]))
        env.define('abs', lambda args: abs(args[0]))
        env.define('print', lambda args: print(*args))
        env.define('вывод', lambda args: print(*args))

    def interpret(self, program):
        result = None
        for task in program.tasks:
            result = self.visit_task(task)
        return result

    def visit_task(self, task):
        task_env = Environment(self.global_env)
        result = None
        for stmt in task.body:
            result = self.visit_statement(stmt, task_env)
        return result

    def visit_statement(self, node, env):
        if isinstance(node, BaseDecl):
            for var_name, var_value in node.variables:
                val = var_value
                if isinstance(var_value, str) and var_value.startswith('"') and var_value.endswith('"'):
                    val = var_value[1:-1]
                env.define(var_name, val)
            for func in node.functions:
                env.define(func, True)
            for lib in node.libs:
                print(f"  [Библиотека {lib} загружена]")
                self.libs_loaded[lib] = True
                env.define(lib, True)
        elif isinstance(node, LaunchCentreNode):
            print(f"  [3D-пространство активировано: {node.mode}]")
            env.define('centre_mode', node.mode)
        elif isinstance(node, RequestAccessNode):
            print(f"  [Доступ к {node.device}: клавиши {''.join(node.keys_list)}]")
            env.define(node.var_name, node.keys_list)
        elif isinstance(node, KeyBindingNode):
            self.key_bindings[node.key_name] = {
                'direction': node.direction,
                'coord': node.fallback_coord
            }
            dir_names = {
                'forward': 'вперёд', 'left': 'влево',
                'back': 'назад', 'right': 'вправо'
            }
            print(f"  [Клавиша {node.key_name}: движение {dir_names.get(node.direction, node.direction)}]")
        elif isinstance(node, WaitAccessNode):
            self._wait_for_keys(env)
        elif isinstance(node, WorkCheckNode):
            lib_loaded = self.libs_loaded.get('moveLiB', False)
            if not node.negative:
                if lib_loaded:
                    return self.visit_statement(node.action, env)
            else:
                if not lib_loaded:
                    return self.visit_statement(node.action, env)
        elif isinstance(node, StartFunctionNode):
            print("  [Функция движения запущена!]")
            self._game_loop(env)
        elif isinstance(node, ErrorModeNode):
            msg = node.message or "Библиотека не загружена"
            print(f"  [ОШИБКА] {msg}")
        elif isinstance(node, Assignment):
            value = self.visit_expression(node.expression, env)
            env.assign(node.name, value)
        elif isinstance(node, SayStatement):
            value = self.visit_expression(node.expression, env)
            if node.label:
                print(f"{node.label}: {value}")
            else:
                print(value)
        elif isinstance(node, IfStatement):
            condition = self.visit_expression(node.condition, env)
            if condition:
                for s in node.then_body:
                    return self.visit_statement(s, env)
            elif node.else_body:
                for s in node.else_body:
                    return self.visit_statement(s, env)
        else:
            return self.visit_expression(node, env)

    def _wait_for_keys(self, env):
        """Эмуляция ожидания клавиатуры"""
        print("  [Ожидание клавиш WASD...]")
        print("  (введи W/A/S/D или 'exit' для выхода)")
        while True:
            key = input("  > ").strip().upper()
            if key == 'EXIT':
                break
            if key in self.key_bindings:
                binding = self.key_bindings[key]
                dir_vectors = {
                    'forward': (0, 1, 0),
                    'left': (-1, 0, 0),
                    'back': (0, -1, 0),
                    'right': (1, 0, 0)
                }
                vec = dir_vectors.get(binding['direction'], (0, 0, 0))
                self.player_pos['x'] += vec[0]
                self.player_pos['y'] += vec[1]
                self.player_pos['z'] += vec[2]
                pos = self.player_pos
                print(f"  Позиция: x={pos['x']}, y={pos['y']}, z={pos['z']}")
            else:
                print(f"  Клавиша {key} не назначена. Используй WASD.")

    def _game_loop(self, env):
        """Игровой цикл"""
        print("  [Игровой цикл запущен. WASD для движения, 'exit' для выхода]")
        self._wait_for_keys(env)

    def visit_expression(self, node, env):
        if node is None:
            return None
        if isinstance(node, NumberLiteral):
            return node.value
        if isinstance(node, StringLiteral):
            return node.value
        if isinstance(node, BooleanLiteral):
            return node.value
        if isinstance(node, NilLiteral):
            return None
        if isinstance(node, VariableRef):
            return env.get(node.name)
        if isinstance(node, Coord3DNode):
            x = self.visit_expression(node.x, env)
            y = self.visit_expression(node.y, env)
            z = self.visit_expression(node.z, env)
            return {'x': x, 'y': y, 'z': z}
        if isinstance(node, Coord2DNode):
            x = self.visit_expression(node.x, env)
            y = self.visit_expression(node.y, env)
            return {'x': x, 'y': y}
        if isinstance(node, CoordToNode):
            return self.visit_expression(node.coord, env)
        if isinstance(node, CoordByNode):
            return self.visit_expression(node.coord, env)
        if isinstance(node, BinaryOp):
            left = self.visit_expression(node.left, env)
            right = self.visit_expression(node.right, env)
            op = node.operator
            if op == '+': return left + right
            if op == '-': return left - right
            if op == '*': return left * right
            if op == '/': return left / right
            if op == '^': return left ** right
            if op == '==': return left == right
            if op == '!=': return left != right
            if op == '>': return left > right
            if op == '<': return left < right
            if op == '>=': return left >= right
            if op == '<=': return left <= right
        if isinstance(node, FunctionCall):
            func = env.get(node.name)
            args = [self.visit_expression(a, env) for a in node.args]
            if callable(func):
                return func(args)
        raise RuntimeError(f"Неизвестный тип: {type(node)}")


# ====================== ЗАПУСК ======================

def run_code(code):
    lexer = Lexer(code)
    tokens = lexer.tokenize()
    parser = Parser(tokens)
    ast = parser.parse()
    interpreter = Interpreter()
    return interpreter.interpret(ast)


def run_file(filename):
    with open(filename, 'r', encoding='utf-8') as f:
        code = f.read()
    return run_code(code)


def repl():
    print(r"""
╔══════════════════════════╗
║  ┌───┬───┬───┬───┬───┐  ║
║  │ M │ A │ T │ H │   │  ║
║  ├───┼───┼───┼───┼───┤  ║
║  │ P │ L │   │   │   │  ║
║  └───┴───┴───┴───┴───┘  ║
║     MathPL v0.2.0       ║
║     Твой синтаксис!     ║
╚══════════════════════════╝
    """)
    print("MathPL REPL. 'выход' для выхода.\n")

    buffer = ""
    while True:
        try:
            prompt = "....> " if buffer else "mpl> "
            line = input(prompt)
            if line.strip() == 'выход':
                break
            buffer += line + "\n"
            if line.strip() == 'close':
                try:
                    run_code(buffer)
                except Exception as e:
                    print(f"Ошибка: {e}")
                buffer = ""
        except KeyboardInterrupt:
            print("\nВыход.")
            break


if __name__ == "__main__":
    if len(sys.argv) > 1:
        run_file(sys.argv[1])
    else:
        repl()