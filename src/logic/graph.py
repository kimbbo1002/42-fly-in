from typing import List
from collections import deque
from .config import Config, ZoneType
from .elements import Node, Edge, Drone


class Graph:
    def __init__(self) -> None:
        self.nodes: List[Node] = []
        self.edges: List[Edge] = []
        self.drones: List[Drone] = []
        self.nb_drone: int
        self.start: Node = None
        self.end: Node = None
        self.turn = 0

    def init_graph(self, config: Config) -> None:
        self.nb_drone = config.nb_drones
        for hub in config.hubs:
            node = Node(
                    hub.name, hub.color, hub.zone,
                    hub.x, hub.y, hub.max_drones
                )
            self.nodes.append(node)
            if hub.name == config.start:
                self.start = node
                self.start.capacity = self.nb_drone
            elif hub.name == config.end:
                self.end = node
                self.end.capacity = self.nb_drone
        for connec in config.connections:
            a = self.find_node(connec.a)
            b = self.find_node(connec.b)
            self.edges.append(
                Edge(a, b, connec.max_link_capacity))
    
    def find_node(self, name: str) -> Node:
        for node in self.nodes:
            if node.name == name:
                return node

    def find_connection(self, node: Node) -> List[Node]:
        neighbors = []
        for edge in self.edges:
            if edge.a == node:
                neighbors.append(edge.b)
        return neighbors

    def min_distance(self) -> None:
        self.end.distance = 0
        queue = deque([self.end])

        while queue:
            curr = queue.popleft()
            for edge in self.edges:
                if edge.b == curr:
                    neighbor = edge.a
                    if neighbor.distance == -1:
                        neighbor.distance = curr.distance + 1
                        if neighbor.type == ZoneType.RESTRICTED:
                            neighbor.distance += 3
                        queue.append(neighbor)

    def sim_turn(self) -> None:
        for drone in self.drones:
            if drone.node == self.end:
                continue
            next = drone.get_next_move(self.find_connection(drone.node),
                                       self.edges)
            if not next:
                continue
            connec = Edge.find_edge(drone.node, next, self.edges)
            connec.occupation.add(drone)
            drone.node.occupation.remove(drone)
            drone.node = next
        for edge in self.edges:
            target = edge.b
            for drone in edge.occupation:
                if target.type == ZoneType.RESTRICTED:
                    drone.restriction = True
                drone.x, drone.y = target.x, target.y
            target.tmp_space.update(edge.occupation)
            edge.occupation.clear()
        self.turn += 1
        print(f"turn: {self.turn}")

    def start_sim(self, config: Config) -> None:
        self.init_graph(config)

        # initializing & placing all drones at start
        for i in range(0, self.nb_drone):
            self.drones.append(Drone(i + 1, self.start.x, self.start.y))
        self.start.occupation.update(self.drones)
        for drone in self.drones:
            drone.node = self.start

        # calculating minimum distance for all nodes
        self.min_distance()

        # main simulation loop
        while len(self.end.occupation) != self.nb_drone:
            self.sim_turn()
            for node in self.nodes:
                node.occupation.update(node.tmp_space)
                node.tmp_space.clear()
