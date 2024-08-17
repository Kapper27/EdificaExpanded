from owlready2 import *

sys.path.insert(0, '../')
from UtilityInterfaces import *

class MyCombination:

    def __init__(self):
        """Costruttore:

            Parametri:
            
            Returns:
            MyCombination: il costruttore genera
                una combinazione di concetti,
                ovvero una lista di concetti

        """
        self.combination = []
    


    def addElement(self,el):
        """Funzione addElement:

            Parametri:
            el (ThingClass): concetto da aggiungere
                alla combinazione
            
            Returns:
            None: la seguente funzione aggiunge il
                concetto alla combinazione

        """
        if el.name not in [z.name for z in self.combination]:
            self.combination.append(el)
        



    def getCombination(self):
        """Funzione getCombination:

            Parametri:
            
            Returns:
            GoalNode: la seguente funzione restituisce 
                la combinazione di concetti

        """
        return self.combination



    def addElements(self,els):
        """Funzione addElements:

            Parametri:
            els([ThingClass]): serie di concetti da 
                aggiungere alla combinazione
            
            Returns:
            None: la seguente funzione aggiunge una serie
                di concetti alla combinazione

        """
        for e in els:
            if e.name not in [z.name for z in self.combination]:
                self.combination.append(e)

    def __str__(self):
        """Funzione __str__:

            Parametri:
            
            Returns:
            str: la seguente funzione produce
                una stringa che rappresenta 
                l'oggetto corrente

        """
        return str(list(set(self.combination))) #di troppo?

class BaseCandidateBuilder(CandidateBuilder):

    ontology_format = "owlready2 ontology"
    tipicality_format = "dict"
    candidate_format = "set of concepts"


    def __init__(self,ontology_path,tipicalities,ontology_format,tipicality_format):
        """Costruttore:

            Parametri:
            ontology_path (str): percorso in cui si trova la ontologia su cui
                fare ragionamento automatico. Si utilizza il percorso per caricare
                di volta in volta la ontologia originale in quanto il ragionamento
                automatico in owlready2 va a "sporcare" la ontologia inserendone
                le inferenze all'interno
            tipicaliteis (dict): gli assiomi di tipicalità
            ontology_format (str): stringa che rappresenta il formato
                dell'ontologia
            tipicality_format (str): stringa che rappresenta il formato
                degli assiomi di tipicalità
            
            Returns:
            BaseCandidateBuilder: il costruttore restitusice un creatore di candidati,
                ovvero un oggetto che, preso un goal, restituisce una lista di candidati
                che possono potenzialmente risolverlo. Un candidato è una lista di 
                concetti della ontologia

        """
        self.ontology_path = ontology_path
        self.tipicalities = tipicalities
        if ontology_format != self.ontology_format:
            raise Exception("Ontology format mistmatch in Candidate Builder!")
        if tipicality_format != self.tipicality_format:
            raise Exception("Tipicalities format mistmatch in Candidate Builder!")

        self.to_viz = dict()
        


   
    def search_expression(self,expression):
        """Funzione serch_expression:

            Parametri:
            expression (ThingClass | Or | Restriction | And | Not): 
                la espressione in input da cui cerchiamo le
                classi equivalenti o le sottoclassi
            
            Returns:
            [ThingClass]: data la espressione in input
                restituisce una lista di classi di owlready2
                che sono equivalenti o sottoclasse di tale
                espressione

        """
        print("SEARCHING EXPRESSION ",expression)
        name = "temp_0"
        self.world = World()
        self.ontology = self.world.get_ontology(self.ontology_path,).load()
        with self.ontology :
            new_class = types.new_class(name, (Thing,))
            new_class.equivalent_to.append(expression)
        try :
            with self.ontology:
                sync_reasoner(self.world)
        except subprocess.CalledProcessError as inst :
            return None
        except :
            return None
        
        print("\tINCONSISTENCIES FOUND:",list(self.world.inconsistent_classes()))
        if list(self.world.inconsistent_classes()) != []:
            self.ontology[name].equivalent_to = []
            return None
        else:
            res = [x for x in self.ontology[name].descendants() if isinstance(x,ThingClass) and x != self.ontology[name] and "temp" not in str(x) and "_" not in x.name] # se ci sono delle classi dovute all'assioma di tipicalità, le tolgo
            to_add = set()
            print("\t DESCENDENTS OF EXPRESSION:",res)
            for x in self.tipicalities.keys():
                if isinstance(expression,ThingClass) and str(expression.name) in [k.strip() for k in self.tipicalities[x].keys()]:
                    n = x[2:len(x)-1]
                    print("\t FOUND IN TIPICALITIES",n,x,self.ontology[n])
                    to_add.add(self.ontology[n])
                if isinstance(expression,Not) and isinstance(expression.Class,ThingClass) and str(expression.Class.name) in [k.strip() for k in self.tipicalities[x].keys()]:
                    n = x[2:len(x)-1]
                    print("\t FOUND IN TIPICALITIES WITH A NOT",n,x,self.ontology[n])
                    to_add.add(self.ontology[n])

            # sono sicuro che to_add sia univoco perchè è un set siamo a parità di ontologia, con ontologia diversa devo controllare io
            res = list(set(res).union(to_add))

            print("CONCEPTS FOUND FOR EXPRESSION :",expression,"\n\t",res)
            return res


    def delete_copies(self,candidates):
        """Funzione delete_copies:

            Parametri:
            candidates ([MyCombination]): 
                una lista di combinazioni di concetti,
                in cui delle combinazioni potrebbero
                essere ripetute
            
            Returns:
            [MyCombination]: data la lista di combinazioni
                in input, si va a generare una lista di
                combinazioni che non sono ripetute

        """
        found = []
        for x in candidates:
            tot = True
            for comb in found:
                new = False
                for k in x.getCombination():
                    if k.name not in [z.name for z in comb]:
                        #k.name sarebbe, per onto.B -> "B"
                        new = True
                tot = tot and new
            if tot == True:
                found.append(x.getCombination())

        print("INITIAL CANDIDATES:",[x.getCombination() for x in candidates])
        print("CANDIDATES WITHOUT DUPLICATES:",found)
                
        res = []
        for f in found:
            r = MyCombination()
            r.addElements(list(f))
            res.append(r)
        return res


    def goal_transformation(self,goal):
        """Funzione goal_transformation:

            Parametri:
            goal (ThingClass | Or | Restriction | And | Not): il
                goal in formato owlready2 da tradurre in 
                concetti singoli o combinazioni di concetti 
            
            Returns:
            [MyCombination]: dato il goal 
                restituisce una lista di combinazioni 
                di concetti

        """
        if isinstance(goal,ThingClass):
            res = []
            classes = self.search_expression(goal)
            if classes != None:
                for x in classes:
                    k = MyCombination()
                    k.addElement(x)
                    res.append(k)
            else:
                return None
            self.to_viz[goal] = res
            return res

        elif isinstance(goal,Or):
            res = [] # volendo potrei cercare anche con la or di search_expression, ma posso tenerla così
            for x in goal.Classes:
                candidates = self.goal_transformation(x)
                if candidates != None:
                    res = res + candidates
            res = self.delete_copies(res)
            if res == []:
                return None
            self.to_viz[goal] = res
            return res

        elif isinstance(goal,Restriction):
            classes = self.search_expression(goal)
            res_p = []
            if classes != None:
                for x in classes:
                    k = MyCombination()
                    k.addElement(x)
                    res_p.append(k)
                k = MyCombination()
                k.addElements(goal.property.domain)
                res_p.append(k)
                res_p = self.delete_copies(res_p)
            else:
                return None
                
            self.to_viz[goal] = res_p
            return res_p

        elif isinstance(goal,Not):
            classes = self.search_expression(goal)
            res_p = []
            if classes != None:
                for x in classes:
                    k = MyCombination()
                    k.addElement(x)
                    res_p.append(k)
            else:
                return None
            
            if isinstance(goal.Class,And):
                z = []
                for x in goal.Class.Classes:
                    z.append(Not(x))
                equivalent_candidates = self.goal_transformation(Or(z)) 
                if equivalent_candidates != None: #in teoria essendo equivalenti, non dovrebbe mai capitare di essere None se quello di partenza non lo è
                    res_p = res_p + equivalent_candidates 
            
            elif isinstance(goal.Class,Or):
                z = []
                for x in goal.Class.Classes:
                    z.append(Not(x))
                equivalent_candidates = self.goal_transformation(And(z)) 
                if equivalent_candidates != None: 
                    res_p = res_p + equivalent_candidates 

            elif isinstance(goal.Class,Restriction):
                restr = goal.Class
                if restr.type == owlready2.SOME:
                    equivalent_candidates = self.goal_transformation(restr.property.only(Not(restr.value)))
                    if equivalent_candidates != None: 
                        res_p = res_p + equivalent_candidates
                elif restr.type == owlready2.ONLY:
                    equivalent_candidates = self.goal_transformation(restr.property.some(Not(restr.value)))
                    if equivalent_candidates != None: 
                        res_p = res_p + equivalent_candidates

            res_p = self.delete_copies(res_p)
            self.to_viz[goal] = res_p
            return res_p

        elif isinstance(goal,And):
            classes = self.search_expression(goal)
            res_p = []
            if classes != None:
                for x in classes:
                    k = MyCombination()
                    k.addElement(x)
                    res_p.append(k)
            else:
                return None
            
            res = []
            res.append(MyCombination())
            for x in goal.Classes:
                tmp_res = []
                child_candidates = self.goal_transformation(x)
                if child_candidates == None:
                    return None
                for j in res:
                    tmp = j
                    for k in child_candidates:
                        r = MyCombination()
                        r.addElements(tmp.getCombination() + k.getCombination())
                        tmp_res.append(r)
                res = tmp_res
            
            res = res_p + res
            res = self.delete_copies(res)

            self.to_viz[goal] = res
            return res
