import heapq

def heuristic(a, b):
    """
    Calculate the Manhattan distance heuristic between two points.
    """
    return abs(a[0] - b[0]) + abs(a[1] - b[1])

def a_star_search(warehouse, start, goal, robot_id, all_robot_positions, congestion_penalty=1):
    """
    Find the optimal path from a start to a goal position using the A* algorithm.
    
    This implementation considers:
    - Static obstacles (storage areas, walls).
    - Dynamic obstacles (other robots).
    - Movement constraints (robots must stay in aisles).
    - Congestion penalty for frequently used paths.
    
    Args:
        warehouse (Warehouse): The warehouse instance.
        start (tuple): The starting position (x, y).
        goal (tuple): The goal position (x, y).
        robot_id (str): The ID of the robot for which the path is being calculated.
        all_robot_positions (dict): A dictionary of current positions for all robots.
        congestion_penalty (float): The penalty multiplier for congested cells.
        
    Returns:
        list: A list of tuples representing the path from start to goal, or an empty list if no path is found.
    """

    # The set of nodes already evaluated
    closed_set = set()
    
    # The set of currently discovered nodes that are not evaluated yet
    open_set = []
    heapq.heappush(open_set, (0, start))  # (f_score, position)
    
    # For each node, which node it can most efficiently be reached from
    came_from = {}
    
    # For each node, the cost of getting from the start node to that node
    g_score = {start: 0}
    
    # For each node, the total cost of getting from the start node to the goal
    # by passing by that node. The value is partly known, partly heuristic.
    f_score = {start: heuristic(start, goal)}
    
    # Get positions of other robots to avoid collisions
    other_robot_positions = {pos for rid, pos in all_robot_positions.items() if rid != robot_id}

    while open_set:
        # Get the node in open_set having the lowest f_score value
        _, current = heapq.heappop(open_set)
        
        # If the goal is reached, reconstruct and return the path
        if current == goal:
            path = []
            while current in came_from:
                path.append(current)
                current = came_from[current]
            path.append(start)
            return path[::-1]  # Return reversed path
            
        closed_set.add(current)
        
        # Explore neighbors
        for dx, dy in [(0, 1), (0, -1), (1, 0), (-1, 0)]:  # Up, Down, Right, Left
            neighbor = (current[0] + dx, current[1] + dy)
            
            # --- Collision and Validity Checks
            # 1. Check if neighbor is within warehouse bounds
            if not warehouse.is_valid_position(neighbor[0], neighbor[1]):
                continue
            
            # 2. Check if neighbor is in the set of already evaluated nodes
            if neighbor in closed_set:
                continue
            
            # 3. Check if the neighbor is a blocked position (storage, etc.)
            if warehouse.is_blocked_position(neighbor[0], neighbor[1]) and neighbor != goal:
                continue
            
            # 4. Check if the neighbor is occupied by another robot
            if neighbor in other_robot_positions:
                continue
                
            # 5. Check if the neighbor is in an aisle
            if not warehouse.is_position_in_aisle(neighbor[0], neighbor[1]) and neighbor != goal:
                continue

            # --- A* Algorithm Logic with Congestion ---
            
            # Calculate congestion cost
            congestion_cost = warehouse.get_congestion(neighbor[0], neighbor[1]) * congestion_penalty
            #print(f"Neighbor: {neighbor}, Congestion Cost: {congestion_cost}")
            
            # The distance from start to a neighbor is the distance from start to current + 1 + congestion
            tentative_g_score = g_score[current] + 1 + congestion_cost
            
            # If this path to the neighbor is better than any previous one, record it
            if tentative_g_score < g_score.get(neighbor, float('inf')):
                came_from[neighbor] = current
                g_score[neighbor] = tentative_g_score
                f_score[neighbor] = tentative_g_score + heuristic(neighbor, goal)
                
                # Add the neighbor to the open set if it's not already there
                if neighbor not in [item[1] for item in open_set]:
                    heapq.heappush(open_set, (f_score[neighbor], neighbor))

    # If the loop completes and the goal was not reached, return an empty list
    return []
