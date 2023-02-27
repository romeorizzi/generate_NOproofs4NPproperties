%Parameters: we need to specify values for these (input data)
int: NUM_NODES = 4; 
int: NUM_EDGES = 4;
array[1..NUM_EDGES,1..2] of int: edges = [|1, 2|1, 3|2,3|3,4|];

% Decision Variable: the solver will find the values of these
array[1..NUM_NODES] of var 1..NUM_NODES: color;

% Our Constraints 
constraint forall(e in 1..NUM_EDGES)(color[edges[e,1]] != color[edges[e,2]]);

% Our Objective Function
%solve minimize max(color);