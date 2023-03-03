%Parameters: we need to specify values for these (input data)
int: NUM_NODES = 10; 
int: NUM_EDGES = 15;
array[1..NUM_EDGES,1..2] of int: edges = [|1,2|2,3|3,4|4,5|5,1|1,6|2,7|3,8|4,9|5,10|6,8|8,10|10,7|7,9|9,6|];

% Decision Variable: the solver will find the values of these
array[1..NUM_NODES] of var 1..NUM_NODES: color;

% Our Constraints 
constraint forall(e in 1..NUM_EDGES)(color[edges[e,1]] != color[edges[e,2]]);

% Our Objective Function
%solve minimize max(color);
