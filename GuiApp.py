import tkinter as tk 
from EdificaMain import *
from tkinter import ttk


from PIL import Image, ImageTk
import plotly.graph_objects as go
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from tkinterhtml import HtmlFrame
import codecs

import sys, os
import plotly.offline

from PyQt5.QtCore import QUrl
from PyQt5.QtWebEngineWidgets import *
from PyQt5.QtWidgets import * 

if sys.platform.startswith('linux'):
    print("WE ARE ON LINUX")
    from OpenGL import GL

global e 
e = None

class Welcome(tk.Frame):

    my_text = "\n\n\n\n\n\n\n\n"
    my_text = my_text + "Che cosa è EDIFICA?\n EDIFICA è un software che combina i concetti che conosce per generarne, all'occorrenza di nuovi\n\n"

    my_text = my_text + "Il software è diviso in sezioni, qui sopra riportati. Attualmente ti trovi nella pagina di benvenuto.\n\n"
    my_text = my_text + "Selezionando Ontology potrai inserire nel sistema la conoscenza che questo gestirà.\n"
    my_text = my_text + "Ci sono due tipi di conoscenza da inserire, entrambe tramite file: un file di conoscenza rigida e un file di conoscenza tipica.\n"
    my_text = my_text + "Una volta scelti i file, la conoscenza che questi rappresentano verrà caricata all'interno di EDIFICA"
    
    def __init__(self, parent, controller):
        super().__init__(parent,bg="lightblue")
        self.controller = controller
        label = tk.Label(self, text=self.my_text,bg="lightblue",justify=tk.CENTER,wraplength=900,font=("Arial", 25)) #, font=controller.title_font)
        label.pack(side="top", fill="x", pady=10)
        self.bind("<<ShowFrame>>", self.on_show_frame)
        print("\tLOADING WELCOME FRAME... DONE")

    def on_show_frame(self, event):
        global e 
        e = Edifica()

    def __str__(self):
        return "Welcome"

    def clear(self):
        pass


import networkx as nx
import matplotlib.pyplot as plt
import numpy as np
from pyvis.network import Network



class Ontology(tk.Frame):

    app2 = QApplication(sys.argv+ ['--no-sandbox'])

    def show_ont(self):
        G = nx.DiGraph()
        o = e.ontology
        for c in o.classes():
            print(c)
            G.add_node(str(c.name))

        for c in o.classes():
            for k in c.is_a:
                if isinstance(k,ThingClass):
                    G.add_edge(str(k.name),str(c.name))

        pos = nx.spring_layout(G, scale=20, k = 4) #k=3/np.sqrt(G.order())) #(G,scale=0.1) #(G, scale=2)
        pos = nx.nx_agraph.graphviz_layout(G, prog="dot")
        dist = dict()
        for edge in G.edges:
            if edge[0] not in dist.keys():
                dist[edge[0]] = dict()
                dist[edge[0]][edge[1]] = abs(len(str(edge[0]).split(".")[-1].split("#")[-1]) - len(str(edge[1]).split(".")[-1].split("#")[-1]))*100 + 300
            else:
                dist[edge[0]][edge[1]] = abs(len(str(edge[0]).split(".")[-1].split("#")[-1]) - len(str(edge[1]).split(".")[-1].split("#")[-1]))*100 + 300

        labeldict = {}
        for node in G.nodes:
            labeldict[node] = str(str(node).split(".")[-1].split("#")[-1])

        G = G.reverse()

        net = Network(
        height="750px", width = "1500px",
        notebook = True,
        directed = True,
        select_menu = True, # Show part 1 in the plot (optional)
        filter_menu = True, # Show part 2 in the plot (optional),
        cdn_resources= "in_line"
        )
        net.show_buttons() # Show part 3 in the plot (optional)
        net.from_nx(G) # Create directly from nx graph

        #Genera il contenuto HTML
        html_content = net.generate_html()

        # Scrivi il contenuto HTML nel file finale con la codifica UTF-8
        with open('./Temp/ontology.html', 'w', encoding='utf-8') as f:
            f.write(html_content)

        file_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "./Temp/ontology.html"))
        print(file_path)
        QUrl.fromLocalFile(file_path)

        web = QWebEngineView()
        web.load(QUrl.fromLocalFile(file_path))
        qw = QWidget()
        vbox = QVBoxLayout(qw)
        vbox.addWidget(web)
        qw.setLayout(vbox)
        width= self.winfo_screenwidth()
        height= self.winfo_screenheight()
        qw.setGeometry(0,0, width, height)
        qw.setWindowTitle('Ontology')
        qw.show()
        self.app2.exit(self.app2.exec_())


    def __init__(self, parent, controller):
        super().__init__(parent,bg="lightblue")
        self.controller = controller
        label = tk.Label(self, text="Benvenuto nella pagina della conoscenza del sistema!",bg="lightblue",font=("Arial", 25)) #, font=controller.title_font)
        label.pack(side="top", fill="x", pady=10)
        self.bind("<<ShowFrame>>", self.on_show_frame)
        self.tree = ttk.Treeview(self)
        self.tree.pack(side="top", fill="x", pady=10)
        print("\tLOADING KNOWLEDGE FRAME... DONE")

    def getKB(self):
        from tkinter.filedialog import askopenfilename
        filename = askopenfilename()
        print(filename)
        if filename != () and filename != "":
            e.setKnowledgeBaseBuilder(KnowledgeBaseBuilderManchester,ManchesterParser,file_path=filename)
            self.show_ont()
            return True
        else:
            return False

    def getTip(self):
        from tkinter.filedialog import askopenfilename
        filename = askopenfilename()
        if filename != () and filename != "":
            label = tk.Label(self, text="Carico le tipicalità...",bg="lightblue",font=("Arial", 25)) #, font=controller.title_font)

            e.setTipicalityBaseBuilder(BaseTipicalityBuilder, None,tipicality_path=filename)
            label.pack(side="top", fill="x", pady=10)
            label.update()
            try:
                e.checkConsistency(BaseOntologyChecker)
                label.destroy()
                for x in e.tipicalities.keys():
                    a = self.tree.insert("","end",text=str(x),open=True)
                    for y in e.tipicalities[x]:
                        b = self.tree.insert(a,"end",text=str(y) + ":" + str(e.tipicalities[x][y]),open=True)
            except Exception as ex:
                label.config(text=str(ex))
                label.update()
                return False
            return True
        else:
            return False

    def on_show_frame(self, event):
        label = tk.Label(self, text="",bg="lightblue",font=("Arial", 25))
        label.pack(side="top", fill="x", pady=10)
        res = self.getKB()
        if res:
            res = self.getTip()
            if res:
                label.config(text="Caricamento avvenuto con successo")
                label.update()
            else:
                label.config(text="Errore nel caricamento delle informazioni flessibili")
                label.update()
        else:
            label.config(text="Errore nel caricamento delle informazioni rigide")
            label.update()

    def __str__(self):
        return "Ontology"

    def clear(self):
        alls = [a for a in self.winfo_children() if isinstance(a,tk.Label)]
        alls = [a for a in alls if a.cget("text") != "Benvenuto nella pagina della conoscenza del sistema!"]
        for a in alls:
            a.destroy()
        for item in self.tree.get_children():
            self.tree.delete(item)




class Goals(tk.Frame):

    def __init__(self, parent, controller):
        super().__init__(parent,bg="lightblue")
        self.controller = controller
        label = tk.Label(self, text="Benvenuto nella pagina deli goal!",bg="lightblue",font=("Arial", 25)) #, font=controller.title_font)
        label.pack(side="top", fill="x", pady=10)
        self.bind("<<ShowFrame>>", self.on_show_frame)
        self.label1 = tk.Label(self)
        print("DONE")


    app3 = QApplication(sys.argv+ ['--no-sandbox'])

    def show_goal(self):

        file_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "./Temp/goals.html"))
        print(file_path)
        QUrl.fromLocalFile(file_path)
        web3 = QWebEngineView()
        web3.load(QUrl.fromLocalFile(file_path))
        qw = QWidget()
        vbox = QVBoxLayout(qw)
        vbox.addWidget(web3)
        qw.setLayout(vbox)
        width= self.winfo_screenwidth()
        height= self.winfo_screenheight()
        qw.setGeometry(0,0, width, height)
        qw.setWindowTitle('Goals')
        qw.show()
        self.app3.exit(self.app3.exec_())


    def getG(self):
        from tkinter.filedialog import askopenfilename
        filename = askopenfilename()
        print(filename)
        label = tk.Label(self, text="Carico i goals...",bg="lightblue",font=("Arial", 25))
        label.pack(side="top", fill="x", pady=10)
        if filename != () and filename != "":
            e.setGoal(BaseGoalBuilder,ManchesterParser,goal_path=filename)
            G = e.goal_builder.graph[0]
            if G != None:
                net = Network(
                height="750px", width = "1500px",
                notebook = True,
                directed = True,
                select_menu = True, # Show part 1 in the plot (optional)
                filter_menu = True, # Show part 2 in the plot (optional)
                cdn_resources= "in_line"
                )
                net.show_buttons() # Show part 3 in the plot (optional)
                net.from_nx(G) # Create directly from nx graph
                # Genera il contenuto HTML
                html_content = net.generate_html()

                # Salva il contenuto HTML con codifica UTF-8
                with open('./Temp/goals.html', 'w', encoding='utf-8') as f:
                    f.write(html_content)

                self.show_goal()

                label.config(text="Fatto")
                label.update()
                self.update()
            else:
                label.config(text="Nessun goal rilevato")
                label.update()
                self.update()


    def on_show_frame(self, event):
        self.getG()

    def __str__(self):
        return "Goals"

    def clear(self):
        alls = [a for a in self.winfo_children() if isinstance(a,tk.Label)]
        alls = [a for a in alls if a.cget("text") != "Benvenuto nella pagina deli goal!"]
        for a in alls:
            a.destroy()


class Reasoning(tk.Frame):

    def __init__(self, parent, controller):
        super().__init__(parent,bg="lightblue")
        self.controller = controller
        label = tk.Label(self, text="Benvenuto nella pagina del ragionamento",bg="lightblue",font=("Arial", 25)) #, font=controller.title_font)
        label.pack(side="top", fill="x", pady=10)
        self.bind("<<ShowFrame>>", self.on_show_frame)
        self.tree = ttk.Treeview(self)
        self.tree.pack(side="top", fill="x", pady=10)
        print("DONE")

    app1 = QApplication(sys.argv+ ['--no-sandbox'])
 
    def show_conflicts(self):
        file_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "./Temp/consistency_graph.html"))
        print(file_path)

        if(os.path.exists(file_path)):
        
            web1 = QWebEngineView()
            QUrl.fromLocalFile(file_path)
            print(QUrl.fromLocalFile(file_path))
            web1.load(QUrl.fromLocalFile(file_path))
            w = 900
            h = 800
            qw = QWidget()
            vbox = QVBoxLayout(qw)
            vbox.addWidget(web1)
            qw.setLayout(vbox)
            width= self.winfo_screenwidth()               
            height= self.winfo_screenheight()               
            qw.setGeometry(0,0, width, height)
            qw.setWindowTitle('Consistency Graph')
            qw.show()
            self.app1.exit(self.app1.exec_())
       


    def on_show_frame(self, event):
        solution = e.resolve_goal(BaseOntologyChecker)
        if solution != None:
            goal = solution[0]
            result = solution[1]
            tips = solution[2]
            l1 = tk.Label(self, text="IL RISULTATO FINALE E': " + str(result) + "\n" ,bg="lightblue",font=("Arial", 25)) #, font=controller.title_font)
            l1.pack(side="top", fill="x", pady=10)
            l2 = tk.Label(self, text="GOAL RISOLTO: " + str(goal),bg="lightblue",font=("Arial", 25)) #, font=controller.title_font)
            l2.pack(side="top", fill="x", pady=10)
            self.tree.tag_configure('t1', background = 'green')
            self.tree.tag_configure('t2', background = 'red')
            self.tree.tag_configure('t3', background = 'orange')
            self.tree.tag_configure('t4', background = 'lightblue')
            found = False
            for x in e.to_show.keys():
                a = self.tree.insert("","end",text=str(x),open=True)
                for y in e.to_show[x]:
                    print(y)
                    if [False for a in y if a not in result] != [] and found:
                        print("\tNOT IN RESULT:",y)
                        b = self.tree.insert(a,"end",text=str(y),open=True)
                    if [False for a in y if a not in result] != [] and not found:
                        print("\tNOT IN RESULT:",y)
                        b = self.tree.insert(a,"end",text=str(y),open=True,tags = ['t2'])
                    if [False for a in y if a not in result] == []:
                        print("\tIN RESULT:",y)
                        b = self.tree.insert(a,"end",text=str(y),open=True,tags = ['t1'])
                        found = True
    
                    i = 0
                    if And(y) in e.goal_solver.to_show.keys():
                        for k in e.goal_solver.to_show[And(y)]:
                            all_couples = zip(k,tips)
                            if [False for ((a,b),(c,d)) in all_couples if a.name != c.name or bool(b) != bool(d)] == []:
                                c = self.tree.insert(b,"end",text=str(k),open=True,tags = ['t4'])
                            else:
                                c = self.tree.insert(b,"end",text=str(k),open=True,tags = ['t3'])
                            i = i + 1

            self.show_conflicts()
        else:
            l1 = tk.Label(self, text="NON E' STATO TROVATO UN RISULTATO:\n" ,bg="lightblue",font=("Arial", 25))
            l1.pack(side="top", fill="x", pady=10)
    

    def __str__(self):
        return "Reasoning"


    def clear(self):
        alls = [a for a in self.winfo_children() if isinstance(a,tk.Label)]
        alls = [a for a in alls if a.cget("text") != "Benvenuto nella pagina del ragionamento"]
        for a in alls:
            a.destroy()
        for item in self.tree.get_children():
            self.tree.delete(item)

 
OPTIONS = [Welcome, Ontology,Goals,Reasoning] 



class GuiApp(tk.Tk): 

    
    def __init__(self): 
        super().__init__() 
        self.title("Edifica")
        width= self.winfo_screenwidth()               
        height= self.winfo_screenheight()               
        self.geometry("%dx%d" % (width, height))
        self.config(bg="skyblue")

        self.frames = {}

        principal = tk.Frame(self)
        principal.pack(side="top", fill="both", expand=True)
    
        
        principal.grid_rowconfigure(1, weight=1)
        principal.grid_rowconfigure(0, weight=0)        

        for i in range(0,len(OPTIONS)):
            principal.grid_columnconfigure(i, weight=1)

        for name in OPTIONS:
            frame = name(parent=principal, controller=self) 
            self.frames[str(frame)] = frame
            frame.grid(row=1, column=0, sticky="nsew",columnspan=len(OPTIONS))

        self.btns = dict()
        self.current = None
        
        i = 0
        for name in OPTIONS:
            kk = str(OPTIONS[i]).split(".")[-1][:-2]
            print("KK:",kk)
            btn = tk.Button(principal,text=kk,  disabledforeground="black",  highlightbackground = "lightblue", highlightthickness=1,bg = "white",activebackground="#fca9b3",command=lambda j=kk: self.show_frame(j),bd=0)
            btn.grid(row=0, column=i, sticky="nsew")
            self.btns[kk] = btn
            i = i + 1

        starting_frame = tk.Frame(principal)
        
        label = tk.Label(starting_frame, text="BENVENUTO IN EDIFICA!",bg="lightblue",justify=tk.CENTER,wraplength=900,font=("Arial", 25))
        label.pack(side="top", fill="both", expand=True)

        starting_frame.grid(row=1, column=0, sticky="nsew",columnspan=len(OPTIONS))
        principal.tkraise()

    
    def show_frame(self,name):
        print("SHOWING NEW FRAME:",name)
        cc = None
        #frame.clear()
        if self.current != None:
            print("OK")
            cc = self.current
        frame = self.frames[name]
        self.current = self.btns[name]
        if cc != None:
            cc.config(bg = "white",activebackground="#fca9b3")
            print("CC:",cc.cget('text'))
            self.frames[cc.cget('text')].clear()
        self.current.config(bg = "lightblue",activebackground="lightblue")
        if cc != None:
            cc.config(state=tk.NORMAL)
        self.current.config(state=tk.DISABLED)
        
        frame.tkraise()
        frame.event_generate("<<ShowFrame>>")
        print("NEW FRAME LOADED SUCCESSFULLY")
    
    
    
import IPython
from ipywidgets import Output,VBox
if __name__ == "__main__": 
    app = GuiApp() 
    app.mainloop() 
