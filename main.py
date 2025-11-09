#!/usr/bin/env python3
"""
Main script to demonstrate the warehouse optimization system.
Creates an initial warehouse layout with infrastructure and robots, then displays it.
"""

from warehouse import Warehouse
from robot import Robot


class RobotController:
    def __init__(self, warehouse):
        self.warehouse = warehouse
        self.robot_commands = {}  # Store command queues for each robot
        self.step_count = 0
    
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
        
        Returns:
            bool: True if any robot moved, False if no movements occurred
        """
        self.step_count += 1
        print(f"\n--- Step {self.step_count} ---")
        
        movements_made = 0
        robots_with_commands = 0
        
        for robot in self.warehouse.active_robots:
            robot_id = robot.robot_id
            
            # Check if robot has commands queued
            if robot_id in self.robot_commands and self.robot_commands[robot_id]:
                robots_with_commands += 1
                direction = self.robot_commands[robot_id].pop(0)  # Get next command
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
                    new_pos = robot.get_current_position()
                    print(f"{robot_id}: {old_pos} → {new_pos} (moved {direction})")
                    movements_made += 1
                else:
                    print(f"{robot_id}: Blocked - cannot move {direction} from {old_pos}")
        
        if robots_with_commands == 0:
            print("All robots have completed their queued commands")
            return False
        
        return movements_made > 0
    
    def execute_all_steps(self):
        """
        Execute all queued commands until none remain or all robots are blocked.
        """
        while any(commands for commands in self.robot_commands.values()):
            if not self.execute_one_step():
                break
        
        print("All queued movements completed!")
    
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

def simulate_robot_movement_queued(warehouse):
    """
    Simulate robot movement using queued commands approach.
    This demonstrates how to add movement commands incrementally.
    
    Args:
        warehouse (Warehouse): The warehouse with robots
    """
    print(f"\n" + "=" * 60)
    print(f"SIMULATING ROBOT MOVEMENT (QUEUED COMMANDS)")
    print("=" * 60)
    print("Note: Commands are added incrementally and executed step by step")
    
    # Create robot controller
    controller = RobotController(warehouse)
    
    # Phase 1: Add initial movement commands
    print("\n=== PHASE 1: Adding Initial Commands ===")
    
    # Method 1: Add commands one by one
    controller.add_command("ROBOT_001", "up")
    controller.add_command("ROBOT_001", "up") 
    controller.add_command("ROBOT_001", "up")
    
    # Method 2: Add multiple commands at once
    controller.add_commands("ROBOT_002", ["up", "up", "up", "up"])
    
    # Method 3: Add using dictionary format (like original system)
    initial_commands = {
        "ROBOT_003": ["up", "up"],
        "ROBOT_004": ["right", "right", "right"],
        "ROBOT_005": ["right", "right"]
    }
    controller.add_command_dict(initial_commands)
    
    print(f"Queue status after Phase 1: {controller.get_queue_status()}")
    print(f"Total queued commands: {controller.get_total_queued_commands()}")
    
    # Execute first few steps
    print(f"\nExecuting first 4 steps...")
    for i in range(4):
        if not controller.execute_one_step():
            break
    
    # Phase 2: Add more commands dynamically (simulating real-time planning)
    print(f"\n=== PHASE 2: Adding More Commands Dynamically ===")
    
    # Add more movements based on current positions
    more_commands = {
        "ROBOT_001": ["up", "up", "up", "up", "up", "up", "up", "up", "up", "up", "up", "right"],  # Continue to PACK_1
        "ROBOT_002": ["up", "up", "up", "up", "up", "up", "up", "up", "up", "up", "right"],  # Continue to PACK_2
        "ROBOT_003": ["up", "up", "up", "up", "up", "up", "up", "up", "up", "up", "up", "up", "right"],  # Continue to PACK_3
        "ROBOT_004": ["right", "right", "right", "right", "right", "up", "up", "up", "up", "up", "up", "up", "right"],  # Continue to PACK_4
        "ROBOT_005": ["right", "right", "right", "right", "right", "right", "right", "right", "right", "down", "down"]  # Continue to DOCK_D
    }
    controller.add_command_dict(more_commands)
    
    print(f"Queue status after Phase 2: {controller.get_queue_status()}")
    print(f"Total queued commands: {controller.get_total_queued_commands()}")
    
    # Phase 3: Execute remaining commands
    print(f"\n=== PHASE 3: Executing All Remaining Commands ===")
    controller.execute_all_steps()
    
    print(f"\nFinal queue status: {controller.get_queue_status()}")
    
    return controller



def main():
    """
    Main function to demonstrate the warehouse system.
    
    Args:
        simulation_mode (str): "queued" for incremental commands, "legacy" for all-at-once
    """
    # Create the warehouse and add infrastructure
    print("Creating warehouse layout...")
    warehouse = create_sample_warehouse()
    
    # Add robots to the warehouse
    print("Adding robots...")
    robots = create_sample_robots(warehouse)
    
    # Capture initial robot positions
    initial_positions = {}
    for robot in warehouse.active_robots:
        initial_positions[robot.robot_id] = robot.get_current_position()
    

    # Simulate robot movement using queued commands approach
    controller = simulate_robot_movement_queued(warehouse)
    
    # Final robot positions and energy consumption
    print(f"\nFinal robot positions and energy consumption:")
    for robot in warehouse.active_robots:
        status = "✓ AT TARGET" if robot.is_at_target() else f"→ {robot.distance_to_target()} units to go"
        in_aisle = "✓ In aisle" if warehouse.is_position_in_aisle(*robot.get_current_position()) else "✗ Outside aisle"
        energy_report = robot.get_energy_report()
        efficiency = f"{energy_report['energy_efficiency']:.1%}"
        print(f"  {robot.robot_id}: {robot.get_current_position()} {status} ({in_aisle})")
        print(f"    Energy: {energy_report['total_energy_spent']:.1f} units | Moves: {energy_report['successful_moves']} successful, {energy_report['blocked_attempts']} blocked | Efficiency: {efficiency}")
    
    # Display both initial and final states in one window
    print(f"\n" + "=" * 60)
    print("DISPLAYING BEFORE AND AFTER COMPARISON")
    print("=" * 60)
    print("Opening graphical visualization window with both states...")
    warehouse.visualize_before_after(
        initial_positions=initial_positions,
        title="Warehouse Robot Movement - Before and After Comparison"
    )
    
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