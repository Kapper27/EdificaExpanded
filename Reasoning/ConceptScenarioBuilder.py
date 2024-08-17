from consistency_checker3 import *
from ScenarioManager import *

sys.path.insert(0, '../')
from BaseOntologyChecker import *

class ConceptScenarioBuilder:


    def __init__(self,tipicalities,ontology_path,ontology_checker_type,ontology_format,tipicalities_format):
        """Costruttore:

            Parametri:
            tipicalities (dict): struttura dati in cui
                abbiamo memorizzato le tipicalità
            ontology_path (str): percorso in cui trovare la    
                ontologia da utilizzare
            ontology_checker_type (OntologyChecker): il tipo
                di ontology checker che verrà utilizzato per verificare
                che i concetti fusione siano consistenti
            ontology_format (str): stringa che rappresenta il formato
                in cui è rappresentata l'ontologia
            tipicalities_format (str): stringa che rappresenta
                il formato in cui sono rappresentati gli assiomi di 
                tipicalità
            
            Returns:
            ConceptScenarioBuilder: viene generato 
                un gestore di scenari per un concetto
                fusione dati una serie di concetti da fondere

        """
        self.tipicalities = tipicalities
        self.ontology_path = ontology_path
        self.oc_type = ontology_checker_type 
        self.ontology_format = ontology_format
        self.tipicalities_format = tipicalities_format
        self.world = World()
        self.ontology = self.world.get_ontology(self.ontology_path).load()
        self.scenarios = [] #per la visualizzazione: lista degli scenari testati
        
        
        
    def setGoal(self,goal):
        """Funzione setGoal:
        
            Parametri:
            goal (ThingClass | Or | And | Restriction | Not): il goal
                da risolvere

            Returns:
            None: viene impostato come goal il goal passato come parametro
        """
        self.goal = goal



    def setConcepts(self,concepts):
        """Funzione setConcepts:

            Parametri:
            concepts ([ThingClass]): lista di concetti
                da combinare per trovare una soluzione
            
            Returns:
            void: memorizza al proprio interno i concetti

        """
        self.concepts = [self.ontology[x.name] for x in concepts if x != owl.Thing ]
    


    def __buildBestScenario(self,un_ordered_scenario):
        """Funzione __buildBestScenario:

            Parametri:
            un_ordered_scenario ([(ThingClass,True|False,float)]): 
                lista di triple che rappresentano assiomi di
                tipicalità. Il primo elemento della tripla è 
                il corpo dell'assioma di tipicalità.
                Il secondo elemento è se tale assioma è vero o falso.
                Il terzo elemento è la probabilità con cui tale
                assioma è vero o falso
            
            Returns:
            [(ThingClass,True|False,float)]: lista di triple ordinate
                per probabilità. Tale ordinamento è fatto
                sulla versione della tripla con il valore di verità più probabile.
                Per ogni tripla si prende la configurazione
                con il valore di verità più probabile e poi si ordina
                in base ad esso

        """
        ok = {}
        for (a,b,c) in [(a,b,c) for (a,b,c) in un_ordered_scenario]:
            if a in ok.keys():
                if b == True:
                    ok[a].append(float(c))
                else:
                    ok[a].append(1-float(c))
            else:
                if b == True:
                    ok[a] = [float(c)]
                else:
                    ok[a] = [1-float(c)]
        
        for k in ok.keys():
            ok[k] = min(ok[k])

        alls = [(a,True,c) for (a,c) in ok.items()]
        corrects = [(a,b,c) for (a,b,c) in alls if c >= 0.5]
        reverseds = [(a,not b,1-c) for (a,b,c) in alls if c < 0.5]

        alls = corrects + reverseds
        bs = sorted(alls, key=lambda x: x[2], reverse=True)
        return bs


    def visualizeConsistencyGraph(self,consistency_graph):
        """Funzione visualizeConsistencyGraph:

            Parametri:
            consistency_graph (TreeNode): grafo di consistenze 
                ottenuto dall'analisi delle consistenze tra
                concetti
            
            Returns:
            void: la seguente funzione salva su un file html 
                il grafo risultante

        """
        from pyvis import network

        net = network.Network(height="750px", width = "1500px", notebook=True, directed=True,cdn_resources= "in_line" )            

        for k in consistency_graph.keys():
                net.add_node(str(k), label=str(k), title = str(consistency_graph[k]))

        for k in consistency_graph.keys():
            for p in consistency_graph[k].parent:
                net.add_edge(str(k), p.name) #, physics=False)

        net.toggle_physics(True)

        # Ottieni il contenuto HTML
        html_content = net.generate_html()

        # Scrivi il contenuto nel file finale con la codifica UTF-8
        with open('./Temp/consistency_graph.html', 'w', encoding='utf-8') as f:
            f.write(html_content)

    
    def select(self,to_do,option):
        """Funzione select:

            Parametri:
            to_do ([(ThingClass, True|False)]): scenario 
                del concetto fusione da controllare
            option(int): posizione all'interno della
                lista di concetti da fondere del concetto
                ritenuto più importante degli altri
            
            Returns:
            void: la seguente funzione restituisce True
                se lo scenario è non banale, oppure False
                altrimenti. Per scenario non banale 
                intendiamo uno scenario in cui almeno
                un elemento dello scenario è False e in cui
                almeno uno degli dello scenario riferiti
                al concetto di posizione specificata da
                option è False

        """

        the_scenario_is_all_true = True
        for c in self.concepts:
            name = "T(" + c.name + ")"
            if name in self.tipicalities.keys():
                for x in self.tipicalities[name]:
                    if (self.ontology[x],False) in to_do:
                        the_scenario_is_all_true = False

        print("\tARE ALL THE SCENARIO ELEMENTS TRUE?:",the_scenario_is_all_true)

        if not the_scenario_is_all_true:
            the_head_is_all_true = True
            c = self.concepts[option]
            ops = False
            name = "T(" + c.name + ")"
            if name in self.tipicalities.keys():
                for x in self.tipicalities[name]:
                    if (self.ontology[x],False) in to_do:
                        the_head_is_all_true = False
            print("\tARE ALL THE SCENARIO ELEMENTS OF THE HEAD TRUE?:",the_head_is_all_true)
            return not the_head_is_all_true 
        else:
            return not the_scenario_is_all_true

    def convert(self,to_solve,onto):

        if isinstance(to_solve,ThingClass):
            return onto[to_solve.name]
        if isinstance(to_solve,And):
            return And([self.convert(x,onto) for x in to_solve.Classes])
        if isinstance(to_solve,Or):
            return Or([self.convert(x,onto) for x in to_solve.Classes])
        if isinstance(to_solve,Not):
            return Not(self.convert(to_solve.Class,onto))
        if isinstance(to_solve,Restriction):
            if to_solve.type == SOME:
                return onto[to_solve.property.name].some(self.convert(res,onto))
            else:
                return onto[to_solve.property.name].only(self.convert(res,onto))

    def combine_n_concepts_gocciola1_0(self):
        """Funzione combine_n_concepts:

            Parametri:
            
            Returns:
            ThingClass | None | ([ThingClass],[(ThingClass,True|False)]):

            # CHECK
                la seguente funzione restituisce la combinazione di n concetti
                presenti nel ConceptScenarioBuilder. I risultati possibili 
                sono tre:
                - None: la lista di concetti da combinare è vuota oppure
                    è costituita di un solo concetto oppure
                    sono presenti N concetti da combinare e si costruiscono
                    gli scenari possibili non banali, ma nessuno di questi è consistente,
                    dunque si restituisce None
                - coppia: il primo elemento è la lista dei concetti che vanno
                    a generare il concetto fusione. Il secondo elemento è 
                    una lista che rappresenta lo scenario più probabile consistente
                    trovato. Uno scenario è una lista di coppie in cui il primo 
                    elemento è una classe, che rappresenta il corpo dell'assioma di
                    tipicalità, mentre il secondo elemento rappresenta il valore
                    di verità dell'assioma di tipicalità

        """
        if len(self.concepts) == 1:
            return None
        elif len(self.concepts) == 0:
            return None
        else:

            # PRIMO PASSO: costruzione del grafo delle consistenze

            print("BUILDING CONSISTENCY GRAPH FOR ", self.concepts)
            every_concept = {}
            for c in self.concepts:
                k = "T(" + str(c).split(".")[-1] + ")"
                if k in self.tipicalities.keys():
                    c1s = self.tipicalities[k].keys()
                    every_concept[c]=c1s
            
            if every_concept.keys() != []:
                initialize()
                for (a,b) in [(c1,c2) for c1 in self.concepts for c2 in self.concepts if str(c1) != str(c2) and self.concepts.index(c1)<self.concepts.index(c2)]:  
                    # se la coppia è presente tra le tipicalità la risolvo
                    if a in every_concept.keys() and b in every_concept.keys():
                        c1s = every_concept[a]
                        c2s = every_concept[b]
                        for x in c1s:
                            for y in c2s:
                                print("VISITO:",self.ontology[x] if x != owl.Thing else owl.Thing,self.ontology[y])
                                explore_max(self.ontology[x] if x != owl.Thing else owl.Thing,self.ontology[y] if y != owl.Thing else owl.Thing,set())
                        clean()
                    # se ho solo uno dei due, considero Thing per l'altro giusto per avere un placeholder
                    elif a in every_concept.keys():
                        c1s = every_concept[a]
                        c2s = [Thing]
                        for x in c1s:
                            for y in c2s:
                                print("VISITO:",self.ontology[x], y)
                                explore_max(self.ontology[x] if x != owl.Thing else owl.Thing,y,set())
                        clean()
                    elif b in every_concept.keys():
                        c1s = every_concept[b]
                        c2s = [Thing]
                        for x in c1s:
                            for y in c2s:
                                print("VISITO:",self.ontology[x], y)
                                explore_max(self.ontology[x] if x != owl.Thing else owl.Thing,y,set())
                        clean()
                
            cg = getConsistencyGraph()
            print("CONSISTENCY GRAPH:",cg)
            self.visualizeConsistencyGraph(cg)


            # SECONDO PASSO: COSTRUIAMO GLI SCENARI CONSISTENTI E LI CONTROLLIAMO                 
            for option in range(0,len(self.concepts)):
                self.scenarios = []
                s = []
                for x in self.concepts:
                    name = "T(" + str(x).split(".")[-1] + ")"
                    if name in self.tipicalities.keys():
                        triple_x = [(self.ontology[k],True,float(self.tipicalities[name][k])) for k in self.tipicalities[name].keys()]
                        s = s + triple_x

                best_scenario = self.__buildBestScenario(s)
                sm = ScenarioManager(best_scenario,cg)
                start = [-1 for x in best_scenario]

                print("GENERATING SCENARIOS FOR ", self.concepts)
                consistent_scenarios = sm.generateNextScenario(start,0)

                probs = []
                for cs in consistent_scenarios:
                    probs.append(sm.calculate_probability(cs))
                is_sorted = all(a >= b for a, b in zip(probs, probs[1:]))
                print("\tARE THE SCENARIOS GENERATE ORDERED FOR DECREASING PROBABILITY? ",is_sorted)
                print("\tNUMBER OF CONSISTENT SCENARIOS: ",len(consistent_scenarios))
                print("\n")
                j = 0

                
                for cs in consistent_scenarios:
                    to_do = []
                    i = 0
                    
                    for val in cs:
                        if val == 0:
                            to_do.append((best_scenario[i][0],best_scenario[i][1])) #best_scenario ha il valore di verità più probabile
                        else:
                            to_do.append((best_scenario[i][0],not best_scenario[i][1]))
                        i = i + 1

                    print("SCENARIO TO ANALYZE:",to_do,probs[j],len(to_do))
                    j = j + 1
                    not_easy = True
                    not_easy = self.select(to_do,option)

                    self.scenarios.append(to_do) #aggiungo solo gli scenari che verifichiamo.
                    print("\tAGGIUNGIAMO", to_do)
                    
                    if not_easy:
                        world_copy = World()
                        onto_copy = world_copy.get_ontology(self.ontology_path).load()
                        concepts_copy = [onto_copy[x.name] for x in self.concepts]
                        to_do_copy = [(onto_copy[a.name],b) for (a,b) in to_do]
                        #goal_copy = self.convert(self.goal,onto_copy)
                    
                        # COMPIO LE MODIFICHE SULL'ONTOLOGIA TRAMITE UNA SUA COPIA
                        self.oc = self.oc_type(onto_copy,world_copy,self.tipicalities, self.ontology_format, self.tipicalities_format)
                        k = self.oc.check_new_concept_consistency(to_do_copy,concepts_copy)#,goal_copy)
                        if not k:
                            print("\tTHE SCENARIO IS NOT CONSISTENT")
                        else:
                            print("\tTHE SCENARIO IS CONSISTENT")
                            return (concepts_copy , to_do_copy) 
                    else:
                        print("\t\tTHE SCENARIO IS DISCARDED BECAUSE TRIVIAL")
            return None
