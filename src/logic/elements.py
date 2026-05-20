from __future__ import annotations
from typing import List, Set, Optional
from .config import ZoneType


class Drone:
    def __init__(self, id: int, x: int, y: int):
        self.id = id
        self.x = x
        self.y = y
        self.node: Node = None
        self.restriction = False

    def get_next_move(
            self, connecs: List[Node], edges: List[Edge]
    ) -> Optional[Edge]:
        ret: Node = None
        min = float('inf')
        if self.restriction is True:
            self.restriction = False
            return None
        for connec in connecs:
            edge = Edge.find_edge(self.node, connec, edges)
            if (
                connec.type == ZoneType.BLOCKED or len(connec.occupation) + 1
                > connec.capacity or len(edge.occupation) + 1 > edge.capacity
            ):
                continue
            elif connec.type == ZoneType.PRIORITY:
                if connec.distance != -1:
                    return connec
            elif connec.distance == -1:
                continue
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
        self.tmp_space: Set[Drone] = set()
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
