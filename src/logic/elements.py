from __future__ import annotations
from typing import List, Set, Optional
from .config import ZoneType


class Drone:
    def __init__(self, id: int, x: int, y: int):
        self.id = id
        self.x = x
        self.y = y
        self.node: Node = None
        self.wait = -1

    def get_next_move(
            self, connecs: List[Node], edges: List[Edge]
    ) -> Optional[Node]:
        ret: Node = None
        min = float('inf')
        for connec in connecs:
            edge = Edge.find_edge(self.node, connec, edges)
            if (
                connec.type == ZoneType.BLOCKED or edge.exp_occupation() + 1
                > connec.capacity or len(edge.occupation) + 1 > edge.capacity
            ):
                continue
            elif connec.distance == -1:
                continue
            elif (connec.type == ZoneType.PRIORITY
                  and connec.distance < self.node.distance):
                return connec
            elif min > connec.distance:
                min = connec.distance
                ret = connec

        if ret:
            return ret
        else:
            return None


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
        self.occupation: Set[Drone] = set()
        self.distance = -1
        self.edge_capacity = 0


class Edge:
    def __init__(self, a: Node, b: Node, capacity: int) -> None:
        self.a = a
        self.b = b
        self.capacity = capacity
        self.occupation: Set[Drone] = set()

    @staticmethod
    def find_edge(a: Node, b: Node, edges: List[Edge]) -> Edge:
        for edge in edges:
            if edge.a == a and edge.b == b:
                return edge

    def exp_occupation(self) -> int:
        count = 0
        for drone in self.occupation:
            if drone.wait == -1:
                count += 1
        return count
