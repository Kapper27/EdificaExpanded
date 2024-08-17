import types
from owlready2 import *
from boolean_parser.parsers import Parser 
from boolean_parser.clauses import fxn
from boolean_parser.clauses import words
from boolean_parser import *
from pyparsing.results import *
import pyparsing as pp

sys.path.insert(0, '../')
from UtilityInterfaces import DefinedParser

class Node:
    children = None
    name = None

    def __init__(self,name):
        """Costruttore:

            Parametri:
            name (str): Nome del nodo
            
            Returns:
            Node: dato un nome specificato da name, viene generato:
                - un nodo semplice nel caso sia il nome di una classe
                - un nodo con nodi figli nel caso il nome sia
                  una espressione complessa espressa tramite connettori 
                  logici and, not, or e tramite some, only.

        """
        if isinstance(name,pp.results.ParseResults):
            start = None
            i = 0
            while(i < len(name)):
                if len(name) == 1:
                    start = Node(name[0])
                    i = i + 1
                elif name[i] == "not":
                    start = Node(name[i])
                    i = i + 1
                    start.addChild(Node(name[i]))
                    i = i + 1
                else:
                    if start == None:
                        start = Node(name[i])
                        i = i + 1
                    father = Node(name[i])
                    i = i + 1
                    child = Node(name[i])
                    i = i + 1
                    father.addChild(start)
                    father.addChild(child)
                    start = father
                
            self.name = start.name
            self.children = start.children
        else:
            self.name = name
            self.children = []
    


    def addChild(self,child):
        """Funzione addChild:

            Parametri:
            child (Node): Nodo da aggiungere come figlio
            
            Returns:
            Void: la seguente funzione aggiunge il nodo riferito da
                child come figlio del nodo corrente

        """
        self.children.append(child)

    
    
    def __str__(self):
        """Funzione __str__:

            Parametri:
            
            
            Returns:
            str: la stringa corrispondente al nodo corrente

        """
        s = str(self.name)
        for c in self.children:
            lines = str(c).splitlines()
            for l in lines:
                s = s + "\n->   " + l
        return s



    def create(self,ontology):
        """Funzione create:

            Parametri:
            ontology (Ontology): ontologia di riferimento
            
            Returns:
            ThingClass | And | Or | Not | Restriction: dato il 
                nodo corrente, percorre i figli in maniera ricorsiva
                e costruisce la espressione in owlready2 corrispondente 
                utilizzando le classi specificate da ontology

        """
        res = None
        if str(self.name) == "and":
            c1 = self.children[0].create(ontology)
            c2 = self.children[1].create(ontology)
            to_add = []
            if isinstance(c1, And):
                to_add = to_add + c1.Classes
            else:
                to_add.append(c1)
            if isinstance(c2, And):
                to_add = to_add + c2.Classes
            else:
                to_add.append(c2)
            res = And(to_add)
        elif str(self.name) == "or":
            c1 = self.children[0].create(ontology)
            c2 = self.children[1].create(ontology)
            to_add = []
            if isinstance(c1, Or):
                to_add = to_add + c1.Classes
            else:
                to_add.append(c1)
            if isinstance(c2, Or):
                to_add = to_add + c2.Classes
            else:
                to_add.append(c2)
            
            res = Or(to_add)
        elif str(self.name) == "not":
            c1 = self.children[0].create(ontology)
            if isinstance(c1,Not):
                res = c1.Class
            else:
                res = Not(c1)
        elif str(self.name) == "some":
            c1 = self.children[1].create(ontology)
            res = ontology[self.children[0]].some(c1)
        elif str(self.name) == "only":
            c1 = self.children[1].create(ontology)
            res = ontology[self.children[0]].only(c1)
        else:
            res = ontology[str(self.name)]
        
        return res


from pyparsing import Literal,Word,ZeroOrMore,Forward,nums,oneOf,Group,CaselessKeyword

def Syntax():
    """funzione Syntax():

        Parametri:
        
            
        Returns:
        Forward: funzione che definisce la sintassi della grammatica utilizzata 
            per parsificare espressioni in formato Manchester Syntax

        """

    op = oneOf('and or')
    op2 = oneOf('some only')
    lpar  = Literal( '(' ).suppress()
    rpar  = Literal( ')' ).suppress()
    num = Word(pp.alphas.upper(), pp.alphanums)
    expr = Forward()
    expr_or = Forward()
    atom = Group("not" + expr) | Group(Word(pp.alphas.lower() , pp.alphanums) + op2 + expr) | num | Group(lpar + expr + rpar)
    # expr_or << (Group(atom + 'and' + expr_or) | atom)
    # expr << (Group(expr_or + 'or' + expr) | expr_or)
    expr_or << Group(atom + ZeroOrMore('and' + expr_or))
    expr << Group(expr_or + ZeroOrMore('or' + expr))
    #expr << Group(atom + ZeroOrMore(op + atom))
    return expr



class ManchesterParser(DefinedParser):
    format_read = "manchester syntax"

    def __init__(self,ontology):
        """Costruttore:

            Parametri:
            ontology (Ontology): ontologia di riferimento da cui il parser
                costruirà le espressioni
            
            Returns:
            ManchesterParser: il parser che leggerà espressioni in 
                Manchester Syntax e restituirà espressioni in 
                owlready2 espresse sulla ontologia passata 
                come parametro

        """
        self.ontology = ontology 
    


    def parse(self,s):
        """Funzione parse:

            Parametri:
            s (str): stringa che rappresenta la espressione da parsificare
            
            Returns:
            ThingClass | And | Or | Not | Restriction: la seguente funzione 
                restituisce la espressione in owlready2 sulla ontologia 
                di riferimento corrispondente alla espressione 
                rappresentata da s

        """
        expr = Syntax()
        r = expr.parseString(s)
        print("PARSE:",r)

        start = None
        i = 0

        while(i < len(r)):
            if len(r) == 1:
                start = Node(r[0])
                i = i + 1
            elif r[0] == "not":
                start = Node(r[i])
                i = i + 1
                start.addChild(Node(r[i]))
                i = i + 1
            else:
                if start == None:
                    start = Node(r[i])
                    i = i + 1
                father = Node(r[i])
                i = i + 1
                child = Node(r[i])
                i = i + 1
                father.addChild(start)
                father.addChild(child)
                start = father
        
        res = start.create(self.ontology)
        print(res)
        return res 