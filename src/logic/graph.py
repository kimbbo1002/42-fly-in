from typing import List, Dict, Optional
from collections import deque
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
        self.distance = -1

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
        self.occupation.remove(drone)



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
            self.nodes.append
            if hub.name == "start_hub":
                self.start = node
            elif hub.name == "end_hub":
                self.end = node
        for connec in config.connections:
            self.edges.append(Edge(connec.a, connec.b, connec.max_link_capacity))
    
    def find_connection(self, node: Node) -> List[Node]:
        connections = []
        neigbor_names = []
        for edge in self.edges:
            if edge.a == node.name:
                neigbor_names.append(edge.b)
            elif edge.b == node.name:
                neigbor_names.append(edge.a)
        
        for name in neigbor_names:
            for n in self.nodes:
                if n.name == name:
                    connections.append(n)
                    break
        return connections

    def min_distance(self) -> int:
        self.end.distance = 0
        queue = deque([self.end])

        # bfs to find mininmum distance from end_hub
        while queue:
            curr = queue.popleft()
            for neighbor in self.find_connection(curr):
                if neighbor.distance == -1:
                    neighbor.distance = curr.distance + 1
                    queue.append(neighbor)


    def start_sim(self, config: Config) -> None:
        graph = Graph()
        graph.init_graph(config)

        # initializing & placing all drones at start
        for i in range(0, graph.nb_drone):
            self.start.move_in(Drone(i + 1, self.start.x, self.start.y))
        
        # calculating minimum distance for all nodes
        graph.min_distance()

        # main simulation loop
        while(len(self.end.occupation) != self.nb_drone):
            
