#Parse the file into matrix
import sys
import heapq
from itertools import count

def Parser(filename):
    with open(filename, 'r') as file:
        columns = int(file.readline().strip())
        rows = int(file.readline().strip())

        print(f"No. of columns = {columns}")
        print(f"No. of rows = {rows}")

        grid = []
        for _ in range(rows):
            grid.append(list(file.readline().strip()))

        start = None
        dirtyset = set()

        for row in range(rows):
            for col in range(columns):
                if grid[row][col] == "@":
                    start = (row, col)
                elif grid[row][col] == "*":
                    dirtyset.add((row, col))
        #returning my state basically.
        return grid, start, dirtyset
    
def in_bounds(r, c, grid):
    return 0 <= r < len(grid) and 0 <= c < len(grid[0])

def make_state_key(pos, dirty_set):
    return (pos, tuple(sorted(dirty_set)))

def dfs(grid, start, dirty):
    visited = set()

    def search(pos, dirty_set, path, gen, exp):
        if not dirty_set:
            return path, gen, exp

        state_key = make_state_key(pos, dirty_set)
        if state_key in visited:
            return None, gen, exp
        visited.add(state_key)
        exp += 1

        r, c = pos

        # Vacuum successor
        if (r, c) in dirty_set:
            new_dirty = set(dirty_set)
            new_dirty.remove((r, c))
            child_key = make_state_key(pos, new_dirty)
            gen += 1                              
            if child_key not in visited:
                res, gen, exp = search(pos, new_dirty, path + ['V'], gen, exp)
                if res is not None:
                    return res, gen, exp

        # Moving.
        for action, (dr, dc) in [('N',(-1,0)), ('S',(1,0)), ('W',(0,-1)), ('E',(0,1))]:
            nr, nc = r + dr, c + dc
            if in_bounds(nr, nc, grid) and grid[nr][nc] != '#':
                child_key = make_state_key((nr, nc), dirty_set)
                gen += 1                          # should I be countin duplicates???
                if child_key in visited:
                    continue
                res, gen, exp = search((nr, nc), dirty_set, path + [action], gen, exp)
                if res is not None:
                    return res, gen, exp

        return None, gen, exp

    return search(start, set(dirty), [], 0, 0)
    



#dijkstra/UCS

def ucs(grid, start, dirty):
    start_dirty = tuple(sorted(dirty))
    start_key = (start, start_dirty)

    pq = []
    tiebreak = count()
    heapq.heappush(pq, (0, next(tiebreak), start, start_dirty, []))

    best_cost = { start_key: 0 }
    settled = set()     # ones whos best cost wont change anymore
    gen = 0
    exp = 0

    while pq:
        cost, _, pos, dirty_t, path = heapq.heappop(pq)
        state_key = (pos, dirty_t)

        if state_key in settled:
            continue
        
        if cost > best_cost.get(state_key, float('inf')):
            continue

        if not dirty_t:
            return path, gen, exp 
        #checkin if I achieved cleanliness yet

        settled.add(state_key)
        exp += 1

        r, c = pos

        # cost incrementing and vacuuming, pain in the ASSSSSS
        if (r, c) in dirty_t:
            new_dirty = tuple(d for d in dirty_t if d != (r, c))
            child_key = (pos, new_dirty)
            new_cost = cost + 1
            gen += 1
            if new_cost < best_cost.get(child_key, float('inf')):
                best_cost[child_key] = new_cost
                heapq.heappush(pq, (new_cost, next(tiebreak), pos, new_dirty, path + ['V']))

        # Moving
        for action, (dr, dc) in [('N', (-1, 0)), ('S', (1, 0)), ('W', (0, -1)), ('E', (0, 1))]:
            nr, nc = r + dr, c + dc
            if in_bounds(nr, nc, grid) and grid[nr][nc] != '#':
                new_pos = (nr, nc)
                child_key = (new_pos, dirty_t)
                new_cost = cost + 1
                gen += 1
                if new_cost < best_cost.get(child_key, float('inf')):
                    best_cost[child_key] = new_cost
                    heapq.heappush(pq, (new_cost, next(tiebreak), new_pos, dirty_t, path + [action]))

    return None, gen, exp



if __name__ == "__main__":
    func = sys.argv[1]
    filename = sys.argv[2]
    grid, start, dirtyset = Parser(filename)

    if func == "depth-first":
        plan, nodes_generated, nodes_expanded = dfs(grid, start, dirtyset)
        
    elif func == "uniform-cost":
        plan, nodes_generated, nodes_expanded = ucs(grid, start, dirtyset)

    else:
        print("Unknown algorithm dude wth")
        sys.exit(1)
    if plan is None:
        print("No solution found")
    else:
        for p in plan:
            print(p)
        print(f"{nodes_generated} nodes generated")
        print(f"{nodes_expanded} nodes expanded")
