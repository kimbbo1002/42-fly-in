from __future__ import annotations
from typing import List, Set, Optional, Tuple
from .config import ZoneType


class Drone:
    def __init__(self, id: int, x: float, y: float):
        self.id = id
        self.x = x
        self.y = y
        self.node: Node | None = None
        self.wait = -1
        self.trace: List[Tuple[float, float]] = []

    def get_next_move(
            self, connecs: List[Node | None], edges: List[Edge]
    ) -> Optional[Node]:
        ret: Node | None = None
        min_dist = float('inf')
        for connec in connecs:
            if connec and self.node:
                edge = Edge.find_edge(self.node, connec, edges)
                total_incoming = (
                    edge.exp_occupation() + connec.expect
                    + len(connec.occupation)
                )
                if (
                    connec.type == ZoneType.BLOCKED
                    or total_incoming + 1 > connec.capacity
                    or len(edge.occupation) + 1 > edge.capacity
                    or self.node.distance < connec.distance
                ):
                    continue
                elif connec.distance == -1:
                    continue
                elif (
                    connec.type == ZoneType.PRIORITY
                    and connec.distance < self.node.distance
                ):
                    connec.expect += 1
                    return connec
                elif (
                    min_dist > connec.distance
                ):
                    min_dist = connec.distance
                    ret = connec

        if ret:
            ret.expect += 1
        return ret


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
        self.trace: List[int] = []
        self.expect: int = 0


class Edge:
    def __init__(self, a: Node, b: Node, capacity: int) -> None:
        self.a = a
        self.b = b
        self.capacity = capacity
        self.occupation: Set[Drone] = set()
        self.trace: List[int] = []

    @staticmethod
    def find_edge(
        a: Node | None, b: Node | None, edges: List[Edge]
    ) -> Edge:
        ret: Edge
        for edge in edges:
            if edge.a == a and edge.b == b:
                ret = edge
                break
        return ret

    def exp_occupation(self) -> int:
        count = 0
        for drone in self.occupation:
            if drone.wait == -1:
                count += 1
        return count
