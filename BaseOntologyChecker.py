import string
from owlready2 import *
from UtilityInterfaces import OntologyChecker

class BaseOntologyChecker(OntologyChecker):

    ontology_format = "owlready2 ontology"
    tipicalities_format = "dict"


    def __init__(self,ontology,world,tipicalities, ontology_format, tipicalities_format):
        """Costruttore:

            Parametri:
            ontology (Ontology): ontologia in formato
                owlready2
            world (World): mondo in cui l'ontologia
                è calata
            tipicalities (dict): struttura dati in cui
                abbiamo memorizzato le tipicalità
            ontology_format (str): il formato della ontologia
            tipicalities_format (str): il formato
                degli assiomi di tipicalità
            
            
            Returns:
            BaseOntologyChecker: viene generato 
                un checker di ontologia per controllare che 
                la ontologia con gli assiomi di tipicalità sia
                consistente e per controllare se l'aggiunta di 
                un concetto combinato mantenga consistente la
                ontologia

        """
        self.ontology = ontology
        self.world = world
        self.tipicalities = tipicalities
        if self.ontology_format != ontology_format:
            raise Exception("Ontology format not supported by Ontology Checker")
        if self.tipicalities_format != tipicalities_format:
            raise Exception("Tipicalities format not supported by Ontology Checker")

    
    
    def __create_class(self,name, parent = Thing) :
        """Funzione __create_class:

            Parametri:
            name (str): nome del nuovo concetto
            parent (ThingClass | Or | And | Not | Restriction):
                concetto genitore del nuovo concetto
            
            Returns:
            ThingClass: funzione che crea un nuovo concetto
                nella ontologia e la restituisce. Se il
                genitore non è una ThingClass, allora è
                aggiunto tra gli is_a della classe. Se la
                classe esiste già, aggiunge il genitore
                tra i suoi is_a e restituisce la classe
                già esistente

        """
        with self.ontology :
            if self.ontology[name] == None:
                if isinstance(parent,ThingClass):
                    new_class = types.new_class(name, (parent,))
                    return new_class
                else: 
                    new_class = types.new_class(name, (Thing,))
                    self.ontology[name].is_a.append(parent)
                    return self.ontology[name]
            else:
                self.ontology[name].is_a.append(parent)
                return self.ontology[name]



    def __create_property(self, name) :
        """Funzione __create_property:

            Parametri:
            name (str): nome della nuova proprietà
            
            Returns:
            ThingClass: funzione che crea una nuova proprietà
                nella ontologia e la restituisce

        """
        with self.ontology :
            new_prop = types.new_class(name, (ObjectProperty,))
        return new_prop


    def __add_tipical_combined_attrs(self,tipicalities_to_add,cs): #,goal) :
        """Funzione __add_tipical_combined_attrs:

            Parametri:
            tipicalities_to_add ([(ThingClass,True|False)]): lista
                di concetti di tipicalità da aggiungere con il proprio
                valore di verità
            cs ([ThingClass]): lista di concetti da combinare

            Returns:
            None: prende la lista di concetti, li mette in And e pone
                il concetto combinato come equivalente a tale congiunzione.
                Inoltre prende le relazioni di tipicalità e prova ad aggiungerle
                alla ontologia e controlla che l'ontologia rimanga consistente.
        """
        
        combined = self.__create_class('combined_0')
        total = []
        for a in cs:
            print("\t",a)
            total.append(a)
        total = And(total)
        print("TOTAL:",total)
        print("EQ TO:",combined.equivalent_to)
        combined.equivalent_to.append(total)
        #combined.equivalent_to.append(goal)
        print("EQ TO:",combined.equivalent_to)


        for i in range(len(tipicalities_to_add)) :
            
            x,y = tipicalities_to_add[i]
            name = str(x).replace(' ','_')
            tmp_attr = self.__create_class(name)
                
            if not y:
                tmp_attr = Not(tmp_attr)        
                
            combined1 = self.__create_class('combined0')
            combineds = self.__create_class('combineds0')
            not_combined1 = self.__create_class('not_combined0')

            combineds.equivalent_to.append(combined & combined1)
            not_combined1.equivalent_to.append(Not(combined1))
            combined_r = self.__create_property('combined_R0')
            
            combineds.is_a.append(tmp_attr)
            combined1.is_a.append(combined_r.only(Not(combined) & combined1))
            not_combined1.is_a.append(combined_r.some(combined & combined1))

  
    def __is_consistent(self) :
        """Funzione __is_consistent:

            Parametri:

            Returns:
            True | False: prende l'ontologia e controlla che sia
            consistente sincronizzando il resoner con l'ontologia
        """
        print("JUST CHECKING:", self.ontology['combined_0'].equivalent_to)
        try :
            with self.ontology:
                sync_reasoner(self.world)
        except subprocess.CalledProcessError as inst :
            return False
        except :
            return False

        print("INCONSISTENS:",list(self.world.inconsistent_classes()))
        if list(self.world.inconsistent_classes()) != []:
            return False
        else:
            return True

    def check_ontology_consistency(self):
        """Funzione check_ontology_consistency:

            Parametri:
            
            Returns:
            True | False: controlla se la ontologia è
                consistente, in tal caso restituisce True,
                altrimenti False

        """
        try :
            with self.ontology:
                sync_reasoner(self.world)
        except subprocess.CalledProcessError as inst :
            return False
        except :
            return False
        print("INCONSISTENZE:",list(self.world.inconsistent_classes()))
        if list(self.world.inconsistent_classes()) != []:
            return False
        else:
            return True



    def check_tipicalities_consistency(self):
        """Funzione check_tipicalities_consistency:

            Parametri:
            
            Returns:
            True | False: controlla se la ontologia con,
                aggiunti, gli assiomi di tipicalità è 
                consistente, in tal caso restituisce True,
                altrimenti False

        """

        added = []
        for x in self.tipicalities.keys():
            name = x[2:len(x)-1]
            combined1 = self.__create_class(name+ "_" + str(1))
            combineds = self.__create_class(name + 's_' + str(1))
            not_combined1 = self.__create_class('not_' + name + str(1))

            combined_r = self.__create_property(name + '_R'+ str(1))

            added = added + [combined1,combineds,not_combined1,combined_r]

            for y in self.tipicalities[x].keys():
                if self.ontology[name] == None:
                    self.__create_class(name)
                if self.ontology[y] == None:
                    self.__create_class(y)
                if float(self.tipicalities[x][y]) >= 0.5:
                    tmp_attr = self.ontology[y]
                    combineds.is_a.append(tmp_attr) 
                else:
                    tmp_attr = Not(self.ontology[y])  
                    combineds.is_a.append(tmp_attr)
           
            dsj = dict()
            l = self.tipicalities[x]

            for y in self.tipicalities[x].keys():
                dis = [x.entities for x in self.ontology[y].disjoints()]
                tot = []
                for x in dis:
                    tot = tot + [z.name for z in x]
                dsj[y] = set(tot)
            
            
            all_tips = []
            for k in dsj.keys():
                all_tips.append(k) 
            all_tips = set(all_tips)
            
            for y in all_tips:
                inters = all_tips.intersection(dsj[y])
                if len(inters) > 1:
                    s = 0.0
                    for z in inters:
                        s = s + float(l[z])
                    if s > 1.0:
                        raise Exception("Confidence Interval is inconsistent for " + str(inters))


            combineds.equivalent_to.append(self.ontology[name] & combined1)
            not_combined1.equivalent_to.append(Not(combined1))
            combined1.is_a.append(combined_r.only(Not(self.ontology[name]) & combined1))
            not_combined1.is_a.append(combined_r.some(self.ontology[name] & combined1)) 
        
        if self.check_ontology_consistency() == True:
            return True
        else:
            return False
    



    def check_new_concept_consistency(self,tipicalities_to_add,cs): #,goal):
        self.__add_tipical_combined_attrs(tipicalities_to_add,cs) #,goal)
        k = self.__is_consistent()
        return k

      
    def check_single_class(self,single_class,expr): 
        print("CHECK OF SINGLE CLASS")
        name = single_class.name + "_bis"
        c = self.__create_class(single_class.name + "_bis", single_class)
        self.ontology[name].equivalent_to.append(expr)
        try:
            with self.ontology:
                sync_reasoner(self.world)
        except subprocess.CalledProcessError as inst :
            return False
        except :
            return False
        return True



