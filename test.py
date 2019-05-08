import networkx as nx

g = nx.DiGraph()
g.add_node("a")
g.add_node("b")
g.add_node("c")
g.add_edge("a" , "b",weight=1)
g.add_edge("b" , "a",weight=6)
g.add_edge("a" , "c",weight=1)
g.add_edge("c" , "a",weight=6)
g.add_edge("b" , "c",weight=3)


print(nx.dijkstra_path_length(g,"a","b"))