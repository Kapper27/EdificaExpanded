from owlready2 import *

sys.path.insert(0, '../')
from UtilityInterfaces import *

class ComplexCandidateChooser(CandidateChooser):

    tipicality_format = "dict"

    candidate_format = "set of concepts"

    def __init__(self,tipicalities,complex_cands,tipicality_format):
        """Costruttore:

            Parametri:
            tipicalities (dict): base di conoscenza dedicata agli assiomi
                di tipicalità
            complex_cands (list): lista di candidati complessi da analizzare.
                Si ipotizza che i candidati non siano ripetuti nella lsita
            tipicality_format (str): stringa che rappresenta il formato 
                con cui sono codificati gli assiomi di tipicalità
            
            Returns:
            ComplexCandidateChooser: il costruttore restituisce un oggetto
                che compierà analisi sui candidati complessi passati in input
                tramite la conoscenza aggiuntiva passati in input, in questo
                caso tramite gli assiomi di tipicalità

        """
        self.tipicalities = tipicalities
        self.complex_cands = complex_cands
        self.simple_cands = []

        
        if self.tipicality_format != tipicality_format:
            raise Exception("Tipicalities format mistmatch in Candidate Chooser!")

        simplified = []
        for x in complex_cands:
            inpiu = []
            couples = [(x[i],x[j]) for i in range(0,len(x)) for j in range(i+1,len(x))]
            print([(a,b) for (a,b) in couples])
            for (a,b) in couples:
                if a in b.ancestors():
                    inpiu.append(a)
                elif b in a.ancestors():
                    inpiu.append(b)
            to_add = [k for k in x if k not in inpiu]
            if len(to_add) != len(x):
                print("\t SEMPLIFICATION FOUND: ",to_add)
                tot = True
                for comb in simplified:
                    new = False
                    for k in to_add:
                        if k.name not in [z.name for z in comb]:
                            new = True
                    tot = tot and new
                if tot == True:
                    simplified.append(to_add)               
                
        print("ALL SIMPLIFICATIONS FOUND:", simplified)

        self.simple_cands = [list(k) for k in simplified if len(k) == 1]
        self.complex_cands = complex_cands + [list(k) for k in simplified if len(k) != 1]
        print("SIMPLE CANDIDATES FROM SIMPLIFICATION:",self.simple_cands)
        print("COMPLEX CANDIDATES FROM SIMPLIFICATION:",self.complex_cands)

    def get_simple_candidates(self):
        """Funzione get_simple_candidates:

            Parametri:
            
            Returns:
            list: la seguente funzione restituisce la lista
            costituita da tutti i candidati semplici
            derivati dalla semplificazione 

        """
        return self.simple_cands

    def create_order(self):
        """Funzione create_order:

            Parametri:
            
            Returns:
            list: la seguente funzione restituisce i 
                candidati complessi ordinati secondo uno schema
                basato a coppie in cui il primo elemento è 
                la quantità di classi che formano il candidato,
                mentre il secondo elemento è la quantità di 
                assiomi di tipicalità coinvolti dal candidato 
                complesso

        """
        temp = []
        for x in self.complex_cands:
            count = 0
            for g in x:
                count = count + sum([len(self.tipicalities[k].keys()) for k in self.tipicalities.keys() if "T(" + g.name + ")" == k])
            temp.append((x,count))

        t = sorted(temp,key= lambda x: (len(x[0]),-x[1]) )
        print("NEW ORDER:",t)
        return [a for (a,b) in t]
