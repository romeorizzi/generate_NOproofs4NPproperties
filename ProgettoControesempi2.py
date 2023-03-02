import os, sys, time, math
from minizinc.result import Status
from pyvis.network import Network
from tkinter import Tk
from tkinter.filedialog import askopenfilename
from minizinc import Instance, Model, Result, Solver
from fpdf import FPDF
from copy import copy

stateNodes=1
found=False
limit=False
countExplored=0 

#definizione classe grafo
class Graph:
    def __init__(self, parent):
        self.parent=parent
        self.network=Network(height='1000px', width='1400px',bgcolor="#f4f4f4", font_color="black")

        self.network.toggle_physics(True)

        self.createNetwork(self.parent)
    
    def createNetwork(self, node):
        self.createNodesToNetwork(node)
        self.createEdgesToNetwork(node)
    
    def createNodesToNetwork(self, node):
        if node.state==self.parent.state:
            self.network.add_node(node.state, label=node.state+"\n"+node.assegnamento, color='#3bb0eb', size=20)
        elif not node.childs:
            self.network.add_node(node.state, label=node.state+"\n"+node.assegnamento, color='#3bb0eb', size=20)
        else:
            self.network.add_node(node.state, label=node.state+"\n"+node.assegnamento, color='#3bb0eb', size=20)

        for n in node.childs:
            self.createNetwork(n)
    
    def createEdgesToNetwork(self, node):
        for n in node.childs:
            self.network.add_edge(node.state, n.state, weight=10, color='#000080')
            self.createEdgesToNetwork(n)
    
    def createEdgesToNetworkFromChild(self, node):
        self.network.add_edge(node.parent.state, node.state, weight=10, color='#000080')
    
    def visualizzaNodiFoglia(self, node):
        if not node.childs and node.assegnamento=="":
            print(node.state+"   ", end="")
        else:
            for n in node.childs:
                self.visualizzaNodiFoglia(n)

    def cercaFoglie(self,node,lis):
        if not node.childs and node.assegnamento=="":
            lis.append(node)
        else:
            for n in node.childs:
                self.cercaFoglie(n,lis)
        return lis

    def getFoglie(self,node):
        leaves = []
        leaves = self.cercaFoglie(node,leaves)
        return leaves

    def print(self, path):
        self.network.show(path)
    
    def save_pic(self):
        self.network.save_graph("Picture.html")
    
    
#definizione classe nodo
class Node:
    def __init__(self):
        global stateNodes

        self.state=str(stateNodes)
        self.parent= None
        self.assegnamento=""
        self.childs=list()
        self.model = Model()
        stateNodes+=1
    
    def assegnaModello(self,parent):
        if self.parent != None:
            self.model = copy(self.parent.model)
        else:
            self.model = Model()

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
        print("Ci troviamo nel Nodo: "+self.state)
    
    def toStringAssegnamento(self):
        print(self.assegnamento)
        
    def toStringChilds(self):
        if not len(self.childs):
            print("Il Nodo non ha figli.", end="")
        else:
            print("Figli del Nodo numero "+self.state)
            for child in self.childs:
                print(child.state+"   ", end="")
    
    def toStringParent(self):
        if self.parent==None:
            print("Il Nodo corrente non ha un nodo padre.", end="")
        else:
            print("Nodo Padre: "+self.parent.state, end="")

    def getModel(self):
        return copy(self.model)

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

