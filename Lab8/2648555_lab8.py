# Lab 8 - Strassen's Matrix Multiplication (Divide and Conquer) - basic version
# No NumPy / BLAS is used for multiplication. Random numbers, timing and plotting only.
# Run:  python strassen_lab8.py     (press Enter to accept the [default] shown in a prompt)
import random
import time

try:                                  # plotting only; the program still runs without matplotlib
    import matplotlib
    import matplotlib.pyplot as plt
except ImportError:
    plt = None

mults = 0      # scalar multiplications counted so far
adds = 0       # scalar additions + subtractions counted so far


# ---------------------------------------------------------------- helper functions
def add(A, B):
    global adds
    adds += len(A) * len(A[0])
    return [[x + y for x, y in zip(rowA, rowB)] for rowA, rowB in zip(A, B)]


def sub(A, B):
    global adds
    adds += len(A) * len(A[0])
    return [[x - y for x, y in zip(rowA, rowB)] for rowA, rowB in zip(A, B)]


def split(A):
    # cut an n x n matrix into four n/2 x n/2 blocks
    h = len(A) // 2
    A11 = [row[:h] for row in A[:h]]
    A12 = [row[h:] for row in A[:h]]
    A21 = [row[:h] for row in A[h:]]
    A22 = [row[h:] for row in A[h:]]
    return A11, A12, A21, A22


def combine(C11, C12, C21, C22):
    # glue four blocks back into one matrix
    top = [r1 + r2 for r1, r2 in zip(C11, C12)]
    bottom = [r1 + r2 for r1, r2 in zip(C21, C22)]
    return top + bottom


def pad(A, size):
    # add zero columns, then zero rows, until A is size x size
    rows = [row + [0] * (size - len(row)) for row in A]
    rows += [[0] * size for _ in range(size - len(A))]
    return rows


def same(X, Y):
    # equal within a small tolerance (needed for float data)
    for rowX, rowY in zip(X, Y):
        for x, y in zip(rowX, rowY):
            if abs(x - y) > 1e-6 * max(1, abs(y)):
                return False
    return True


# ---------------------------------------------------------------- Task 1: classical O(n^3)
def classical(A, B):
    global mults, adds
    m, k, p = len(A), len(B), len(B[0])
    mults += m * k * p              # exact count, added once per call
    adds += m * (k - 1) * p
    Bt = [list(col) for col in zip(*B)]     # columns of B (just for speed)
    C = []
    for i in range(m):
        row = []
        for j in range(p):
            total = 0
            for x, y in zip(A[i], Bt[j]):
                total += x * y
            row.append(total)
        C.append(row)
    return C


# ---------------------------------------------------------------- Task 2 + 4: Strassen with cutoff T
def strassen(A, B, T):
    n = len(A)                      # n is a power of two here
    if n <= T:                      # Task 4: small block -> classical method
        return classical(A, B)

    A11, A12, A21, A22 = split(A)
    B11, B12, B21, B22 = split(B)

    # the seven products (only 7 recursive multiplications instead of 8)
    M1 = strassen(add(A11, A22), add(B11, B22), T)    # M1 = (A11 + A22)(B11 + B22)
    M2 = strassen(add(A21, A22), B11, T)              # M2 = (A21 + A22) B11
    M3 = strassen(A11, sub(B12, B22), T)              # M3 = A11 (B12 - B22)
    M4 = strassen(A22, sub(B21, B11), T)              # M4 = A22 (B21 - B11)
    M5 = strassen(add(A11, A12), B22, T)              # M5 = (A11 + A12) B22
    M6 = strassen(sub(A21, A11), add(B11, B12), T)    # M6 = (A21 - A11)(B11 + B12)
    M7 = strassen(sub(A12, A22), add(B21, B22), T)    # M7 = (A12 - A22)(B21 + B22)

    C11 = add(sub(add(M1, M4), M5), M7)               # C11 = M1 + M4 - M5 + M7
    C12 = add(M3, M5)                                 # C12 = M3 + M5
    C21 = add(M2, M4)                                 # C21 = M2 + M4
    C22 = add(add(sub(M1, M2), M3), M6)               # C22 = M1 - M2 + M3 + M6
    return combine(C11, C12, C21, C22)


# ---------------------------------------------------------------- Task 3: any size (pad, multiply, trim)
def multiply(A, B, T, algo=None):
    algo = algo or strassen                 # standard Strassen unless another algorithm is passed
    m, p = len(A), len(B[0])
    size = 1
    while size < max(m, len(B), p):         # next power of two
        size *= 2
    C = algo(pad(A, size), pad(B, size), max(T, 1))
    return [row[:p] for row in C[:m]]       # trim back to m x p


def random_matrix(rows, cols):
    return [[random.randint(0, 9) for _ in range(cols)] for _ in range(rows)]


def show(name, M):
    print(name)
    for row in M:
        print("  ", row)


# ---------------------------------------------------------------- Self-learning: Strassen-Winograd variant
def winograd(A, B, T):
    # Same 7 recursive products as Strassen, but only 15 block additions (Strassen uses 18)
    n = len(A)
    if n <= T:
        return classical(A, B)

    A11, A12, A21, A22 = split(A)
    B11, B12, B21, B22 = split(B)

    # 8 additions/subtractions on the inputs (4 on A, 4 on B), reused between products
    S1 = add(A21, A22)                 # S1 = A21 + A22
    S2 = sub(S1, A11)                  # S2 = S1 - A11
    S3 = sub(A11, A21)                 # S3 = A11 - A21
    S4 = sub(A12, S2)                  # S4 = A12 - S2
    T1 = sub(B12, B11)                 # T1 = B12 - B11
    T2 = sub(B22, T1)                  # T2 = B22 - T1
    T3 = sub(B22, B12)                 # T3 = B22 - B12
    T4 = sub(T2, B21)                  # T4 = T2 - B21

    # the seven products (7 recursive multiplications, as in Strassen)
    M1 = winograd(A11, B11, T)         # M1 = A11 B11
    M2 = winograd(A12, B21, T)         # M2 = A12 B21
    M3 = winograd(S4, B22, T)          # M3 = S4 B22
    M4 = winograd(A22, T4, T)          # M4 = A22 T4
    M5 = winograd(S1, T1, T)           # M5 = S1 T1
    M6 = winograd(S2, T2, T)           # M6 = S2 T2
    M7 = winograd(S3, T3, T)           # M7 = S3 T3

    # 7 additions/subtractions to combine (total 8 + 7 = 15)
    U2 = add(M1, M6)                   # U2 = M1 + M6
    U3 = add(U2, M7)                   # U3 = U2 + M7
    U4 = add(U2, M5)                   # U4 = U2 + M5
    C11 = add(M1, M2)                  # C11 = M1 + M2
    C12 = add(U4, M3)                  # C12 = U4 + M3
    C21 = sub(U3, M4)                  # C21 = U3 - M4
    C22 = add(U3, M5)                  # C22 = U3 + M5
    return combine(C11, C12, C21, C22)


def finish_plot(fig, filename):
    # save the graph next to the script, then try to show it in a window
    fig.savefig(filename, dpi=150)
    print(f"Graph saved: {filename}")
    try:
        plt.show()
    except Exception:
        pass


# ====================================================================== DEMONSTRATION
print("===== TEST 1 : sample from the lab sheet (n = 2) =====")
A = [[1, 2], [3, 4]]
B = [[5, 6], [7, 8]]
expected = [[19, 22], [43, 50]]
show("A x B (classical):", classical(A, B))
show("A x B (Strassen, T = 1):", multiply(A, B, 1))
print("Expected [[19, 22], [43, 50]] ->", "PASS" if same(multiply(A, B, 1), expected) else "FAIL")

print("\n===== TEST 2 : rectangular 3x4 times 4x2 (padding and trimming) =====")
A = random_matrix(3, 4)
B = random_matrix(4, 2)
C1 = classical(A, B)
C2 = multiply(A, B, 1)
show("Classical:", C1)
show("Strassen :", C2)
print("Result size", len(C2), "x", len(C2[0]), "->", "PASS" if same(C2, C1) else "FAIL")

print("\n===== TEST 3 : your own test =====")
n = int(input("Matrix size n [5]: ") or 5)
T = int(input("Cutoff threshold T [2]: ") or 2)
mode = input("Enter matrices by keyboard (k) or random (r) [r]: ") or "r"
if mode == "k":
    print("Enter matrix A, one row per line (numbers separated by spaces):")
    A = [[float(x) for x in input().split()] for _ in range(n)]
    print("Enter matrix B:")
    B = [[float(x) for x in input().split()] for _ in range(n)]
else:
    A = random_matrix(n, n)
    B = random_matrix(n, n)

mults = adds = 0
start = time.perf_counter()
C1 = classical(A, B)
t1 = time.perf_counter() - start
m1, a1 = mults, adds

mults = adds = 0
start = time.perf_counter()
C2 = multiply(A, B, T)
t2 = time.perf_counter() - start
m2, a2 = mults, adds

if n <= 8:
    show("A:", A)
    show("B:", B)
    show("A x B (classical):", C1)
    show("A x B (Strassen) :", C2)
print("Validation:", "PASS" if same(C2, C1) else "FAIL")
print(f"Classical: {m1} multiplications, {a1} additions, {t1:.6f} s")
print(f"Strassen : {m2} multiplications, {a2} additions, {t2:.6f} s  (T = {T})")

# ====================================================================== TASK 5 + 6: BENCHMARK
print("\n===== BENCHMARK (Task 5 and Task 6) =====")
if (input("Run benchmark for n = 2 ... 512? It can take a few minutes. (y/n) [y]: ") or "y") == "y":
    T = int(input("Cutoff T for the benchmark [32]: ") or 32)
    sizes = [2, 4, 8, 16, 32, 64, 128, 256, 512]
    classical_times = []
    strassen_times = []
    print(f"\n{'n':>4} | {'classical mult':>14} {'add':>11} {'time(s)':>9} | {'strassen mult':>13} {'add':>11} {'time(s)':>9} | result")
    for n in sizes:
        A = random_matrix(n, n)
        B = random_matrix(n, n)

        mults = adds = 0
        start = time.perf_counter()
        C1 = classical(A, B)
        t1 = time.perf_counter() - start
        m1, a1 = mults, adds

        mults = adds = 0
        start = time.perf_counter()
        C2 = multiply(A, B, T)
        t2 = time.perf_counter() - start
        m2, a2 = mults, adds

        classical_times.append(t1)
        strassen_times.append(t2)
        result = "PASS" if same(C2, C1) else "FAIL"
        print(f"{n:>4} | {m1:>14} {a1:>11} {t1:>9.4f} | {m2:>13} {a2:>11} {t2:>9.4f} | {result}")

    # Task 5: running time against n (classical vs Strassen)
    if plt:
        fig, axes = plt.subplots(1, 2, figsize=(10, 4))
        for ax, log in zip(axes, [False, True]):
            ax.plot(sizes, classical_times, "o-", label="Classical O(n^3)", color="#4f46e5")
            ax.plot(sizes, strassen_times, "s-", label=f"Strassen (T = {T})", color="#d97706")
            ax.set_xlabel("matrix size n")
            ax.set_ylabel("time (s)")
            ax.grid(alpha=0.3)
            ax.legend()
            if log:
                ax.set_xscale("log", base=2)
                ax.set_yscale("log")
                ax.set_title("Log-log scale")
            else:
                ax.set_title("Linear scale")
        fig.suptitle("Running time: classical vs Strassen (pure Python)")
        fig.tight_layout()
        finish_plot(fig, "time_graph.png")

    # Float data: needs the tolerance in same()
    print("\nFloat matrices (tolerance check):")
    for n in [16, 64]:
        A = [[random.random() for _ in range(n)] for _ in range(n)]
        B = [[random.random() for _ in range(n)] for _ in range(n)]
        print(f"  n = {n}:", "PASS" if same(multiply(A, B, T), classical(A, B)) else "FAIL")

# ====================================================================== SELF-LEARNING: Strassen-Winograd
print("\n===== SELF-LEARNING : Strassen-Winograd variant =====")
if (input("Run the Strassen-Winograd experiment? (y/n) [y]: ") or "y") == "y":
    partA, partB = [], []              # kept for the graph at the end
    print("Part A: operation counts, full recursion (T = 1)")
    print(f"{'n':>4} | {'mult (both)':>11} | {'Strassen add':>13} {'Winograd add':>13} {'saved':>7} | {'Strassen s':>10} {'Winograd s':>10} | result")
    for n in [2, 4, 8, 16, 32, 64]:
        A = random_matrix(n, n)
        B = random_matrix(n, n)
        C0 = classical(A, B)

        mults = adds = 0
        start = time.perf_counter()
        C1 = multiply(A, B, 1)
        ts = time.perf_counter() - start
        ms, a_s = mults, adds

        mults = adds = 0
        start = time.perf_counter()
        C2 = multiply(A, B, 1, winograd)
        tw = time.perf_counter() - start
        mw, aw = mults, adds

        ok = "PASS" if same(C1, C0) and same(C2, C0) and ms == mw else "FAIL"
        partA.append((n, a_s, aw))
        print(f"{n:>4} | {ms:>11} | {a_s:>13} {aw:>13} {100 * (a_s - aw) / a_s:>6.1f}% | {ts:>10.4f} {tw:>10.4f} | {ok}")

    print("\nPart B: running time with cutoff T = 32")
    print(f"{'n':>4} | {'Strassen add':>13} {'Winograd add':>13} | {'Strassen s':>10} {'Winograd s':>10} | result")
    for n in [64, 128, 256, 512]:
        A = random_matrix(n, n)
        B = random_matrix(n, n)

        mults = adds = 0
        start = time.perf_counter()
        C1 = multiply(A, B, 32)
        ts = time.perf_counter() - start
        a_s = adds

        mults = adds = 0
        start = time.perf_counter()
        C2 = multiply(A, B, 32, winograd)
        tw = time.perf_counter() - start
        aw = adds
        partB.append((n, ts, tw))
        print(f"{n:>4} | {a_s:>13} {aw:>13} | {ts:>10.4f} {tw:>10.4f} | {'PASS' if same(C1, C2) else 'FAIL'}")

    print("\nPart C: float matrices and odd sizes (tolerance check)")
    for n in [16, 33, 64]:
        A = [[random.random() for _ in range(n)] for _ in range(n)]
        B = [[random.random() for _ in range(n)] for _ in range(n)]
        print(f"  n = {n}:", "PASS" if same(multiply(A, B, 4, winograd), classical(A, B)) else "FAIL")

    # graph: additions (T = 1) and running time (T = 32), Strassen vs Winograd
    if plt:
        fig, axes = plt.subplots(1, 2, figsize=(10, 3.8))
        for ax, data, labels, xl, yl, title in [
            (axes[0], partA, ("n (T = 1)", "additions (log)", "Additions"), None, None, None),
            (axes[1], partB, ("n (T = 32)", "time (s, log)", "Running time"), None, None, None)]:
            x = range(len(data))
            ax.bar([i - 0.19 for i in x], [d[1] for d in data], 0.38, label="Strassen", color="#d97706")
            ax.bar([i + 0.19 for i in x], [d[2] for d in data], 0.38, label="Winograd", color="#059669")
            ax.set_xticks(list(x))
            ax.set_xticklabels([str(d[0]) for d in data])
            ax.set_yscale("log")
            ax.set_xlabel(labels[0])
            ax.set_ylabel(labels[1])
            ax.set_title(labels[2])
            ax.legend(fontsize=8)
        fig.tight_layout()
        finish_plot(fig, "winograd_graph.png")
