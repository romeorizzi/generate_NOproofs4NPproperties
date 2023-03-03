# generate_NOproofs4NPproperties
tools that support a human in producing in his attempt to produce a human NO proof for an NP-property.
The program wants to help a human subject in an attempt to obtain a demonstration by proceeding by cases, keeping the cases and sub-cases open. 
For example, the project can be used to produce a proof that a counterexample is in fact a counterexample for problems of the classes NP and CO-NP as well.
The user can build the exploration tree, creating as many children as he likes, to which he can impose constraints to try to obtain his proof. Obviously, the system warns the user if the children violate the constraints of the model.
At the basis of the project, there is the Minizinc language, therefore it is necessary that the user knows the modeling language just indicated and basic concepts of constraint programming.
The system offers a browser view of the developed tree and generates PDF reports of the demonstration steps.

--REQUIREMENTS--
- Linux environment
- Python programming language
- Minizinc Python- Python interface for Minizinc https://minizinc-python.readthedocs.io/en/latest/getting_started.html
- The following Python libraries:
    - Pyvis
    - fpdf
    - imgkit
    - tkinter

  as for now you need to install these on your system via pip. For example,
      pip install fpdf 

