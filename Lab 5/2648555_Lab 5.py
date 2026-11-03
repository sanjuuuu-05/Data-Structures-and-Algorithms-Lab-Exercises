V, E = input().split()
E = int(E)

graph = {}
for i in range(E):
    u, v = input().split()
    if u not in graph:
        graph[u] = []
    if v not in graph:
        graph[v] = []
    graph[u].append(v)
    graph[v].append(u)

S, T = input().split()          
if S not in graph:
    graph[S] = []
if T not in graph:
    graph[T] = []

for zone in graph:
    graph[zone].sort()          
zones = sorted(graph)

print("--- ADJACENCY LIST ---")
for zone in zones:
    print(zone, "->", graph[zone])

level = {S: 0}              
parent = {S: None}
bfs_order = []
queue = [S]
while len(queue) > 0:
    u = queue.pop(0)            
    bfs_order.append(u)
    for v in graph[u]:
        if v not in level:
            level[v] = level[u] + 1
            parent[v] = u
            queue.append(v) 

print("\n--- BFS FROM", S, "---")
print("BFS visiting order:", bfs_order)
print("Levels:", level)
last_wave = max(level.values())
for w in range(last_wave + 1):
    wave = []
    for zone in bfs_order:
        if level[zone] == w:
            wave.append(zone)
    print("Wave", w, ":", wave)

print("\n--- ROUTE", S, "to", T, "---")
if T not in level:
    print("Zone", T, "CANNOT be reached from HQ")
else:
    route = []
    z = T
    while z is not None:
        route.append(z)
        z = parent[z]       
    route.reverse()
    print("Route:", route)
    print("Length:", len(route) - 1, "roads")


def dfs(u):
    visited.append(u)
    for v in graph[u]:
        if v not in visited:
            dfs(v)

visited = []
dfs(S)
print("\n--- DFS FROM", S, "---")
print("DFS visiting order:", visited)

visited = []
components = []
for zone in zones:
    if zone not in visited:    
        before = len(visited)
        dfs(zone)
        components.append(visited[before:])

print("\n--- CONNECTED COMPONENTS ---")
print("Number of components:", len(components))
for c in components:
    print(sorted(c))

cut_off = []
for zone in zones:
    if zone not in level:
        cut_off.append(zone)
print("Cut-off zones (unreachable from HQ):", cut_off)


def find_cycle(u, came_from):
    seen.append(u)
    path.append(u)
    for v in graph[u]:
        if v == came_from:
            continue
        if v in path:                   
            start = path.index(v)
            return path[start:] + [v]
        if v not in seen:
            result = find_cycle(v, u)
            if result is not None:
                return result
    path.pop()
    return None

seen = []
path = []
cycle = None
for zone in zones:
    if cycle is None and zone not in seen:
        cycle = find_cycle(zone, None)

print("\n--- LOOP DETECTION ---")
if cycle is None:
    print("Cycle present? NO")
else:
    print("Cycle present? YES")
    print("One cycle:", cycle)