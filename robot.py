class Robot:
    def __init__(self, robot_id, x=0, y=0, warehouse=None):
        self.robot_id = robot_id
        self.current_position = (x, y)
        self.target_position = (x, y)
        self.warehouse = warehouse
        self.is_moving = False
        self.movement_history = [(x, y)]  # Track all positions the robot has visited
        
        # Energy tracking
        self.total_energy_spent = 0
        self.successful_moves = 0
        self.blocked_attempts = 0
        self.total_congestion_penalty = 0  # Track congestion penalty
        self.energy_per_move = 1.0  # Base energy cost for successful movement
        self.energy_per_blocked_attempt = 0.5  # Energy wasted on blocked attempts
    
    def add_congestion_penalty(self, penalty):
        """Add a penalty for moving into a congested cell."""
        self.total_congestion_penalty += penalty
        self.total_energy_spent += penalty  # Congestion contributes to energy spent
    
    def set_target_position(self, x, y):
        self.target_position = (x, y)
    
    def get_current_position(self):
        return self.current_position
    
    def get_target_position(self):
        return self.target_position
    
    def check_collision(self, new_x, new_y):
        if self.warehouse is None:
            return False
        
        if not self.warehouse.is_valid_position(new_x, new_y):
            return True
        
        for robot in self.warehouse.active_robots:
            if robot != self and robot.get_current_position() == (new_x, new_y):
                return True
        
        if self.warehouse.is_blocked_position(new_x, new_y):
            return True
        
        if not self.warehouse.is_position_in_aisle(new_x, new_y):
            return True
        
        return False
    
    def move_left(self):
        current_x, current_y = self.current_position
        new_x = current_x - 1
        
        if not self.check_collision(new_x, current_y):
            self.current_position = (new_x, current_y)
            self.movement_history.append((new_x, current_y))
            self._consume_energy_for_move()
            return True
        else:
            self._consume_energy_for_blocked_attempt()
            return False
    
    def move_right(self):
        current_x, current_y = self.current_position
        new_x = current_x + 1
        
        if not self.check_collision(new_x, current_y):
            self.current_position = (new_x, current_y)
            self.movement_history.append((new_x, current_y))
            return True
        else:
            self._consume_energy_for_blocked_attempt()
            return False
    
    def move_up(self):
        current_x, current_y = self.current_position
        new_y = current_y - 1
        
        if not self.check_collision(current_x, new_y):
            self.current_position = (current_x, new_y)
            self.movement_history.append((current_x, new_y))
            self._consume_energy_for_move()
            return True
        else:
            self._consume_energy_for_blocked_attempt()
            return False
    
    def move_down(self):
        current_x, current_y = self.current_position
        new_y = current_y + 1
        
        if not self.check_collision(current_x, new_y):
            self.current_position = (current_x, new_y)
            self.movement_history.append((current_x, new_y))
            self._consume_energy_for_move()
            return True
        else:
            self._consume_energy_for_blocked_attempt()
            return False
    
    def distance_to_target(self):
        """
        Manhattan distance
        """
        current_x, current_y = self.current_position
        target_x, target_y = self.target_position
        return abs(target_x - current_x) + abs(target_y - current_y)
    
    def is_at_target(self):
        return self.current_position == self.target_position
    
    def get_movement_history(self):
        return self.movement_history.copy()
    
    def clear_movement_history(self):
        self.movement_history = [self.current_position]
    
    def get_path_length(self):
        return len(self.movement_history) - 1
    
    def _consume_energy_for_move(self):
        self.total_energy_spent += self.energy_per_move
        self.successful_moves += 1
    
    def _consume_energy_for_blocked_attempt(self):
        self.total_energy_spent += self.energy_per_blocked_attempt
        self.blocked_attempts += 1
    
    def get_total_energy_spent(self):
        return self.total_energy_spent
    
    def get_successful_moves(self):
        return self.successful_moves
    
    def get_blocked_attempts(self):
        return self.blocked_attempts
    
    def get_energy_efficiency(self):
        """
        Efficiency ratio (successful moves / total attempts)
        """
        total_attempts = self.successful_moves + self.blocked_attempts
        if total_attempts == 0:
            return 1.0  # No attempts made yet
        return self.successful_moves / total_attempts
    
    def get_energy_report(self):
        """
        Get a comprehensive energy usage report for the robot.
        
        """
        return {
            'robot_id': self.robot_id,
            'total_energy_spent': self.total_energy_spent,
            'successful_moves': self.successful_moves,
            'blocked_attempts': self.blocked_attempts,
            'total_attempts': self.successful_moves + self.blocked_attempts,
            'energy_efficiency': self.get_energy_efficiency(),
            'distance_to_target': self.distance_to_target(),
            'path_length': self.get_path_length(),
            'total_congestion_penalty': self.total_congestion_penalty
        }

