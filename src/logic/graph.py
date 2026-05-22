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
        self.start: Node | None = None
        self.end: Node | None = None
        self.turn = 0
        self.output = ""

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
        ret: Node
        for node in self.nodes:
            if node.name == name:
                ret = node
                break
        return ret

    def find_connection(self, node: Node | None) -> List[Node | None]:
        neighbors: List[Node | None] = []
        for edge in self.edges:
            if edge.a == node:
                neighbors.append(edge.b)
        return neighbors

    def min_distance(self) -> None:
        if self.end:
            self.end.distance = 0
            queue = deque([self.end])

            while queue:
                curr = queue.popleft()
                for edge in self.edges:
                    if edge.b == curr:
                        neighbor = edge.a
                        if neighbor.type == ZoneType.BLOCKED:
                            continue
                        if neighbor.distance == -1:
                            neighbor.distance = curr.distance + 1
                            if neighbor.type == ZoneType.RESTRICTED:
                                neighbor.distance += 1
                            queue.append(neighbor)

    def save_trace(self) -> None:
        for drone in self.drones:
            drone.trace.append((drone.x, drone.y))
        for node in self.nodes:
            node.trace.append(len(node.occupation))

    def sim_turn(self) -> None:
        for node in self.nodes:
            if node:
                node.expect = 0
        for drone in sorted(
            self.drones,
            key=lambda d: d.node.distance if d.node else d.id
        ):
            if drone.node:
                if drone.node == self.end:
                    continue
                if drone.wait == 1:
                    continue
                next = drone.get_next_move(self.find_connection(drone.node),
                                           self.edges)
                if not next:
                    continue
                if next.type == ZoneType.RESTRICTED:
                    drone.wait = 0
                connec = Edge.find_edge(drone.node, next, self.edges)
                connec.occupation.add(drone)
                drone.node.occupation.remove(drone)
                drone.node = next
        for edge in self.edges:
            target = edge.b
            for drone in edge.occupation.copy():
                if drone.node:
                    if target.type == ZoneType.RESTRICTED:
                        drone.wait += 1
                    if drone.wait == 1:
                        drone.x = (drone.x + target.x) / 2
                        drone.y = (drone.y + target.y) / 2
                        self.output += (
                            f"D{drone.id}-<{drone.node.name}-{target.name}>"
                        )
                    else:
                        drone.x, drone.y = target.x, target.y
                        target.occupation.add(drone)
                        edge.occupation.remove(drone)
                        drone.wait = -1
                        self.output += f"D{drone.id}-<{target.name}>"
        self.save_trace()
        self.turn += 1

    def start_sim(self, config: Config) -> None:
        self.init_graph(config)

        # initializing & placing all drones at start
        if self.start:
            for i in range(0, self.nb_drone):
                self.drones.append(Drone(i + 1, self.start.x, self.start.y))
            self.start.occupation.update(self.drones)
            for drone in self.drones:
                drone.node = self.start

        # calculating minimum distance for all nodes
        self.min_distance()

        if self.start and self.start.distance == -1:
            raise ValueError(
                "\033[0;31mCONFIG ERROR:\033[0m"
                "Invalid map: No passage found."
            )
        # main simulation loop
        self.save_trace()
        if self.end:
            while len(self.end.occupation) != self.nb_drone:
                self.sim_turn()
                self.output += "\n"

    def print_output(self) -> None:
        file_name = "output.txt"
        with open(file_name, "w") as file:
            file.write(self.output)
