# Hashing lab - PNR lookup: linear probing + tombstones + rehashing
EMPTY, DEL = None, "DEL"
m = 11
table = [EMPTY] * m
rehash_on = True

def load():                                  # alpha = occupied / m
    n = 0
    for x in table:
        if x is not EMPTY and x != DEL:
            n += 1
    return n / m

def find(pnr):                               # returns (index, probes); -1 if absent
    i = pnr % m
    for p in range(1, m + 1):                # at most m probes, never loops forever
        if table[i] is EMPTY: return -1, p   # EMPTY ends the chain
        if table[i] != DEL and table[i][0] == pnr: return i, p
        i = (i + 1) % m                      # DEL: keep walking
    return -1, m

def insert(r):                               # r = (pnr, name, train, status)
    if find(r[0])[0] != -1: print("Duplicate PNR"); return
    i = r[0] % m
    for p in range(1, m + 1):
        if table[i] is EMPTY or table[i] == DEL:     # reuse tombstone
            table[i] = r
            print("home", r[0] % m, "final", i, "probes", p)
            break
        i = (i + 1) % m
    else:
        print("Hash table overflow"); return
    if rehash_on and load() > 0.7: rehash()

def search(pnr):
    if load() == 0: print("Table is empty"); return
    i, p = find(pnr)
    print(table[i] if i != -1 else "Not Found", "| probes", p)

def delete(pnr):
    if load() == 0: print("Table is empty"); return
    i = find(pnr)[0]
    if i == -1: print("PNR not found")
    else: table[i] = DEL        # DEL, not EMPTY, so chains stay unbroken

def next_prime(x):
    while not all(x % d for d in range(2, x)): x += 1
    return x

def rehash():                                # new size = prime >= 2m, re-insert all
    global m, table
    old = [x for x in table if x is not EMPTY and x != DEL]
    m = next_prime(2 * m)
    table = [EMPTY] * m
    for r in old: insert(r)                  # k mod m changes, so cannot just copy

def display():
    for i in range(m):
        if table[i] is EMPTY: print(i, "EMPTY")
        elif table[i] == DEL: print(i, "DELETED")
        else: print(i, table[i][0])
    print("load", round(load(), 2))

def reset():
    # back to an empty table of size 11 so each demo starts clean
    global m, table, rehash_on
    m, table, rehash_on = 11, [EMPTY] * 11, True
    entered.clear()
    print("Table reset: size 11, empty, rehashing ON")

# ---- Self-learning: which probing is better? Same 8 keys, m = 11 ----
def avg_probes(keys, step, m=11):
    t, total = [None] * m, 0
    for k in keys:
        for i in range(m):
            j = (k % m + step(k, i)) % m     # only 'step' differs between methods
            if t[j] is None:
                t[j] = k
                total += i + 1
                break
    return total / len(keys)

def compare(keys):
    print("Linear    :", avg_probes(keys, lambda k, i: i))               # h + i
    print("Quadratic :", avg_probes(keys, lambda k, i: i * i))           # h + i^2
    print("Double    :", avg_probes(keys, lambda k, i: i * (7 - k % 7))) # h + i*h2

def valid(s):                                # B4: exactly 10 digits
    return len(s) == 10 and s.isdigit()

def demo():
    # Task 5: the 8 bookings and the required sequence of operations
    global m, table, rehash_on
    m, table, rehash_on = 11, [EMPTY] * 11, True
    data = [(8203416572, "Ananya Rao", 12627, "CONFIRMED"),
            (8203416583, "Rahul Menon", 12627, "RAC"),
            (8203416540, "Fatima Sheikh", 16526, "CONFIRMED"),
            (8203416599, "Vikram Iyer", 12008, "WAITLIST"),
            (8203416615, "Divya Nair", 12627, "CONFIRMED"),
            (8203416561, "Arjun Patil", 16526, "RAC"),
            (8203416604, "Sneha Kulkarni", 12008, "CONFIRMED"),
            (8203416626, "Karthik Gowda", 12627, "WAITLIST")]
    for r in data[:7]:
        insert(r)
    print("Load factor after insertion #7:", round(load(), 3))
    delete(8203416583)                   # Rahul cancels
    search(8203416561)                   # found past the tombstone
    search(8203416583)                   # Not Found
    insert(data[7])                      # reuses the tombstone; no rehash (7/11 = 0.64)

LAB_KEYS = [8203416572, 8203416583, 8203416540, 8203416599,
            8203416615, 8203416561, 8203416604, 8203416626]
entered = []                                 # keys you typed in, for the comparison
while True:
    ch = input("\n1.Insert \n2.Search \n3.Delete \n4.Display \n5.Compare probing \n6.Rehashing ON/OFF \n7.Reset \n8.Demo \n9.Exit : ").strip()
    if ch in ("1", "2", "3"):
        s = input("PNR (10 digits): ").strip()
        if not valid(s):
            print("Invalid PNR")
            continue
        pnr = int(s)
        if ch == "1":
            insert((pnr, input("Name: "), input("Train no: "), input("Status: ")))
            if find(pnr)[0] != -1 and pnr not in entered:
                entered.append(pnr)
        elif ch == "2":
            search(pnr)
        else:
            delete(pnr)
    elif ch == "4":
        display()
    elif ch == "5":
        compare(entered or LAB_KEYS)         # your keys, or the lab keys if none typed
    elif ch == "6":
        rehash_on = not rehash_on
        print("Rehashing is now", "ON" if rehash_on else "OFF")
    elif ch == "7":
        reset()
    elif ch == "8":
        demo()
    elif ch == "9":
        break
    else:
        print("Invalid choice")