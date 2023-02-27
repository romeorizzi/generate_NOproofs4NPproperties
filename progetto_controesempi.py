import os, sys, time, math
from minizinc.result import Status
from pyvis.network import Network
import networkx as nx
import pandas as pd
from tkinter import Tk
from tkinter.filedialog import askopenfilename
import re
from minizinc import Instance, Model, Result, Solver
import matplotlib.pyplot as plt
import random


stateNodes=1
found=False
limit=False
countExplored=0

#definizione classe grafo
class Graph:
    def __init__(self, parent):
        self.parent=parent
        self.network=Network(bgcolor="#888888", font_color="white")

        self.network.toggle_physics(True)

        self.createNetwork(self.parent)
    
    def createNetwork(self, node):
        self.createNodesToNetwork(node)
        self.createEdgesToNetwork(node)
    
    def createNodesToNetwork(self, node):
        if node.state==self.parent.state:
            self.network.add_node(node.state, label=node.state+"\n"+node.assegnamento, color='#00ff1e', size=30)
        elif not node.childs:
            self.network.add_node(node.state, label=node.state+"\n"+node.assegnamento, color='#00ff1e', size=30)
        else:
            self.network.add_node(node.state, label=node.state+"\n"+node.assegnamento, color='#00ff1e', size=30)

        for n in node.childs:
            self.createNetwork(n)
    
    def createEdgesToNetwork(self, node):
        for n in node.childs:
            self.network.add_edge(node.state, n.state, weight=10, color='#000080')
            self.createEdgesToNetwork(n)
    
    def createEdgesToNetworkFromChild(self, node):
        self.network.add_edge(node.parent.state, node.state, weight=10, color='#000080')
    
    def visualizzaNodiFoglia(self, node):
        if not node.childs:
            print(node.state+"   ", end="")
        else:
            for n in node.childs:
                self.visualizzaNodiFoglia(n)
    
    def print(self, path):
        self.network.show(path)
    
    
#definizione classe nodo
class Node:
    def __init__(self):
        global stateNodes

        self.state=str(stateNodes)
        self.parent= None
        self.assegnamento=""
        self.childs=list()

        stateNodes+=1
    
    def addParent(self, parent):
        self.parent=parent
    
    def setAssegnamento(self, assegnamento):
        self.assegnamento=assegnamento
    
    def addAssegnamento(self, assegnamento):
        self.assegnamento=self.assegnamento+assegnamento
    
    def addChild(self, child):
        self.childs.append(child)
        child.addParent(self)
    
    def addChilds(self, childs):
        for child in childs:
            self.addChild(child)
            child.addParent(self)
    
    def buildPath(self):
        if self.parent==None:
            print(self.state+" -> ", end="")
        else:
            self.parent.buildPath()
            print(self.state+" -> ", end="")
    
    def buildPath(self, state):
        if self.parent==None and self.state==state:
            print(self.state, end="")
        elif self.parent==None:
            print(self.state+" -> ", end="")
        elif self.state==state:
            self.parent.buildPath(state)
            print(self.state, end="")
        else:
            self.parent.buildPath(state)
            print(self.state+" -> ", end="")
    
    def toString(self):
        self.toStringState()
        print("Assegnamento: "+self.assegnamento)
    
    def toStringState(self):
        print("Stato nodo: "+self.state)
    
    def toStringAssegnamento(self):
        print(self.assegnamento)
        
    def toStringChilds(self):
        if not len(self.childs):
            print("Nodo non ha figli.", end="")
        else:
            print("Figli del nodo con stato: "+self.state)
            for child in self.childs:
                print(child.state+"   ", end="")
    
    def toStringParent(self):
        if self.parent==None:
            print("Non non ha un nodo padre.", end="")
        else:
            print("Padre: "+self.parent.state, end="")

#input dati del problema
def requestDataProblem():
    nNodes=int(input("Dimmi il numero di nodi che vuoi inserire nel grafo: "))

    nodesString=input("Dimmi i nodi: ")

    nodesString=nodesString.split(",")

    edgesString=input("Dimmi gli edges: ")

    edgesString=edgesString.split(",")
    
    return nNodes, nodesString, edgesString

def tranformStringsToNodes(nodes, edges):
    node=[]

    for state in nodes:
        node.append(Node())

    for edge in edges:
        edge=edge.split(":")

        for n1 in node:
            if(n1.state==edge[0]):
                for n2 in node:
                    if(n2.state==edge[1]):
                        n1.addChild(n2)
    
    return node

def requestNodes(nNodes):
    node=[]

    for i in range(0,nNodes):
        print("Nodo nr."+str(i+1)+", dimmi il suo stato: ")
        state=input()
        node.append(Node())
    
    return node

#costruzione percorso del nodo nel grafo
def buildNodePath(node, state):
    if node.parent==None:
        print(node.state+" -> ", end="")
    elif node.state==state:
        buildNodePath(node.parent, state)
        print(node.state)
    else:
        buildNodePath(node.parent, state)
        print(node.state+" -> ", end="")      

#BFS
def BFS(graph, goalState):
    print("_______________________________________________________________________________________________________\n\nALGORITMO DI RICERCA: BFS\n\nPercorso nodi esplorati:")
    
    visited=[]
    frontier=[]
    global countExplored
    countExplored=0

    node=graph.parent

    visited.append(node)
    frontier.append(node)

    while frontier:
        n=frontier.pop(0)
        countExplored+=1
        
        print(n.state+" -> ", end="")

        if n.state==goalState:
            print("goal\n\nNumero nodi esplorati: "+str(countExplored)+"\n_______________________________________________________________________________________________________\n")
            countExplored=0
            return

        for neighbour in n.childs:
            if neighbour not in visited and neighbour not in frontier:
                visited.append(neighbour)
                frontier.append(neighbour)
    
    print("failure\n\nNumero nodi esplorati: "+str(countExplored)+"\n_______________________________________________________________________________________________________\n")
    countExplored=0
    return

#DFS
def DFS(graph, goalState):
    print("_______________________________________________________________________________________________________\n\nALGORITMO DI RICERCA: DFS\n\nPercorso nodi esplorati:")
    DFS_algorithm(graph.parent, goalState)
    DFS_control()

def DFS_algorithm(node, goalState):
    visited=set()
    global found
    global countExplored

    if node not in visited and found==False:
        print(node.state+" -> ", end="")
        countExplored+=1
        
        if node.state==goalState:
            print("goal\n\nNumero nodi esplorati: "+str(countExplored)+"\n_______________________________________________________________________________________________________\n")
            found=True
        visited.add(node)
        for neighbour in node.childs:
            DFS_algorithm(neighbour, goalState)

def DFS_control():
    global found
    global countExplored

    if found==False:
        print("failure\n\nNumero nodi esplorati: "+str(countExplored)+"\n_______________________________________________________________________________________________________\n")
    
    found=False
    
    countExplored=0

#DLS
def DLS(graph, profondità, goalState):
    print("_______________________________________________________________________________________________________\n\nALGORITMO DI RICERCA: DLS\n\nPercorso nodi esplorati:")
    DLS_algorithm(graph.parent, profondità, goalState)
    DLS_control()

def DLS_algorithm(node, profondità, goalState):
    visited=set()
    global found
    global limit
    global countExplored

    if profondità>=0:
        if node not in visited and found==False:
            print(node.state+" -> ", end="")
            countExplored+=1
            if node.state==goalState:
                print("goal\n\nNumero nodi esplorati: "+str(countExplored)+"\n_______________________________________________________________________________________________________\n")
                found=True
            visited.add(node)
            for neighbour in node.childs:
                DLS_algorithm(neighbour, profondità-1, goalState)
    else:
        limit=True

def DLS_control():
    global found
    global limit
    global countExplored

    if limit and found==False:
        print("limit\n\nNumero nodi esplorati: "+str(countExplored)+"\n_______________________________________________________________________________________________________\n")
    elif found==False:
        print("failure\n\nNumero nodi esplorati: "+str(countExplored)+"\n_______________________________________________________________________________________________________\n")
    
    limit=False
    found=False
    countExplored=0

def changeColor(ass,colors):
        c = int(ass.split("=")[1])
        color_ = colors[c-1]
        return color_

def esplorazioneGuidataAlbero(old_m,model,graph, node):
    if graph.parent==node:
        print("Ci troviamo nella radice dell'albero. ")
    
    node.toString()
    node.toStringParent()
    print("")
    node.toStringChilds()
    print("\nPath Node: ", end="")
    node.buildPath(node.state)

    scelta=int(input("\n\nFai una scelta:\n1) Aggiungi un assegnamento al nodo\n2) Torna al nodo padre\n3) Vai in un nodo figlio\n4) Aggiungi un commento\n5) Mappa\n6) Nodi spenti\n7) Visualizza nodi foglia\n8) Cambia o aggiorna modello\n0) Esci\n\nScelta: "))

    while scelta<0 or scelta>9:
        scelta=int(input("Scelta non ammessa!\n\nFai una scelta:\n1) Aggiungi un assegnamento al nodo\n2) Torna al nodo padre\n3) Vai in un nodo figlio\n4) Aggiungi un commento\n5) Mappa\n6) Nodi spenti\n7) Visualizza nodi foglia\n8) Cambia o aggiorna modello\n0) Esci\n\nScelta: "))

    if scelta==0:
        sys.exit()
    elif scelta==1:
        assegnamento=input("\nDimmi l'assegnamento da aggiungere al nodo: ").strip()
        if check_assegnamento(assegnamento,model) == True:
            part = assegnamento.split("constraint")[1].strip()
            node.addAssegnamento(part)
            old_m.add_string(assegnamento + ";")
            if "color" in part:
                col = changeColor(part,colors)
                graph.network.add_node(int(node.state), label=node.state+"\n"+node.assegnamento, color= col, size=30)
                print("")
            else:
                graph.network.add_node(int(node.state), label=node.state+"\n"+node.assegnamento, color= '#00ff1e', size=30)
                
        else:
            model = old_m
            print("L'assegnamento inserito viola i vincoli del problema.")
            print("In particolare, questi sono i vincoli inseriti:")
            print(model._code_fragments)
            print("E questo l'assegnamento:")
            print(assegnamento)
        esplorazioneGuidataAlbero(old_m,model,graph, node)
    elif scelta==2:
        if node.parent==None:
            print("Questo nodo non ha nodo padre, spostamento non ammesso!\n")
            esplorazioneGuidataAlbero(old_m,model,graph, node)
        else:
            print("")
            esplorazioneGuidataAlbero(old_m,model,graph, node.parent)
    elif scelta==3:
        if not len(node.childs):
            print("Questo nodo non ha figli, spostamento non ammesso!\n")
            esplorazioneGuidataAlbero(old_m,model,graph, node)
        else:
            print("")
            node.toStringChilds()
            sf=input("\n\nScegli figlio: ")

            for n in node.childs:
                if n.state==sf:
                    print("")
                    esplorazioneGuidataAlbero(old_m,model,graph, n)
                    return
            
            print("Nodo figlio non presente, spostamento non ammesso!\n")

            esplorazioneGuidataAlbero(old_m,model,graph, node)
    elif scelta==4:
        ass = input("Inserisci il commento:")
        newNode=Node()
        newNode.addParent(node)

        node.addChild(newNode)
        newNode.addAssegnamento(ass)
        graph.createNodesToNetwork(newNode)
        graph.createEdgesToNetworkFromChild(newNode)

        print("\nNodo figlio creato correttamente!\n")

        esplorazioneGuidataAlbero(old_m,model,graph, node)
    elif scelta==5:
        graph.print('Prova.html')

        print("")

        esplorazioneGuidataAlbero(old_m,model,graph, node)
    elif scelta==6:
        graphNode=Graph(graph.parent)
        posizioneNodo(graphNode, node)
        print("")

        esplorazioneGuidataAlbero(old_m,model,graph, node)
    elif scelta==7:
        print("\nNodi foglia: ", end="")
        graph.visualizzaNodiFoglia(graph.parent)
        print("\n")

        esplorazioneGuidataAlbero(old_m,model,graph, node)   
    elif scelta == 8:
        return


def posizioneNodo(graph, node):
    graph.network.add_node(int(node.state), label=node.state+"\n"+node.assegnamento, color='#222222', size=30)

    if node.parent==None:
        graph.print("PosizioneNodo.html")
    else:
        posizioneNodo(graph, node.parent)

def check_assegnamento(ass,m):
    m.add_string(ass + ";")
    inst = Instance(gecode, m)
    res = inst.solve()
    print(res)
    if res.solution is not None and res.status == Status.SATISFIED:
        return True
    else:
        return False

def extract_parameters(filename):
    out_list = list()
    #impostiamo che i file abbiamo sempre NUMNODES ecc
    f = open(filename, "r")
    lines = f.readlines()
    for line in lines:
        if ": NUM_NODES" in line and "array" not in line:
            out_list.append(int(line.split("=")[1].replace(";","")))
        elif ": NUM_EDGES" in line and "array" not in line:
            out_list.append(int(line.split("=")[1].replace(";","")))
        elif "edges ="in line:
            out_list.append((line.split("=")[1].replace(";","").replace("\n","")))

    return out_list

def build_graph(nodes, l_edges):
    edges = list(l_edges.replace("[","").replace("]","").replace(" ","").split("|"))

    node=[]

    for state in range(1,nodes+1):
        node.append(Node())
    
    for item in edges:
        if item != "":
            edge = item.split(",")
            for n1 in node:
                if(n1.state== str(edge[0])):
                    for n2 in node:
                        if(n2.state== str(edge[1])):
                            n1.addChild(n2)
    g = Graph(node[0])
    return g


def create_default_graph(quant):
    node=[]

    for i in range(1,quant+1):
        node.append(Node())

    for item in range(0,quant-1):
        print(item)
        succ = item+1
        node[item].addChild(node[succ])
    
    graph=Graph(node[0])

    return graph

start = True
while start:
    Tk().withdraw() # we don't want a full GUI, so keep the root window from appearing
    filename = askopenfilename() 
    model = Model(filename)
    old_m = Model(filename)
    gecode = Solver.lookup("gecode")
    print("Modello selezionato:")
    print(filename)

    #aggiugere checker
    checker = input("Vuoi aggiungere un checker al modello? y/n")
    if checker.strip() == 'y':
        Tk().withdraw() # we don't want a full GUI, so keep the root window from appearing
        checker = askopenfilename()
        model.add_file(checker)

    inst = Instance(gecode, model)
    res = inst.solve()
    if res.status.has_solution() == True:
        print("Possibile soluzione:")
        print(res)
        #build our graph directly from file
        list_of_parameters = extract_parameters(filename) #here as argument we have to pass the filename
        if list_of_parameters == []:
            print("Per creare il grafo degli assegnamenti, ti chiediamo alcuni parametri:")
            parametro = input("Inserire il parametro:")
            quantità = int(input("Inserire la cardinalità del parametro:"))
            inst[parametro] = quantità
            graph = create_default_graph(quantità)
        else:
            graph = build_graph(int(list_of_parameters[0]),list_of_parameters[2])
            get_colors = lambda n: ["#%06x" % random.randint(0, 0xFFFFFF) for _ in range(n)]
            colors = get_colors(int(list_of_parameters[0]))

        #parte per avviare il menu di verifica del controesempio
        risposta = input("Vuoi verificare un constroesempio? y/n")
        if risposta.strip() == 'y':
            esplorazioneGuidataAlbero(old_m,model,graph, graph.parent)
        else:
            start = False
    else:
        print("Non ci sono soluzioni per il modello. Controlla che sia scritto correttamente.")
        start = False