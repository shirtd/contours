from itertools import permutations, product
import numpy.linalg as la
from tqdm import tqdm
import scipy.fftpack
import numpy as np
import scipy

import contours.util


def lipschitz_grid(F, G):
    def c(i,j,a,b):
        return abs(F[i,j] - F[i+a,j+b]) / la.norm(G[:,i,j] - G[:,i+a,j+b])
    it = tqdm(list(product(range(1, F.shape[0]-1), range(1, F.shape[1]-1))), desc='lips')
    return max(c(i,j,a,b) for i,j in it for a,b in permutations([-1,0,1],2))

def get_grid(res=16, width=1, height=1):
    x_rng = np.linspace(-width,width,int(width*res))
    y_rng = np.linspace(-height,height,int(height*res))
    return np.meshgrid(x_rng, y_rng)

def down_sample(G, l):
    N, M = G.shape
    _N, nrem = divmod(N, l)
    _M, mrem = divmod(M, l)
    if nrem > 0 and mrem > 0:
        G = G[nrem//2:-nrem//2, mrem//2:-mrem//2]
    elif nrem > 0:
        G = G[nrem//2:-nrem//2, :]
    elif mrem > 0:
        G = G[:, mrem//2:-mrem//2]
    D = np.zeros((_N, _M), dtype=float)
    for j in tqdm(range(_M), desc=f'downsample {l}'):
        for i in range(_N):
            x = G[i*l:(i+1)*l, j*l:(j+1)*l].sum() / (l ** 2)
            D[i, j] = x if x > 0 else 0
    return D

def ripple(t, f=1, l=1, d=1, w=1, s=1):
    t = w * (t + s)
    return np.exp(-t / l) * np.cos(2*np.pi*f**(1/d)*t)

def get_ripple_grid(x, y, f=1, l=1, d=1, w=1, s=1):
    return ripple(la.norm(np.stack((x, y), axis=2), axis=2), f, l, d, w, s)

def ripple_field(x, y, f=1, l=1, d=1, w=1, s=1, exp=-3, noise=False, scale=False):
    field = get_ripple_grid(x, y, f, l, d, w, s)
    if noise:
        field *= (1 + gaussian_random_field(exp, x.shape[0]*x.shape[1]))
    return util.scale(field) if scale else field

def make_circle(x, y, n=128, r=[0.2, 1.], c=[[0,0],[0,0]]):
    xy = np.stack((x,y), axis=2)
    t = np.linspace(0, 2*np.pi, n)
    z = np.vstack([np.vstack((rr*np.sin(t), rr*np.cos(t))).T + np.array(cc) for rr,cc in zip(r,c)])
    return np.array([[la.norm(z - xy[i,j], axis=1).min() for j in range(xy.shape[1])] for i in range(xy.shape[0])])

def gaussian(X, Y, c=[0., 0.], s=[0.5, 0.5]):
    return np.exp(-((X-c[0])**2 / (2*s[0]**2) + (Y-c[1])**2 / (2*s[1]**2)))

def gaussian_field(X, Y, args):
    return sum(w*gaussian(X, Y, c, r) for w, c, r in args)

def gaussian_random_field(alpha=-3.0, m=128, normalize=True):
    size = int(np.sqrt(m))
    k_ind = np.mgrid[:size, :size] - int((size + 1) / 2)
    k_idx = sp.fftpack.fftshift(k_ind)
    # Defines the amplitude as a power law 1/|k|^(alpha/2)
    amplitude = np.power(k_idx[0] ** 2 + k_idx[1] ** 2 + 1e-10, alpha / 4.0)
    amplitude[0,0] = 0
    # Draws a complex gaussian random noise with normal (circular) distribution
    noise = np.random.normal(size = (size, size)) + 1j * np.random.normal(size = (size, size))
    G = np.fft.ifft2(noise * amplitude).real # To real space
    return util.stats.scale(G) if normalize else G
