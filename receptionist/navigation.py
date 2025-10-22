from heapq import heappush, heappop
from typing import List, Tuple

GridPos = Tuple[int, int]

def heuristic(a: GridPos, b: GridPos) -> int:
    return abs(a[0]-b[0]) + abs(a[1]-b[1])

def neighbors(pos: GridPos) -> List[GridPos]:
    x, y = pos
    return [(x+1,y),(x-1,y),(x,y+1),(x,y-1)]

def plan_path(start: GridPos, goal: GridPos, obstacles: List[GridPos] = []) -> List[GridPos]:
    """Simple A* path planner on a grid with static obstacles.

    This is a lightweight simulator for demonstration.
    """
    obstacle_set = set(obstacles)
    open_set = []
    heappush(open_set, (0 + heuristic(start, goal), 0, start))
    came_from = {start: None}
    gscore = {start: 0}

    while open_set:
        _, cost, current = heappop(open_set)
        if current == goal:
            # reconstruct path
            path = []
            node = current
            while node:
                path.append(node)
                node = came_from[node]
            return list(reversed(path))
        for n in neighbors(current):
            if n in obstacle_set:
                continue
            tentative = gscore[current] + 1
            if tentative < gscore.get(n, 1e9):
                came_from[n] = current
                gscore[n] = tentative
                heappush(open_set, (tentative + heuristic(n, goal), tentative, n))
    return []

def avoid_obstacle(path: List[GridPos], dynamic_obstacle: GridPos) -> List[GridPos]:
    """Given a planned path and a dynamic obstacle, compute a small detour.

    For demo, if the obstacle lies on the path, remove that point and re-plan
    a one-step detour by sidestepping.
    """
    if dynamic_obstacle not in path:
        return path
    idx = path.index(dynamic_obstacle)
    # try sidestep positions
    x, y = dynamic_obstacle
    options = [(x+1,y),(x-1,y),(x,y+1),(x,y-1)]
    for opt in options:
        if opt not in path:
            new_path = path[:idx] + [opt] + path[idx+1:]
            return new_path
    # fallback: return original but robot should stop
    return path
