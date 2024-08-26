import math
import re

def ShuntingYard(expr):
    tokens = []
    output = []
    pattern = ' *([+\-*/()]|\d+\.\d+|\d+) *'
    tokens = re.split(pattern, expr)
    for i in tokens:
        if i == '':
            tokens.remove(i)
    op = { '*': 1, '/': 1, '+': 0, '-': 0}
    op_stack = []
    for token in tokens:
        token = str(token)
        if token.isdigit():
            output.append(token)
        elif token == '(':
            op_stack.append(token)
        elif token == ')':
            if op_stack[0] != ')':
                output.append(op_stack.pop())
                for i in op_stack:
                    if i == '(':
                        op_stack.remove(i)
        elif token == '*' or '/' or '+' or '-':
            op_stack.append(token)
        elif op[token]==1 and len(op_stack)>1 and op_stack[-1] == '*' or '/':
            output.append(op_stack.pop())
            op_stack.append(token)
    output = output + op_stack     
    evaluate_stack = []
    for op in output:
        if op in ['-', '+', '*', '/']:
            op1 = evaluate_stack.pop()
            op2 = evaluate_stack.pop()
            if op=='-': result = op2 - op1
            if op=='+': result = op2 + op1
            if op=='*': result = op2 * op1
            if op=='/': result = op2 / op1
            evaluate_stack.append(result)
        else:
            evaluate_stack.append(float(op))

    result = str(evaluate_stack.pop())
 
    return result

