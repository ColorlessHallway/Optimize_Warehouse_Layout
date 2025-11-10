# Warehouse Layout Optimization

This project implements and analyzes algorithms for optimizing a warehouse layout to improve the efficiency of autonomous robots. It explores both single-objective and multi-objective optimization techniques to minimize travel distance, reduce congestion, and lower energy consumption.

## Table of Contents
- [Project Overview](#project-overview)
- [How to Run](#how-to-run)
  - [Running a Single Simulation](#running-a-single-simulation)
  - [Running the Optimization Benchmark](#running-the-optimization-benchmark)
- [Core Components](#core-components)
- [Algorithm Implementation](#algorithm-implementation)
  - [Pathfinding: A* Search (Deterministic)](#pathfinding-a-search-deterministic)
  - [Single-Objective Optimization: Simulated Annealing (SA)](#single-objective-optimization-simulated-annealing-sa)
  - [Multi-Objective Optimization: MOSA](#multi-objective-optimization-mosa)
- [Performance Analysis](#performance-analysis)
  - [Runtime, Convergence, and Optimality](#runtime-convergence-and-optimality)
  - [Visualization](#visualization)
- [Pareto Front Analysis](#pareto-front-analysis)
- [Discussion: Deterministic vs. Stochastic Approaches](#discussion-deterministic-vs-stochastic-approaches)

## Project Overview

The goal of this system is to find an optimal arrangement of storage shelves and aisles within a warehouse. An efficient layout allows robots to complete their tasks (e.g., moving items from docks to packing stations) faster, with less congestion, and using less energy.

The project uses a simulation-based approach where:
1.  A warehouse layout is defined.
2.  Robots are assigned tasks to move between locations.
3.  A deterministic pathfinding algorithm (A*) finds the best path for each robot, considering obstacles and other robots.
4.  A stochastic optimization algorithm (Simulated Annealing) iteratively modifies the layout and evaluates its performance to find better configurations.

## How to Run

### Running a Single Simulation

To see a single simulation of robots operating in a randomly generated warehouse, run `main.py`. This will generate a layout, create robots with tasks, and visualize their movement from start to finish.

```bash
python main.py
```

### Running the Optimization Benchmark

To run the layout optimization algorithms and see the results, execute `benchmark.py`. This script will:
1.  Run the single-objective Simulated Annealing (SA) optimizer and show its convergence.
2.  Run the Multi-Objective Simulated Annealing (MOSA) optimizer.
3.  Plot the resulting Pareto front of optimal trade-off solutions.

```bash
python benchmark.py
```

## Core Components

-   `warehouse.py`: Defines the `Warehouse` class, which manages the grid, layout elements (docks, stations, aisles, storage), and robot positions.
-   `robot.py`: Defines the `Robot` class, which handles movement, energy consumption, and state tracking.
-   `pathfinding.py`: Implements the A* search algorithm for optimal pathfinding between two points.
-   `main.py`: Contains the main simulation logic, including the `RobotController` that directs robots and handles collisions and re-planning.
-   `optimization.py`: Implements the core optimization algorithms: `simulated_annealing_optimizer` (single-objective) and `mosa_optimizer` (multi-objective).
-   `benchmark.py`: A script to run and evaluate the performance of the optimization algorithms and visualize their results.

## Algorithm Implementation

The system uses a deterministic algorithm for pathfinding and stochastic algorithms for layout optimization.

### Pathfinding: A* Search (Deterministic)

The A* algorithm is used to find the shortest path for a robot from a starting point to a target. It is **deterministic**, meaning it will always find the same, optimal path given the same inputs.

-   **Implementation**: The `a_star_search` function in `pathfinding.py` navigates the warehouse grid.
-   **Cost Function**: The cost to travel to a node `n` is `f(n) = g(n) + h(n)`, where:
    -   `g(n)` is the actual cost from the start to `n` (including a penalty for moving through congested cells).
    -   `h(n)` is the heuristic (Manhattan distance) from `n` to the goal.
-   **Constraints**: The algorithm respects physical constraints, avoiding walls, storage areas, and other robots.

**Pseudocode for A* Search:**

```
FUNCTION a_star(start, goal, warehouse):
  open_set = {start}
  came_from = {}
  g_score = {start: 0}
  f_score = {start: heuristic(start, goal)}

  WHILE open_set is not empty:
    current = node in open_set with the lowest f_score
    IF current == goal:
      RETURN reconstruct_path(came_from, current)

    remove current from open_set
    FOR each neighbor of current:
      tentative_g_score = g_score[current] + dist(current, neighbor) + congestion_penalty(neighbor)
      IF tentative_g_score < g_score[neighbor]:
        came_from[neighbor] = current
        g_score[neighbor] = tentative_g_score
        f_score[neighbor] = g_score[neighbor] + heuristic(neighbor, goal)
        IF neighbor not in open_set:
          add neighbor to open_set
  RETURN failure
```

-   **Time Complexity**: `O(W * H * log(W * H))`, where `W` and `H` are the width and height of the warehouse grid. The complexity is dominated by the priority queue operations in the worst case where most cells are visited.

### Single-Objective Optimization: Simulated Annealing (SA)

Simulated Annealing is a **stochastic** metaheuristic used to find a single, "good" solution by exploring the solution space. It balances exploration (trying new, sometimes worse, solutions) and exploitation (improving on the current best solution).

-   **Objective**: Minimize a single cost value, which is a weighted sum of the three metrics: `Cost = w_d * Distance + w_c * Congestion + w_e * Energy`.
-   **Neighbor Generation**: A "neighbor" layout is created by making a small, random change to the current layout (e.g., swapping a storage cell with an aisle cell).
-   **Acceptance Criteria**: A worse neighbor solution can be accepted with a probability `P = exp(-delta_cost / Temperature)`. This allows the algorithm to escape local optima.

**Pseudocode for Simulated Annealing:**

```
FUNCTION simulated_annealing(initial_layout, temp, cool_rate, iters):
  current_layout = initial_layout
  current_cost = evaluate(current_layout)
  best_layout = current_layout

  FOR i from 1 to iters:
    neighbor_layout = get_neighbor(current_layout)
    neighbor_cost = evaluate(neighbor_layout)

    cost_diff = neighbor_cost - current_cost
    IF cost_diff < 0 OR random() < exp(-cost_diff / temp):
      current_layout = neighbor_layout
      current_cost = neighbor_cost

    IF current_cost < cost(best_layout):
      best_layout = current_layout

    temp = temp * cool_rate

  RETURN best_layout
```

-   **Time Complexity**: `O(I * (T_eval + T_neighbor))`, where `I` is the number of iterations, `T_eval` is the time to evaluate one layout (running a full simulation), and `T_neighbor` is the time to generate a neighbor. The evaluation step is the bottleneck.

### Multi-Objective Optimization: MOSA

Multi-Objective Simulated Annealing (MOSA) is an extension of SA that finds a set of trade-off solutions, known as the **Pareto front**, instead of a single best solution.

-   **Objective**: Simultaneously minimize all three objectives (Distance, Congestion, Energy) without combining them into a single value.
-   **Dominance**: A solution `A` *dominates* `B` if it is strictly better in at least one objective and no worse in all others.
-   **Pareto Archive**: MOSA maintains an archive of non-dominated solutions found so far.
-   **Acceptance Criteria**: The decision to accept a neighbor is based on dominance. A neighbor that dominates the current solution is always accepted. A non-dominated neighbor is accepted with some probability to encourage exploration along the Pareto front.

**Pseudocode for MOSA:**

```
FUNCTION mosa(initial_layout, temp, cool_rate, iters):
  current_layout = initial_layout
  current_metrics = evaluate(current_layout)
  archive = {current_metrics}

  FOR i from 1 to iters:
    neighbor_layout = get_neighbor(current_layout)
    neighbor_metrics = evaluate(neighbor_layout)

    IF neighbor_metrics dominates current_metrics:
      current_layout = neighbor_layout
      current_metrics = neighbor_metrics
    ELSE IF not (current_metrics dominates neighbor_metrics): // Non-dominated
      // Accept with some probability to explore
      IF random() < 0.5:
        current_layout = neighbor_layout
        current_metrics = neighbor_metrics
    ELSE: // Neighbor is dominated
      // Accept with a small probability based on temperature
      IF random() < exp(-1 / temp):
        current_layout = neighbor_layout
        current_metrics = neighbor_metrics

    update_archive(archive, neighbor_metrics)
    temp = temp * cool_rate

  RETURN archive
```

-   **Time Complexity**: Similar to SA, `O(I * (T_eval + T_neighbor))`, but with a small overhead for maintaining the Pareto archive.

## Performance Analysis

### Runtime, Convergence, and Optimality

-   **Runtime**: The primary driver of runtime is the `evaluate_layout` function, which runs a full multi-robot simulation. Runtime scales with the number of optimization iterations, warehouse size, and number of robots.
-   **Convergence**:
    -   In **SA**, convergence is monitored by plotting the cost function over iterations. A downward trend that flattens out indicates convergence.
    -   In **MOSA**, convergence is observed by the growth and stabilization of the Pareto archive size.
-   **Optimality**:
    -   **A*** guarantees an optimal path for a single robot in a static environment.
    -   **SA and MOSA** are metaheuristics and do not guarantee a globally optimal layout. They are designed to find "good enough" solutions in a reasonable amount of time for a problem that is too complex to solve exhaustively.

### Visualization

The project uses `matplotlib` to provide critical insights:
-   **Layout Evolution**: By visualizing the layout before and after optimization, we can see how the arrangement of aisles and storage changes.
-   **Search Paths**: The `visualize_before_after` function in `warehouse.py` plots the exact paths taken by robots, highlighting inefficiencies.
-   **Congestion Map**: A heatmap shows which parts of the warehouse are most frequently used, identifying bottlenecks.
-   **Pareto Front Plot**: A 3D scatter plot visualizes the trade-off solutions found by MOSA.

## Pareto Front Analysis

The `plot_pareto_front` function in `benchmark.py` generates a 3D scatter plot of the trade-offs between the three objectives: **Total Distance**, **Max Congestion**, and **Total Energy**.

-   **Each point** on the plot represents a non-dominated warehouse layout configuration.
-   **Non-dominated Solutions**: These are the "best" trade-off solutions. For any point on the front, you cannot improve one objective without worsening another. For example, a layout that drastically reduces travel distance might do so at the cost of creating a single, highly congested corridor.
-   **Decision Making**: The Pareto front allows a human operator to choose a layout that best fits their priorities. They might choose a layout with slightly higher energy use if it significantly reduces congestion, or they might prioritize the lowest possible travel distance if energy and congestion are less critical.

## Discussion: Deterministic vs. Stochastic Approaches

This project demonstrates a combination of deterministic and stochastic methods.

-   **Deterministic (A*)**:
    -   **Role**: Used for micro-level decisions (a robot's path).
    -   **Strengths**: Fast, reliable, and optimal for its specific task. It provides a clear, repeatable evaluation of a given layout.
    -   **Limitations**: It cannot optimize the layout itself. It only finds the best path within the existing layout.

-   **Stochastic (SA/MOSA)**:
    -   **Role**: Used for macro-level decisions (the overall warehouse layout).
    -   **Strengths**: Usable for exploring vast, complex solution spaces where the "perfect" solution is unknown or too hard to compute. Can find "good enough" solutions.
    -   **Limitations**: They are non-deterministic and do not guarantee global optimality.

### When Does Each Paradigm Excel?

-   **A\*** is essential for the operational phase, where robots need to find paths quickly and efficiently. It excels at providing a fast, definitive answer to a well-defined problem.
-   **SA/MOSA** are suited for the design phase, where we need to find a good layout from trillions of possibilities. They excel when the problem is too complex for brute-force or exact methods. A stochastic approach is faster at finding a "good" layout than trying to exhaustively test all possible layouts.

### Impact of Parameters

-   **Temperature Scheduling (SA/MOSA)**: The initial temperature and cooling rate are critical.
    -   A **high initial temperature** allows the algorithm to explore more of the solution space and avoid getting stuck in local optima early on.
    -   A **slow cooling rate** (`cool_rate` close to 1.0) allows for a more thorough search but increases runtime. A fast cooling rate may converge too quickly to a suboptimal solution.
-   **Heuristic Admissibility (A*)**: The A* heuristic (Manhattan distance) is **admissible** because it never overestimates the true cost. This is crucial because it guarantees that A* will find the shortest path. If the heuristic were inadmissible, A* might find a suboptimal path faster, but it would lose its guarantee of optimality.
