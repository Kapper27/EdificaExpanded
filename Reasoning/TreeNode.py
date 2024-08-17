class TreeNode:
    def __init__(self,name):
        # controlla abbia o meno onto.
        """Costruttore :

            Parametri:
            name (str): nome del concetto
            
            Returns:
            TreeNode: restituisce un nodo 
                del grafo delle inconsistenze

        """
        self.enemies = set()
        self.friends = set()
        self.children = set()
        self.parent = set()
        self.name = name

    def __str__(self):
        """Funzione __str__:

            Parametri:     
            
            Returns:
            str: viene generata una stringa
                che rappresenta il nodo corrente

        """
        res = "Name: " + str(self.name) + " \nConflict nodes in graph: "
        for e in self.enemies:
        	res = res + "\n\t" + str(e)
        
        return res
    
    def addChild(self,child):
        """Funzione addChild:

            Parametri:  
            child (TreeNode): il nodo
                da aggiungere come figlio
                di quello corrente   
            
            Returns:
            void: il nodo viene aggiunto tra i 
                figli del nodo corrente

        """
        if child not in self.children: #siamo sicuri? Meglio usare il nome direi... 
            self.children.add(child)

    def addParent(self,p):
        """Funzione addParent:

            Parametri:  
            p (TreeNode): il nodo da aggiungere 
                come padre di quello corrente   
            
            Returns:
            void: il nodo viene aggiunto tra i 
                nodi genitore del nodo corrente

        """
        if p not in self.parent:
            self.parent.add(p)
    
    def addEnemy(self,enemy):
        """Funzione addEnemy:

            Parametri:  
            enemy (TreeNode): il nodo da aggiungere 
                come "nemico" di quello corrente   
            
            Returns:
            void: il nodo viene aggiunto tra i 
                nodi "nemici" del nodo corrente

        """
        if enemy not in self.enemies:
            self.enemies.add(enemy)

    def adjust(self):
        """Funzione adjust:

            Parametri:  
            
            Returns:
            void: il nodo cancella dalla lista
                degli "amici" quei nodi che sono
                nella lista dei "nemici"

        """
        for k in self.enemies:
            if k in self.friends:
                self.friends.remove(k)

    