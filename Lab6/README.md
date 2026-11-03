# MediQueue Lab Question 6: BST vs AVL vs Red-Black Tree

Single-file Python implementation comparing a plain Binary Search Tree, an AVL tree and a Red-Black tree on a patient-record workload (key = Patient ID, value = Patient Name). No tree libraries are used.

**File:** `2648555_lab_6.py`

## Requirements

- Python 3.8 or newer
- `matplotlib` (optional, only used to draw the height graph)

If `matplotlib` is missing, the script still runs, skips the graph and prints a notice. The CSV is always saved.

```bash
pip install matplotlib
```

## How to Run

From the folder containing the script:

```bash
python3 2648555_lab_6.py
```

On Windows you can use `python 2648555_lab_6.py`.

No arguments or input files are needed.

## What Happens When You Run It

The script runs three stages in order:

1. **Demo.** Inserts the lab sample input `10, 20, 30, 40, 50, 25` into each tree and prints the tree sideways (right subtree on top, root at the left), the height, the rotation count and the in-order traversal. Red-Black nodes are suffixed `R` or `B` for their colour.
2. **Stress test.** Performs 4000 random inserts and deletes on each tree and checks against a reference set that the in-order output is sorted and correct. It also checks the BST, AVL balance and Red-Black rules. Prints `BST stress test passed`, `AVLTree stress test passed` and `RedBlackTree stress test passed`.
3. **Full experiment.** Runs every combination of:
   - Trees: BST, AVL, RedBlack
   - Datasets: Sequential, Random, NearlySorted (about 5% random swaps)
   - Sizes: N = 1000, 5000, 10000

   For each combination it measures height, theoretical minimum height, insert time, rotations, average search comparisons over 1000 random lookups, and height after deleting 20% of the keys.

The full experiment can take a little while because the plain BST degenerates to a linked list on sequential data. A progress line (`done <tree> <dataset> <N>`) is printed after each run.

## Output Files

Both files are written to the current working directory.

| File | Description |
|---|---|
| `results.csv` | One row per tree, dataset and size combination with all metrics |
| `height_comparison.png` | Two plots for sequential data: N vs height and N vs average search comparisons (log scale) |

### CSV Columns

`tree, dataset, N, height, min_height, insert_time_s, rotations, avg_search_cmp, height_after_20pct_delete`

## Notes

- Height is counted in nodes (an empty tree has height 0).
- `min_height` is `floor(log2 N)`, as the lab sheet asks. Add 1 to compare it with the node-counted height.
- The plain BST uses iterative insert, search and delete, so sequential data does not hit Python's recursion limit.
- Random datasets use fixed seeds (42 for data, 7 for queries), so results are reproducible apart from timing.
- Any failed `assert` means a tree broke its invariants. A normal run finishes without assertion errors.

## Running Only Part of the Script

To run a single stage, comment out the other calls at the bottom of the file:

```python
if __name__ == "__main__":
    demo()          # sample input 10,20,30,40,50,25
    stress_test()   # correctness checks
    main()          # full comparison -> results.csv + height_comparison.png
```
