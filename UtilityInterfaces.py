class KnowledgeBaseBuilder:

    structure_of_file = "-"
    format_read = "-"
    ontology_format = None
    
    def __init__(self, parser, ontology_path = 'knowledge_base', path = 'knowledge_base') : 
        pass

    def getOntology(self):
        pass

    def getWorld(self):
        pass

    def buildKnowledgeBase(self):
        pass

    def getOntologyFormat(self):
        pass


class TipicalityBuilder:

    structure_of_file = "-"
    format_read = "-"
    tipicality_format = None
    
    def __init__(self, parser, path = 'tipicality_base') : 
        pass

    def getTipicalities(self):
        pass

    def getTipicalityFormat(self):
        pass
    
    def buildTipicalities(self):
        pass

class GoalBuilder:

    structure_of_file = "-"
    format_read = "-"
    goals_format = None
    
    def __init__(self, parser, path = 'goal') : 
        pass

    def getGoals(self):
        pass

    def buildGoals(self):
        pass


class DefinedParser:

    format_read = "-"

    def parse(self,text):
        pass

class CandidateBuilder:

    ontology_format = "-"
    tipicalities_format = "-"
    candidate_format = "-"
    

    def goal_transformation(self,goal):
        pass


class GoalSolver:

    ontology_format = "-"
    tipicality_format = "-"
    candidate_format = "-"

    def resolve(self,concepts):
        pass

class OntologyChecker:
    
    ontology_format = "-"
    tipicalities_format = "-"

    def __init__(self,ontology,world,tipicalities, ontology_format, tipicalities_format):
        pass


    def check_ontology_consistency(self):
        pass

    def check_tipicalities_consistency(self):
        pass

    
    def check_new_concept_consistency(self,tipical_attrs,cs):
        pass

    def check_single_class(self,single_class,expr):
        pass

       
class CandidateChooser:

    candidate_format = "-"

    def create_order(self):
        pass

        