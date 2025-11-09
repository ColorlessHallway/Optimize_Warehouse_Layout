from warehouse import Position


class Robot:

    
    def __init__(self, robot_id: int, current_x: int, current_y: int):
        self.robot_id = robot_id
        self.current_position = Position(current_x, current_y)
        self.target_position = None  # Position or None
        self.energy_efficiency = 0.0  # Total energy consumed
    
    def set_target(self, target_x: int, target_y: int):
        self.target_position = Position(target_x, target_y)
    
    def move_to_target(self):
        """
        Move one step towards the target and update energy efficiency.
        """
        if self.target_position is None:
            return
        
        # Simple movement: one step at a time
        dx = self.target_position.x - self.current_position.x
        dy = self.target_position.y - self.current_position.y
        
        # Move one step in the direction with larger difference
        if abs(dx) > abs(dy):
            step_x = 1 if dx > 0 else -1
            step_y = 0
        elif abs(dy) > 0:
            step_x = 0
            step_y = 1 if dy > 0 else -1
        else:
            # Already at target
            return
        
        # Update position
        new_x = self.current_position.x + step_x
        new_y = self.current_position.y + step_y
        
        # Calculate energy cost for this movement
        distance = ((step_x)**2 + (step_y)**2)**0.5
        self.energy_efficiency += distance
        
        # Update current position
        self.current_position = Position(new_x, new_y)
    
    def is_at_target(self) -> bool:
        """Check if robot has reached its target."""
        if self.target_position is None:
            return True
        return self.current_position == self.target_position
    
    def get_current_position(self) -> Position:
        """Get current position."""
        return self.current_position
    
    def get_target_position(self) -> Position:
        """Get target position."""
        return self.target_position
    
    def get_energy_efficiency(self) -> float:
        """Get total energy consumed."""
        return self.energy_efficiency
