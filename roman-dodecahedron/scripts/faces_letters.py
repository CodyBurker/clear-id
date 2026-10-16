"""Map the report's face letters (Hitchens 2023, Fig. 2) onto the .scad face indices."""
import numpy as np, itertools
PHI = (1 + 5 ** .5) / 2
N = np.array([(1,0,-PHI),(-1,0,-PHI),(-PHI,-1,0),(-PHI,1,0),(0,-PHI,1),(0,-PHI,-1),
              (PHI,-1,0),(-1,0,PHI),(1,0,PHI),(0,PHI,-1),(PHI,1,0),(0,PHI,1)], float)
N /= np.linalg.norm(N, axis=1)[:, None]
HOLE = dict(A=29, B=20.3, C=13.4, D=19.4, E=20.4, F=20, G=27, H=17.6, I=17.5, J=9.9, K=16.2, L=17)
def nb(i): return [j for j in range(12) if abs(N[j] @ N[i] - 0.4472) < 1e-3]
def opp(i): return [j for j in range(12) if N[j] @ N[i] < -0.99][0]
def letters(A, B):
    up = -(N[A] - (N[A] @ N[B]) * N[B]); up /= np.linalg.norm(up)
    right = np.cross(up, N[B])                     # screen-right looking at B from outside
    m = dict(A=A, B=B, G=opp(A))
    m['C'] = [j for j in nb(B) if j in nb(A) and N[j] @ right < 0][0]
    m['F'] = [j for j in nb(B) if j in nb(A) and N[j] @ right > 0][0]
    m['D'] = [j for j in nb(m['C']) if j in nb(A) and j != B][0]
    m['E'] = [j for j in nb(m['D']) if j in nb(A) and j != m['C']][0]
    m['H'] = [j for j in nb(B) if j in nb(m['G']) and N[j] @ right > 0][0]
    m['I'] = [j for j in nb(B) if j in nb(m['G']) and N[j] @ right < 0][0]
    m['J'] = [j for j in nb(m['I']) if j in nb(m['G']) and j != m['H']][0]
    m['K'] = [j for j in nb(m['J']) if j in nb(m['G']) and j != m['I']][0]
    m['L'] = [j for j in nb(m['K']) if j in nb(m['G']) and j != m['J']][0]
    assert len(set(m.values())) == 12
    # consistency with Fig. 2: C adj I,J ; F adj H,L ; K adj D,E
    assert m['C'] in nb(m['I']) and m['C'] in nb(m['J']) and m['F'] in nb(m['H']) and m['F'] in nb(m['L'])
    assert m['K'] in nb(m['D']) and m['K'] in nb(m['E'])
    return m
