class Node():

    def __init__(self,name,value,prob):
        """Costruttore:

            Parametri:
            name (str): nome della classe nel corpo
                dell'assioma di tipicalità
            value (True | False): il valore di 
                verità dell'assioma di tipicalità
            prob (dict): probabilità dell'assioma
            
            
            Returns:
            Node: viene generato un nodo in cui sono 
                rappresentate le informazioni di un
                assioma di tipicalità.

        """
        self.name = name
        self.value = value
        self.prob = prob
        self.coherence = {}
        self.coherence["both_true"] = []
        self.coherence["both_false"] = []
        self.coherence["opposite"] = []


    def addOnTrue(self,n):
        """Funzione addOnTrue:

            Parametri:
            n (Node): nodo da aggiungere a quello corrente
            
            Returns:
            None: si aggiunge una dipendenza: se un nodo è
                un assioma vero, allora anche il nodo corrente
                deve essere vero

        """
        if n.name not in self.coherence["both_true"]:
            self.coherence["both_true"].append(n.name)



    def addOnFalse(self,n):
        """Funzione addOnFalse:

            Parametri:
            n (Node): nodo da aggiungere a quello corrente
            
            Returns:
            None: si aggiunge una dipendenza: se un nodo è
                un assioma falso, allora anche il nodo corrente
                deve essere falso

        """
        if n.name not in self.coherence["both_false"]:
            self.coherence["both_false"].append(n.name)



    def addOpposite(self,n):
        """Funzione addOpposite:

            Parametri:
            n (Node): nodo da aggiungere a quello corrente
            
            Returns:
            None: si aggiunge una dipendenza: il nodo
                passato come parametro e il nodo corrente
                sono potenzialmente inconsistenti tra loro

        """
        if n.name not in self.coherence["opposite"]:
            self.coherence["opposite"].append(n.name)
        if self.name not in n.coherence["opposite"]:
            n.addOpposite(self)



    def __str__(self):
        """Funzione __str__:

            Parametri:
            
            Returns:
            str: si restituisce stringa che rappresenta
                l'assioma rappresentato dal nodo

        """
        return "(" + str(self.name) + "," + str(self.value) + "," + str(self.prob) + ")"



    def get_value(self,opt):
        """Funzione get_value:

            Parametri:
            opt (int): opzione per chiedere quale
                versione dell'assioma restituire.
                Se posta a zero si restituisce la versione
                con probabilità maggiore, altrimenti la
                versione con probabilità minore
            
            Returns:
            (True|False, float): si restituisce la
                versione dell'assioma richiesta, con il 
                proprio valore di verità e la propria
                probabilità

        """
        if opt == 0:
            if self.prob >= 0.5:
                return (self.value,self.prob)
            else:
                return (not self.value,1-self.prob)
        elif opt == 1:
            if self.prob >= 0.5:
                return (not self.value,1-self.prob) 
            else:
                return (self.value,self.prob)
        else:
            return None



class ScenarioNode():
    node = None


    def __init__(self,node):
        """Costruttore:

            Parametri:
            node (Node): nodo da aggiungere allo scenario
            
            Returns:
            ScenarioNode: il costruttore restituisce
                un nodo che rappresenta un assioma di 
                tipicalità utilizzato in uno scenario.
                La seguente classe permette di gestire
                tale assioma in base alle opzioni 
                presenti nello scenario. Tali
                opzioni consistono nel prendere
                o meno un assioma di tipicalità

        """
        self.node = node



    def get_option(self,value):
        """Funzione get_option:

            Parametri:
            value (int): valore di verità richiesto
            
            Returns:
            int: se il valore di verità è quello
                più probabile si restituisce la opzione
                0, altrimenti 1

        """
        if self.node.prob >= 0.5:
            if value == self.node.value:
                return 0
            else:
                return 1
        else:
            if value == self.node.value:
                return 1
            else:
                return 0

    

from bitstring import BitArray
import math
import itertools
from heapq import merge


class ScenarioManager():
        
    def __init__(self,best_scenario,consistency_graph):
        """Costruttore:

            Parametri:
            best_scenario (list): scenario più probabile
            consistency_graph: grafo di consistenza da interrogare
                per ottenere le dipendenze tra nodi di scenario
            
            Returns:
            ScenarioManager: si restituisce un gestore di scenari
                che combina le possibili opzioni mantenendole coerenti

        """
        self.scenario_nodes = []
        self.nodes = {}
        print("BEST SCENARIO:",best_scenario)
        for (a,b,c) in best_scenario:
            n = Node(a,b,c)
            k = ScenarioNode(n)
            if a not in self.nodes.keys():
                self.nodes[a] = [n]
            else:
                self.nodes[a].append(n)
            self.scenario_nodes.append(k)
        

        self.__addConsistencies(best_scenario, consistency_graph, self.nodes)
    


    def __addConsistencies(self, best_scenario,consistency_graph,nodes):
        """Funzione __addConsistencies:

            Parametri:
            best_scenario (list): scenario più probabile
            consistency_graph: grafo di consistenza da interrogare
                per ottenere le dipendenze tra nodi di scenario

            Returns:
            None: si aggiungono le dipendenze tra i nodi
                dello scenario in base al grafo delle
                consistenze

        """
        for (a,b,c) in best_scenario:
            for x in consistency_graph[a].enemies:
                for y in nodes[a]:
                    if x in nodes.keys():
                        for z in nodes[x]:
                            print("ADDING", y.name, z.name )
                            y.addOpposite(z)

        for (a,b,c) in best_scenario:
            if len(nodes[a]) > 1:
                equivs = [(k, b) for k in range(0,len(nodes[a])) for b in range(k+1,len(nodes[a]))]
                for (x,y) in equivs:
                    nodes[a][x].addOnTrue(nodes[a][y])
                    nodes[a][x].addOnFalse(nodes[a][y])
                    nodes[a][y].addOnTrue(nodes[a][x])
                    nodes[a][y].addOnFalse(nodes[a][x])
            
        for i in range(0,len(best_scenario)):
            for j in range(i,len(best_scenario)):
                if best_scenario[j][0] in best_scenario[i][0].is_a:
                    nodes[best_scenario[i][0]].addOnTrue(nodes[best_scenario[j][0]])
                    nodes[best_scenario[j][0]].addOnFalse(nodes[best_scenario[i][0]])
                if best_scenario[i][0] in best_scenario[j][0].is_a:
                    nodes[best_scenario[j][0]].addOnTrue(nodes[best_scenario[i][0]])
                    nodes[best_scenario[i][0]].addOnFalse(nodes[best_scenario[j][0]])


    
    def calculate_probability(self,bits):
        """Funzione calculate_probability:

            Parametri:
            bits (list): lista di bit in cui ogni bit indica la
                opzione da prendere per il singolo assioma di 
                tipicalità

            Returns:
            float: la probabilità dello scenario rappresentato
                da tali opzioni
                
        """
        prob = 1
        for i in range(0,len(bits)):
            n = self.scenario_nodes[i]
            v,p = n.node.get_value(bits[i])
            prob = prob * p
        return prob


    def my_sum(self,node_a,bits,pos):
        """Funzione my_sum:

            Parametri:
            node_a (ScenarioNode):il nodo dello scenario
                di cui dobbiamo controllare la coerenza
                a livello di probabilità dei nodi
                veri con cui è in conflitto
            bits ([int]): lista che rappresenta la scelta
                presa per ogni nodo nello scenario. Con 0
                si indica il prendere la versione più 
                probabile dell'assioma di tipicalità di
                tale nodo, con 1 si indica il prendere la 
                versione meno probabile
            pos (int): posizione del nodo node_a all'interno
                dello scenario

            Returns:
            float: la somma delle probabilità degli assiomi
                veri che sono in conflitto con l'assioma
                espresso dal nodo node_a
                
        """
        tot_sum = 0
        if bits[pos] != -1:
            if node_a.node.get_value(bits[pos])[0] == True:
                tot_sum = node_a.node.get_value(bits[pos])[1]
                j = 0
                for y in self.scenario_nodes:
                    if y.node.name in node_a.node.coherence["opposite"]:
                        if bits[j] != -1:
                            bit = y.get_option(True)
                            if bits[j] == bit:
                                tot_sum = tot_sum + y.node.get_value(bit)[1]
                    j = j + 1
        return tot_sum



    def update(self,n,opt,k,y,bits):
        """Funzione update:

            Parametri:
            n (ScenarioNode): nodo che rappresenta
                un assioma di tipicalità da valutare
            opt (int): opzione dell'assioma espresso
                dal nodo n: con 0 si indica la sua versione
                più probabile con 1 la sua versione 
                meno probabile
            k (ScenarioNode): nodo con cui confrontare n 
            y (int): opzione dell'assioma espresso dal 
                nodo k, definito in maniera analoga ad opt
                per n
            bits ([int]): opzioni dello scenario. Per ogni
                posizione viene associato un nodo dello scenario
                e viene specificata una opzione: 0 per prenderne
                la versione più probabile, 1 per quella meno probabile
                e -1 per dire che non è ancora stata compiuta una
                scelta

            Returns:
            True | False: si restituisce True se il nodo n e il nodo
                k sono consistenti tra loro nello scenario espresso
                dalle opzioni in bits, False altrimenti
                
        """
        f = True
        (v,p) = n.node.get_value(opt)
        if v == True:
            if k.node.name in n.node.coherence["opposite"] and bits[y] != -1:
                tot_sum = self.my_sum(k,bits,y)
                if tot_sum > 1:
                    f = False
            
            if k.node.name in n.node.coherence["both_true"]:
                bit = k.get_option(True)
                if int(bits[y]) == -1:
                    bits[y] = bit
                else:
                    if int(bits[y]) != int(bit):
                        f = False
        else:
            if k.node.name in n.node.coherence["both_false"]:
                bit = k.get_option(False)
                if int(bits[y]) == -1:
                    bits[y] = bit
                else:
                    if int(bits[y]) != int(bit):
                        f = False
        return f



    def merge(self,list1,list2):
        """Funzione merge:

            Parametri:
            list1 (list): lista di scenari ordinata per probabilità
                in maniera decrescente
            list2 (list): lista di scenari ordinata per probabilità
                in maniera decrescente

            Returns:
            list: lista fusione di list1 e list2 ordinata per
                probabilità in maniera decrecente
                
        """
        p_l1 = 0
        p_l2 = 0

        p1 = -1
        p2 = -1

        res = []

        if p_l1 < len(list1):
            p1 = self.calculate_probability(list1[p_l1])
        if p_l2 < len(list2):
            p2 = self.calculate_probability(list2[p_l2])

        for i in range(0,len(list1 + list2)):
            if p1 >= p2:
                res.append(list1[p_l1])
                p_l1 = p_l1 + 1
                if p_l1 < len(list1):
                    p1 = self.calculate_probability(list1[p_l1])
                else:
                    p1 = -1
            else:
                res.append(list2[p_l2])
                p_l2 = p_l2 + 1
                if p_l2 < len(list2):
                    p2 = self.calculate_probability(list2[p_l2])
                else:
                    p2 = -1
        
        return res



    def generateNextScenario(self,bits,pos):
        """Funzione generateNextScenario:

            Parametri:
            bits ([int]): lista opzioni per generare uno
                scenario
            pos (int): posizione della lista fin dove
                siamo arrivati nel generare scenari

            Returns:
            list: lista degli scenari consistenti
                
        """
        if pos > len(bits)-1:
            return [bits]

        if bits[pos] != -1:
            n = self.scenario_nodes[pos]
            bits_2 = [x for x in bits]
            
            y = 0
            f = True  
            
            tot_sum = self.my_sum(n,bits,pos)
            if tot_sum > 1:
                f = False

            for k in self.scenario_nodes:
                if f:
                    f = f and self.update(n,bits_2[pos],k,y,bits_2)
                y = y + 1
            
            if f:
                return self.generateNextScenario(bits_2,pos+1)
            else:
                return []

        else:
            n = self.scenario_nodes[pos]
            bits_0 = [x for x in bits]
            bits_1 = [x for x in bits]
            bits_0[pos] = 0
            bits_1[pos] = 1

            bits_a = []
            bits_b = []

            y = 0
            f = True

            tot_sum = self.my_sum(n,bits_0,pos)
            if tot_sum > 1:
                f = False                


            for k in self.scenario_nodes:
                if f:
                    f = f and self.update(n,bits_0[pos],k,y,bits_0)
                y = y + 1

            if f:
                bits_a = self.generateNextScenario(bits_0,pos+1)

            y = 0
            f = True

            tot_sum = self.my_sum(n,bits_1,pos)
            if tot_sum > 1:
                f = False

            for k in self.scenario_nodes:
                if f:
                    f = f and self.update(n,bits_1[pos],k,y,bits_1)
                y = y + 1

            if f:
                bits_b = self.generateNextScenario(bits_1,pos+1)
        
            res = self.merge(bits_a,bits_b)
            return res