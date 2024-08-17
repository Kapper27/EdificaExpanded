from pprint import *
import os

from ManchesterParser import *
from owlready2 import *

import sys
sys.path.insert(0, '../')
from UtilityInterfaces import KnowledgeBaseBuilder



class KnowledgeBaseBuilderManchester(KnowledgeBaseBuilder):
    structure_of_file = "properties name - class definition - property ranges - general axioms"
    format_read = "manchester syntax"
    ontology_format = "owlready2 ontology"

    
    def __init__(self, parser, ontology_name = 'knowledge_base', path = './knowledge_base'): 
        """Costruttore:

            Parametri:
            parser (Parser): classe del parser da utilizzare
            ontology_name (str): il nome della ontologia
            path (str): il percorso in cui trovare l'ontologia

            Returns:
            KnowledgeBaseBuilderManchester: rappresenta il costrutture della ontologia.
                Se come path è specificato un file in formato owl si tiene conto di ciò
                e in seguito si caricherà l'ontologia nella classe.
                Se viene specificato come path un file non in formato owl si crea una 
                ontologia inizialmente vuota con nome specificato da ontology_name. 
                Per popolare tale ontologia sono state prestabilite apposite funzioni.

        """        
        if "owl" ==  path.split(".")[-1]:
            if not os.path.isfile(path):
                raise Exception("Knowledge Base file does not exists!")
            
            self.path = path 
            self.world = World()
            self.content_lines = []
        else:
            if not os.path.isfile(path):
                raise Exception("Knowledge Base file does not exists!")

            self.path = path         
            with open(path) as f:
                input_lines = f.readlines()
            self.content_lines = [x.strip() for x in input_lines if x.strip() != '' and x.strip()[0] != '\n']
            self.world = World()
            self.ontology = self.world.get_ontology("http://www.example.org/onto.owl#"+ontology_name)
            self.parser = parser(self.ontology)   
            
            if self.parser.format_read != self.format_read:
                raise Exception("Parser and Knowledge-Base Builder have different formats")           

    
    
    def __create_class(self, name, parent = Thing) :
        """Funzione __create_class:

            Parametri:
            name (str): Nome della classe da aggiungere alla ontologia
            parent (ThingClass | Restriction | And | Or | Not): 
                classe genitore della classe che andremo a creare

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
            name (str): Nome della property da aggiungere alla ontologia

            Returns:
            ObjectProperty: la seguente funzione restituisce la property appena 
                creata tramite il parametro name

        """
        with self.ontology :
            new_prop = types.new_class(name, (ObjectProperty,))
        return new_prop



    def __readProperties(self):
        """Funzione __readProperties:

            Parametri:

            Returns:
            Void: legge da file le linee in cui si definiscono il nome delle properties
                e crea di conseguenza le properties sulla ontologia di partenza 

        """
        properties_lines = [x for x in self.content_lines if "Properties:" in x] 
        for line in properties_lines:
            property_names = line[11:].split(",")
            for p_name in property_names:
                self.__create_property(p_name.strip())



    def __readClasses(self):
        """Funzione __readClasses:

            Parametri:

            Returns:
            Void: legge da file le linee in cui si menzionano le classi: se ne prende
                il nome, le proprietà di equivalenza di classe e di sottoclasse e si
                creano nella ontologia di partenza le classi corrispondenti

        """
        start = -1
        end = -1

        i = 0
        found = False
        while i < len(self.content_lines) and (not found):
            if "Classes:" in self.content_lines[i]:
                found = True
            else:
                i = i + 1
        if found:
            start = i
            
        i = 0
        found = False
        while i < len(self.content_lines) and (not found):
            if "Properties Domain-Ranges:" in self.content_lines[i] or "General Axioms:" in self.content_lines[i]:
                found = True
            else:
                i = i + 1
        
        if found:
            end = i
        else:
            end = len(self.content_lines)

        if start != -1:
            
            class_positions = [i for i in range(start,end) if "class " in self.content_lines[i]] + [end]
            class_intervals = zip(class_positions,class_positions[1:])
            class_lines = []
            for (a,b) in class_intervals:
                class_lines.append(self.content_lines[a:b])
            
            for lines in class_lines:
                class_intestation = lines[0]
                name = class_intestation[6:]
                name = name[:len(name)-1]
    
                subclass_of_index = [i for i in range(1,len(lines)) if "subClass of:" in lines[i]]
                subclasses = ",".join([lines[i][12:] for i in subclass_of_index])
                is_a = [s.strip() for s in subclasses.split(",") if s.strip() != '']
                
                equivalentclass_of_index = [i for i in range(1,len(lines)) if "equivalentClass:" in lines[i]]
                equivalentclasses = ",".join([lines[i][17:] for i in equivalentclass_of_index])
                eq_to = [s.strip() for s in equivalentclasses.split(",") if s.strip() != '']
                
                               
                to_add = []
                for k in is_a:
                    if k == "owl.Thing":
                        to_add = [Thing] + to_add
                    else:
                        r = self.parser.parse(k)
                        if isinstance(r,ThingClass):
                            to_add = [r] + to_add
                        else:
                            to_add.append(r)

                if to_add == [] or not isinstance(to_add[0],ThingClass):
                    to_add = [Thing] + to_add

                for ta in to_add:
                    self.__create_class(name,ta)
                
                to_add = []
                for k in eq_to:
                    if k == "owl.Thing":
                        to_add = [Thing] + to_add
                    else:
                        r = self.parser.parse(k)
                        if isinstance(r,ThingClass):
                            to_add = [r] + to_add
                        else:
                            to_add.append(r)

                for ta in to_add:
                    self.ontology[name].equivalent_to.append(ta)



    def __readPropertyDomainRanges(self):
        """Funzione __readPropertyDomainRanges:

            Parametri:

            Returns:
            Void: legge da file le linee in cui si menzionano i range e
                i domain delle properties e si aggiornano di conseguenza
                range e domain delle corrispondenti properties nella ontologia
                di partenza

        """
        start = -1
        end = -1

        i = 0
        found = False
        while i < len(self.content_lines) and (not found):
            if "Properties Domain-Ranges:" in self.content_lines[i]:
                found = True
            else:
                i = i + 1
        if found:
            start = i
            
        i = 0
        found = False
        while i < len(self.content_lines) and (not found):
            if "General Axioms:" in self.content_lines[i]:
                found = True
            else:
                i = i + 1
        
        if found:
            end = i
        
        if start != -1:     
            for line in self.content_lines[start+1:end]:
                elements = line.split(":")
                name = elements[0].strip()
                descriptions = elements[1].split(",")
                for description in descriptions:
                    description = description.split("->")
                    domain_p = description[0].strip()
                    range_p = description[1].strip()
                    d_r = self.parser.parse(domain_p)
                    r_r = self.parser.parse(range_p)
                    self.ontology[name].domain.append(d_r)
                    self.ontology[name].range.append(r_r)

            for prop in self.ontology.object_properties():
                if prop.domain == []:
                    prop.domain.append(Thing)
                if prop.range == []:
                    prop.range.append(Thing)
                
    

    def __readAxioms(self):
        """Funzione __readAxioms:

            Parametri:

            Returns:
            Void: legge da file le linee in cui si menzionano gli assiomi di
                disgiunzione tra classi e di partizione di una classe: tali assiomi
                sono inseriti nella ontologia di partenza

        """
        start = -1
        i = 0
        found = False
        while i < len(self.content_lines) and (not found):
            if "General Axioms:" in self.content_lines[i]:
                found = True
            else:
                i = i + 1
        if found:
            start = i
        
        if start != -1:
            for line in self.content_lines[start+1:]:
                if "disjoint" in line:
                    parts = line.split("disjoint")
                    AllDisjoint([self.ontology[x.strip()] for x in parts]) #accetto solo disgiunzioni come coppie
                if "disjUnion of" in line:
                    parts = line.split("disjUnion of")[1]
                    parts = parts.split(",") # prendo solo le parti a destra, che sono quelle disgiunte, il resto?
                    AllDisjoint([self.ontology[x.strip()] for x in parts])
                    

   
    def getOntology(self):
        """Funzione getOntology:

            Parametri:

            Returns:
            Ontology: restituisce la ontologia gestita dalla classe

        """
        return self.ontology
    


    def getWorld(self):
        """Funzione getWorld:

            Parametri:

            Returns:
            World: restituisce il mondo a cui la ontologia gestita
                dalla classe è associata 

        """
        return self.world
    

    def getOntologyFormat(self):
        """Funzione getOntologyFormat:

            Parametri:

            Returns:
            str: restituisce il formato della ontologia gestita
                dalla classe 

        """
        return self.ontology_format


    def buildKnowledgeBase(self):
        """Funzione buildKnowledgeBase:

            Parametri:

            Returns:
            Void: se abbiamo specificato un file owl per la ontologia
                questa funzione non fa nulla, mentre se si è specificato 
                un file non-owl, si procede a popolare la ontologia
        """

        if self.content_lines != []:
            self.__readProperties()    
            self.__readClasses()
            self.__readPropertyDomainRanges() 
            self.__readAxioms()
        else:
            self.ontology = self.world.get_ontology(path).load()