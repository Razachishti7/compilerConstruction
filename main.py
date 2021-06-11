
import copy
import re




def tokenizer(input_expression):

    current = 0
    tokens = []

    alphabet = re.compile(r"[a-z]", re.I)

    numbers = re.compile(r"[0-9]")

    whiteSpace = re.compile(r"\s")

    while current < len(input_expression):

        char = input_expression[current]

        if re.match(whiteSpace, char):
            current = current + 1
            continue

        if char == '(':
            tokens.append({
                'type': 'left_paren',
                'value': '('
            })

            current = current + 1
            continue

        if char == ')':
            tokens.append({
                'type': 'right_paren',
                'value': ')'
            })

            current = current + 1
            continue

        if re.match(numbers, char):
            value = ''

            while re.match(numbers, char):
                value += char
                current = current + 1
                char = input_expression[current]
            tokens.append({
                'type': 'number',
                'value': value
            })
            continue

        if re.match(alphabet, char):
            value = ''

            while re.match(alphabet, char):
                value += char
                current = current + 1
                char = input_expression[current]
            tokens.append({
                'type': 'name',
                'value': value
            })
            continue

        raise ValueError('what are THOSE?: ' + char)
    return tokens



def parser(tokens):

    global current
    current = 0


    def walk():

        global current
        token = tokens[current]

        if token.get('type') == 'number':
            current = current + 1
            return {
                'type': 'NumberLiteral',
                'value': token.get('value')
            }


        if token.get('type') == 'left_paren':

            current = current + 1
            token = tokens[current]

            node = {
                'type': 'CallExpression',
                'name': token.get('value'),
                'params': []
            }
            current = current + 1
            token = tokens[current]

            while token.get('type') != 'right_paren':

                node['params'].append(walk())
                token = tokens[current]
            current = current + 1
            return node

        raise TypeError(token.get('type'))


    ast = {
        'type': 'Program',
        'body': []
    }

    while current < len(tokens):
        ast['body'].append(walk())

    return ast



def traverser(ast, visitor):

    def traverseArray(array, parent):

        for child in array:

            traverseNode(child, parent)
    def traverseNode(node, parent):
        method = visitor.get(node['type'])
        if method:
            method(node, parent)
        if node['type'] == 'Program':
            traverseArray(node['body'], node)
        elif node['type'] == 'CallExpression':
            traverseArray(node['params'], node)
        elif node['type'] == 'NumberLiteral':
            0
        else:
            raise TypeError(node['type'])

    traverseNode(ast, None)



def transformer(ast):

    newAst = {
        'type': 'Program',
        'body': []
    }

    oldAst = ast
    ast = copy.deepcopy(oldAst)

    ast['_context'] = newAst.get('body')

    def CallExpressionTraverse(node, parent):
        expression = {
            'type': 'CallExpression',
            'callee': {
                'type': 'Identifier',
                'name': node['name']
            },
            'arguments': []
        }
        node['_context'] = expression['arguments']
        if parent['type'] != 'CallExpression':
            expression = {
                'type': 'ExpressionStatement',
                'expression': expression
            }
        parent['_context'].append(expression)
    def NumberLiteralTraverse(node, parent):
        parent['_context'].append({
            'type': 'NumberLiteral',
            'value': node['value']
        })
    traverser(ast, {
        'NumberLiteral': NumberLiteralTraverse,
        'CallExpression': CallExpressionTraverse
    })
    return newAst



def codeGenerator(node):
    if node['type'] == 'Program':
        return '\n'.join([code for code in map(codeGenerator, node['body'])])
    elif node['type'] == 'Identifier':
        return node['name']
    elif node['type'] == 'NumberLiteral':
        return node['value']
    elif node['type'] == 'ExpressionStatement':
        expression = codeGenerator(node['expression'])
        return '%s;' % expression
    elif node['type'] == 'CallExpression':
        callee = codeGenerator(node['callee'])
        params = ', '.join([code for code in map(codeGenerator, node['arguments'])])
        return "%s(%s)" % (callee, params)
    else:
        raise TypeError(node['type'])



def compiler(input_expression):

    tokens = tokenizer(input_expression)

    ast = parser(tokens)

    newAst = transformer(ast)

    output = codeGenerator(newAst)

    return output


def main():
    # test
    print("(add 2 (subtract 4 2))");
    a =input("Enter a line in LISP:")

    output = compiler(a)
    print(output)


if __name__ == "__main__":
    main()