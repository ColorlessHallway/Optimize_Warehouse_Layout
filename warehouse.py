from robot import Robot
import matplotlib
matplotlib.use('TkAgg')  # Use TkAgg backend for better Windows compatibility
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import numpy as np


class Warehouse:
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.entry_docks = []
        self.packing_stations = []
        self.aisles = []
        self.active_robots = []
        self.blocked_positions = set()
        self.congestion_map = {}  # To track path congestion

    def record_congestion(self, x, y):
        """Record that a robot has passed through a certain cell."""
        pos = (x, y)
        self.congestion_map[pos] = self.congestion_map.get(pos, 0) + 1

    def get_congestion(self, x, y):
        """Get the congestion level of a cell."""
        #print(f"Getting congestion for position: ({x}, {y}): {self.congestion_map.get((x, y), 0)}")
        return self.congestion_map.get((x, y), 0)

    def reset_congestion(self):
        """Reset the congestion map."""
        #print(f"Resetting congestion map: {self.congestion_map}")
        self.congestion_map.clear()
        
    def add_entry_dock(self, x, y, dock_id=None):
        dock = {
            'position': (x, y),
            'dock_id': dock_id or f"dock_{len(self.entry_docks)}"
        }
        self.entry_docks.append(dock)
        self.blocked_positions.add((x, y))
    
    def add_packing_station(self, x, y, station_id=None):
        station = {
            'position': (x, y),
            'station_id': station_id or f"station_{len(self.packing_stations)}"
        }
        self.packing_stations.append(station)
        #self.blocked_positions.add((x, y))
    
    def add_aisle(self, start_x, start_y, end_x, end_y, aisle_id=None):
        aisle = {
            'start': (start_x, start_y),
            'end': (end_x, end_y),
            'aisle_id': aisle_id or f"aisle_{len(self.aisles)}",
            'positions': []
        }
        
        if start_x == end_x: 
            min_y, max_y = min(start_y, end_y), max(start_y, end_y)
            aisle['positions'] = [(start_x, y) for y in range(min_y, max_y + 1)]
        elif start_y == end_y: 
            min_x, max_x = min(start_x, end_x), max(start_x, end_x)
            aisle['positions'] = [(x, start_y) for x in range(min_x, max_x + 1)]
        else:
            aisle['positions'] = [(start_x, y) for y in range(start_y, end_y + 1)]
            aisle['positions'].extend([(x, end_y) for x in range(start_x + 1, end_x + 1)])
        
        self.aisles.append(aisle)
    
    def add_robot(self, robot):
        if isinstance(robot, Robot):
            robot.warehouse = self 
            self.active_robots.append(robot)
        else:
            raise TypeError("Only Robot instances can be added to the warehouse")
    
    def create_and_add_robot(self, robot_id, x=0, y=0):
        robot = Robot(robot_id, x, y, self)
        self.active_robots.append(robot)
        return robot
    
    def remove_robot(self, robot_id):
        for i, robot in enumerate(self.active_robots):
            if robot.robot_id == robot_id:
                self.active_robots.pop(i)
                return True
        return False
    
    def get_robot_by_id(self, robot_id):
        for robot in self.active_robots:
            if robot.robot_id == robot_id:
                return robot
        return None
    
    def is_valid_position(self, x, y):
        return 0 <= x < self.width and 0 <= y < self.height
    
    def is_blocked_position(self, x, y):
        return (x, y) in self.blocked_positions
    
    def is_position_in_aisle(self, x, y):
        """
        Check if a position is within any aisle (robots can only move in aisles).
        
        Args:
            x (int): X coordinate to check
            y (int): Y coordinate to check
            
        Returns:
            bool: True if position is in an aisle, False otherwise
        """
        # Check if position is in any aisle
        for aisle in self.aisles:
            if (x, y) in aisle['positions']:
                return True
        
        # Also allow movement on entry docks and packing stations
        # (robots need to access these for loading/unloading)
        for dock in self.entry_docks:
            if dock['position'] == (x, y):
                return True
        
        for station in self.packing_stations:
            if station['position'] == (x, y):
                return True
        
        return False
    
    def add_blocked_position(self, x, y):
        self.blocked_positions.add((x, y))
    
    def remove_blocked_position(self, x, y):
        self.blocked_positions.discard((x, y))
    
    def get_entry_docks(self):
        return self.entry_docks.copy()
    
    def get_packing_stations(self):
        return self.packing_stations.copy()
    
    def get_aisles(self):
        return self.aisles.copy()
    
    def get_active_robots(self):
        return self.active_robots.copy()
    
    def get_robot_positions(self):
        return {robot.robot_id: robot.get_current_position() for robot in self.active_robots}
    
    def is_position_occupied_by_robot(self, x, y):
        for robot in self.active_robots:
            if robot.get_current_position() == (x, y):
                return robot
        return None
    
    def visualize_congestion_map(self, title="Warehouse Congestion Map", save_path=None):
        """
        Visualize the congestion map as a heatmap.
        """
        fig, ax = plt.subplots(figsize=(12, 9))
        
        congestion_grid = np.zeros((self.height, self.width))
        for (x, y), count in self.congestion_map.items():
            if self.is_valid_position(x, y):
                congestion_grid[y, x] = count
        
        if not self.congestion_map:
            max_congestion = 1
        else:
            max_congestion = max(self.congestion_map.values()) if self.congestion_map else 1

        # Create the heatmap
        cax = ax.imshow(congestion_grid, cmap='hot', interpolation='nearest', vmin=0, vmax=max_congestion)
        
        # Add a color bar
        fig.colorbar(cax, label='Number of Times Visited')
        
        # Overlay the warehouse structure for context
        self._overlay_warehouse_structure(ax)
        
        ax.set_title(title, fontsize=14, fontweight='bold')
        ax.set_xlabel('X Coordinate')
        ax.set_ylabel('Y Coordinate')
        
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=300)
            print(f"Congestion map saved to: {save_path}")
            
        try:
            plt.show()
        except Exception as e:
            print(f"Display error: {e}")

    def _overlay_warehouse_structure(self, ax):
        """Helper to draw the warehouse layout on top of a plot."""
        # Draw blocked positions
        for x, y in self.blocked_positions:
            rect = patches.Rectangle((x - 0.5, y - 0.5), 1, 1, linewidth=1, edgecolor='black', facecolor='gray', alpha=0.5)
            ax.add_patch(rect)
            
        # Draw docks
        for dock in self.entry_docks:
            x, y = dock['position']
            rect = patches.Rectangle((x - 0.5, y - 0.5), 1, 1, linewidth=1, edgecolor='blue', facecolor='none')
            ax.add_patch(rect)
            ax.text(x, y, 'D', ha='center', va='center', color='blue', fontweight='bold')

        # Draw stations
        for station in self.packing_stations:
            x, y = station['position']
            rect = patches.Rectangle((x - 0.5, y - 0.5), 1, 1, linewidth=1, edgecolor='green', facecolor='none')
            ax.add_patch(rect)
            ax.text(x, y, 'P', ha='center', va='center', color='green', fontweight='bold')

    def get_warehouse_layout(self):
        layout = [['.' for _ in range(self.width)] for _ in range(self.height)]
        
        # Mark entry docks
        for dock in self.entry_docks:
            x, y = dock['position']
            if self.is_valid_position(x, y):
                layout[y][x] = 'D'
        
        # Mark packing stations
        for station in self.packing_stations:
            x, y = station['position']
            if self.is_valid_position(x, y):
                layout[y][x] = 'P'
        
        # Mark aisles
        for aisle in self.aisles:
            for x, y in aisle['positions']:
                if self.is_valid_position(x, y) and layout[y][x] == '.':
                    layout[y][x] = 'A'
        
        # Mark blocked positions
        for x, y in self.blocked_positions:
            if self.is_valid_position(x, y) and layout[y][x] == '.':
                layout[y][x] = 'X'
        
        # Mark robots
        for robot in self.active_robots:
            x, y = robot.get_current_position()
            if self.is_valid_position(x, y):
                layout[y][x] = 'R'
        
        return layout
    
    def visualize_robot_movement_step(self, step_number, title_prefix="Step"):
        title = f"{title_prefix} {step_number} - Robot Positions"
        return self.visualize_warehouse(title=title, show_grid=True)
    
    def visualize_before_after(self, initial_positions, title="Warehouse Layout - Before and After Movement", save_path=None):
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(20, 9))
        
        # Store current positions and histories temporarily
        current_positions = {}
        current_histories = {}
        for robot in self.active_robots:
            current_positions[robot.robot_id] = robot.current_position
            current_histories[robot.robot_id] = robot.movement_history.copy()
        
        # Create left plot (initial state)
        self._create_warehouse_plot(ax1, "Initial State", show_target_arrows=True, initial_state=True, initial_positions=initial_positions)
        
        # Create right plot (final state with paths)
        self._create_warehouse_plot(ax2, "Final State with Movement Paths", show_target_arrows=False, initial_state=False)
        
        # Set overall title
        fig.suptitle(title, fontsize=16, fontweight='bold')
        
        # Adjust layout
        plt.tight_layout()
        
        # Save if path provided
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            print(f"Warehouse layout saved to: {save_path}")
        
        # Show the plot
        try:
            plt.show()
        except Exception as e:
            print(f"Display error: {e}")
            print("Trying to save plot instead...")
            if not save_path:
                save_path = f"warehouse_before_after_{title.replace(' ', '_').lower()}.png"
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            print(f"Plot saved to: {save_path}")
        
        return fig, (ax1, ax2)
    
    def _create_warehouse_plot(self, ax, title, show_target_arrows=True, initial_state=False, initial_positions=None):
        colors = {
            'empty': '#FFFFFF',      
            'blocked': '#8B4513',    
            'aisle': '#E6E6FA',      
            'entry_dock': '#4169E1', 
            'packing_station': '#32CD32', 
            'robot': '#FF6347',      
            'robot_target': '#FFB6C1' 
        }
        
        # Create the base grid
        warehouse_grid = np.ones((self.height, self.width, 3))  
        
        # Fill empty spaces
        warehouse_grid[:, :] = [1.0, 1.0, 1.0]  
        
        # Mark blocked positions (storage areas)
        for x, y in self.blocked_positions:
            if self.is_valid_position(x, y):
                warehouse_grid[y, x] = [0.545, 0.271, 0.075]  # Brown
        
        # Mark aisles
        for aisle in self.aisles:
            for x, y in aisle['positions']:
                if self.is_valid_position(x, y):
                    warehouse_grid[y, x] = [0.902, 0.902, 0.980]  # Light lavender
        
        # Mark entry docks
        for dock in self.entry_docks:
            x, y = dock['position']
            if self.is_valid_position(x, y):
                warehouse_grid[y, x] = [0.255, 0.412, 0.882]  # Royal blue
        
        # Mark packing stations
        for station in self.packing_stations:
            x, y = station['position']
            if self.is_valid_position(x, y):
                warehouse_grid[y, x] = [0.196, 0.804, 0.196]  # Lime green
        
        # Mark robot targets (before robots so robots appear on top)
        for robot in self.active_robots:
            target_x, target_y = robot.get_target_position()
            if self.is_valid_position(target_x, target_y):
                warehouse_grid[target_y, target_x] = [1.0, 0.714, 0.757]  # Light pink
        
        # Display the grid
        ax.imshow(warehouse_grid, aspect='equal', origin='upper')
        
        # Robot colors for paths
        robot_colors = ['#FF1493', '#00CED1', '#FFD700', '#9370DB', '#FF4500']
        
        # Add robots and paths
        for i, robot in enumerate(self.active_robots):
            robot_color = robot_colors[i % len(robot_colors)]
            
            if initial_state and initial_positions:
                # Show robot at initial position
                x, y = initial_positions.get(robot.robot_id, robot.get_current_position())
                if self.is_valid_position(x, y):
                    circle = patches.Circle((x, y), 0.3, color='#FF6347', zorder=10)
                    ax.add_patch(circle)
                    ax.text(x, y, robot.robot_id.split('_')[-1], 
                           ha='center', va='center', fontsize=8, fontweight='bold', 
                           color='white', zorder=11)
                
                # Show arrow to target for initial state
                if show_target_arrows and not (x, y) == robot.get_target_position():
                    target_x, target_y = robot.get_target_position()
                    ax.annotate('', xy=(target_x, target_y), xytext=(x, y),
                               arrowprops=dict(arrowstyle='->', color='red', alpha=0.7, lw=1.5),
                               zorder=5)
            else:
                # Show current robot position and movement history
                x, y = robot.get_current_position()
                if self.is_valid_position(x, y):
                    circle = patches.Circle((x, y), 0.3, color='#FF6347', zorder=10)
                    ax.add_patch(circle)
                    ax.text(x, y, robot.robot_id.split('_')[-1], 
                           ha='center', va='center', fontsize=8, fontweight='bold', 
                           color='white', zorder=11)
                
                # Draw movement path
                movement_history = robot.get_movement_history()
                if len(movement_history) > 1:
                    # Extract x and y coordinates for the path
                    path_x = [pos[0] for pos in movement_history]
                    path_y = [pos[1] for pos in movement_history]
                    
                    # Draw the path line
                    ax.plot(path_x, path_y, color=robot_color, alpha=0.6, linewidth=2, 
                           linestyle='-', zorder=6)
                    
                    # Draw dots for each position in the path (excluding current position)
                    for j, (px, py) in enumerate(movement_history[:-1]):  # Exclude current position
                        circle = patches.Circle((px, py), 0.15, color=robot_color, alpha=0.8, zorder=7)
                        ax.add_patch(circle)
                
                # Show arrow to target if enabled
                if show_target_arrows and not robot.is_at_target():
                    target_x, target_y = robot.get_target_position()
                    ax.annotate('', xy=(target_x, target_y), xytext=(x, y),
                               arrowprops=dict(arrowstyle='->', color=robot_color, alpha=0.9, lw=2),
                               zorder=8)
        
        # Add labels for infrastructure
        label_offset = 0.25
        
        # Label entry docks
        for dock in self.entry_docks:
            x, y = dock['position']
            if self.is_valid_position(x, y):
                ax.text(x, y + label_offset, 'D', ha='center', va='center', 
                       fontsize=10, fontweight='bold', color='white')
        
        # Label packing stations
        for station in self.packing_stations:
            x, y = station['position']
            if self.is_valid_position(x, y):
                ax.text(x, y + label_offset, 'P', ha='center', va='center', 
                       fontsize=10, fontweight='bold', color='white')
        
        # Set up the plot
        ax.set_xlim(-0.5, self.width - 0.5)
        ax.set_ylim(self.height - 0.5, -0.5)  # Flip Y axis to match grid coordinates
        ax.set_xlabel('X Coordinate')
        ax.set_ylabel('Y Coordinate')
        ax.set_title(title, fontsize=12, fontweight='bold')
        
        # Add grid
        ax.set_xticks(range(self.width))
        ax.set_yticks(range(self.height))
        ax.grid(True, alpha=0.3)
        
        # Create legend (only for the right plot to avoid duplication)
        if not initial_state:
            robot_colors = ['#FF1493', '#00CED1', '#FFD700', '#9370DB', '#FF4500']
            legend_elements = [
                patches.Patch(color='#E6E6FA', label='Aisles'),
                patches.Patch(color='#8B4513', label='Storage Areas'),
                patches.Patch(color='#4169E1', label='Entry Docks (D)'),
                patches.Patch(color='#32CD32', label='Packing Stations (P)'),
                patches.Patch(color='#FF6347', label='Robots (Current)'),
                patches.Patch(color='#FFB6C1', label='Robot Targets'),
            ]
            
            # Add path legends for the first few robots
            for i, robot in enumerate(self.active_robots):
                if i < len(robot_colors):
                    legend_elements.append(
                        patches.Patch(color=robot_colors[i], label=f'{robot.robot_id} Path')
                    )
            
            ax.legend(handles=legend_elements, loc='upper left', bbox_to_anchor=(1.02, 1))

