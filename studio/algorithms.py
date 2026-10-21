"""Deterministic, UI-independent algorithm traces.

Every frame owns its data, so playback can move backward without rerunning work.
"""
from dataclasses import dataclass, field
import heapq


@dataclass
class Frame:
    values: list
    message: str
    active: tuple = ()
    settled: tuple = ()
    comparisons: int = 0
    writes: int = 0
    nodes: dict = field(default_factory=dict)
    edges: list = field(default_factory=list)
    visited: tuple = ()


SORTS = ["Bubble sort", "Insertion sort", "Selection sort", "Merge sort", "Quick sort", "Heap sort", "Shell sort"]
SEARCHES = ["Linear search", "Binary search"]
STRUCTURES = ["Singly linked list", "Doubly linked list", "Stack", "Queue", "Binary search tree", "AVL tree", "Min heap", "Max heap", "Hash table"]
GRAPHS = ["Breadth-first search", "Depth-first search", "Dijkstra", "Prim", "Kruskal"]
CATEGORIES = {"Sorting": SORTS, "Searching": SEARCHES, "Data structures": STRUCTURES, "Graphs": GRAPHS, "Compression": ["Huffman coding"]}
INFO = {
    "Bubble sort": ("O(n²)", "O(1)", "Compare neighbors and swap them when they are out of order. Each pass settles one more value."),
    "Insertion sort": ("O(n²)", "O(1)", "Grow a sorted prefix by moving each new value into its correct position."),
    "Selection sort": ("O(n²)", "O(1)", "Find the next smallest value in the remaining array, then place it at the boundary."),
    "Merge sort": ("O(n log n)", "O(n)", "Split the array recursively, then merge sorted halves back together."),
    "Quick sort": ("O(n log n) avg", "O(n) worst", "Partition around a pivot. Recursively sort the values on either side."),
    "Heap sort": ("O(n log n)", "O(1)", "Build a heap, then repeatedly move its root to the end of the array."),
    "Shell sort": ("O(n²) worst", "O(1)", "Use decreasing gaps to move distant values, finishing with insertion sort at gap 1."),
    "Linear search": ("O(n)", "O(1)", "Inspect each value until the target is found or the array is exhausted."),
    "Binary search": ("O(log n)", "O(1)", "Search a sorted array by repeatedly halving the remaining interval. Input is sorted automatically."),
    "Breadth-first search": ("O(V + E)", "O(V)", "Visit the fixed sample graph from A, exploring neighbors level by level using a queue."),
    "Depth-first search": ("O(V + E)", "O(V)", "Visit the fixed sample graph from A, following a branch before backtracking."),
    "Dijkstra": ("O(V² + E)", "O(V)", "Find shortest paths from A in the nonnegative weighted sample graph. Labels show current distances."),
    "Prim": ("O(VE)", "O(V + E)", "Grow a minimum spanning tree from A by choosing the cheapest edge leaving the tree."),
    "Kruskal": ("O(E log E)", "O(V + E)", "Build a minimum spanning tree by adding edges in weight order and skipping cycles."),
    "Huffman coding": ("O(n log n)", "O(n)", "Treat numbers as symbol frequencies. Repeatedly combine the two smallest weights into a prefix-code tree."),
}
for name in STRUCTURES:
    INFO[name] = ("O(n) per insert" if name in ["Binary search tree", "Hash table"] else "O(log n) per insert" if name in ["AVL tree", "Min heap", "Max heap"] else "O(1) per append", "O(n)", {
        "Singly linked list": "Append nodes in input order. Each arrow points to the next node; the tail points to null.",
        "Doubly linked list": "Append nodes with links in both directions. Each node knows its previous and next neighbor.",
        "Stack": "Push values onto a last-in, first-out stack. Pop removes the most recently added value.",
        "Queue": "Enqueue values into a first-in, first-out queue. Dequeue removes the oldest value.",
        "Binary search tree": "Insert smaller values to the left and larger values to the right. Duplicate values are skipped.",
        "AVL tree": "Insert values into a search tree and rotate unbalanced subtrees to keep heights within one.",
        "Min heap": "Insert values and sift upward so every parent is no greater than its children.",
        "Max heap": "Insert values and sift upward so every parent is no less than its children.",
        "Hash table": "Hash integers into seven buckets using value modulo 7. Collisions use separate chaining.",
    }[name])


def sorting(name, values, descending=False):
    a = list(values)
    frames = []
    comparisons = writes = 0
    def emit(msg, active=(), settled=()):
        frames.append(Frame(a.copy(), msg, tuple(active), tuple(settled), comparisons, writes))
    def before(x, y):
        nonlocal comparisons
        comparisons += 1
        return x > y if descending else x < y
    def swap(i, j):
        nonlocal writes
        a[i], a[j] = a[j], a[i]
        writes += 2
    emit("Ready. Play the trace or advance one step at a time.")
    n = len(a)
    if name == "Bubble sort":
        for end in range(n - 1, 0, -1):
            changed = False
            for j in range(end):
                wrong = before(a[j + 1], a[j])
                emit(f"Compare {a[j]} and {a[j + 1]}.", (j, j + 1), range(end + 1, n))
                if wrong:
                    swap(j, j + 1); changed = True
                    emit("Swap the out-of-order neighbors.", (j, j + 1), range(end + 1, n))
            if not changed:
                break
    elif name in ["Insertion sort", "Shell sort"]:
        gaps = [1]
        if name == "Shell sort":
            gaps = []; gap = n // 2
            while gap:
                gaps.append(gap); gap //= 2
        for gap in gaps:
            for i in range(gap, n):
                j = i
                while j >= gap:
                    wrong = before(a[j], a[j - gap])
                    emit(f"Compare positions {j - gap} and {j}; gap {gap}.", (j - gap, j))
                    if not wrong: break
                    swap(j, j - gap)
                    emit("Move the value toward its sorted position.", (j, j - gap))
                    j -= gap
    elif name == "Selection sort":
        for i in range(n):
            best = i
            for j in range(i + 1, n):
                if before(a[j], a[best]): best = j
                emit(f"Find the next value for position {i}.", (best, j), range(i))
            if i != best: swap(i, best)
            emit(f"Position {i} is settled.", (i,), range(i + 1))
    elif name == "Merge sort":
        def merge(lo, hi):
            nonlocal writes
            if hi - lo < 2: return
            mid = (lo + hi) // 2
            emit(f"Split positions {lo}–{hi - 1} at {mid}.", range(lo, hi))
            merge(lo, mid); merge(mid, hi)
            left, right = a[lo:mid], a[mid:hi]
            i = j = 0; out = []
            while i < len(left) and j < len(right):
                take_right = before(right[j], left[i])
                emit(f"Compare {left[i]} and {right[j]} for the merge.", (lo + i, mid + j))
                if take_right: out.append(right[j]); j += 1
                else: out.append(left[i]); i += 1
            out.extend(left[i:]); out.extend(right[j:])
            for k, value in enumerate(out, lo):
                a[k] = value; writes += 1
                emit(f"Write {value} to position {k}.", (k,))
        merge(0, n)
    elif name == "Quick sort":
        def quick(lo, hi):
            if lo >= hi: return
            pivot = a[hi]; i = lo
            emit(f"Choose {pivot} as pivot.", (hi,))
            for j in range(lo, hi):
                move = before(a[j], pivot)
                emit(f"Compare {a[j]} with pivot {pivot}.", (j, hi))
                if move:
                    swap(i, j); emit("Move value into the pivot's first partition.", (i, j)); i += 1
            swap(i, hi); emit(f"Pivot {pivot} reaches position {i}.", (i,))
            quick(lo, i - 1); quick(i + 1, hi)
        quick(0, n - 1)
    elif name == "Heap sort":
        def sift(root, end):
            while root * 2 + 1 < end:
                child = root * 2 + 1
                if child + 1 < end and before(a[child], a[child + 1]): child += 1
                move = before(a[root], a[child])
                emit("Compare the heap parent with its selected child.", (root, child), range(end, n))
                if not move: break
                swap(root, child); emit("Restore the heap property.", (root, child), range(end, n)); root = child
        for root in range(n // 2 - 1, -1, -1): sift(root, n)
        for end in range(n - 1, 0, -1):
            swap(0, end); emit("Move the heap root to its final position.", (end,), range(end, n)); sift(0, end)
    else:
        raise ValueError(f"Unknown sorting algorithm: {name}")
    emit("Complete. Every value is in order.", settled=range(n))
    return frames


def searching(name, values, target):
    a = sorted(values) if name == "Binary search" else list(values)
    frames = [Frame(a.copy(), "Input sorted for binary search." if name == "Binary search" else f"Search for {target}.")]
    lo, hi, count = 0, len(a) - 1, 0
    while lo <= hi:
        mid = (lo + hi) // 2 if name == "Binary search" else lo
        count += 1
        frames.append(Frame(a.copy(), f"Inspect position {mid}: {a[mid]} versus target {target}.", (mid,), comparisons=count))
        if a[mid] == target:
            frames.append(Frame(a.copy(), f"Found {target} at zero-based index {mid}.", settled=(mid,), comparisons=count)); return frames
        if name == "Binary search" and a[mid] > target: hi = mid - 1
        else: lo = mid + 1
    frames.append(Frame(a.copy(), f"Target {target} was not found.", comparisons=count))
    return frames


GRAPH_NODES = {0: "A", 1: "B", 2: "C", 3: "D", 4: "E", 5: "F", 6: "G"}
GRAPH_EDGES = [(0, 1, 4), (0, 2, 2), (1, 3, 5), (1, 4, 3), (2, 4, 1), (3, 5, 2), (4, 5, 4), (4, 6, 6), (5, 6, 1)]


def graph_trace(name):
    frames = []; visited = []; chosen = []
    def emit(msg, active=(), labels=None):
        frames.append(Frame([], msg, tuple(active), nodes=dict(labels or GRAPH_NODES), edges=list(GRAPH_EDGES), visited=tuple(visited), settled=tuple(chosen)))
    emit("Explore the weighted, undirected sample graph. Start vertex: A.")
    adjacent = {u: [] for u in GRAPH_NODES}
    for u, v, w in GRAPH_EDGES:
        adjacent[u].append((v, w)); adjacent[v].append((u, w))
    if name in ["Breadth-first search", "Depth-first search"]:
        pending = [0]; seen = {0}
        while pending:
            u = pending.pop(0 if name == "Breadth-first search" else -1); visited.append(u)
            for v, _ in (adjacent[u] if name == "Breadth-first search" else reversed(adjacent[u])):
                if v not in seen:
                    seen.add(v); pending.append(v)
            emit(f"Visit {GRAPH_NODES[u]}. Frontier: {', '.join(GRAPH_NODES[v] for v in pending) or 'empty'}.", (u,))
        emit("Traversal complete: " + " → ".join(GRAPH_NODES[u] for u in visited))
    elif name == "Dijkstra":
        dist = {u: float("inf") for u in GRAPH_NODES}; dist[0] = 0
        for _ in GRAPH_NODES:
            u = min((v for v in GRAPH_NODES if v not in visited), key=lambda v: dist[v]); visited.append(u)
            for v, w in adjacent[u]:
                if dist[u] + w < dist[v]: dist[v] = dist[u] + w
            emit(f"Settle {GRAPH_NODES[u]} at distance {dist[u]}; relax its neighbors.", (u,), {v: f"{GRAPH_NODES[v]} · {dist[v] if dist[v] != float('inf') else '∞'}" for v in dist})
        emit("Shortest distances from A: " + ", ".join(f"{GRAPH_NODES[v]}={dist[v]}" for v in dist), labels={v: f"{GRAPH_NODES[v]} · {dist[v]}" for v in dist})
    else:
        total = 0; parents = list(GRAPH_NODES)
        def root(v):
            while parents[v] != v: v = parents[v]
            return v
        remaining = sorted(GRAPH_EDGES, key=lambda e: e[2]); visited.append(0)
        while len(chosen) < len(GRAPH_NODES) - 1:
            eligible = [e for e in remaining if (e[0] in visited) != (e[1] in visited)] if name == "Prim" else remaining
            if not eligible: break
            u, v, w = eligible[0]; remaining.remove((u, v, w))
            if name == "Kruskal" and root(u) == root(v):
                emit(f"Skip {GRAPH_NODES[u]}–{GRAPH_NODES[v]}: it would create a cycle.", (u, v)); continue
            parents[root(u)] = root(v); chosen.append((u, v)); total += w
            visited[:] = list(dict.fromkeys(visited + [u, v]))
            emit(f"Add {GRAPH_NODES[u]}–{GRAPH_NODES[v]} (weight {w}). Total weight: {total}.", (u, v))
        emit(f"Minimum spanning tree complete. Total weight: {total}.")
    return frames


def structure_trace(name, values):
    frames = [Frame([], "Build the structure by inserting each input value.")]
    a = []; nodes = {}; edges = []; root_id = None; next_id = 0
    def emit(msg, active=()):
        frames.append(Frame(a.copy(), msg, tuple(active), nodes={k: v['value'] for k, v in nodes.items()}, edges=list(edges)))
    def refresh():
        edges[:] = [(k, v[side], 0) for k, v in nodes.items() for side in ['left', 'right'] if v[side] is not None]
    def height(k): return 0 if k is None else 1 + max(height(nodes[k]['left']), height(nodes[k]['right']))
    def rotate(k, left):
        side, other = ('right', 'left') if left else ('left', 'right')
        child = nodes[k][side]; nodes[k][side] = nodes[child][other]; nodes[child][other] = k
        return child
    def insert(k, value):
        nonlocal next_id
        if k is None:
            new = next_id; next_id += 1
            nodes[new] = dict(value=value, left=None, right=None); return new
        if value == nodes[k]['value']: return k
        side = 'left' if value < nodes[k]['value'] else 'right'
        nodes[k][side] = insert(nodes[k][side], value)
        if name == "AVL tree":
            balance = height(nodes[k]['left']) - height(nodes[k]['right'])
            if balance > 1:
                if value > nodes[nodes[k]['left']]['value']: nodes[k]['left'] = rotate(nodes[k]['left'], True)
                return rotate(k, False)
            if balance < -1:
                if value < nodes[nodes[k]['right']]['value']: nodes[k]['right'] = rotate(nodes[k]['right'], False)
                return rotate(k, True)
        return k
    for value in values:
        if name in ["Binary search tree", "AVL tree"]:
            duplicate = value in [v['value'] for v in nodes.values()]
            root_id = insert(root_id, value); refresh()
            emit(f"{'Skip duplicate' if duplicate else 'Insert'} {value}." + (" Rebalance where needed." if name == "AVL tree" else ""))
        elif name in ["Min heap", "Max heap"]:
            a.append(value); i = len(a) - 1
            emit(f"Insert {value} at the next leaf.", (i,))
            while i and ((a[i] < a[(i - 1) // 2]) if name == "Min heap" else (a[i] > a[(i - 1) // 2])):
                p = (i - 1) // 2; a[i], a[p] = a[p], a[i]
                emit("Sift upward to restore the heap property.", (i, p)); i = p
        else:
            a.append(value)
            emit(f"Insert {value} into bucket {value % 7}; collisions form a chain." if name == "Hash table" else f"{'Push' if name == 'Stack' else 'Enqueue' if name == 'Queue' else 'Append'} {value}.", (len(a) - 1,))
    emit("Construction complete. " + ("Use Pop to remove the top value." if name == "Stack" else "Use Dequeue to remove the front value." if name == "Queue" else "Each step preserves the structure's invariant."))
    return frames


def huffman_trace(values):
    if any(v <= 0 for v in values): raise ValueError("Huffman frequencies must be positive integers.")
    nodes = {i: f"{chr(65 + i)} · {v}" for i, v in enumerate(values)}
    edges = []; heap = [(v, i) for i, v in enumerate(values)]; heapq.heapify(heap)
    frames = [Frame([], "Each letter is a symbol; its input number is its frequency.", nodes=nodes.copy())]
    children = {}; next_id = len(values)
    while len(heap) > 1:
        w1, left = heapq.heappop(heap); w2, right = heapq.heappop(heap)
        nodes[next_id] = str(w1 + w2); edges.extend([(next_id, left, '0'), (next_id, right, '1')])
        children[next_id] = (left, right); heapq.heappush(heap, (w1 + w2, next_id))
        frames.append(Frame([], f"Combine the smallest weights: {w1} + {w2} = {w1 + w2}.", (left, right, next_id), nodes=nodes.copy(), edges=edges.copy())); next_id += 1
    codes = {}
    def walk(k, prefix):
        if k not in children: codes[chr(65 + k)] = prefix or '0'; return
        left, right = children[k]; walk(left, prefix + '0'); walk(right, prefix + '1')
    walk(heap[0][1], '')
    frames.append(Frame([], "Prefix codes: " + "   ".join(f"{k}={v}" for k, v in sorted(codes.items())), nodes=nodes.copy(), edges=edges.copy()))
    return frames


def trace(name, values, descending=False, target=42):
    if not values or len(values) > 24: raise ValueError("Enter between 1 and 24 integers.")
    if name in SORTS: return sorting(name, values, descending)
    if name in SEARCHES: return searching(name, values, target)
    if name in STRUCTURES: return structure_trace(name, values)
    if name in GRAPHS: return graph_trace(name)
    if name == "Huffman coding": return huffman_trace(values)
    raise ValueError(f"Unknown algorithm: {name}")
