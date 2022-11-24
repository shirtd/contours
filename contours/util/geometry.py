from itertools import combinations, product, permutations
from scipy.spatial.distance import cdist
import numpy.linalg as la
from tqdm import tqdm
import numpy as np

from contours.util.grid import ripple


def greedy(P, seed=0, distance='euclidean'):
    S = cdist(P, P, distance)
    j, D = seed, S[seed]
    for _ in P:
        yield j
        j = D.argmax()
        D = np.minimum(S[j], D)


def greedysample(P, delta, seed=0, distance='euclidean'):
    S = cdist(P, P, distance)
    j, D = seed, S[seed]
    output = []
    for _ in P:
        output.append(j)
        j = D.argmax()
        if D[j] < delta:
            return output
        D = np.minimum(S[j], D)

def get_delta(n, w=1, h=1):
    return 2 / (n-1) * np.sqrt(w ** 2 + h ** 2)

def lipschitz(F, P):
    return max(abs(fp - fq) / la.norm(p - q) for (fp,p), (fq,q) in tqdm(list(combinations(zip(F,P), 2))))

def coords_to_meters(lon1, lat1, lon2, lat2, R=6378.137):
    coords = np.array([[lon1, lon2], [lat1, lat2]]) * np.pi / 180
    dlon, dlat = coords[0,1] - coords[0,0], coords[1,1] - coords[1,0]
    a = np.sin(dlat/2)**2 + np.sin(dlon/2)**2 * np.cos(coords[1,0]) * np.cos(coords[1,1])
    return 2 * np.arctan2(np.sqrt(a), np.sqrt(1 - a)) * R * 1000

def ripple_lips(a=0, b=1, n=1024, f=1, l=1, d=1, w=1, s=1):
    t = np.linspace(a, b, n)
    f = ripple(t, f, l, d, w, s)
    return lipschitz(f, t)

def tri_circumradius_2d(T):
    a,b,c = [la.norm(y - x) for x,y in combinations(T,2)]
    s = (a + b + c) / 2
    return (a * b * c) / (4 * np.sqrt(s*(a+b-s)*(a+c-s)*(b+c-s)))

def tri_circumcenter_2d(T):
    a, b, c = T
    ba, ca, cb = b-a, c-a, c-b
    u = cb / la.norm(cb)
    v = np.array([u[1], -u[0]])
    if np.dot(-ba,v) < 0:
        v *= -1
    R = tri_circumradius_2d(T)
    d = R * np.dot(ba, ca) / (la.norm(ba) * la.norm(ca))
    l = np.sqrt(R ** 2 - d ** 2)
    return b + u*l + v*d

def circumcenter(S):
    dim = S.shape[-2]-1
    return (tet_circumcenter(S) if dim == 3
        else tri_circumcenter(S) if dim == 2
        else edge_circumcenter(S) if dim == 1
        else S)

def tet_circumcenter(T):
    D = np.vstack(((T.T * T.T).sum(0)[None], T.T, np.ones(T.T.shape[1:])[None]))
    f = lambda ij: la.det(D[[0,ij[0],ij[1],-1]].T) * (-1) ** (ij[1]-ij[0]-1)
    c = (np.vstack(map(f, zip((2,1,1),(3,3,2)))) / (2 * la.det(D[1:].T))).T
    return c if T.ndim > 2 else c[0]

def tri_circumcenter(T):
    ca,ba = T.T[:,2] - T.T[:,0], T.T[:,1] - T.T[:,0]
    if T.shape[-1] == 3:
        baxca = np.cross(ba, ca, axis=0)
        xca = la.norm(ca, axis=0) ** 2 * np.cross(baxca, ba, axis=0)
        xba = la.norm(ba, axis=0) ** 2 * np.cross(-baxca, ca, axis=0)
        return (T.T[:,0] + (xca + xba) / (2 * la.norm(baxca, axis=0) ** 2)).T
    if T.ndim > 2:
        return np.array([tri_circumcenter_2d(t) for t in T])
    return tri_circumcenter_2d(T)

def edge_circumcenter(E):
    return E.T.sum(1).T / 2


def circumradius(S):
    dim = S.shape[-2]-1
    return (tet_circumradius(S) if dim == 3
        else tri_circumradius(S) if dim == 2
        else edge_circumradius(S) if dim == 1
        else 0.)

def tet_circumradius(T):
    if T.ndim > 2:
        return la.norm(T[:,0] - tet_circumcenter(T), axis=1)
    return la.norm(T[0] - tet_circumcenter(T))

def tri_circumradius(T):
    if T.shape[-1] == 3:
        return la.norm(T[:,0] - tri_circumcenter(T), axis=1)
    return la.norm(T[0] - tri_circumcenter(T))

def edge_circumradius(E):
    if E.ndim > 2:
        return la.norm(E.T[:,0] - E.T[:,1], axis=0) / 2
    return la.norm(diff(E)) / 2
