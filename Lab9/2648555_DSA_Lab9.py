import re
import sys
# --------------------------------------------------------------------------- #
# Task 1: DP table
# --------------------------------------------------------------------------- #
def lcs_table(X, Y):
    """Return table L of size (m+1) x (n+1); L[i][j] = LCS length of X[:i], Y[:j]."""
    m, n = len(X), len(Y)
    L = [[0] * (n + 1) for _ in range(m + 1)]          # row 0 / column 0 stay 0
    for i in range(1, m + 1):
        for j in range(1, n + 1):
            if X[i - 1] == Y[j - 1]:                    # match: extend diagonal
                L[i][j] = L[i - 1][j - 1] + 1
            else:                                       # no match: best of up / left
                L[i][j] = max(L[i - 1][j], L[i][j - 1])
    return L
# --------------------------------------------------------------------------- #
# Task 2: traceback
# --------------------------------------------------------------------------- #
def lcs_traceback(L, X, Y):
    """Walk from L[m][n] back to the border; return one LCS as a list."""
    i, j = len(X), len(Y)
    result = []
    while i > 0 and j > 0:
        if X[i - 1] == Y[j - 1]:        # part of LCS, go diagonally
            result.append(X[i - 1])
            i -= 1
            j -= 1
        elif L[i - 1][j] >= L[i][j - 1]:  # tie -> go up (deterministic choice)
            i -= 1
        else:
            j -= 1
    result.reverse()
    return result

def lcs(X, Y):
    """Convenience: returns (table, length, one LCS)."""
    L = lcs_table(X, Y)
    return L, L[len(X)][len(Y)], lcs_traceback(L, X, Y)
# --------------------------------------------------------------------------- #
# Task 3: word-level ROUGE-L
# --------------------------------------------------------------------------- #
def tokenize(text):
    """Lowercase, strip punctuation, split into words (apostrophes inside words are dropped)."""
    text = text.lower().replace("'", "")
    return re.sub(r"[^a-z0-9\s]", " ", text).split()

def rouge_l(reference, candidate):
    """Return (precision, recall, f1, lcs_len, lcs_words, table, ref_words, cand_words)."""
    R, C = tokenize(reference), tokenize(candidate)
    L, l, words = lcs(R, C)
    precision = l / len(C) if C else 0.0      # empty candidate -> 0 (avoids ZeroDivision)
    recall = l / len(R) if R else 0.0
    f1 = 2 * precision * recall / (precision + recall) if l > 0 else 0.0
    return precision, recall, f1, l, words, L, R, C

# --------------------------------------------------------------------------- #
# Printing helpers
# --------------------------------------------------------------------------- #
def print_table(L, X, Y):
    """Pretty-print the DP table with row / column labels."""
    width = max([len(str(w)) for w in list(X) + list(Y)] + [2]) + 1
    print(" " * (width + 2) + "".join(f"{'':>{width}}" if k == 0 else f"{Y[k-1]:>{width}}" for k in range(len(Y) + 1)))
    for i in range(len(X) + 1):
        label = "" if i == 0 else X[i - 1]
        print(f"{label:>{width}} |" + "".join(f"{v:>{width}}" for v in L[i]))

def report_pair(idx, reference, candidate):
    p, r, f, l, words, L, R, C = rouge_l(reference, candidate)
    print(f"--- Pair {idx} ---")
    print(f"Reference : {' '.join(R)}")
    print(f"Candidate : {' '.join(C)}")
    print("DP table  :")
    print_table(L, R, C)
    print(f"LCS length : {l}")
    print(f"LCS words  : {' '.join(words)}")
    print(f"Precision  : {p:.3f}" + (f"   ({l}/{len(C)})" if C else "   (empty candidate)"))
    print(f"Recall     : {r:.3f}" + (f"   ({l}/{len(R)})" if R else "   (empty reference)"))
    print(f"F1         : {f:.3f}\n")
    return f

# --------------------------------------------------------------------------- #
# Task 4: batch evaluation
# --------------------------------------------------------------------------- #
def batch(lines):
    K = int(lines[0])
    assert 1 <= K <= 10, "K must be between 1 and 10"
    body = lines[1:] + [""] * (2 * K)               # tolerate missing trailing empty lines
    best_idx, best_f = 1, -1.0
    for k in range(K):
        ref, cand = body[2 * k], body[2 * k + 1]
        assert len(tokenize(ref)) <= 200 and len(tokenize(cand)) <= 200, "max 200 words per summary"
        f = report_pair(k + 1, ref, cand)
        if f > best_f:                              # strict '>' -> earliest pair wins ties
            best_f, best_idx = f, k + 1
    print(f"Best pair  : {best_idx}  (F1 = {best_f:.3f})")

# --------------------------------------------------------------------------- #
# Self-learning: space-optimised LCS and Hirschberg
# --------------------------------------------------------------------------- #
def lcs_length_two_rows(X, Y):
    """LCS length with only two rows; the shorter sequence indexes the columns -> O(min(m,n)) space."""
    if len(Y) > len(X):
        X, Y = Y, X                                  # LCS is symmetric, so swapping is safe
    prev = [0] * (len(Y) + 1)
    for xi in X:
        curr = [0] * (len(Y) + 1)
        for j in range(1, len(Y) + 1):
            curr[j] = prev[j - 1] + 1 if xi == Y[j - 1] else max(prev[j], curr[j - 1])
        prev = curr
    return prev[-1]

def _last_row(X, Y):
    """Last row of the LCS table of X vs Y, computed in O(len(Y)) space."""
    prev = [0] * (len(Y) + 1)
    for xi in X:
        curr = [0] * (len(Y) + 1)
        for j in range(1, len(Y) + 1):
            curr[j] = prev[j - 1] + 1 if xi == Y[j - 1] else max(prev[j], curr[j - 1])
        prev = curr
    return prev

def hirschberg(X, Y):
    """Return one LCS in linear space (divide & conquer around the middle of X)."""
    if len(X) == 0 or len(Y) == 0:
        return []
    if len(X) == 1:
        return [X[0]] if X[0] in Y else []
    mid = len(X) // 2
    top = _last_row(X[:mid], Y)                                  # forward scores
    bottom = _last_row(X[mid:][::-1], Y[::-1])                   # backward scores
    # split Y where forward + backward is maximal
    split = max(range(len(Y) + 1), key=lambda j: top[j] + bottom[len(Y) - j])
    return hirschberg(X[:mid], Y[:split]) + hirschberg(X[mid:], Y[split:])

def lcs_brute_force(X, Y, i=0, j=0):
    """Plain recursion, exponential - used only to cross-check on tiny inputs."""
    if i == len(X) or j == len(Y):
        return 0
    if X[i] == Y[j]:
        return 1 + lcs_brute_force(X, Y, i + 1, j + 1)
    return max(lcs_brute_force(X, Y, i + 1, j), lcs_brute_force(X, Y, i, j + 1))

def is_subsequence(S, T):
    it = iter(T)
    return all(any(s == t for t in it) for s in S)

# --------------------------------------------------------------------------- #
# Demonstration (Task 5)
# --------------------------------------------------------------------------- #
def demo():
    print("=" * 60 + "\nSAMPLE 1 - character sequences\n" + "=" * 60)
    X, Y = list("ABCBDAB"), list("BDCABA")
    L, l, s = lcs(X, Y)
    print_table(L, X, Y)
    print("LCS length :", l, "\nOne LCS    :", "".join(s), "\n")
    assert l == 4 and len(s) == 4 and is_subsequence(s, X) and is_subsequence(s, Y)

    print("=" * 60 + "\nSAMPLE 2 + 8 OWN TEST CASES (batch mode)\n" + "=" * 60)
    pairs = [
        ("the cat sat on the mat", "the cat is on the mat today"),                 # sample 2
        ("", "some candidate text"),                                               # empty reference
        ("a reference summary", ""),                                               # empty candidate
        ("", ""),                                                                  # both empty
        ("The court upheld the ruling.", "the court UPHELD the ruling"),           # identical (case/punct)
        ("apples and oranges", "dogs run fast"),                                   # completely different
        ("a a a b b", "a b a b a"),                                                # repeated words
        ("the the the the", "the the"),                                            # heavy repetition
        ("The government announced new tax rules on Monday.",
         "New tax rules were announced by the government."),                       # realistic
        ("Company profits rose sharply in the third quarter.",
         "Profits rose in the quarter."),                                          # short candidate
    ]
    print("NOTE on Sample 2: the question paper prints LCS length 4 / P=4/7 / F1=0.615, but its own LCS words")
    print("'the cat on the mat' are 5 words. Correct values are l=5, P=5/7=0.714, R=5/6=0.833, F1=0.769 (Pair 1 below).\n")
    lines = [str(len(pairs))] + [t for p in pairs for t in p]
    batch(lines)

    print("\n" + "=" * 60 + "\nSELF-LEARNING CHECKS\n" + "=" * 60)
    import random
    random.seed(7)
    for trial in range(300):
        a = [random.choice("ABC") for _ in range(random.randint(0, 9))]
        b = [random.choice("ABC") for _ in range(random.randint(0, 9))]
        base = lcs(a, b)[1]
        assert base == lcs_length_two_rows(a, b) == lcs_brute_force(a, b), (a, b)
        h = hirschberg(a, b)
        assert len(h) == base and is_subsequence(h, a) and is_subsequence(h, b), (a, b, h)
    print("300 random tests: DP table == two-row == brute force; Hirschberg LCS valid & optimal.  OK")
    big_x = [random.choice("ACGT") for _ in range(2000)]
    big_y = [random.choice("ACGT") for _ in range(1500)]
    print("2000 x 1500 sequences -> DP:", lcs(big_x, big_y)[1],
          "| two-row:", lcs_length_two_rows(big_x, big_y),
          "| Hirschberg length:", len(hirschberg(big_x, big_y)))

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--demo" or sys.stdin.isatty():
        demo()
    else:
        batch(sys.stdin.read().split("\n"))