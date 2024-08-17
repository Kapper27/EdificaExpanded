from owlready2 import * 
from TreeNode import *
import pickle
import json
import dill 
import pprint

global res 
res = None
def explore(c1, c2,visited):
    """Funzione explore:

            Parametri:
            c1 (ThingClass | Not | And | Or | Restriction): 
                concetto da confrontare con c2. Una volta
                aver confrontato c1 e c2, si confrontano
                gli antenati o i concetti equivalenti di c1
                con c2
            c2 (ThingClass | Not | And | Or | Restriction): 
                concetto da confrontare con c1.
            visited (set): insieme dei nodi della parte di c1 
                visitati confrontando con c2. Questo input
                ci permette di tenere traccia di quali nodi
                abbiamo già visitato evitando circolarità
            
            
            Returns:
            void: vengono generati dei nodi, ognuno 
                che rappresenta un concetto, e vengono
                aggiornati i loro rapporti: possono essere
                nodi in conflitto (possono generare 
                inconsistenze) oppure no

        """

    if c1 not in visited:
        visited.add(c1)
        
        if c1 not in res.keys():
            res[c1] = TreeNode(str(c1))

        if c2 not in res.keys():
            res[c2] = TreeNode(str(c2))

        print("EXPLORE:",c1,c2,c1.is_a)

        if c2 not in (res[c1].enemies.union(res[c1].friends)) and c2 != c1:
            if c1 != owl.Thing and isinstance(c1,ThingClass):
                for axiom in c1.disjoints():
                    disjoints_of_c = set(axiom.entities).difference(set([c1]))
                    if c2 in disjoints_of_c:
                        res[c1].enemies.add(c2)
                        res[c2].enemies.add(c1)


                if isinstance(c2,Not) and c2.Class == c1:
                    res[c1].enemies.add(c2)
                    res[c2].enemies.add(c1)

            elif c1 == owl.Thing:
                res[c1].friends.add(c2)
                res[c2].friends.add(c1)

            if (isinstance(c1,Not) and c1.Class == c2) or (isinstance(c2,Not) and c2.Class == c1):
                res[c1].enemies.add(c2)
                res[c2].enemies.add(c1)
            elif (isinstance(c1,Not)):
                c = c1.Class
                if isinstance(c, And):
                    args = c.Classes
                    c3 = Or([Not(a) for a in args])
                    explore(c3,c2,visited)
                    res[c1].addChild(res[c3])
                    res[c3].addParent(res[c1])
                    res[c1].enemies = res[c1].enemies.union(res[c3].enemies)
                if isinstance(c,Or):
                    args = c.Classes
                    c3 = And([Not(a) for a in args])
                    explore(c3,c2,visited)
                    res[c1].addChild(res[c3])
                    res[c3].addParent(res[c1])
                    res[c1].enemies = res[c1].enemies.union(res[c3].enemies)
                if isinstance(c,Restriction):
                    if(c.type == owlready2.SOME):
                        c3 = (c.property).only(Not(c.value))
                        explore(c3,c2,visited)
                        res[c1].addChild(res[c3])
                        res[c3].addParent(res[c1])
                        res[c1].enemies = res[c1].enemies.union(res[c3].enemies)
                    if(c.type == owlready2.ONLY):
                        c3 = (c.property).some(Not(c.value))
                        explore(c3,c2,visited)
                        res[c1].addChild(res[c3])
                        res[c3].addParent(res[c1])
                        res[c1].enemies = res[c1].enemies.union(res[c3].enemies)
                    if(c.type == owlready2.VALUE):
                        c3 = (c.property).value(Not(c.value))
                        explore(c3,c2,visited)
                        res[c1].addChild(res[c3])
                        res[c3].addParent(res[c1])
                        res[c1].enemies = res[c1].enemies.union(res[c3].enemies)
            
            if(isinstance(c1,And)):
                args = c1.Classes
                for a in args:
                    explore(a,c2,visited)
                    res[a].addChild(res[c1])
                    res[c1].addParent(res[a])
                    res[c1].enemies = res[c1].enemies.union(res[a].enemies) 
                
            
            if(isinstance(c1,Or)):
                args = c1.Classes
                tmp = set()
                first = True
                for a in args:
                    explore(a,c2,visited)
                    res[a].addChild(res[c1])
                    res[c1].addParent(res[a])
                    if not first:
                        tmp = tmp.intersection(res[a].enemies) 
                    else:
                        tmp = res[a].enemies
                        first = False
                res[c1].enemies = res[c1].enemies.union(tmp) 

            
            if isinstance(c1,Restriction) and isinstance(c2,Restriction):
                if(c1.type == owlready2.SOME and c2.type == owlready2.ONLY and c1.property == c2.property):
                    explore_max(c1.value, c2.value,set())
                    if c2.value in res[c1.value].enemies:
                        res[c2].enemies.add(c1)
                        res[c1].enemies.add(c2)
                elif(c1.type == owlready2.ONLY and c2.type == owlready2.SOME and c1.property == c2.property):
                    explore_max(c1.value, c2.value,set())
                    if c2.value in res[c1.value].enemies:
                        res[c2].enemies.add(c1)
                        res[c1].enemies.add(c2)
                elif(c1.type == owlready2.ONLY and c2.type == owlready2.ONLY and c1.property == c2.property):
                    explore_max(c1.value, c2.value,set())
                    if c2.value in res[c1.value].enemies:
                        res[c2].enemies.add(c1)
                        res[c1].enemies.add(c2)
                elif(c1.type == owlready2.VALUE and c2.type == owlready2.ONLY and c1.property == c2.property):
                    if c1.value not in c2.value.instances():
                        res[c2].enemies.add(c1)
                        res[c1].enemies.add(c2)
                elif(c1.type == owlready2.ONLY and c2.type == owlready2.VALUE and c1.property == c2.property):
                    if c2.value not in c1.value.instances():
                        res[c2].enemies.add(c1)
                        res[c1].enemies.add(c2)
                elif(c1.type == owlready2.VALUE and c2.type == owlready2.VALUE and c1.property == c2.property):
                    if FunctionalProperty in c1.property.is_a and isinstance(c1.value.__class__, ThingClass):
                        l = []
                        for k in c2.value.differents():
                            l = l + k.entities
                        if (c1.value in l):
                            res[c2].enemies.add(c1)
                            res[c1].enemies.add(c2)
                    elif FunctionalProperty in c1.property.is_a and (c1.value != c2.value): 
                        res[c2].enemies.add(c1)
                        res[c1].enemies.add(c2)
                
            if isinstance(c1,ThingClass):
                print("\tORA VISITIAMO I PARENTI")
                for concept in c1.equivalent_to:
                    print("\tVISITO",concept)
                    explore(concept,c2,visited)
                    res[concept].addChild(res[c1])
                    res[c1].addParent(res[concept])
                    res[c1].addChild(res[concept])
                    res[concept].addParent(res[c1])
                    res[c1].enemies = res[c1].enemies.union(res[concept].enemies)
                
                for concept in c1.equivalent_to:
                    res[concept].enemies = res[c1].enemies
                
                for k in res[c1].enemies:
                    res[k].enemies = res[k].enemies.union(set([c for c in c1.equivalent_to]))
        
                for concept in c1.is_a:
                    print("\tVISITO",concept)
                    explore(concept,c2,visited)
                    res[concept].addChild(res[c1])
                    res[c1].addParent(res[concept])
                    res[c1].enemies = res[c1].enemies.union(res[concept].enemies)
                
                for en in res[c1].enemies :
                    res[en].enemies.add(c1)

       

def explore_max(c1,c2,visited):
    """Funzione explore_max:

            Parametri:
            c1 (ThingClass | Not | And | Or | Restriction): 
                concetto da confrontare con c2. 
            c2 (ThingClass | Not | And | Or | Restriction): 
                concetto da confrontare con c1. Una volta
                aver confrontato c1 e c2, si confrontano
                gli antenati o i concetti equivalenti di c2
                con c1
            visited (set): insieme dei nodi della parte di c1 
                visitati confrontando con c2. Questo input
                ci permette di tenere traccia di quali nodi
                abbiamo già visitato evitando circolarità
            
            
            Returns:
            void: vengono generati dei nodi, ognuno 
                che rappresenta un concetto, e vengono
                aggiornati i loro rapporti: possono essere
                nodi in conflitto (possono generare 
                inconsistenze) oppure no

        """

    if c2 not in visited:
        visited.add(c2)
    
        if c2 not in res.keys():
            res[c2] = TreeNode(str(c2))
        
        if c1 not in res.keys():
            res[c1] = TreeNode(str(c1))
               
        if c1 not in (res[c2].enemies.union(res[c2].friends)) and c2 != c1:
            
            direct_parents = []           
            equivalents = []
            if isinstance(c2,ThingClass):
                direct_parents = [concept for concept in c2.is_a]
                equivalents = [e for e in c2.equivalent_to]
                all_enemies = set()
                for e in equivalents:
                    if e not in res.keys():
                        res[e] = TreeNode(str(e))
                    res[e].addChild(res[c2])
                    res[c2].addParent(res[e])
                    res[c2].addChild(res[e])
                    res[e].addParent(res[c2])
                    explore_max(c1,e,visited)
                    all_enemies = all_enemies.union(res[e].enemies)
                res[c2].enemies = res[c2].enemies.union(all_enemies)
                for en in res[c2].enemies :
                    res[en].enemies.add(c2)

                for e in equivalents:
                    res[e].enemies = res[c2].enemies
                    for en in res[e].enemies :
                        res[en].enemies.add(e)
                
            if isinstance(c2,ThingClass) or isinstance(c2,Restriction):
                if c2 == owl.Thing:
                    explore(c1,c2,set())
                else:
                    explore(c1,c2,set())
                    all_enemies = set()
                    for parent in direct_parents:
                        if parent not in res.keys():
                            res[parent] = TreeNode(str(parent))
                        res[parent].addChild(res[c2])
                        res[c2].addParent(res[parent])
                        explore_max(c1,parent,visited)
                        all_enemies = all_enemies.union(res[parent].enemies)
                        
                    res[c2].enemies = res[c2].enemies.union(all_enemies)
                    
                    for en in res[c2].enemies :
                        res[en].enemies.add(c2)

                    for e in equivalents:
                        res[e].enemies = res[c2].enemies
                        for en in res[c2].enemies :
                            res[en].enemies.add(e)
                
            elif isinstance(c2,And):
                args = c2.Classes
                for a in args:
                    explore_max(c1,a,visited) 
                    res[a].addChild(res[c2])
                    res[c2].addParent(res[a])
                    res[c2].enemies.union(res[a].enemies)
                    for en in res[a].enemies:
                        res[en].enemies.add(c2)
            
            elif isinstance(c2,Or):
                args = c2.Classes
                tmp = set()
                first = True
                for a in args:
                    explore_max(c1,a,visited)
                    res[a].addChild(res[c2])
                    res[c2].addParent(res[a])
                    if not first:
                        tmp = tmp.intersection(res[a].enemies)
                    else:
                        tmp = res[a].enemies
                        first = False

                res[c2].enemies = res[c2].enemies.union(tmp)
                for en in tmp:
                    res[en].enemies.add(c2)

            elif isinstance(c2,Not):
                explore(c1,c2,set())
                c = c2.Class
                if isinstance(c, And):
                    args = c.Classes
                    c3 = Or([Not(a) for a in args])
                    explore_max(c1,c3,visited)
                    res[c2].addChild(res[c3])
                    res[c3].addParent(res[c2])
                    res[c2].enemies = res[c2].enemies.union(res[c3].enemies)
                if isinstance(c,Or):
                    args = c.Classes
                    c3 = And([Not(a) for a in args])
                    explore_max(c1,c3,visited)
                    res[c2].addChild(res[c3])
                    res[c3].addParent(res[c2])
                    res[c2].enemies = res[c2].enemies.union(res[c3].enemies)
                if isinstance(c,Restriction):
                    if(c.type == owlready2.SOME):
                        c3 = (c.property).only(Not(c.value))
                        explore_max(c1,c3,visited)
                        res[c2].addChild(res[c3])
                        res[c3].addParent(res[c2])
                        res[c2].enemies = res[c2].enemies.union(res[c3].enemies)
                    if(c.type == owlready2.ONLY):
                        c3 = (c.property).some(Not(c.value))
                        explore_max(c1,c3,visited)
                        res[c2].addChild(res[c3])
                        res[c3].addParent(res[c2])
                        res[c2].enemies = res[c2].enemies.union(res[c3].enemies)
                    if(c.type == owlready2.VALUE):
                        c3 = (c.property).value(Not(c.value))
                        explore_max(c1,c3,visited)
                        res[c2].addChild(res[c3])
                        res[c3].addParent(res[c2])
                        res[c2].enemies = res[c2].enemies.union(res[c3].enemies)
                                    

def clean():
    """Funzione clean:

            Parametri:
            
            Returns:
            void: ogni nodo nel grafo viene
                "pulito", ovvero: per ogni
                nodo viene posto come nodo "amico"
                tutti gli altri nodi del grafo
                e poi vengono tolti dalla lista degli
                amici quei nodi con cui è in conflitto

        """
    f = set([r for r in res.keys() if r != owl.Thing])
    for k in res.keys():
        res[k].friends = f

    for k in res.keys():
        res[k].adjust() 


def getConsistencyGraph():
    """Funzione getConsistencyGraph:

            Parametri:
            
            Returns:
            dict: viene restituito il grafo
                delle consistenze: un dizionario
                con chiave il nome del concetto
                e come valore il nodo del grafo

        """
    return res

def initialize():
    global res
    res = {}