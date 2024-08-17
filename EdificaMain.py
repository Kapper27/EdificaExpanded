import sys
sys.path.append('./Input/')
sys.path.append('./Reasoning/')


from UtilityInterfaces import *
from KnowledgeBaseBuilderManchester import *
from ManchesterParser import *
from BaseTipicalityBuilder import *
from BaseOntologyChecker import *
from BaseGoalBuilder import *

from BaseCandidateBuilder import *
from BaseGoalSolver import *
from ComplexCandidateChooser import *




class Edifica: 

    def setKnowledgeBaseBuilder(self, kb_builder,parser_kb,ontology_name = 'knowledge_base', file_path = './knowledge_base'):
        print("\tREADING KNOWLEDGE BASE...")
        self.knowledge_base_builder = kb_builder(parser_kb,ontology_name,file_path)
        self.knowledge_base_builder.buildKnowledgeBase()
        self.ontology = self.knowledge_base_builder.getOntology()
        self.world = self.knowledge_base_builder.getWorld()
        self.ontology_format = self.knowledge_base_builder.getOntologyFormat()
        #self.ontology.save(file = "./Temp/ontology.owl", format = "rdfxml") # per la visualizzazione
        print("\tDONE\n")



    def setTipicalityBaseBuilder(self, tb_builder,parser_tb,tipicality_path = './tipicality_base'):
        print("\tREADING TIPICALITY BASE...")
        self.tipicality_builder = tb_builder(parser_tb,tipicality_path)
        self.tipicality_builder.buildTipicalities()
        self.tipicalities = self.tipicality_builder.getTipicalities()
        self.tipicalities_format = self.tipicality_builder.getTipicalityFormat()
        print("\tDONE\n")

    
    def checkConsistency(self,ontology_checker):
        self.oc = ontology_checker(self.ontology,self.world,self.tipicalities, self.ontology_format, self.tipicalities_format)
        print("\tCHECKING CONSISTENCY OF KNOWLEDGE BASE")
        if not self.oc.check_ontology_consistency():
            raise Exception("Ontology is inconsistent")
        print("\tDONE\n")
        print("\tCHECKING CONSISTENCY OF KNOWLEDGE BASE + TIPICALITY AXIOMS")
        if not self.oc.check_tipicalities_consistency():
            raise Exception("Ontology + tipicality axioms are inconsistent")
        self.ontology.save(file = "./Temp/onto.owl", format = "rdfxml")
        print("\tDONE\n")

    
    
    def setGoal(self,goal_builder,parser,goal_path='goal'):
        print("\tREADING GOALS...")
        self.goal_builder = goal_builder(parser,self.ontology,goal_path)
        self.goal_builder.buildGoals()
        print("\tDONE\n")

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
    
    def resolve_goal(self,ontology_checker):
        solution = None
        to_solve = None
        self.to_show = dict()

        while(solution == None):
            
            to_solve = self.goal_builder.getGoals()
            if to_solve == None:
                return None

            index = to_solve
            
            w = World()
            onto = w.get_ontology("./Temp/onto.owl",).load()
                        
            self.candidate_builder = BaseCandidateBuilder("./Temp/onto.owl",self.tipicalities,self.knowledge_base_builder.ontology_format, self.tipicality_builder.tipicality_format)
            
            self.goal_solver = BaseGoalSolver("./Temp/onto.owl",self.tipicalities,ontology_checker,self.knowledge_base_builder.ontology_format, self.tipicality_builder.tipicality_format,self.candidate_builder)
            
            to_solve = self.convert(to_solve,onto) 
            candidates = self.candidate_builder.goal_transformation(to_solve)
                    
            if candidates == None:
                print("IMPOSSIBILE COMBINARE DUE CLASSI CHE GENERANO INCONSISTENZA")
            else:
                candidates = sorted(candidates,key=lambda x: len(x.getCombination()))
                print("ALL CANDIDATES AVAILABLE:",[x.getCombination() for x in candidates])

                self.to_show[index] = [c.getCombination() for c in candidates]  #prendo tutti i candidati
                self.to_show[index] = [[onto[a.name] if a != owl.Thing else owl.Thing for a in x] for x in self.to_show[index]] #e li metto in onto

                thing_candidates = [onto[x.getCombination()[0].name] for x in candidates if len(x.getCombination()) == 1 and x.getCombination()[0] != owl.Thing] 
                thing_candidates = thing_candidates + [owl.Thing for x in candidates if len(x.getCombination()) == 1 and x.getCombination()[0] == owl.Thing] 
                result = None
                i = 0
                print(thing_candidates)
                while result == None and i < len(thing_candidates):
                    w_one = World()
                    onto_one = w_one.get_ontology("./Temp/onto.owl",).load()
                    onto_c = ontology_checker(onto_one,w_one,self.tipicalities, self.knowledge_base_builder.ontology_format, self.tipicality_builder.tipicality_format)
                    if thing_candidates[i] == owl.Thing:
                        result = thing_candidates[i]
                    elif onto_c.check_single_class(onto[thing_candidates[i].name],to_solve):
                        result = thing_candidates[i]
                    i = i + 1

                solution = result
                print("SOLUTION FOUND FOR SIMPLE CANDIDATES",solution)
                
                if solution == None:
                    complex_goals = [x.getCombination() for x in candidates if x not in thing_candidates]
                    complex_goals = [[onto[x.name] if x != owl.Thing else owl.Thing for x in c] for c in complex_goals]
                    # complex_goals = complex_goals + [[onto["C"], onto["C"]]]
                    # complex_goals = complex_goals + [[onto["B"],onto["A"]]] 
                    cgc = ComplexCandidateChooser(self.tipicalities,complex_goals, self.tipicality_builder.tipicality_format)
                    complex_goals = cgc.create_order()
                    #complex_goals = [[owl.Thing, onto["Stump"]]] + complex_goals # per osservare a quali conclusioni arriva il mio gocciola con gli stessi concetti da combinare
                    #complex_goals = [[onto["Metal"], onto["Wood"]]] + complex_goals
                    #complex_goals = [[onto["Hairband"], onto["Stump"]]] + complex_goals
                    #complex_goals = [[onto["Hammer"], onto["Stone"],onto["Stump"]]] + complex_goals
                    #complex_goals = [[onto["Metal"], onto["Stump"]]] + complex_goals
                    #complex_goals = [[onto["Shelf"], onto["Stump"]]] + complex_goals
                    
                    print("TRYING COMPLEX GOALS")
                    simple_candidates_remaining = cgc.get_simple_candidates() #[onto["Metal"]] + cgc.simple_goals

                    self.to_show[index] = cgc.get_simple_candidates() + complex_goals # se non trovo candidati semplici, allora cerco di crearmene e ci metto quelli complessi

                    i = 0
                    result = None
                    while result == None and i < len(simple_candidates_remaining):
                        w_one = World()
                        onto_one = w_one.get_ontology("./Temp/onto.owl",).load()
                        onto_c = ontology_checker(onto_one,w_one,self.tipicalities, self.knowledge_base_builder.ontology_format, self.tipicality_builder.tipicality_format)
                        sg = onto_one[simple_candidates_remaining[i][0].name] if simple_candidates_remaining[i][0] != owl.Thing else owl.Thing
                        if onto_c.check_single_class(sg,self.convert(to_solve,onto_one)):
                            result = simple_candidates_remaining[i][0]
                        i = i + 1

                    solution = result

                    print("SOLUTION FOUND FOR SIMPLE CANDIDATES GENERATED FROM COMPLEX GOALS SEMPLIFICATION",solution)
                    if solution != None:
                        tips = []
                        if solution != owl.Thing and "T(" + solution.name + ")" in self.tipicalities.keys():
                            for (a,b) in self.tipicalities["T(" + solution.name + ")"].items():
                                if float(b) >= 0.5:
                                    tips.append((a,True))
                                else:
                                    tips.append((a,False))
                        if solution != owl.Thing:
                            return (to_solve,[onto[solution.name]],tips)
                        else:
                            return (to_solve,[owl.Thing],tips)
                    
                    print("PROCESSING COMPLEX GOALS")
                    
                    
                    i = 0
                    result = None
                    while result == None and i < len(complex_goals):
                        result = self.goal_solver.resolve(complex_goals[i],to_solve)
                        i = i + 1
                    
                    if result != None:
                        print("RESULT:",result)
                        solution = [onto[x.name] for x in result[0]] 
                        tips = result[1]
                        if "T(" + solution[0].name + ")" in self.tipicalities.keys():
                            for (a,b) in self.tipicalities["T(" + solution[0].name + ")"].items():
                                if float(b) >= 0.5:
                                    tips.append((a,True))
                                else:
                                    tips.append((a,False))

                        return (to_solve,complex_goals[i-1],tips)

                else:
                    tips = []
                    if "T(" + solution.name + ")" in self.tipicalities.keys():
                        for (a,b) in self.tipicalities["T(" + solution.name + ")"].items():
                            if float(b) >= 0.5:
                                tips.append((a,True))
                            else:
                                tips.append((a,False))
                    if solution != owl.Thing:
                        return (to_solve,[onto[solution.name]],tips)
                    else:
                        return (to_solve,[owl.Thing],tips)               
        return None        
                    



    def __init__(self):
        print("STARTING EDIFICA")  
        self.to_show = dict()    #per la visualizzazione. Come chiave abbiamo il goal da risolvere, sia esso quello originale o quello indebolito, mentre come valore i candidati

if __name__ == "__main__":
    g = Edifica()
    g.setKnowledgeBaseBuilder(KnowledgeBaseBuilderManchester, ManchesterParser, file_path="Files/knowledge_base")
    g.setTipicalityBaseBuilder(BaseTipicalityBuilder, None, tipicality_path="Files/tipicality_base")
    g.checkConsistency(BaseOntologyChecker)
    g.setGoal(BaseGoalBuilder, ManchesterParser, goal_path="Files/goal")
    res = g.resolve_goal(BaseOntologyChecker)
    if res == None:
        print("IMPOSSIBILE RISOLVERE IL GOAL")
    else:
        goal = res[0]
        solution = res[1]
        tips = res[2]
        print("GOAL RISOLTO:", goal)
        print("CONCETTI FUSI:", solution)
        print("CARATTERISTICHE TIPICHE DEL CONCETTO FUSIONE:", tips)

            



# g = Edifica()
# g.setKnowledgeBaseBuilder(KnowledgeBaseBuilderManchester,ManchesterParser,file_path="Files/knowledge_base")
# g.setTipicalityBaseBuilder(BaseTipicalityBuilder, None,tipicality_path="Files/tipicality_base")
# g.checkConsistency(BaseOntologyChecker)
# g.setGoal(BaseGoalBuilder,ManchesterParser,goal_path="Files/goal")
# res = g.resolve_goal(BaseOntologyChecker)
# if res == None:
#     print("IMPOSSIBILE RISOLVERE IL GOAL")
# else:
#     goal = res[0]
#     solution = res[1] 
#     tips = res[2]
#     print("GOAL RISOLTO:",goal)
#     print("CONCETTI FUSI:",solution)
#     print("CARATTERISTICHE TIPICHE DEL CONCETTO FUSIONE:",tips)


