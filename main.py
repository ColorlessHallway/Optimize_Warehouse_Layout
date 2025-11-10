"""
Main script to demonstrate the warehouse optimization system.
Creates an initial warehouse layout with infrastructure and robots, then displays it.
"""

from warehouse import Warehouse
from robot import Robot
from pathfinding import a_star_search
import random


class RobotController:
    def __init__(self, warehouse):
        self.warehouse = warehouse
        self.robot_commands = {}  # Store command queues for each robot
        self.step_count = 0
    
    def generate_path_commands(self, robot_id, is_replanning=False):
        """
        Generates a path for a robot using A* and adds the corresponding
        movement commands to its queue.
        """
        robot = self.warehouse.get_robot_by_id(robot_id)
        if not robot:
            print(f"Robot {robot_id} not found.")
            return

        # Clear old commands before generating a new path, especially for re-planning
        if robot_id in self.robot_commands:
            self.robot_commands[robot_id].clear()

        start = robot.get_current_position()
        goal = robot.get_target_position()
        
        # Get current positions of all robots for collision avoidance
        all_robot_positions = self.warehouse.get_robot_positions()

        # Find the path using A*
        path = a_star_search(self.warehouse, start, goal, robot_id, all_robot_positions)

        if path and len(path) > 1:
            # Convert path (list of coordinates) to movement commands
            directions = self.convert_path_to_directions(path)
            self.add_commands(robot_id, directions)
            if is_replanning:
                print(f"Re-planned path for {robot_id} from {start} to {goal} with {len(directions)} moves.")
            else:
                print(f"Path found for {robot_id} from {start} to {goal} with {len(directions)} moves.")
        else:
            if is_replanning:
                print(f"Could not find a new path for {robot_id} from {start} to {goal}. Waiting.")
            else:
                print(f"No path found for {robot_id} from {start} to {goal}.")

    def convert_path_to_directions(self, path):
        """
        Converts a list of (x, y) coordinates to a list of movement directions.
        
        Args:
            path (list): A list of (x, y) tuples.
            
        Returns:
            list: A list of direction strings ("up", "down", "left", "right").
        """
        directions = []
        for i in range(len(path) - 1):
            current_pos = path[i]
            next_pos = path[i+1]
            
            dx = next_pos[0] - current_pos[0]
            dy = next_pos[1] - current_pos[1]
            
            if dx == 1:
                directions.append("right")
            elif dx == -1:
                directions.append("left")
            elif dy == 1:
                directions.append("down")
            elif dy == -1:
                directions.append("up")
        return directions
    
    def add_command(self, robot_id, direction):
        """
        Args:
            robot_id (str): ID of the robot
            direction (str): Direction to move ("up", "down", "left", "right")
        """
        if robot_id not in self.robot_commands:
            self.robot_commands[robot_id] = []
        
        self.robot_commands[robot_id].append(direction)
    
    def add_commands(self, robot_id, directions):
        """
        Add multiple movement commands to a robot's queue.
        
        Args:
            robot_id (str): ID of the robot
            directions (list): List of directions to move
        """
        if robot_id not in self.robot_commands:
            self.robot_commands[robot_id] = []
        
        self.robot_commands[robot_id].extend(directions)
    
    def add_command_dict(self, command_dict):
        """
        Add commands using a dictionary format like the original system.
        
        Args:
            command_dict (dict): Dictionary with robot_id as key and list of directions as value
        """
        for robot_id, directions in command_dict.items():
            self.add_commands(robot_id, directions)
    
    
    def execute_one_step(self):
        """
        Execute one movement step for all robots that have commands queued.
        If a robot is blocked, it will attempt to re-plan its path.
        
        Returns:
            bool: True if any robot moved, False if no movements occurred
        """
        self.step_count += 1
        print(f"\n--- Step {self.step_count} ---")
        
        movements_made = 0
        robots_with_commands = 0
        
        robots_to_replan = []

        for robot in self.warehouse.active_robots:
            robot_id = robot.robot_id
            
            # If a robot has no commands but hasn't reached its target, generate a path
            if not self.robot_commands.get(robot_id) and not robot.is_at_target():
                self.generate_path_commands(robot_id)

            # Check if robot has commands queued
            if robot_id in self.robot_commands and self.robot_commands[robot_id]:
                robots_with_commands += 1
                direction = self.robot_commands[robot_id][0]  # Peek at next command
                old_pos = robot.get_current_position()
                
                # Execute movement
                success = False
                if direction == "up":
                    success = robot.move_up()
                elif direction == "down":
                    success = robot.move_down()
                elif direction == "left":
                    success = robot.move_left()
                elif direction == "right":
                    success = robot.move_right()
                
                if success:
                    self.robot_commands[robot_id].pop(0)  # Remove command only on success
                    new_pos = robot.get_current_position()
                    
                    # Record congestion
                    self.warehouse.record_congestion(new_pos[0], new_pos[1])
                    
                    # Add congestion penalty and check for re-planning
                    congestion_level = self.warehouse.get_congestion(new_pos[0], new_pos[1])
                    if congestion_level > 1:
                        # Apply a small penalty for moving into a congested cell
                        penalty = 1 * (congestion_level - 1)
                        robot.add_congestion_penalty(penalty)
                        
                        # Re-plan if moving into a congested area
                        print(f"{robot_id}: Moved into congested area at {new_pos}. Re-planning path.")
                        if robot_id not in robots_to_replan:
                            robots_to_replan.append(robot_id)

                    print(f"{robot_id}: {old_pos} → {new_pos} (moved {direction})")
                    movements_made += 1
                else:
                    print(f"{robot_id}: Blocked trying to move {direction}. Re-planning path.")
                    if robot_id not in robots_to_replan:
                        robots_to_replan.append(robot_id)
        
        # Re-plan paths for blocked robots after all other robots have attempted to move
        if robots_to_replan:
            for robot_id in robots_to_replan:
                self.generate_path_commands(robot_id, is_replanning=True)

        if robots_with_commands == 0 and not any(not r.is_at_target() for r in self.warehouse.active_robots):
            print("All robots have completed their tasks.")
            return False
        
        if movements_made == 0 and robots_with_commands > 0 and not robots_to_replan:
            print("Gridlock detected: No robots could move, and no re-planning was possible.")
            return False
            
        return True
    
    def execute_all_steps(self, max_steps=50):
        """
        Execute all queued commands until all robots reach their targets or gridlock occurs.
        Includes a timeout to prevent infinite loops.
        """
        # Reset congestion map at the start of a full execution run
        self.warehouse.reset_congestion()
        
        # Initial path generation for all robots
        for robot in self.warehouse.get_active_robots():
            if not robot.is_at_target():
                self.generate_path_commands(robot.robot_id)

        # Loop until all robots are at their targets or max_steps is reached
        while any(not robot.is_at_target() for robot in self.warehouse.get_active_robots()):
            if self.step_count > max_steps:
                print(f"Simulation timed out after {max_steps} steps. Aborting.")
                break
            if not self.execute_one_step():
                break
        
        print("\nAll movements completed or gridlock/timeout reached!")
    
    def get_queue_status(self):
        """
        Get the current status of all robot movement queues.
        
        Returns:
            dict: Dictionary with robot IDs and their queue lengths
        """
        return {robot_id: len(queue) for robot_id, queue in self.robot_commands.items()}
    
    def clear_all_queues(self):
        """Clear all queued commands for all robots."""
        self.robot_commands.clear()
        self.step_count = 0
    
    def get_total_queued_commands(self):
        """Get total number of commands across all robot queues."""
        return sum(len(queue) for queue in self.robot_commands.values())


def create_sample_warehouse():
    # Create a 20x15 warehouse
    warehouse = Warehouse(20, 15)
    
    # Add entry docks along the bottom edge
    warehouse.add_entry_dock(2, 14, "DOCK_A")
    warehouse.add_entry_dock(7, 14, "DOCK_B")
    warehouse.add_entry_dock(12, 14, "DOCK_C")
    warehouse.add_entry_dock(17, 14, "DOCK_D")
    
    # Add packing stations along the top edge
    warehouse.add_packing_station(3, 0, "PACK_1")
    warehouse.add_packing_station(8, 0, "PACK_2")
    warehouse.add_packing_station(13, 0, "PACK_3")
    warehouse.add_packing_station(18, 0, "PACK_4")
    
    # Create main horizontal aisles
    warehouse.add_aisle(0, 2, 19, 2, "MAIN_AISLE_1")
    warehouse.add_aisle(0, 7, 19, 7, "MAIN_AISLE_2")
    warehouse.add_aisle(0, 12, 19, 12, "MAIN_AISLE_3")
    
    # Create vertical connecting aisles that connect to entry docks and packing stations
    warehouse.add_aisle(2, 0, 2, 14, "DOCK_A_CONNECTOR")  # Connects DOCK_A and area near PACK_1
    warehouse.add_aisle(3, 0, 3, 2, "PACK_1_CONNECTOR")   # Connects PACK_1 to main aisle
    warehouse.add_aisle(7, 0, 7, 14, "DOCK_B_CONNECTOR")  # Connects DOCK_B and area near PACK_2
    warehouse.add_aisle(8, 0, 8, 2, "PACK_2_CONNECTOR")   # Connects PACK_2 to main aisle
    warehouse.add_aisle(12, 0, 12, 14, "DOCK_C_CONNECTOR") # Connects DOCK_C and area near PACK_3
    warehouse.add_aisle(13, 0, 13, 2, "PACK_3_CONNECTOR")  # Connects PACK_3 to main aisle
    warehouse.add_aisle(17, 0, 17, 14, "DOCK_D_CONNECTOR") # Connects DOCK_D and area near PACK_4
    warehouse.add_aisle(18, 0, 18, 2, "PACK_4_CONNECTOR")  # Connects PACK_4 to main aisle
    
    # Additional vertical aisles for better connectivity
    warehouse.add_aisle(4, 0, 4, 14, "VERTICAL_1")
    warehouse.add_aisle(9, 0, 9, 14, "VERTICAL_2")
    warehouse.add_aisle(14, 0, 14, 14, "VERTICAL_3")
    
    # Add storage areas (blocked positions to simulate shelving)
    # Avoid blocking the connector aisles (x=2,7,12,17) and main connector paths
    
    # Storage block 1 (left side)
    for x in range(0, 2):
        for y in range(3, 6):
            warehouse.add_blocked_position(x, y)
    
    # Storage block 2 (between connectors)
    for x in range(5, 7):
        for y in range(3, 6):
            warehouse.add_blocked_position(x, y)
    
    # Storage block 3 (between connectors)
    for x in range(10, 12):
        for y in range(3, 6):
            warehouse.add_blocked_position(x, y)
    
    # Storage block 4 (between connectors)  
    for x in range(15, 17):
        for y in range(3, 6):
            warehouse.add_blocked_position(x, y)
    
    # Storage block 5 (left side)
    for x in range(0, 2):
        for y in range(8, 11):
            warehouse.add_blocked_position(x, y)
    
    # Storage block 6 (between connectors)
    for x in range(5, 7):
        for y in range(8, 11):
            warehouse.add_blocked_position(x, y)
    
    # Storage block 7 (between connectors)
    for x in range(10, 12):
        for y in range(8, 11):
            warehouse.add_blocked_position(x, y)
    
    # Storage block 8 (between connectors)
    for x in range(15, 17):
        for y in range(8, 11):
            warehouse.add_blocked_position(x, y)
    
    return warehouse


def create_random_warehouse(width, height, num_robots, storage_density=0.8):
    """
    Generates a warehouse with a randomized layout.

    Args:
        width (int): The width of the warehouse.
        height (int): The height of the warehouse.
        num_robots (int): The number of robots, used to determine the number of docks/stations.
        storage_density (float): The percentage of non-aisle space to be filled with storage.

    Returns:
        Warehouse: A new warehouse instance with a random layout.
    """
    warehouse = Warehouse(width, height)
    
    num_docks = num_robots
    num_stations = num_robots

    # --- Create Docks and Packing Stations ---
    # Ensure they don't overlap and have some spacing
    available_x_dock = list(range(1, width - 1))
    dock_xs = sorted(random.sample(available_x_dock, min(num_docks, len(available_x_dock))))
    
    available_x_station = list(range(1, width - 1))
    station_xs = sorted(random.sample(available_x_station, min(num_stations, len(available_x_station))))

    dock_positions = []
    for i, x in enumerate(dock_xs):
        y = height - 1
        warehouse.add_entry_dock(x, y, f"DOCK_{i}")
        dock_positions.append((x, y))

    station_positions = []
    for i, x in enumerate(station_xs):
        y = 0
        warehouse.add_packing_station(x, y, f"PACK_{i}")
        station_positions.append((x, y))

    # --- Create Aisles ---
    all_aisle_xs = sorted(list(set(dock_xs + station_xs)))
    
    # Create vertical aisles connecting all docks and stations
    for x in all_aisle_xs:
        warehouse.add_aisle(x, 0, x, height - 1, f"V_AISLE_{x}")

    # Create a few horizontal aisles for connectivity
    num_horizontal_aisles = min(height // 4, 4)
    available_y_aisle = list(range(2, height - 2))
    aisle_ys = random.sample(available_y_aisle, min(num_horizontal_aisles, len(available_y_aisle)))
    for i, y in enumerate(aisle_ys):
        warehouse.add_aisle(0, y, width - 1, y, f"H_AISLE_{i}")

    # --- Create Storage Areas ---
    for x in range(width):
        for y in range(height):
            # Check if the position is already part of an aisle, dock, or station
            if not warehouse.is_position_in_aisle(x, y):
                # Add storage with a certain probability
                if random.random() < storage_density:
                    warehouse.add_blocked_position(x, y)
    
    return warehouse, dock_positions, station_positions


def create_sample_robots(warehouse):
    # Create robots at entry docks (on the aisle connectors)
    robot1 = warehouse.create_and_add_robot("ROBOT_001", 2, 14)  # At DOCK_A
    robot1.set_target_position(3, 0)  # Target: PACK_1
    
    robot2 = warehouse.create_and_add_robot("ROBOT_002", 7, 14)  # At DOCK_B
    robot2.set_target_position(8, 0)  # Target: PACK_2
    
    robot3 = warehouse.create_and_add_robot("ROBOT_003", 12, 14)  # At DOCK_C
    robot3.set_target_position(13, 0)  # Target: PACK_3
    
    # Create additional robots in the warehouse
    robot4 = warehouse.create_and_add_robot("ROBOT_004", 9, 7)  # On main aisle
    robot4.set_target_position(18, 0)  # Target: PACK_4
    
    robot5 = warehouse.create_and_add_robot("ROBOT_005", 4, 2)  # On main aisle
    robot5.set_target_position(17, 14)  # Target: DOCK_D
    
    return [robot1, robot2, robot3, robot4, robot5]

def simulate_robot_movement_with_astar(warehouse, initial_positions, visualize=True):
    """
    Simulate robot movement using A* pathfinding.
    """
    print(f"\n" + "=" * 60)
    print(f"SIMULATING ROBOT MOVEMENT (A* PATHFINDING)")
    print("=" * 60)
    
    # Create robot controller and store initial positions
    controller = RobotController(warehouse)
    controller.initial_positions = initial_positions
    
    # Generate paths for all robots
    print("\n=== Generating Paths with A* ===")
    for robot in warehouse.get_active_robots():
        controller.generate_path_commands(robot.robot_id)
    
    print(f"\nInitial queue status: {controller.get_queue_status()}")
    print(f"Total queued commands: {controller.get_total_queued_commands()}")
    
    # Execute all commands
    print(f"\n=== Executing All Commands ===")
    controller.execute_all_steps()
    
    print(f"\nFinal queue status: {controller.get_queue_status()}")
    
    if visualize:
        # Final robot positions and energy consumption
        print(f"\nFinal robot positions and energy consumption:")
        for robot in warehouse.active_robots:
            status = "✓ AT TARGET" if robot.is_at_target() else f"→ {robot.distance_to_target()} units to go"
            in_aisle = "✓ In aisle" if warehouse.is_position_in_aisle(*robot.get_current_position()) else "✗ Outside aisle"
            energy_report = robot.get_energy_report()
            efficiency = f"{energy_report['energy_efficiency']:.1%}"
            print(f"  {robot.robot_id}: {robot.get_current_position()} {status} ({in_aisle})")
            print(f"    Energy: {energy_report['total_energy_spent']:.1f} units | Moves: {energy_report['successful_moves']} | Blocked: {energy_report['blocked_attempts']} | Congestion Penalty: {energy_report['total_congestion_penalty']:.1f}")
        
        # Display both initial and final states in one window
        print(f"\n" + "=" * 60)
        print("DISPLAYING BEFORE AND AFTER COMPARISON")
        print("=" * 60)
        print("Opening graphical visualization window with both states...")
        warehouse.visualize_before_after(
            initial_positions=controller.initial_positions,
            title="Warehouse Robot Movement - Before and After Comparison"
        )
        
        # Display congestion map
        print("\nVisualizing path congestion...")
        warehouse.visualize_congestion_map()

    return controller



def main():
    """
    Main function to demonstrate the warehouse system.
    """
    # --- OPTION 1: Create a warehouse with a pre-defined layout ---
    # print("Creating warehouse with a static layout...")
    # warehouse = create_sample_warehouse()
    # print("Adding robots...")
    # robots = create_sample_robots(warehouse)

    # --- OPTION 2: Create a warehouse with a randomized layout ---
    print("Creating warehouse with a random layout...")
    num_robots = 5
    warehouse, dock_positions, station_positions = create_random_warehouse(20, 20, num_robots)
    
    print("Adding robots to random docks and assigning unique stations...")
    robots = []
    
    # Ensure we have unique start and target positions for each robot
    random.shuffle(dock_positions)
    random.shuffle(station_positions)

    initial_positions = {}
    for i in range(num_robots):
        robot_id = f"ROBOT_{i:03d}"
        
        # Pop a unique start and target position for each robot
        if not dock_positions or not station_positions:
            print("Warning: Not enough unique docks or stations for all robots.")
            break
            
        start_pos = dock_positions.pop()
        target_pos = station_positions.pop()
        
        robot = warehouse.create_and_add_robot(robot_id, start_pos[0], start_pos[1])
        robot.set_target_position(target_pos[0], target_pos[1])
        robots.append(robot)
        initial_positions[robot_id] = start_pos

    # Simulate robot movement using A* pathfinding
    controller = simulate_robot_movement_with_astar(warehouse, initial_positions, visualize=True)
    
    print(f"\n" + "=" * 60)
    print("DEMONSTRATION COMPLETE")
    print("=" * 60)


def demo_incremental_usage():
    """
    Show practical examples of how to use incremental commands.
    """
    print(f"\n" + "=" * 80)
    print("PRACTICAL INCREMENTAL COMMAND EXAMPLES")
    print("=" * 80)
    
    # Create a simple setup
    warehouse = create_sample_warehouse()
    robot = Robot("TEST_ROBOT", x=2, y=14, warehouse=warehouse)
    robot.set_target_position(3, 0)
    warehouse.add_robot(robot)
    
    controller = RobotController(warehouse)
    
    print("Example 1: Adding commands one by one")
    print("controller.add_command('TEST_ROBOT', 'up')")
    controller.add_command("TEST_ROBOT", "up")
    
    print("controller.add_command('TEST_ROBOT', 'up')")  
    controller.add_command("TEST_ROBOT", "up")
    
    print(f"Queue status: {controller.get_queue_status()}")
    
    print("\nExample 2: Adding multiple commands")
    print("controller.add_commands('TEST_ROBOT', ['up', 'up', 'right'])")
    controller.add_commands("TEST_ROBOT", ["up", "up", "right"])
    
    print(f"Queue status: {controller.get_queue_status()}")
    
    print("\nExample 3: Using dictionary format")
    commands = {"TEST_ROBOT": ["up", "up"]}
    print(f"controller.add_command_dict({commands})")
    controller.add_command_dict(commands)
    
    print(f"Final queue status: {controller.get_queue_status()}")
    print(f"Total commands queued: {controller.get_total_queued_commands()}")
    
    print("\nExecuting all commands...")
    controller.execute_all_steps()
    
    # Show energy report
    energy_report = robot.get_energy_report()
    print(f"\nEnergy Report:")
    print(f"  Total energy: {energy_report['total_energy_spent']:.1f} units")
    print(f"  Efficiency: {energy_report['energy_efficiency']:.1%}")


if __name__ == "__main__":
    # Run the main queued simulation
    main()
    
    # Uncomment below to see practical examples
    # demo_incremental_usage()