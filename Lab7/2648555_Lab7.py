import heapq
import math
import random
import time

INF = float("inf")
n = 6
names = ["Hebbal Hub", "Indiranagar", "Koramangala", "MG Road", "Jayanagar", "Electronic City"]
roads = [(0, 1, 4), (0, 2, 8), (1, 2, 2), (1, 3, 5), (2, 4, 10), (3, 4, 2), (3, 5, 6), (4, 5, 3)]
start = 0
blocked = (1, 3)          

def dijkstra(roads, start, n):
    graph = [[] for _ in range(n)]
    for u, v, w in roads:
        graph[u].append((v, w))
        graph[v].append((u, w))

    dist = [INF] * n          
    parent = [-1] * n 
    dist[start] = 0
    heap = [(0, start)]
    while heap:
        d, u = heapq.heappop(heap)       
        if d > dist[u]: continue         
        for v, w in graph[u]:
            if d + w < dist[v]:          
                dist[v] = d + w
                parent[v] = u
                heapq.heappush(heap, (dist[v], v))
    return dist, parent


def show(dist, parent):
    print("Locality             Time   Route")
    for t in range(n):
        if dist[t] == INF:
            print(f"{t} {names[t]:<18} INF    Not reachable")
        else:
            path = []
            x = t
            while x != -1:             
                path.append(x)
                x = parent[x]
            path.reverse()
            print(f"{t} {names[t]:<18} {dist[t]:<6} {path}")

negative = False
for u, v, w in roads:
    if w < 0:
        negative = True

print("===== SET A : DIJKSTRA =====")
if negative:
    print("Error: negative road time found. Dijkstra needs weights >= 0 (use Bellman-Ford).")
else:
    print("--- Normal traffic ---")
    dist1, parent1 = dijkstra(roads, start, n)
    show(dist1, parent1)

    if blocked is not None:
        open_roads = []                 
        for r in roads:
            if (r[0], r[1]) != blocked and (r[1], r[0]) != blocked:
                open_roads.append(r)
        print(f"\n--- Road {blocked[0]}-{blocked[1]} blocked ---")
        dist2, parent2 = dijkstra(open_roads, start, n)
        show(dist2, parent2)

        print("\nLocalities whose time changed:")
        for t in range(n):
            if dist1[t] != dist2[t]:
                print(f"  {names[t]}: {dist1[t]} -> {dist2[t]}")


points = [(0, 3), (1, 1), (2, 2), (4, 4), (0, 0), (1, 2), (3, 1), (3, 3)]


def cross(o, a, b):
    return (a[0] - o[0]) * (b[1] - o[1]) - (a[1] - o[1]) * (b[0] - o[0])


print("\n===== SET B : GRAHAM SCAN =====")
points = list(set(points))                

if len(points) < 3:                        
    print("Hull not possible: need at least 3 distinct points.")
else:
    anchor = points[0]
    for p in points:
        if p[1] < anchor[1] or (p[1] == anchor[1] and p[0] < anchor[0]):
            anchor = p

    others = []
    for p in points:
        if p != anchor:
            angle = round(math.atan2(p[1] - anchor[1], p[0] - anchor[0]), 9)
            others.append((angle, math.dist(anchor, p), p))
    others.sort()

    stack = [anchor]
    for angle, d, p in others:
        while len(stack) >= 2 and cross(stack[-2], stack[-1], p) <= 0:
            stack.pop()
        stack.append(p)

    if len(stack) < 3:                     
        print("All points are collinear. No proper hull, only a line from", stack[0], "to", stack[-1])
    else:
        perimeter = 0
        area = 0
        for i in range(len(stack)):
            x1, y1 = stack[i]
            x2, y2 = stack[(i + 1) % len(stack)]
            perimeter += math.dist((x1, y1), (x2, y2))
            area += x1 * y2 - x2 * y1
        area = abs(area) / 2
        print("Hull vertices (counter-clockwise):", stack)
        print(f"Perimeter: {perimeter:.2f} km")
        print(f"Area     : {area:.2f} sq km")

# =====================================================================
# SELF-LEARNING (Set A) - array version O(V^2) vs heap version O((V+E) log V)
# =====================================================================
print("\n===== SELF-LEARNING : ARRAY vs HEAP =====")
V = 1000
for label, E in [("Sparse", 2 * V), ("Dense", V * V // 4)]:
    graph = [[] for _ in range(V)]
    for i in range(1, V):                         
        j = random.randrange(i)
        w = random.randint(1, 100)
        graph[i].append((j, w))
        graph[j].append((i, w))
    for _ in range(E - (V - 1)):                  
        a, b, w = random.randrange(V), random.randrange(V), random.randint(1, 100)
        graph[a].append((b, w))
        graph[b].append((a, w))    
    begin = time.time()
    dist = [INF] * V
    finished = [False] * V
    dist[0] = 0
    for _ in range(V):
        u = -1
        for i in range(V):
            if not finished[i] and (u == -1 or dist[i] < dist[u]):
                u = i
        finished[u] = True
        for v, w in graph[u]:
            if dist[u] + w < dist[v]:
                dist[v] = dist[u] + w
    array_time = time.time() - begin
    begin = time.time()
    dist2 = [INF] * V
    dist2[0] = 0
    heap = [(0, 0)]
    while heap:
        d, u = heapq.heappop(heap)
        if d > dist2[u]: continue
        for v, w in graph[u]:
            if d + w < dist2[v]:
                dist2[v] = d + w
                heapq.heappush(heap, (dist2[v], v))
    heap_time = time.time() - begin
    print(f"{label:<7} V={V} E={E:<7} array={array_time:.3f}s  heap={heap_time:.3f}s  same answer: {dist == dist2}")