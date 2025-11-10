"""
This module implements the Simulated Annealing algorithm to optimize the warehouse layout.

The optimizer attempts to find a layout that minimizes a weighted cost function 
of travel distance, congestion, and energy usage.
"""

import random
import math
import copy
from main import simulate_robot_movement_with_astar
from warehouse import Warehouse

def evaluate_layout(warehouse, num_robots):
    """
    Runs a full simulation for a given warehouse layout and returns performance metrics.
    This is the objective function for our optimization.

    Args:
        warehouse (Warehouse): The warehouse layout to evaluate.
        num_robots (int): The number of robots to use in the simulation.

    Returns:
        dict: A dictionary containing performance metrics for the layout.
    """
    # The simulation needs robots. We need to add them based on the layout's docks/stations.
    docks = warehouse.get_entry_docks()
    stations = warehouse.get_packing_stations()

    dock_positions = [d['position'] for d in docks]
    station_positions = [s['position'] for s in stations]

    random.shuffle(dock_positions)
    random.shuffle(station_positions)

    # Ensure the warehouse is clean before evaluation
    warehouse.active_robots.clear()
    warehouse.reset_congestion()

    # Create and place robots
    initial_positions = {}
    for i in range(num_robots):
        robot_id = f"ROBOT_{i:03d}"
        if not dock_positions or not station_positions:
            break
        start_pos = dock_positions.pop()
        target_pos = station_positions.pop()
        robot = warehouse.create_and_add_robot(robot_id, start_pos[0], start_pos[1])
        robot.set_target_position(target_pos[0], target_pos[1])
        initial_positions[robot_id] = start_pos

    # Run the simulation without visualization
    controller = simulate_robot_movement_with_astar(warehouse, initial_positions, visualize=False)

    # Collect metrics
    total_distance = 0
    total_energy = 0
    
    for robot in warehouse.get_active_robots():
        report = robot.get_energy_report()
        total_distance += report['successful_moves']
        total_energy += report['total_energy_spent']
        
    max_congestion = max(warehouse.congestion_map.values()) if warehouse.congestion_map else 0
    
    metrics = {
        "total_distance": total_distance,
        "total_energy": total_energy,
        "max_congestion": max_congestion,
    }
    return metrics

def calculate_cost(metrics, weights):
    """
    Calculates the total cost of a layout based on its metrics and given weights.
    """
    cost = (weights['w_d'] * metrics['total_distance'] +
            weights['w_c'] * metrics['max_congestion'] +
            weights['w_e'] * metrics['total_energy'])
    return cost

def get_neighbor_layout(warehouse):
    """
    Generates a new layout by making a small, random change to the current one.
    It swaps a random storage cell with a random, non-essential aisle cell,
    ensuring the aisle data structure is correctly updated.
    """
    new_warehouse = copy.deepcopy(warehouse)
    
    # Find candidate cells for swapping
    # Ensure we don't move docks/stations which are also in blocked_positions
    infrastructure_cells = {d['position'] for d in new_warehouse.entry_docks} | \
                           {s['position'] for s in new_warehouse.packing_stations}
    
    storage_cells = [cell for cell in new_warehouse.blocked_positions if cell not in infrastructure_cells]
    
    # Get a flat list of all aisle positions that are not infrastructure
    aisle_cells = []
    for aisle in new_warehouse.aisles:
        for pos in aisle['positions']:
            if pos not in infrastructure_cells:
                aisle_cells.append(pos)
    
    if not storage_cells or not aisle_cells:
        return new_warehouse # Cannot make a swap

    # Choose random cells to swap
    storage_to_become_aisle = random.choice(storage_cells)
    aisle_to_become_storage = random.choice(aisle_cells)

    # Perform the swap in the blocked_positions set
    new_warehouse.remove_blocked_position(storage_to_become_aisle[0], storage_to_become_aisle[1])
    new_warehouse.add_blocked_position(aisle_to_become_storage[0], aisle_to_become_storage[1])
    
    # Update the aisle data structure to reflect the change
    # Find which aisle contained the old aisle position and replace it with the new one.
    # This is a simple but more robust way to handle the swap.
    found_and_swapped = False
    for aisle in new_warehouse.aisles:
        if aisle_to_become_storage in aisle['positions']:
            aisle['positions'].remove(aisle_to_become_storage)
            aisle['positions'].append(storage_to_become_aisle)
            found_and_swapped = True
            break
    
    # If the aisle cell wasn't in a specific aisle for some reason, add it to a general one
    if not found_and_swapped and new_warehouse.aisles:
        new_warehouse.aisles[0]['positions'].append(storage_to_become_aisle)

    return new_warehouse

def simulated_annealing_optimizer(initial_warehouse, num_robots, weights, temp, cool_rate, iters):
    """
    Optimizes warehouse layout using Simulated Annealing for a single objective.
    """
    print("\nStarting Single-Objective Simulated Annealing Optimization...")
    
    current_solution = initial_warehouse
    current_metrics = evaluate_layout(current_solution, num_robots)
    current_cost = calculate_cost(current_metrics, weights)
    
    best_solution = current_solution
    best_metrics = current_metrics
    best_cost = current_cost
    
    history = {'temp': [], 'cost': []}

    for i in range(iters):
        neighbor = get_neighbor_layout(current_solution)
        neighbor_metrics = evaluate_layout(neighbor, num_robots)
        neighbor_cost = calculate_cost(neighbor_metrics, weights)
        
        # Acceptance probability
        cost_diff = neighbor_cost - current_cost
        
        if cost_diff < 0 or random.uniform(0, 1) < math.exp(-cost_diff / temp):
            current_solution = neighbor
            current_cost = neighbor_cost
            current_metrics = neighbor_metrics
        
        if current_cost < best_cost:
            best_solution = current_solution
            best_cost = current_cost
            best_metrics = current_metrics
            
        # Update history and cool down
        history['temp'].append(temp)
        history['cost'].append(current_cost)
        temp *= cool_rate
        
        print(f"Iter {i+1}/{iters} | Temp: {temp:.2f} | Current Cost: {current_cost:.2f} | Best Cost: {best_cost:.2f}")

    print("Simulated Annealing complete.")
    return best_solution, best_metrics, history


# --- Multi-Objective Optimization Functions ---

def dominates(metrics_a, metrics_b):
    """
    Check if solution A dominates solution B.
    Minimize all objectives: distance, congestion, energy.
    """
    a_better = False
    for key in metrics_a:
        if metrics_a[key] > metrics_b[key]:
            return False  # A is worse in at least one objective
        if metrics_a[key] < metrics_b[key]:
            a_better = True  # A is strictly better in at least one
    return a_better

def update_archive(archive, new_solution_metrics):
    """
    Updates the archive of non-dominated solutions.
    """
    new_archive = []
    is_dominated_by_new = False
    
    for old_metrics in archive:
        if dominates(new_solution_metrics, old_metrics):
            continue  # Old solution is dominated by new, so don't keep it
        if dominates(old_metrics, new_solution_metrics):
            is_dominated_by_new = True
            break # New solution is dominated by an existing one, so don't add it
        new_archive.append(old_metrics)
        
    if not is_dominated_by_new:
        new_archive.append(new_solution_metrics)
        
    return new_archive

def mosa_optimizer(initial_warehouse, num_robots, temp, cool_rate, iters):
    """
    Optimizes warehouse layout using Multi-Objective Simulated Annealing (MOSA).
    Finds a set of Pareto-optimal solutions.
    """
    print("\nStarting Multi-Objective Simulated Annealing (MOSA) Optimization...")
    
    current_solution = initial_warehouse
    current_metrics = evaluate_layout(current_solution, num_robots)
    
    # The archive stores the metrics of the non-dominated solutions
    archive = [current_metrics]
    
    history = {'temp': [], 'archive_size': []}

    for i in range(iters):
        # Generate a neighbor from the current solution
        neighbor_layout = get_neighbor_layout(current_solution)
        neighbor_metrics = evaluate_layout(neighbor_layout, num_robots)
        
        # --- Acceptance Criterion ---
        # 1. If neighbor dominates current, always accept
        if dominates(neighbor_metrics, current_metrics):
            current_solution = neighbor_layout
            current_metrics = neighbor_metrics
        # 2. If non-dominated, accept based on temperature
        elif not dominates(current_metrics, neighbor_metrics):
            # This is a simplification. A more complex criterion could be used.
            # For now, we accept non-dominated moves with a probability.
            if random.uniform(0, 1) < 0.5: # 50% chance to explore non-dominated solutions
                current_solution = neighbor_layout
                current_metrics = neighbor_metrics
        # 3. If neighbor is dominated by current, accept with a small probability
        else:
            # Probability of accepting a worse solution
            # We need a way to quantify "how much worse" in a multi-objective context.
            # For simplicity, we use a fixed low probability, but this could be improved.
            if random.uniform(0, 1) < math.exp(-1 / temp):
                current_solution = neighbor_layout
                current_metrics = neighbor_metrics

        # Update the archive with the potentially new solution
        archive = update_archive(archive, neighbor_metrics)
            
        # Update history and cool down
        history['temp'].append(temp)
        history['archive_size'].append(len(archive))
        temp *= cool_rate
        
        print(f"Iter {i+1}/{iters} | Temp: {temp:.2f} | Archive Size: {len(archive)}")

    print("MOSA complete.")
    return archive, history
