import os

import sys
sys.path.insert(0, '../')
from UtilityInterfaces import TipicalityBuilder


class BaseTipicalityBuilder(TipicalityBuilder):
    structure_of_file = "tipicality axioms"
    format_read = "T(A)-B:prob"
    tipicality_format = "dict"

    
    def __init__(self, parser=None, path = 'tipicality_base'): 
        """Costruttore:

            Parametri:
            parser (Parser): classe del parser da utilizzare, in questo caso non se ne usa nessuno di particolare
            path (str): il percorso in cui trovare il file contenente gli assiomi di tipicalità

            Returns:
            BaseTipicalityBuilder: è un oggetto in grado di leggere il file specificato da path
                utilizzando, come parsificatore, parser passato come parametro

        """
        self.path = path         
        self.tipicality = dict()
        if not os.path.isfile(path):
            raise Exception("Tipicality Axioms file does not exists!")




    def getTipicalities(self):
        """getTipicalities:

            Parametri:

            Returns:
            dict(): un dizionario contenente informazioni strutturate per ogni
                assioma di tipicalità

        """
        return self.tipicality

    

    def getTipicalityFormat(self):
        """getTipicalityFormat:

            Parametri:

            Returns:
            str: una stringa che rappresenta come è fatto il formato con cui
                sono espressi gli assiomi di tipicalità

        """
        return self.tipicality_format
    
    def buildTipicalities(self):
        """buildTipicalities:

            Parametri:

            Returns:
            Void: tramite il percorso e il parser specificati nel costruttore,
                viene letto il file e parsificato e gli assiomi di tipicalità 
                trovati sono aggiunti a una struttura dati interna alla classe             

        """
        with open(self.path) as f:
            input_lines = f.readlines()
        content_lines = [x.strip() for x in input_lines if x.strip() != '' and x.strip()[0] != '\n']
        for line in content_lines:
            tmp = line.split("-")
            tmp2 = tmp[1].split(":")
            infos = [tmp[0]] + tmp2
            infos = [x.strip() for x in infos]
            if infos[0] in self.tipicality.keys():
                if infos[1] not in self.tipicality[infos[0]].keys():
                    self.tipicality[infos[0]][infos[1]] = infos[2]
            else:
                self.tipicality[infos[0]] = dict()
                self.tipicality[infos[0]][infos[1]] = infos[2]

