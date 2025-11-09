from typing import List, Dict, Tuple
from warehouse import Warehouse, Position
from robot import Robot


class WarehouseSimulation:
    def __init__(self, warehouse: Warehouse, num_robots: int = 5):
        self.warehouse = warehouse
        self.robots: List[Robot] = []
        
        self._initialize_robots(num_robots)
        
    def _initialize_robots(self, num_robots: int):
        """Initialize robots at bottom row evenly spaced."""
        for i in range(num_robots):
            x = i * (self.warehouse.width // num_robots)
            y = self.warehouse.height - 1
            robot = Robot(i, x, y)
            self.robots.append(robot)
            self.warehouse.set_robot_position(i, x, y)
    
    def assign_robot_target(self, robot_id: int, target_x: int, target_y: int):
        if robot_id < len(self.robots):
            self.robots[robot_id].set_target(target_x, target_y)
    
    def step(self):
        """Execute one simulation time step - move all robots."""
        for robot in self.robots:
            robot.move_to_target()

            pos = robot.get_current_position()
            self.warehouse.set_robot_position(robot.robot_id, pos.x, pos.y)
    
    def run(self, num_steps: int):
        for _ in range(num_steps):
            self.step()
    
    def get_total_energy(self) -> float:
        return sum(robot.get_energy_efficiency() for robot in self.robots)
    