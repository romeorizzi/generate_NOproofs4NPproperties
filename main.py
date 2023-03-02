from ProgettoControesempi2 import *
import os, sys, time, math
from minizinc.result import Status
from pyvis.network import Network
from tkinter import Tk
from tkinter.filedialog import askopenfilename
from minizinc import Instance, Model, Result, Solver
from fpdf import FPDF
import imgkit


def fix_strings(codeline):
    l = str(codeline).replace("[","").replace("]","").replace('\'',"").replace(";","").split(",")
    app = list()
    for item in l:
        if item.strip() not in app:
            app.append(item)
    return app


def create_PDF(graph,node):

    f = open("tmp.txt", "a")
    l1 = "Report Dimostrazione\n"
    l11 = "Ci troviamo nel nodo numero: " + node.state +"\n"
    l2 = "Modello Minizinc (file inserito):" + filename + "\n"
    f.writelines([l1,l11,l2])
    l3 = "Vincoli inseriti nel modello per questo branch:\n"
    f.writelines([l3])
    l4 = fix_strings(node.model._code_fragments)
    for item in l4:
        f.write(item.strip()+"\n")
    f.close()

    pdf = FPDF()  
    pdf.add_page()
    f = open("tmp.txt","r")
    for x in f:
        if x == l1:
            pdf.set_font("Arial", 'B',size = 17)
            pdf.cell(200, 10, txt = x, ln = 1, align = 'C')
        else:
            pdf.set_font("Arial", size = 11)
            pdf.cell(100, 10, txt = x, ln = 1, align = 'L')

    f.close()
    graph.save_pic()
    imgkit.from_file('Picture.html', 'graph.jpg')
    pdf.image("graph.jpg", w= 195, h=150)
    pdf.output("Report.pdf")  
    
    os.remove("tmp.txt")
    return


def check_assegnamento(modello,assegnamento):
    modello.add_string(assegnamento + ";")
    gecode = Solver.lookup("gecode")
    inst = Instance(gecode,modello)
    res = inst.solve()
    print(res)
    if res.solution is not None and res.status == Status.SATISFIED:
        return True
    else:
        return False
    

def esplorazioneGuidataAlbero(graph, node):
    if graph.parent== node:
        print("Ci troviamo nella radice dell'albero. ")
    
    node.toString()
    node.toStringParent()
    print("")
    node.toStringChilds()
    print("\nPath Node: ", end="")
    node.buildPath(node.state)

    scelta=int(input("\n\nFai una scelta:\n1) Raffina assegnamento parziale\n2) Torna al nodo padre\n3) Vai in un nodo figlio\n4) Aggiungi figli\n5) Visualizza assegnamento nodo corrente\n6) Visualizza nodi foglia\n7) Esporta su file\n0) Esci\n\nScelta: "))

    while scelta<0 or scelta>7:
        scelta=int(input("Scelta non ammessa!\n\nFai una scelta:\n1) Raffina assegnamento parziale\n2) Torna al nodo padre\n3) Vai in un nodo figlio\n4) Aggiungi figli\n5) Visualizza assegnamento nodo corrente\n6) Visualizza nodi foglia\n7) Esporta su file\n0) Esci\n\nScelta: "))

    if scelta==0:
        sys.exit()
    elif scelta==1:
        if node.assegnamento != "":
            print("Il nodo presenta già un assegnamento, creare un nuovo sottocaso.")
            esplorazioneGuidataAlbero(graph, node)
        modello_temp = Model()
        modello_temp = node.getModel()
        assegnamento=input("\nDimmi l'assegnamento da aggiungere al nodo: ").strip()
        if check_assegnamento(modello_temp,assegnamento) == True:
            part = assegnamento.split("constraint")[1].strip()
            node.addAssegnamento(part)
            node.model.add_string(assegnamento + ";")
            graph.network.add_node(int(node.state), label=node.state+"\n"+node.assegnamento, color= '#00ff1e', size=20)
        else:
            print("L'assegnamento inserito viola i vincoli del problema.")
            print("Il modello presenta i seguenti vincoli:")
            print(node.model._code_fragments)
            print("Controlla la tua soluzione.")
        esplorazioneGuidataAlbero(graph, node)

    elif scelta==2:
        if node.parent==None:
            print("Questo nodo non ha nodo padre, spostamento non ammesso!\n")
            esplorazioneGuidataAlbero(graph, node)
        else:
            print("")
            esplorazioneGuidataAlbero(graph, node.parent)
    elif scelta==3:
        if not len(node.childs):
            print("Questo nodo non ha figli, spostamento non ammesso!\n")
            esplorazioneGuidataAlbero(graph, node)
        else:
            print("")
            node.toStringChilds()
            sf=input("\n\nScegli figlio: ")

            for n in node.childs:
                if n.state==sf:
                    print("")
                    esplorazioneGuidataAlbero(graph, n)
                    return
            
            print("Nodo figlio non presente, spostamento non ammesso!\n")

            esplorazioneGuidataAlbero(graph, node)
    elif scelta==4:
        nNodes=int(input("Quanti nodi figli vuoi creare? "))
        while nNodes<=0:
            print("ERRORE! Numero nodi figli non ammesso!")
            nNodes=int(input("Quanti nodi figli vuoi creare? "))
        
        for i in range(nNodes):
            child=Node()
            node.addChild(child)
            child.addParent(node)
            child.assegnaModello(node)
            graph.createNodesToNetwork(child)
            graph.createEdgesToNetworkFromChild(child)

        print("\nNodi figli creati correttamente!\n")

        esplorazioneGuidataAlbero(graph, node)
    elif scelta==5:
        graph.print('Picture.html')
        print("")

        esplorazioneGuidataAlbero(graph, node)
    elif scelta==6:
        print("\nNodi foglia: ", end="")
        graph.visualizzaNodiFoglia(graph.parent)
        print("\n")

        foglie = graph.getFoglie(graph.parent)

        if len(foglie) == 0:
            print("Non sono presenti nodi foglia")
            esplorazioneGuidataAlbero(graph, n)
            return
        
        s=input("Vuoi chiudere un nodo foglia? (s,n): ")

        if(s=="s"):
            f=input("\n\nScegli nodo foglia: ").strip()
            for n in foglie:
                if n.state==f:
                    commento=input("Dimmi il commento che vuoi aggiungere al nodo: ")
                    n.assegnamento=commento
                    graph.network.add_node(int(n.state), label=n.state+"\n"+n.assegnamento, color= '#000000', size=20)
                    print("Commento aggiunto correttamente!")
                    print("Ricorda ora il nodo è chiuso, quindi non è più utilizzabile per la dimostrazione.")
                    esplorazioneGuidataAlbero(graph, n)
                    return
                
                print("Nodo foglia non presente, commento non aggiunto!\n")
        
        esplorazioneGuidataAlbero(graph, node)   
    elif scelta==7:
        print("Salvataggio dell'albero di ricorsione in corso...")
        print("Creazione del pdf in corso...")
        create_PDF(graph,node)
        esplorazioneGuidataAlbero(graph, node) 

start = True
while start:
    print("Selezionare il modello Minizinc (solo file .mzn)")
    Tk().withdraw()
    filename = askopenfilename() 
    model = Model(filename)
    gecode = Solver.lookup("gecode")
    print("Modello selezionato:")
    print(filename)

    #aggiugere checker
    checker = input("Vuoi aggiungere un checker al modello? y/n")
    if checker.strip() == 'y':
        Tk().withdraw() 
        checker = askopenfilename()
        model.add_file(checker)

    inst = Instance(gecode, model)
    res = inst.solve()
    if res.status.has_solution() == True:
        print("Il modello presenta almeno una soluzione.")
        print("Possibile soluzione: ")
        print(res)
        node = []
        node.append(Node())
        node[0].model = Model(filename)
        graph = Graph(node[0])
        print("Creazione dell'albero in corso...")
        esplorazioneGuidataAlbero(graph, graph.parent)
    else:
        print("Non ci sono soluzioni per il modello. Controlla che sia stato scritto correttamente.")
        start = False