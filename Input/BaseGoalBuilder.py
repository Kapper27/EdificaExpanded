from owlready2 import *

sys.path.insert(0, '../')
from UtilityInterfaces import *

import networkx as nx
import matplotlib.pyplot as plt
import io
import matplotlib.image as mpimg

from networkx.drawing.nx_agraph import write_dot, graphviz_layout

from BaseGoalExpander import *


class NodeGoal:

    def __init__(self, goal):
        """Costruttore:

            Parametri:
            goal(ThingClass| And | Or | Not | Restriction): il
                goal a cui il nodo è associato

            Returns:
            NodeGoal: restituisce un nodo goal. Ogni nodo goal
                ha una serie di nodi "figli" che rappresentano
                sotto-goal del goal associato al nodo goal.

        """
        self.graph = None
        self.done = 0
        self.children = []
        self.approx = None
        if isinstance(goal, ThingClass):
            self.goal = goal
        elif isinstance(goal, And) or isinstance(goal, Or):
            for x in goal.Classes:
                self.goal = goal
                n = NodeGoal(x)
                self.addChildren(n)
        elif isinstance(goal, Not):
            x = goal.Class
            self.goal = goal
            n = NodeGoal(x)
            self.addChildren(n)
            if isinstance(self.goal.Class, Or):
                self.eq = NodeGoal(And([Not(x) for x in self.children[0].goal.Classes]))
            elif isinstance(self.goal.Class, And):
                self.eq = NodeGoal(Or([Not(x) for x in self.children[0].goal.Classes]))
            elif isinstance(self.goal.Class, Restriction):
                if self.children[0].goal.type == owlready2.SOME:
                    self.eq = NodeGoal(
                        (self.children[0].goal.property).only(Not(self.children[0].goal.value)))  # diventa only
                elif self.children[0].goal.type == owlready2.ONLY:
                    self.eq = NodeGoal(
                        (self.children[0].goal.property).some(Not(self.children[0].goal.value)))  # diventa some
            else:
                self.eq = NodeGoal(self.children[0].goal)
        else:
            x = goal.value
            self.goal = goal
            n = NodeGoal(x)
            self.addChildren(n)

    def addChildren(self, child):
        """Funzione addChildren:

            Parametri:
            child (NodeGoal): nodo che rappresenta un sotto-goal
                del goal del nodo attuale

            Returns:
            None: si aggiunge il nodo che rappresenta un sotto-goal
                ai figli del nodo attuale

        """
        self.children.append(child)

    def __str__(self):
        """Funzione __str__:

            Parametri:

            Returns:
            str: la seguente funzione restituisce una stringa
                che rappresenta il nodo goal

        """
        res = ""
        if isinstance(self.goal, ThingClass):
            res = self.goal.name  # +str(id(self))
        elif isinstance(self.goal, And):
            first = True
            for x in self.children:
                if first:
                    res = str(x)
                    first = False
                else:
                    res = res + " & " + str(x)
        elif isinstance(self.goal, Or):
            first = True
            for x in self.children:
                if first:
                    res = str(x)
                    first = False
                else:
                    res = res + " | " + str(x)
        elif isinstance(self.goal, Not):
            res = "- " + str(self.children[0])
        else:
            if self.goal.type == owlready2.SOME:
                res = self.goal.property.name + " some " + str(self.children[0])
            else:
                res = self.goal.property.name + " only " + str(self.children[0])

        return res

    def getGraph(self, G):
        """Funzione getGraph:

            Parametri:
            G (DiGraph): grafo a cui aggiungere il nodo con i propri figli

            Returns:
            DiGraph: la seguente funzione restituisce un
                grafo risultante dalla aggiunta dei nodi

        """
        G.add_node(str(self))
        for node in self.children:
            node.getGraph(G)
            G.add_edge(str(self), str(node))
        return G

    def setVisualization(self):
        """Funzione setVisualization:

            Parametri:

            Returns:
            None: la seguente funzione imposta come grafo
                la coppia composta dal grafo diretto
                in cui compaiono i concetti del goal
                e il layout di posizionamento dei nodi
                nel grafo

        """
        G = nx.DiGraph()
        self.getGraph(G)
        pos = nx.spring_layout(G)
        self.graph = (G, pos)

    def setLastGoalApprox(self, approx):
        """Funzione setLastGoalApprox:

            Parametri:
            approx(ThingClass | And | Or | Not | Restriction):
                la approssimazione del goal rappresentato
                dal nodo attuale

            Returns:
            None: la seguente funzione va a impostare approx
                come la approssimazione del nodo attuale

        """
        self.approx = approx

    def getNextGoal(self):
        """Funzione getNextGoal:

            Parametri:

            Returns:
            ThingClass | And | Or | Not | Restriction: la seguente funzione
                restituisce la espressione in owlready2 riferita al nodo goal
                attuale che sia una approssimazione del goal iniziale.
                La approssimazione consiste in un escludere mano a mano dei
                "pezzi" del goal originale

        """
        if isinstance(self.goal, ThingClass):
            if self.approx == self.goal:
                self.setLastGoalApprox(None)
                return None
            else:
                self.setLastGoalApprox(self.goal)
                return self.goal

        if isinstance(self.goal, Or):
            if self.done == 0:
                self.done = 1
                children_and = [x for x in self.children if not isinstance(x.goal, ThingClass)]
                ands = [x.goal for x in children_and]

                others = [x.goal for x in self.children if x not in children_and]
                elements = []
                for i in range(0, len(ands)):
                    k = children_and[i].getNextGoal()
                    elements.append(k)
                res = elements + others
                self.setLastGoalApprox(Or(res))
                return Or(res)

            if self.done == 2:
                self.done = 3
                self.setLastGoalApprox(self.goal)
                return self.goal

            children_and = [x for x in self.children if not isinstance(x.goal, ThingClass)]
            ands = [x.goal for x in children_and]
            others = [x.goal for x in self.children if x not in children_and]
            lench = len(ands)
            res = None
            elements = []
            i = lench - 1
            while res == None and i >= 0:
                k = children_and[i].getNextGoal()
                if k == None:
                    k = children_and[i].getNextGoal()
                    i = i - 1
                    elements.append(k)
                    res = None
                else:
                    res = k
                    elements.append(k)
            if res != None:
                if i != -1:
                    elements = elements + [x.approx for x in children_and[:i]]
                elements = elements + others
                self.setLastGoalApprox(Or(elements))
                return Or(elements)
            else:
                self.done = 2
                self.setLastGoalApprox(None)
                return None

        if isinstance(self.goal, Not):
            res = self.eq.getNextGoal()
            if res != None:
                if isinstance(self.eq.goal, And):
                    if isinstance(res, Not):
                        self.setLastGoalApprox(res)
                        return res
                    else:
                        self.setLastGoalApprox(Not(Or([x.Class for x in res.Classes])))
                        return Not(Or([x.Class for x in res.Classes]))
                elif isinstance(self.eq.goal, Or):
                    if isinstance(res, Not):
                        self.setLastGoalApprox(res)
                        return res
                    else:
                        self.setLastGoalApprox(Not(And([x.Class for x in res.Classes])))
                        return Not(And([x.Class for x in res.Classes]))
                elif isinstance(self.eq.goal, Restriction):
                    if res.type == owlready2.SOME:
                        arg = res.value.Class
                        self.setLastGoalApprox(Not(res.property.only(arg)))
                        return Not(self.eq.goal.property.only(arg))
                    elif res.type == owlready2.ONLY:
                        arg = res.value.Class
                        self.setLastGoalApprox(Not(res.property.some(arg)))
                        return Not(self.eq.goal.property.some(arg))
                else:
                    self.setLastGoalApprox(Not(res))
                    return Not(res)
            else:
                self.setLastGoalApprox(None)
                return None

        if isinstance(self.goal, And):
            if self.done == 0:
                self.done = 1
                elements = []
                for i in range(0, len(self.children)):
                    k = self.children[i].getNextGoal()
                    elements.append(k)
                self.setLastGoalApprox(And(elements))
                return And(elements)

            lench = len(self.children)
            res = None
            elements = []
            i = lench - 1

            while res == None and i >= 0:
                k = self.children[i].approx
                if k != None:
                    k = self.children[i].getNextGoal()
                    elements.append(k)
                    res = True
                else:
                    k = self.children[i].getNextGoal()
                    elements.append(k)
                    i = i - 1

            elements = elements + [x.approx for x in self.children[:i] if x.approx != None]
            elements = [x for x in elements if x != None]
            if elements == []:
                self.done = 0
                self.setLastGoalApprox(None)
                return None
            else:
                if len(elements) == 1:
                    self.setLastGoalApprox(elements[0])
                    return elements[0]
                else:
                    self.setLastGoalApprox(And(elements))
                    return And(elements)

        if isinstance(self.goal, Restriction):
            res = self.children[0].getNextGoal()
            if res == None:
                self.setLastGoalApprox(None)
                return None
            else:
                if self.goal.type == SOME:
                    self.setLastGoalApprox(self.goal.property.some(res))
                    return self.goal.property.some(res)
                elif self.goal.type == ONLY:
                    self.setLastGoalApprox(self.goal.property.only(res))
                    return self.goal.property.only(res)


class BaseGoalBuilder(GoalBuilder):
    structure_of_file = "goals expressed in Manchester Syntax"
    format_read = "manchester syntax"
    goals_format = "goal-graph"

    graph = None  # da esporre all'esterno, per la GUI

    def __init__(self, parser, ontology, path='goal2'):
        """Costruttore:

            Parametri:
            parser (Parser): parser per poter tradurre il goal in un goal
                in formato owlready2
            ontology (Ontology): ontologia di riferimento da cui il parser
                costruirà le espressioni
            path (str): stringa che rappresenta il percorso in cui trovare
                il file contenente il goal da risolvere

            Returns:
            BaseGoalBuilder: il goal builder che permette di
                costruire leggere da file e definire il goal
                in owlready2 e per poter costruire le sue
                approssimazioni

        """
        if not os.path.isfile(path):
            raise Exception("Goal file does not exists!")

        self.path = path
        self.ontology = ontology
        self.parser = parser(ontology)
        self.goals = []

        if parser.format_read != self.format_read:
            raise Exception("Parser and Goal have different formats!")

        self.goal_expander = BaseGoalExpander(self.parser, self.ontology)

    def getGoals(self):
        """Funzione getGoals:

            Parametri:

            Returns:
            GoalNode: la seguente funzione restituisce un nodo
                goal da cui possiamo ottenere il goal originale ed
                eventuali goal approssimazione

        """
        res = self.goals.getNextGoal()
        return res

    def buildGoals(self):
        """Funzione buildGoals:

            Parametri:


            Returns:
            None: la seguente funzione legge da file il goal e costruisce
                i NodeGoal che lo rappresentano
        """
        with open(self.path) as f:
            input_lines = f.readlines()
        goal_line = [x for x in input_lines if x.strip() != '' and x.strip()[0] != '\n'][0]  # il goal è solo una riga

        expanded_goal_line = self.goal_expander.expand_goal(goal_line)
        res = self.parser.parse(expanded_goal_line)

        print(res, expanded_goal_line)

        self.goals = NodeGoal(res)
        self.goals.setVisualization()
        self.graph = self.goals.graph