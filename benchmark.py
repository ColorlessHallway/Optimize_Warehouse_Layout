"""
Benchmark script for the warehouse optimization system.
This script runs the simulation with various configurations to measure
performance metrics like runtime, congestion, and energy usage.
"""

import matplotlib.pyplot as plt
from main import create_random_warehouse
from optimization import simulated_annealing_optimizer, mosa_optimizer, evaluate_layout

def run_single_objective_optimization():
    """
    Runs the single-objective Simulated Annealing optimizer to find one good solution.
    """
    print("=" * 80)
    print("RUNNING SINGLE-OBJECTIVE OPTIMIZATION")
    print("=" * 80)

    num_robots = 5
    weights = {'w_d': 0.5, 'w_c': 0.3, 'w_e': 0.2} # A balanced approach

    print(f"\n--- Running Optimizer with Weights: {weights} ---")
    initial_warehouse, _, _ = create_random_warehouse(20, 20, num_robots)
    
    best_layout, best_metrics, history = simulated_annealing_optimizer(
        initial_warehouse=initial_warehouse,
        num_robots=num_robots,
        weights=weights,
        temp=1000,
        cool_rate=0.95,
        iters=100
    )
    
    print(f"--- Single-Objective Optimization Complete. Best Metrics: {best_metrics} ---")

    # Visualize the final optimized layout and its performance
    best_layout.visualize_congestion_map(
        title=f"Single-Objective Optimized Layout"
    )
    
    # Plot convergence
    plt.figure(figsize=(10, 6))
    plt.plot(history['cost'])
    plt.xlabel("Iteration")
    plt.ylabel("Cost")
    plt.title("Convergence of Single-Objective Simulated Annealing")
    plt.grid(True)
    plt.show()

def run_multi_objective_optimization():
    """
    Runs the MOSA optimizer to generate a set of Pareto-optimal solutions.
    """
    print("=" * 80)
    print("RUNNING MULTI-OBJECTIVE (MOSA) OPTIMIZATION")
    print("=" * 80)

    num_robots = 5
    initial_warehouse, _, _ = create_random_warehouse(20, 20, num_robots)
    
    pareto_archive, history = mosa_optimizer(
        initial_warehouse=initial_warehouse,
        num_robots=num_robots,
        temp=1000,
        cool_rate=0.95,
        iters=100  # More iterations for MOSA to explore the space
    )
    
    print(f"--- MOSA Complete. Found {len(pareto_archive)} non-dominated solutions. ---")
    return pareto_archive

def plot_pareto_front(pareto_front):
    """
    Plots the generated Pareto front in a 3D scatter plot.
    """
    if not pareto_front:
        print("Cannot plot Pareto front: No data.")
        return

    fig = plt.figure(figsize=(12, 9))
    ax = fig.add_subplot(111, projection='3d')

    # Extract data for plotting
    distances = [p['total_distance'] for p in pareto_front]
    congestions = [p['max_congestion'] for p in pareto_front]
    energies = [p['total_energy'] for p in pareto_front]

    ax.scatter(distances, congestions, energies, c='blue', s=60, marker='o')

    ax.set_xlabel('Total Distance (Lower is Better)')
    ax.set_ylabel('Max Congestion (Lower is Better)')
    ax.set_zlabel('Total Energy (Lower is Better)')
    ax.set_title('Pareto Front: Distance vs. Congestion vs. Energy', fontsize=16)
    
    # Invert axes so that the 'best' corner is visually apparent (front-left-bottom)
    ax.invert_xaxis()
    ax.invert_yaxis()
    ax.invert_zaxis()

    plt.show()

def main():
    """
    Main function to run both single and multi-objective optimization and plot the results.
    """
    # 1. Run single-objective optimization for comparison
    run_single_objective_optimization()
    
    # 2. Run multi-objective optimization to find the Pareto front
    pareto_results = run_multi_objective_optimization()
    
    # 3. Plot the resulting Pareto front
    plot_pareto_front(pareto_results)


if __name__ == "__main__":
    main()
