import math
import heapq
import config

GRID_SIZE = 25

class PathfindingGrid:
    def __init__(self, width=config.MAP_WIDTH, height=config.MAP_HEIGHT, grid_size=GRID_SIZE):
        self.width = width
        self.height = height
        self.grid_size = grid_size
        self.cols = int(math.ceil(width / float(grid_size)))
        self.rows = int(math.ceil(height / float(grid_size)))

    def pos_to_grid(self, x, y):
        col = max(0, min(self.cols - 1, int(x // self.grid_size)))
        row = max(0, min(self.rows - 1, int(y // self.grid_size)))
        return col, row

    def grid_to_pos(self, col, row):
        x = col * self.grid_size + self.grid_size / 2.0
        y = row * self.grid_size + self.grid_size / 2.0
        return x, y

    def build_obstacle_grid(self, game_state):
        if not hasattr(game_state, '_cached_obstacle_grid') or game_state._cached_obstacle_grid is None or getattr(game_state, '_obstacle_grid_dirty', True):
            obstacle_grid = [[False for _ in range(self.rows)] for _ in range(self.cols)]

            for b in game_state.buildings:
                if not b.alive:
                    continue
                rad = b.radius + 8
                min_c, min_r = self.pos_to_grid(b.x - rad, b.y - rad)
                max_c, max_r = self.pos_to_grid(b.x + rad, b.y + rad)

                for c in range(min_c, max_c + 1):
                    for r in range(min_r, max_r + 1):
                        gx, gy = self.grid_to_pos(c, r)
                        if (gx - b.x)**2 + (gy - b.y)**2 <= rad * rad:
                            obstacle_grid[c][r] = True

            for res in game_state.resources:
                if not res.alive:
                    continue
                rad = res.radius + 8
                min_c, min_r = self.pos_to_grid(res.x - rad, res.y - rad)
                max_c, max_r = self.pos_to_grid(res.x + rad, res.y + rad)

                for c in range(min_c, max_c + 1):
                    for r in range(min_r, max_r + 1):
                        gx, gy = self.grid_to_pos(c, r)
                        if (gx - res.x)**2 + (gy - res.y)**2 <= rad * rad:
                            obstacle_grid[c][r] = True

            game_state._cached_obstacle_grid = obstacle_grid
            game_state._obstacle_grid_dirty = False
            game_state._path_cache = {}

        return game_state._cached_obstacle_grid

    def _get_ignored_cells(self, ignore_entity):
        ignored = set()
        if ignore_entity:
            rad = ignore_entity.radius + 8
            min_c, min_r = self.pos_to_grid(ignore_entity.x - rad, ignore_entity.y - rad)
            max_c, max_r = self.pos_to_grid(ignore_entity.x + rad, ignore_entity.y + rad)
            for c in range(min_c, max_c + 1):
                for r in range(min_r, max_r + 1):
                    gx, gy = self.grid_to_pos(c, r)
                    if (gx - ignore_entity.x)**2 + (gy - ignore_entity.y)**2 <= rad * rad:
                        ignored.add((c, r))
        return ignored

    def is_line_clear(self, x1, y1, x2, y2, obstacle_grid, ignored_cells=None):
        # Raycast / DDA check between two points
        dist = math.hypot(x2 - x1, y2 - y1)
        if dist == 0:
            return True

        steps = int(math.ceil(dist / (self.grid_size / 2.0)))
        for i in range(steps + 1):
            t = i / float(max(1, steps))
            cx = x1 + (x2 - x1) * t
            cy = y1 + (y2 - y1) * t
            col, row = self.pos_to_grid(cx, cy)
            if obstacle_grid[col][row]:
                if ignored_cells and (col, row) in ignored_cells:
                    continue
                return False
        return True

    def find_path(self, start_pos, goal_pos, game_state, ignore_entity=None):
        sx, sy = start_pos
        gx, gy = goal_pos

        obstacle_grid = self.build_obstacle_grid(game_state)
        ignored_cells = self._get_ignored_cells(ignore_entity) if ignore_entity else None

        # Direct line of sight check first (fast path)
        if self.is_line_clear(sx, sy, gx, gy, obstacle_grid, ignored_cells):
            return [(gx, gy)]

        start_col, start_row = self.pos_to_grid(sx, sy)
        goal_col, goal_row = self.pos_to_grid(gx, gy)

        # Check path cache on game_state
        cache_key = (start_col, start_row, goal_col, goal_row, id(ignore_entity) if ignore_entity else None)
        if hasattr(game_state, '_path_cache') and cache_key in game_state._path_cache:
            cached = game_state._path_cache[cache_key]
            # Replace final waypoint with precise target
            res_path = list(cached[:-1]) + [(gx, gy)] if cached else [(gx, gy)]
            return res_path

        # Helper to check if a cell is blocked
        def is_blocked(c, r):
            if obstacle_grid[c][r]:
                if ignored_cells and (c, r) in ignored_cells:
                    return False
                return True
            return False

        # If goal is blocked, find nearest unblocked grid cell around goal
        if is_blocked(goal_col, goal_row):
            found_alt = False
            for r in range(1, 8):
                for dc in range(-r, r + 1):
                    for dr in range(-r, r + 1):
                        nc, nr = goal_col + dc, goal_row + dr
                        if 0 <= nc < self.cols and 0 <= nr < self.rows:
                            if not is_blocked(nc, nr):
                                goal_col, goal_row = nc, nr
                                found_alt = True
                                break
                    if found_alt:
                        break
                if found_alt:
                    break

        # Fast Octile distance heuristic
        def heuristic(c, r):
            dc = abs(c - goal_col)
            dr = abs(r - goal_row)
            return max(dc, dr) + 0.414 * min(dc, dr)

        # A* Search
        open_set = []
        heapq.heappush(open_set, (0, start_col, start_row))
        came_from = {}
        g_score = {(start_col, start_row): 0}

        found = False
        directions = [(-1,0), (1,0), (0,-1), (0,1), (-1,-1), (-1,1), (1,-1), (1,1)]
        max_expansions = 350
        expansions = 0

        best_node = (start_col, start_row)
        best_h = heuristic(start_col, start_row)

        while open_set and expansions < max_expansions:
            expansions += 1
            _, curr_c, curr_r = heapq.heappop(open_set)

            if (curr_c, curr_r) == (goal_col, goal_row):
                found = True
                best_node = (curr_c, curr_r)
                break

            h_val = heuristic(curr_c, curr_r)
            if h_val < best_h:
                best_h = h_val
                best_node = (curr_c, curr_r)

            for dc, dr in directions:
                nc, nr = curr_c + dc, curr_r + dr
                if 0 <= nc < self.cols and 0 <= nr < self.rows:
                    if is_blocked(nc, nr):
                        continue

                    # Prevent cutting diagonal corners if orthogonal cells are blocked
                    if dc != 0 and dr != 0:
                        if is_blocked(curr_c + dc, curr_r) or is_blocked(curr_c, curr_r + dr):
                            continue
                        cost = 1.414
                    else:
                        cost = 1.0

                    tentative_g = g_score[(curr_c, curr_r)] + cost

                    if (nc, nr) not in g_score or tentative_g < g_score[(nc, nr)]:
                        came_from[(nc, nr)] = (curr_c, curr_r)
                        g_score[(nc, nr)] = tentative_g
                        # Tie-breaking heuristic multiplier for faster search
                        f_score = tentative_g + heuristic(nc, nr) * 1.001
                        heapq.heappush(open_set, (f_score, nc, nr))

        if not found and best_node == (start_col, start_row):
            # Fallback: direct line to target
            res = [(gx, gy)]
            if hasattr(game_state, '_path_cache'):
                game_state._path_cache[cache_key] = res
            return res

        # Reconstruct path
        path_nodes = []
        curr = best_node if not found else (goal_col, goal_row)
        while curr in came_from:
            path_nodes.append(curr)
            curr = came_from[curr]
        path_nodes.reverse()

        # Convert grid nodes to world positions
        raw_waypoints = [self.grid_to_pos(c, r) for c, r in path_nodes]
        raw_waypoints.append((gx, gy))

        # Smooth path / string pulling
        smoothed = []
        curr_pos = (sx, sy)
        idx = 0
        while idx < len(raw_waypoints):
            # Find furthest visible waypoint
            next_idx = idx
            for j in range(len(raw_waypoints) - 1, idx, -1):
                wx, wy = raw_waypoints[j]
                if self.is_line_clear(curr_pos[0], curr_pos[1], wx, wy, obstacle_grid, ignored_cells):
                    next_idx = j
                    break

            if next_idx == idx:
                smoothed.append(raw_waypoints[idx])
                curr_pos = raw_waypoints[idx]
                idx += 1
            else:
                smoothed.append(raw_waypoints[next_idx])
                curr_pos = raw_waypoints[next_idx]
                idx = next_idx + 1

        final_path = smoothed if smoothed else [(gx, gy)]
        if hasattr(game_state, '_path_cache'):
            game_state._path_cache[cache_key] = final_path
        return final_path
