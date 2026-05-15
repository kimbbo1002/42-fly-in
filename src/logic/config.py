import sys
from typing import Dict, Any, List
from enum import Enum
from pydantic import (
    BaseModel,
    field_validator,
    model_validator,
)
from enums import ConfigOptions, Colors


class ZoneType(Enum):
    NORMAL = "normal"
    BLOCKED = "blocked"
    RESTRICTED = "restricted"
    PRIORITY = "priority"

class Hub(BaseModel):
    name: str
    x: int
    y: int
    zone: ZoneType = ZoneType.NORMAL
    color: str = "none"
    max_drones: int = 1

    @field_validator("name")
    def validate_name(cls, v):
        if ' ' in v or '-' in v:
            raise ValueError(
                "Hub zone names cannot include space or dash"
            )
        return v
    
    @field_validator("max_drones")
    def validate_capacity(cls, v):
        if v <= 0:
            raise ValueError("max_drones must be a positive integer")
        return v

class Connection(BaseModel):
    a: str
    b: str
    max_link_capacity: int = 1

    @field_validator("max_link_capacity")
    def validate_capacity(cls, v):
        if v <= 0:
            raise ValueError("max_link_capacity must be a positive integer")
        return v


class Config(BaseModel):
    nb_drones: int
    start: str
    end: str
    hubs: List[Hub]
    connections: List[Connection]

    @model_validator(mode="after")
    def validate_logic(self) -> "Config":
        names = [h.name for h in self.hubs]
        coords = [(h.x, h.y) for h in self.hubs]

        # check if name / coordinate are unique
        if len(set(names)) != len(names):
            raise ValueError("All hub names must be unique")
        if len(set(coords)) != len(coords):
            raise ValueError("All hub coordinates must be unique")
        
        # check if start / end are defined
        if self.start not in names:
            raise ValueError("Start hub is not defined")
        if self.end not in names:
            raise ValueError("End hub is not defined")        

        # check duplicate connections
        connections = set()
        for conn in self.connections:
            if conn.a not in names or conn.b not in names:
                raise ValueError(
                    f"Connection links undefined zones: {conn.a}-{conn.b}"
                )
            pair = set([conn.a, conn.b])
            if pair in connections:
                raise ValueError(
                    f"Duplicate connection detected: {conn.a}-{conn.b}"
                )
            connections.add(pair)
        
        return self


def parse_metadata(metadata: str) -> Dict[str, Any]:
    data = {}
    items = metadata.strip("[] ").split()
    for item in items:
        try:
            key, val = item.split('=')
            if key == "max_drones":
                val = int(val)
            data[key] = val
        except ValueError:
            raise ValueError(f"Invalid metadata format: {item}")
    return data


def parse_raw_config(file_name: str) -> Dict[str, Any]:
    raw = {"hubs": [], "connections": [], "nb_drones": None, "start": None, "end": None}

    with open(file_name, "r") as file:
        for line_num, line in enumerate(file, 1):
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            if line_num == 1 and not line.startswith("nb_drones"):
                raise ValueError("First line must define 'nb_drones'")
            key, _, val = line.partition(':')
            val = val.strip()
            try:
                if key == 'nb_drones':
                    raw['nb_drones'] = int(val)
                    if raw['nb_drones'] <= 0:
                        raise ValueError(
                            'nb_drones must be a positive intger'
                        )
                elif key in ['start_hub', 'end_hub', 'hub']:
                    parts = val.split()
                    if len(parts) > 4:
                        raise ValueError(f"Too many arguments: {parts}")
                    name, x, y = parts[0], int(parts[1]), int(parts[2])
                    hub_data = {"name": name, "x": x, "y": y}
                    if len(parts) > 3:
                        hub_data.update(parse_metadata(parts[3]))
                        raw['hubs'].append(hub_data)
                        if key == "start_hub":
                            raw['start'] = name
                        elif key == "end_hub":
                            raw["end"] = name
                elif key == "connection":
                    connec, _, meta = val.partition(' ')
                    a, b = connec.split('-')
                    connec_data = {"a": a, "b": b}
                    if meta:
                        connec_data.update(parse_metadata(meta))
                    raw["connections"].append(connec_data)
            except Exception as e:
                raise ValueError(f"Error parsing line {line_num}: {e}")
    return raw


def check_config() -> Config:
    if len(sys.argv) < 2:
        raise ValueError("Usage: python script.py <config_file>")
    try:
        raw_data = parse_raw_config(sys.argv[1])
        return Config(**raw_data)
    except Exception as e:
        raise ValueError(
            f"{Colors.RED}CONFIG ERROR: {Colors.RESET}{e}"
        )