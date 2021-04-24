import numbers
import numpy
import re

class Container():

    def __init__(self):
        self._items = []

    def size(self):
        return len(self._items)

    def is_empty(self):
        return self.size() == 0

    def push(self, item):
        self._items.append(item)

    def pop(self):                  #Metodene er ennå ikke implementert, da de skal overstyres av arvende klasser
        raise NotImplementedError

    def peek(self):
        raise NotImplementedError


class Queue(Container):  #Klasse som beskriver kø-funksjonalitet slik oppgaven spurte etter

    def __init__(self):
        super(Queue, self).__init__()

    def peek(self):
        if (not self.is_empty()):
            return self._items[0]
        else:
            return "Empty queue"

    def pop(self):
        if (not self.is_empty()):
            return self._items.pop(0)
        else:
            return "Empty queue"


class Stack(Container): #Klasse som beskriver stack-funksjonalitet slik oppgaven spør etter

    def __init__(self):
        super(Stack, self).__init__()

    def peek(self):
        if (not self.is_empty()):
            return self._items[-1]
        else:
            return "Empty stack"

    def pop(self):
        if (not self.is_empty()):
            return self._items.pop()
        else:
            return "Empty stack"


class Function():  #Klasse som håndterer funksjoner som objekter. Disse "låner" igjen fra numpy

    def __init__(self, func):
        self.func = func

    def execute(self, element, debug=True):
        if not isinstance(element, numbers.Number):
            raise TypeError("Cannot execute func if element is not a number")
        result = self.func(element)

        if debug is True:
            print("Function: " + self.func.__name__ + "({:f}) = {:f}".format(element, result))

        return result


class Operator(): #Som Functions, bare for operatorer med tilpasset syntaks

    def __init__(self, operator, strength):
        self.operator = operator
        self.strength = strength

    def execute(self, element1, element2, debug=True):
        if (not isinstance(element1, numbers.Number)) or (not isinstance(element2, numbers.Number)):
            raise TypeError("Cannot execute func if element is not a number")
        result = self.operator(element1, element2)

        if debug is True:
            print("Operator: " + "{:f}" + self.operator.__name__ + "({:f}) = {:f}".format(element1, element2, result))

        return result


class Calculator(): #Hovedklassen som utfører oppgaven og benytter seg av alle klasser

    def __init__(self):    #Her instansieres funksjoner og operatorer. Vi kan velge blant alt som finnes, så lenge vi har riktig navnnotasjon med tanke på tekstparseren, og den finnes i numpy
        self.functions = {"EXP": Function(numpy.exp),
                          "LOG": Function(numpy.log),
                          "SIN": Function(numpy.sin),
                          "COS": Function(numpy.cos),
                          "SQRT": Function(numpy.sqrt)}

        self.operators = {"PLUSS": Operator(numpy.add, 0),
                          "GANGE": Operator(numpy.multiply, 1),
                          "DELE": Operator(numpy.divide, 1),
                          "MINUS": Operator(numpy.subtract, 0)}

        self.output_queue = Queue()

    def calculate(self, RPNqueue): #Tar inn RPN-notert kø og gir resultatet

        self.output_queue = RPNqueue
        NUMstack = Stack()

        for i in range(0, RPNqueue.size()):
            elem = self.output_queue.pop()
            if (isinstance(elem, numbers.Number)):
                NUMstack.push(elem)
            elif (type(elem) is Function):
                x = NUMstack.pop()
                y = elem.execute(x)
                NUMstack.push(y)
            elif (type(elem) is Operator):
                x = NUMstack.pop()
                y = NUMstack.pop()
                print("x:", x)
                print("y:", y)
                z = elem.execute(y,x)
                NUMstack.push(z)

        return NUMstack.pop()

    def shuntingyard(self, iQueue): #Stokker om "vanlig" notasjon til RPN-notasjon
        o_queue = Queue()
        o_stack = Stack()
        for i in range(0, iQueue.size()):

            elem = iQueue.pop()
            if (isinstance(elem, numbers.Number)):
                o_queue.push(elem)

            elif ((type(elem) is Function) or (elem is "(")):
                o_stack.push(elem)

            elif (elem == ')'):
                while (not (o_stack.peek() is "(")):
                    o_queue.push(o_stack.pop())
                o_stack.pop()
            elif (type(elem) is Operator):
                control = 1
                while ((control == 1) and (not o_stack.is_empty())):
                    peeked = o_stack.peek()

                    if (peeked is "("):
                        control = 0
                    elif (not type(peeked) is Operator):
                        o_queue.push(o_stack.pop())
                    elif (type(peeked) is Operator):

                        if (peeked.strength >= elem.strength):
                            o_queue.push(o_stack.pop())

                        else:
                            control = 0

                o_stack.push(elem)

        print("finished forloop")
        while (not o_stack.is_empty()):
            o_queue.push(o_stack.pop())

        return o_queue


    def parser(self, text): #Formatterer tekststreng til "vanlig" notasjon

        returnarray = Queue()
        text = text.replace(" ", "").upper()
        print(text)
        targets = "|".join(["^" + func for func in self.functions.keys()])
        targets2 = "|".join(["^" + operator for operator in self.operators.keys()])

        print(targets)

        check = re.search("^[-0123456789.]+", text)
        check2 = re.search(targets, text)
        check3 = re.search(targets2, text)
        check4 = re.search("^(|^)", text)

        while ((not check is None) or (not check2 is None) or (not check3 is None) or (not check4 is None)):
            if (not check is None):
                returnarray.push(float(check.group(0)))
                text = text[check.end(0):]
                print("num")
            elif (not check2 is None):
                returnarray.push(self.functions[check2.group(0)])
                text = text[check2.end(0):]
                print("function")
            elif (not check3 is None):
                returnarray.push(self.operators[check3.group(0)])
                text = text[check3.end(0):]
                print("operator")
            else:
                for i in check4.group(0):
                    returnarray.push(i)
                text = text[check4.end(0):]
                print("parentheses")

            check = re.search("^[-0123456789.]+", text)
            check2 = re.search(targets, text)
            check3 = re.search(targets2, text)
            check4 = re.search("^[()]+", text)

        return returnarray


    def calculate_expression(self, txt): #Hovedmetode som forener alle metodene på en oversiktlig måte
        iQueue = self.parser(txt)
        newQueue = self.shuntingyard(iQueue)

        
        return self.calculate(newQueue)
