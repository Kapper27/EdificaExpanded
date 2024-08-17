
from owlready2 import *
from ConceptScenarioBuilder import *

sys.path.insert(0, '../')
from UtilityInterfaces import *

class BaseGoalSolver(GoalSolver):

    ontology_format = "owlready2 ontology"
    tipicality_format = "dict"
    candidate_format = "set of concepts"

    def __init__(self,ontology_path,tipicalities,ontology_checker_type,ontology_format,tipicality_format,candidate_builder):
        """Costruttore:

            Parametri:
            ontology_path (str): percorso in cui troviamo la
                ontologia su cui agire
            tipicalities (dict): struttura dati
                in cui sono memorizzate le tipicalità
            ontology_checker_type (OntologyChecker): il
                tipo di ontology checker utilizzato per controllare
                le inferenze
            ontology_format (str): il formato con cui è espressa
                la ontologia
            tipicality_format (str): il formato con cui sono espressi
                gli assiomi di tipicalità
            candidate_builder: il costruttore di candidati, da cui
                prendiamo i candidati per risolvere il goal.
            
            Returns:
            BaseGoalSolver: il costruttore genera
                un GoalSolver il cui compito è quello 
                di, dato un goal e un gruppo di concetti,
                agire per fondere tali concetti

        """

       
        self.csb = ConceptScenarioBuilder(tipicalities,ontology_path,ontology_checker_type,ontology_format,tipicality_format)
        self.inconsistents = set()
        self.to_show = dict()   #visualizzazione: la chiave è la congiunzione di concetti e il valore sono gli scenari VERIFICATI
        self.candidate_builder = candidate_builder

        if ontology_format != self.ontology_format:
            raise Exception("Ontology format mistmatch in Goal Solver!")
        if tipicality_format != self.tipicality_format:
            raise Exception("Tipicalities format mistmatch in Goal Solver!")
        if candidate_builder.candidate_format != self.candidate_format:
            raise Exception("Candidate format mistmatch in Goal Solver!")
        if ontology_format != ontology_checker_type.ontology_format:
            raise Exception("Ontology format mistmatch in Ontology Checker!")
        if tipicality_format != ontology_checker_type.tipicalities_format:
            raise Exception("Tipicalities format mistmatch in Ontology Checker!")

   
    
    def resolve(self,concepts,goal):
        """Funzione resolve:

            Parametri:
            concepts ([ThingClass]): lista di concetti
                da combinare per trovare una soluzione
            
            Returns:
            ([ThingClass],[(ThingClass, True | False)] | None: 
                dati i concetti in input tenta di combinare tali concetti e di 
                ottenere un concetto combinato. Se tale
                concetto è ottenuto si restituisce una coppia:
                    - il primo elemento è la lista di concetti fusi
                    - il secondo elemento è la lista delle sue
                        caratteristiche tipiche: ogni caratteristica
                        è una coppia (Concetto_corpo, valore_verita')
                Se la fusione fallisce si restituisce None

        """
        expr = And(concepts + [goal])
        if expr in self.inconsistents:
            return None
        
        k = self.candidate_builder.search_expression(expr)
        if k == None:
            self.inconsistents.add(expr)
            return None
        else:
            self.csb.setConcepts(concepts)
            #self.csb.setGoal(goal)
            res = self.csb.combine_n_concepts_gocciola1_0()

            self.to_show[And(concepts)] = self.csb.scenarios
                    
            if res == None:
                self.inconsistents.add(expr)
            return res
        