"""
Warehouse System Simulation - Simplified
This module defines the warehouse layout storing only robot and shelf positions.
"""

from typing import List, Tuple, Dict


class Position:    
    def __init__(self, x: int, y: int):
        self.x = x
        self.y = y
    
    def __eq__(self, other):
        return self.x == other.x and self.y == other.y
    
    def __hash__(self):
        return hash((self.x, self.y))
    
    def __repr__(self):
        return f"({self.x}, {self.y})"
    
    def distance_to(self, other: 'Position') -> float:
        return ((self.x - other.x)**2 + (self.y - other.y)**2)**0.5


class Warehouse:    
    def __init__(self, width: int, height: int):
        self.width = width
        self.height = height
        
        self.shelf_positions: List[Position] = []
        self.robot_positions: Dict[int, Position] = {} 
    
    def add_shelf(self, x: int, y: int):
        position = Position(x, y)
        if position not in self.shelf_positions:
            self.shelf_positions.append(position)
    
    def add_shelves(self, positions: List[Tuple[int, int]]):
        for x, y in positions:
            self.add_shelf(x, y)
    
    def set_robot_position(self, robot_id: int, x: int, y: int):
        self.robot_positions[robot_id] = Position(x, y)
    
    def get_robot_position(self, robot_id: int) -> Position:
        return self.robot_positions.get(robot_id)
    
    def get_shelf_positions(self) -> List[Position]:
        return self.shelf_positions
    
    def get_all_robot_positions(self) -> Dict[int, Position]:
        return self.robot_positions
