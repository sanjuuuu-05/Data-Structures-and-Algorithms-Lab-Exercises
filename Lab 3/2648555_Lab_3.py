def compute_lps(pattern):
    lps = [0] * len(pattern)
    length = 0
    i = 1
    while i < len(pattern):
        if pattern[i] == pattern[length]:
            length += 1
            lps[i] = length
            i += 1
        else:
            if length != 0:
                length = lps[length - 1]
            else:
                lps[i] = 0
                i += 1

    return lps

def naive_search(text, pattern):
    positions = []
    comparisons = 0

    n = len(text)
    m = len(pattern)
    if m > n:
        return positions, comparisons
    for i in range(n - m + 1):
        j = 0
        while j < m:
            comparisons += 1
            if text[i + j] != pattern[j]:
                break
            j += 1
        if j == m:
            positions.append(i)
    return positions, comparisons

def kmp_search(text, pattern):
    positions = []
    comparisons = 0
    n = len(text)
    m = len(pattern)
    lps = compute_lps(pattern)
    i = 0
    j = 0
    while i < n:
        comparisons += 1
        if text[i] == pattern[j]:
            i += 1
            j += 1
            if j == m:
                positions.append(i - j)
                j = lps[j - 1]
        else:
            if j != 0:
                j = lps[j - 1]
            else:
                i += 1
    return positions, comparisons

def char_value(ch):
    if ch=='A':
        return 0
    elif ch=='C':
        return 1
    elif ch=='G':
        return 2
    elif ch=='T':
        return 3
    return -1
    
def rabin_karp(text,pattern):
    positions=[]
    n=len(text)
    m=len(pattern)
    BASE=4
    PRIME=1000000007
    spurious_hits=0
    comparisons=0

    if m>n:
        return positions,spurious_hits,comparisons

    high_power=1
    for i in range(m-1):
        high_power=(high_power*BASE)%PRIME

    pattern_hash=0
    text_hash=0

    for i in range(m):
        pattern_hash=(pattern_hash*BASE+char_value(pattern[i]))%PRIME
        text_hash=(text_hash*BASE+char_value(text[i]))%PRIME

    for i in range(n-m+1):
        if pattern_hash==text_hash:
            match=True
            for j in range(m):
                comparisons+=1
                if text[i+j]!=pattern[j]:
                    match=False
                    break
            if match:
                positions.append(i)
            else:
                spurious_hits+=1

        if i<n-m:
            old_value=char_value(text[i])
            new_value=char_value(text[i+m])
            text_hash=(text_hash-old_value*high_power)%PRIME
            text_hash=(text_hash*BASE+new_value)%PRIME

    return positions,spurious_hits,comparisons

def main():
    text=input().strip()
    pattern=input().strip()
    valid_characters=set("ACGT")
    if not set(text).issubset(valid_characters) or not set(pattern).issubset(valid_characters):
        print("Invalid input")
        return
    lps=compute_lps(pattern)
    naive_positions,naive_comparisons=naive_search(text,pattern)
    kmp_positions,kmp_comparisons=kmp_search(text,pattern)
    rk_positions,spurious_hits,rk_comparisons=rabin_karp(text,pattern)

    print("LPS Array :",*lps)

    if len(naive_positions)==0:
        print("Naive : Positions = NONE | Count = 0 | Comparisons =",naive_comparisons)
    else:
        print("Naive : Positions =",*naive_positions,"| Count =",len(naive_positions),"| Comparisons =",naive_comparisons)

    if len(kmp_positions)==0:
        print("KMP : Positions = NONE | Count = 0 | Comparisons =",kmp_comparisons)
    else:
        print("KMP : Positions =",*kmp_positions,"| Count =",len(kmp_positions),"| Comparisons =",kmp_comparisons)

    if len(rk_positions)==0:
        print("Rabin-Karp : Positions = NONE | Count = 0 | Spurious Hits =",spurious_hits)
    else:
        print("Rabin-Karp : Positions =",*rk_positions,"| Count =",len(rk_positions),"| Spurious Hits =",spurious_hits)

if __name__=="__main__":
    main()