from typing import List
from config import Config, ZoneType
from drone import Drone


class Node:
    def __init__(
            self,
            name: str,
            color: str,
            type: ZoneType,
            x: int,
            y: int,
            capacity: int
    ) -> None:
        self.name = name
        self.color = color
        self.type = type
        self.x = x
        self.y = y
        self.capacity = capacity
        self.occupation: List[Drone] = []
        self.distance: int

    def can_move_in(self) -> bool:
        if self.type == ZoneType.BLOCKED:
            return False
        if len(self.occupation) == self.capacity:
            return False
        return True
    
    def move_in(self, drone: Drone):
        self.occupation.append(drone)
        drone.x = self.x
        drone.y = self.y
    
    def move_out(self, drone: Drone):
        self.occupation.pop(drone)



class Edge:
    def __init__(self, a: Node, b: Node, capacity: int) -> None:
        self.a = a
        self.b = b
        self.capacity = capacity


class Graph:
    def __init__(self) -> None:
        self.nodes: List[Node] = []
        self.edges: List[Edge] = []
        self.nb_drone: int
        self.start: Node
        self.end: Node
        self.turn = 0

    def init_graph(self, config: Config) -> None:
        self.nb_drone = config.nb_drones
        for hub in config.hubs:
            node = Node(
                    hub.name, hub.color, hub.zone,
                    hub.x, hub.y, hub.max_drones
                )
            if hub.name not in ["start_hub", "end_hub"]:
                self.nodes.append(node)
            else:
                if hub.name is "start_hub":
                    self.start = node
                else:
                    self.end = node
        for connec in config.connections:
            self.edges = Edge(connec.a, connec.b, connec.max_link_capacity)
    
    def find_connection(self, node: Node) -> List[Node]:
        connections = []
        names = []
        for edge in self.edges:
            if edge.a == node.name:
                names.append(edge.a)
        
        for name in names:
            for n in self.nodes:
                if name == n.name:
                    connections.append(n)
        return connections

    def min_distance(self, node: Node) -> int:
        distances = []
        curr = node
        while (curr.name is not "end_hub"):
            

            
            
        

    def start_sim(self, config: Config) -> None:
        graph = Graph()
        graph.init_graph(config)

        # placing all drones at start
        start = self.start
        for i in range(0, graph.nb_drone):
            start.move_in(Drone(i + 1, start.x, start.y))
        
        # calculate minimum moves from end for all nodes
        for node in self.nodes:

        
        # main simulation loop
        while(len(self.end.occupation) != self.nb_drone):
            pass
