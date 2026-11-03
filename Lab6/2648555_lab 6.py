import random
import time
import csv


# ======================================================================
# 1. PLAIN BST (Part A) - iterative, so no recursion-limit problem
# ======================================================================
class Node:
    def __init__(self, key, value):
        self.key = key        # Patient ID
        self.value = value    # Patient Name
        self.left = None
        self.right = None


class BST:
    def __init__(self):
        self.root = None
        self.comparisons = 0   # counts nodes examined during search
        self.rotations = 0     # always 0 for a plain BST (kept for same interface)

    # ---------- insert ----------
    def insert(self, key, value):
        new = Node(key, value)
        if self.root is None:
            self.root = new
            return
        cur = self.root
        while True:
            if key == cur.key:            # duplicate ID: just update the name
                cur.value = value
                return
            elif key < cur.key:
                if cur.left is None:
                    cur.left = new
                    return
                cur = cur.left
            else:
                if cur.right is None:
                    cur.right = new
                    return
                cur = cur.right

    # ---------- search ----------
    def search(self, key):
        cur = self.root
        while cur is not None:
            self.comparisons += 1         # one comparison per node visited
            if key == cur.key:
                return cur.value
            cur = cur.left if key < cur.key else cur.right
        return None

    # ---------- delete ----------
    def delete(self, key):
        parent = None
        cur = self.root
        while cur is not None and cur.key != key:     # find the node
            parent = cur
            cur = cur.left if key < cur.key else cur.right
        if cur is None:
            return False                              # key not present

        # Case 3: two children -> copy inorder successor, then delete successor
        if cur.left is not None and cur.right is not None:
            parent = cur
            succ = cur.right
            while succ.left is not None:
                parent = succ
                succ = succ.left
            cur.key, cur.value = succ.key, succ.value
            cur = succ                                # now remove the successor

        # Case 1 (leaf) and Case 2 (one child): cur has at most one child
        child = cur.left if cur.left is not None else cur.right
        if parent is None:
            self.root = child
        elif parent.left is cur:
            parent.left = child
        else:
            parent.right = child
        return True

    # ---------- traversal / checks ----------
    def inorder(self):
        result, stack, cur = [], [], self.root
        while stack or cur is not None:
            while cur is not None:
                stack.append(cur)
                cur = cur.left
            cur = stack.pop()
            result.append(cur.key)
            cur = cur.right
        return result

    def height(self):
        if self.root is None:
            return 0
        best, stack = 0, [(self.root, 1)]
        while stack:
            node, depth = stack.pop()
            best = max(best, depth)
            if node.left:
                stack.append((node.left, depth + 1))
            if node.right:
                stack.append((node.right, depth + 1))
        return best

    def is_bst(self):
        """BST property: every key lies strictly between its ancestors' bounds."""
        if self.root is None:
            return True
        stack = [(self.root, float("-inf"), float("inf"))]
        while stack:
            node, low, high = stack.pop()
            if not (low < node.key < high):
                return False
            if node.left:
                stack.append((node.left, low, node.key))
            if node.right:
                stack.append((node.right, node.key, high))
        return True

    def print_tree(self):
        """Sideways print: right subtree on top, root at left. (iterative)"""
        stack = [(self.root, 0)]
        lines = []
        # reverse in-order: right, node, left
        cur, depth = self.root, 0
        stack = []
        while stack or cur is not None:
            while cur is not None:
                stack.append((cur, depth))
                cur, depth = cur.right, depth + 1
            cur, depth = stack.pop()
            lines.append("    " * depth + str(cur.key))
            cur, depth = cur.left, depth + 1
        print("\n".join(lines))


# ======================================================================
# 2. AVL TREE (Part B)
# ======================================================================
class AVLNode:
    def __init__(self, key, value):
        self.key = key
        self.value = value
        self.left = None
        self.right = None
        self.height = 1       # extra memory: one int per node


def h(node):
    return node.height if node else 0


def update(node):
    node.height = 1 + max(h(node.left), h(node.right))


def balance_factor(node):
    return h(node.left) - h(node.right) if node else 0


class AVLTree:
    def __init__(self):
        self.root = None
        self.comparisons = 0
        self.rotations = 0    # every single rotation counts 1 (double = 2)

    # ---------- the two basic rotations ----------
    def rotate_right(self, y):
        x = y.left
        y.left = x.right
        x.right = y
        update(y)
        update(x)
        self.rotations += 1
        return x              # new root of this subtree

    def rotate_left(self, x):
        y = x.right
        x.right = y.left
        y.left = x
        update(x)
        update(y)
        self.rotations += 1
        return y

    # ---------- rebalance: handles all 4 cases ----------
    def rebalance(self, node):
        update(node)
        bf = balance_factor(node)
        if bf > 1:                                    # left heavy
            if balance_factor(node.left) < 0:         # Left-Right case
                node.left = self.rotate_left(node.left)
            return self.rotate_right(node)            # Left-Left case
        if bf < -1:                                   # right heavy
            if balance_factor(node.right) > 0:        # Right-Left case
                node.right = self.rotate_right(node.right)
            return self.rotate_left(node)             # Right-Right case
        return node

    # ---------- insert ----------
    def insert(self, key, value):
        self.root = self._insert(self.root, key, value)

    def _insert(self, node, key, value):
        if node is None:
            return AVLNode(key, value)
        if key < node.key:
            node.left = self._insert(node.left, key, value)
        elif key > node.key:
            node.right = self._insert(node.right, key, value)
        else:
            node.value = value
            return node
        return self.rebalance(node)

    # ---------- search ----------
    def search(self, key):
        cur = self.root
        while cur is not None:
            self.comparisons += 1
            if key == cur.key:
                return cur.value
            cur = cur.left if key < cur.key else cur.right
        return None

    # ---------- delete ----------
    def delete(self, key):
        self._found = False                  # set to True inside _delete
        self.root = self._delete(self.root, key)
        return self._found

    def _delete(self, node, key):
        if node is None:
            return None
        if key < node.key:
            node.left = self._delete(node.left, key)
        elif key > node.key:
            node.right = self._delete(node.right, key)
        else:
            self._found = True
            if node.left is None:         # leaf or only right child
                return node.right
            if node.right is None:        # only left child
                return node.left
            succ = node.right             # two children: inorder successor
            while succ.left:
                succ = succ.left
            node.key, node.value = succ.key, succ.value
            node.right = self._delete(node.right, succ.key)
        return self.rebalance(node)

    # ---------- traversal / checks ----------
    def inorder(self):
        out = []
        def walk(n):
            if n:
                walk(n.left)
                out.append(n.key)
                walk(n.right)
        walk(self.root)
        return out

    def height(self):
        return h(self.root)

    def is_balanced(self):
        """Every node: |balance factor| <= 1 AND stored height is correct."""
        def check(n):
            if n is None:
                return True, 0
            lok, lh = check(n.left)
            rok, rh = check(n.right)
            ok = lok and rok and abs(lh - rh) <= 1 and n.height == 1 + max(lh, rh)
            return ok, 1 + max(lh, rh)
        return check(self.root)[0]

    def is_bst(self):
        def check(n, low, high):
            if n is None:
                return True
            if not (low < n.key < high):
                return False
            return check(n.left, low, n.key) and check(n.right, n.key, high)
        return check(self.root, float("-inf"), float("inf"))

    def print_tree(self, node="root", depth=0):
        if node == "root":
            node = self.root
        if node:
            self.print_tree(node.right, depth + 1)
            print("    " * depth + str(node.key))
            self.print_tree(node.left, depth + 1)


# ======================================================================
# 3. RED-BLACK TREE (self-learning component)
# ======================================================================
RED, BLACK = True, False


class RBNode:
    def __init__(self, key=None, value=None, color=RED):
        self.key = key
        self.value = value
        self.color = color
        self.left = None
        self.right = None
        self.parent = None


class RedBlackTree:
    def __init__(self):
        self.NIL = RBNode(color=BLACK)       # shared empty leaf
        self.root = self.NIL
        self.comparisons = 0
        self.rotations = 0

    # ---------- rotations (same idea as AVL, but fix parent pointers) ----------
    def rotate_left(self, x):
        y = x.right
        x.right = y.left
        if y.left is not self.NIL:
            y.left.parent = x
        y.parent = x.parent
        if x.parent is None:
            self.root = y
        elif x is x.parent.left:
            x.parent.left = y
        else:
            x.parent.right = y
        y.left = x
        x.parent = y
        self.rotations += 1

    def rotate_right(self, x):
        y = x.left
        x.left = y.right
        if y.right is not self.NIL:
            y.right.parent = x
        y.parent = x.parent
        if x.parent is None:
            self.root = y
        elif x is x.parent.right:
            x.parent.right = y
        else:
            x.parent.left = y
        y.right = x
        x.parent = y
        self.rotations += 1

    # ---------- insert ----------
    def insert(self, key, value):
        parent, cur = None, self.root
        while cur is not self.NIL:                    # normal BST descent
            parent = cur
            if key == cur.key:
                cur.value = value
                return
            cur = cur.left if key < cur.key else cur.right
        node = RBNode(key, value, RED)                # new nodes start RED
        node.left = node.right = self.NIL
        node.parent = parent
        if parent is None:
            self.root = node
        elif key < parent.key:
            parent.left = node
        else:
            parent.right = node
        self._fix_insert(node)

    def _fix_insert(self, z):
        # Only problem possible: z and its parent are both RED (breaks rule 3)
        while z.parent is not None and z.parent.color == RED:
            gp = z.parent.parent
            if z.parent is gp.left:
                uncle = gp.right
                if uncle.color == RED:                # Case 1: recolour
                    z.parent.color = BLACK
                    uncle.color = BLACK
                    gp.color = RED
                    z = gp
                else:
                    if z is z.parent.right:           # Case 2: triangle -> line
                        z = z.parent
                        self.rotate_left(z)
                    z.parent.color = BLACK            # Case 3: line -> rotate
                    gp.color = RED
                    self.rotate_right(gp)
            else:                                     # mirror image
                uncle = gp.left
                if uncle.color == RED:
                    z.parent.color = BLACK
                    uncle.color = BLACK
                    gp.color = RED
                    z = gp
                else:
                    if z is z.parent.left:
                        z = z.parent
                        self.rotate_right(z)
                    z.parent.color = BLACK
                    gp.color = RED
                    self.rotate_left(gp)
        self.root.color = BLACK

    # ---------- search ----------
    def search(self, key):
        cur = self.root
        while cur is not self.NIL:
            self.comparisons += 1
            if key == cur.key:
                return cur.value
            cur = cur.left if key < cur.key else cur.right
        return None

    # ---------- delete (CLRS) ----------
    def _transplant(self, u, v):          # replace subtree u by subtree v
        if u.parent is None:
            self.root = v
        elif u is u.parent.left:
            u.parent.left = v
        else:
            u.parent.right = v
        v.parent = u.parent

    def delete(self, key):
        z = self.root
        while z is not self.NIL and z.key != key:
            z = z.left if key < z.key else z.right
        if z is self.NIL:
            return False
        y, y_color = z, z.color
        if z.left is self.NIL:
            x = z.right
            self._transplant(z, z.right)
        elif z.right is self.NIL:
            x = z.left
            self._transplant(z, z.left)
        else:                                          # two children
            y = z.right
            while y.left is not self.NIL:
                y = y.left
            y_color = y.color
            x = y.right
            if y.parent is z:
                x.parent = y
            else:
                self._transplant(y, y.right)
                y.right = z.right
                y.right.parent = y
            self._transplant(z, y)
            y.left = z.left
            y.left.parent = y
            y.color = z.color
        if y_color == BLACK:        # removed a BLACK node -> rule 4 may break
            self._fix_delete(x)
        return True

    def _fix_delete(self, x):
        # x carries an "extra black"; push it up or absorb it
        while x is not self.root and x.color == BLACK:
            if x is x.parent.left:
                w = x.parent.right                     # sibling
                if w.color == RED:                     # Case 1
                    w.color = BLACK
                    x.parent.color = RED
                    self.rotate_left(x.parent)
                    w = x.parent.right
                if w.left.color == BLACK and w.right.color == BLACK:
                    w.color = RED                      # Case 2
                    x = x.parent
                else:
                    if w.right.color == BLACK:         # Case 3
                        w.left.color = BLACK
                        w.color = RED
                        self.rotate_right(w)
                        w = x.parent.right
                    w.color = x.parent.color           # Case 4
                    x.parent.color = BLACK
                    w.right.color = BLACK
                    self.rotate_left(x.parent)
                    x = self.root
            else:                                      # mirror image
                w = x.parent.left
                if w.color == RED:
                    w.color = BLACK
                    x.parent.color = RED
                    self.rotate_right(x.parent)
                    w = x.parent.left
                if w.right.color == BLACK and w.left.color == BLACK:
                    w.color = RED
                    x = x.parent
                else:
                    if w.left.color == BLACK:
                        w.right.color = BLACK
                        w.color = RED
                        self.rotate_left(w)
                        w = x.parent.left
                    w.color = x.parent.color
                    x.parent.color = BLACK
                    w.left.color = BLACK
                    self.rotate_right(x.parent)
                    x = self.root
        x.color = BLACK

    # ---------- traversal / checks ----------
    def inorder(self):
        out = []
        def walk(n):
            if n is not self.NIL:
                walk(n.left)
                out.append(n.key)
                walk(n.right)
        walk(self.root)
        return out

    def height(self):
        def hh(n):
            return 0 if n is self.NIL else 1 + max(hh(n.left), hh(n.right))
        return hh(self.root)

    def is_valid(self):
        """Checks rules 2, 3, 4 and the BST property."""
        if self.root.color != BLACK:
            return False
        def check(n, low, high):          # returns black height or -1 if broken
            if n is self.NIL:
                return 1
            if not (low < n.key < high):
                return -1
            if n.color == RED and (n.left.color == RED or n.right.color == RED):
                return -1
            lb = check(n.left, low, n.key)
            rb = check(n.right, n.key, high)
            if lb == -1 or rb == -1 or lb != rb:
                return -1
            return lb + (1 if n.color == BLACK else 0)
        return check(self.root, float("-inf"), float("inf")) != -1

    def print_tree(self, node=None, depth=0):
        if node is None:
            node = self.root
        if node is not self.NIL:
            self.print_tree(node.right, depth + 1)
            print("    " * depth + str(node.key) + ("R" if node.color == RED else "B"))
            self.print_tree(node.left, depth + 1)


# ======================================================================
# 4. WORKLOAD GENERATOR (Part C)
# ======================================================================
def sequential(n):
    return list(range(1, n + 1))


def random_perm(n, seed=42):
    ids = list(range(1, n + 1))
    random.Random(seed).shuffle(ids)
    return ids


def nearly_sorted(n, seed=42):
    ids = list(range(1, n + 1))
    rng = random.Random(seed)
    for _ in range(int(0.05 * n)):          # ~5% random swaps
        i, j = rng.randrange(n), rng.randrange(n)
        ids[i], ids[j] = ids[j], ids[i]
    return ids


DATASETS = {"Sequential": sequential, "Random": random_perm, "NearlySorted": nearly_sorted}


# ======================================================================
# 5. EXPERIMENTS (Part D)
# ======================================================================
SIZES = [1000, 5000, 10000]
TREES = {"BST": BST, "AVL": AVLTree, "RedBlack": RedBlackTree}


def min_height(n):
    """floor(log2 n) as asked in the lab sheet (add 1 for height counted in nodes)."""
    k = 0
    while n > 1:
        n //= 2
        k += 1
    return k


def verify(tree):
    """Assertions used in tests: BST property + balance rules."""
    if isinstance(tree, BST):
        assert tree.is_bst()
    elif isinstance(tree, AVLTree):
        assert tree.is_bst() and tree.is_balanced()
    else:
        assert tree.is_valid()


def run_one(tree_name, ds_name, n):
    ids = DATASETS[ds_name](n)
    tree = TREES[tree_name]()

    start = time.perf_counter()
    for k in ids:
        tree.insert(k, "Patient_%d" % k)
    insert_time = time.perf_counter() - start
    verify(tree)
    assert tree.inorder() == sorted(ids)          # sorted output => BST intact

    height = tree.height()
    rotations = tree.rotations

    rng = random.Random(7)                        # 1000 random existing IDs
    queries = [rng.choice(ids) for _ in range(1000)]
    tree.comparisons = 0
    for q in queries:
        assert tree.search(q) is not None
    avg_cmp = tree.comparisons / 1000

    victims = rng.sample(ids, n // 5)             # delete random 20%
    for k in victims:
        assert tree.delete(k)
    verify(tree)
    assert len(tree.inorder()) == n - len(victims)

    return {"tree": tree_name, "dataset": ds_name, "N": n,
            "height": height, "min_height": min_height(n),
            "insert_time_s": round(insert_time, 4), "rotations": rotations,
            "avg_search_cmp": round(avg_cmp, 2), "height_after_20pct_delete": tree.height()}


def main():
    rows = []
    for n in SIZES:
        for ds in DATASETS:
            for t in TREES:
                rows.append(run_one(t, ds, n))
                print("done", t, ds, n, flush=True)

    cols = list(rows[0].keys())
    print("\n" + " | ".join("%-12s" % c[:12] for c in cols))
    for r in rows:
        print(" | ".join("%-12s" % r[c] for c in cols))
    with open("results.csv", "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=cols)
        w.writeheader()
        w.writerows(rows)
    print("\nSaved results.csv")

    try:                                          # graph (matplotlib only for drawing)
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
        fig, ax = plt.subplots(1, 2, figsize=(11, 4))
        for t in TREES:
            seq = [r for r in rows if r["tree"] == t and r["dataset"] == "Sequential"]
            ax[0].plot([r["N"] for r in seq], [r["height"] for r in seq], marker="o", label=t)
            ax[1].plot([r["N"] for r in seq], [r["avg_search_cmp"] for r in seq], marker="o", label=t)
        ax[0].set_title("Sequential data: N vs height")
        ax[1].set_title("Sequential data: N vs avg search comparisons")
        for a in ax:
            a.set_xlabel("N"); a.set_yscale("log"); a.legend()
        ax[0].set_ylabel("height"); ax[1].set_ylabel("comparisons")
        plt.tight_layout()
        plt.savefig("height_comparison.png", dpi=120)
        print("Saved height_comparison.png")
    except ImportError:
        print("matplotlib not installed - skipped graph (CSV is still saved)")



# ======================================================================
# 6. DEMO (lab sample input) AND STRESS TEST
# ======================================================================
def demo():
    for name, tree in [("Plain BST", BST()), ("AVL", AVLTree()), ("Red-Black", RedBlackTree())]:
        for k in [10, 20, 30, 40, 50, 25]:
            tree.insert(k, "Patient_%d" % k)
        print("=== %s ===" % name)
        tree.print_tree()
        print("Height:", tree.height(), "| Rotations:", tree.rotations)
        print("In-order:", tree.inorder(), "\n")


def stress_test():
    rng = random.Random(1)
    for cls in (BST, AVLTree, RedBlackTree):
        t, ref = cls(), set()
        for step in range(4000):
            k = rng.randrange(300)
            if rng.random() < 0.55:
                t.insert(k, "x"); ref.add(k)
            else:
                t.delete(k); ref.discard(k)
            if step % 50 == 0:
                assert t.inorder() == sorted(ref)
                if cls is BST: assert t.is_bst()
                elif cls is AVLTree: assert t.is_bst() and t.is_balanced()
                else: assert t.is_valid()
        print(cls.__name__, "stress test passed")


if __name__ == "__main__":
    demo()          # sample input 10,20,30,40,50,25
    stress_test()   # correctness checks
    main()          # full comparison -> results.csv + height_comparison.png