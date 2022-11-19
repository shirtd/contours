import matplotlib.pyplot as plt

import numpy as np
import os


def get_lims(dgms):
    mx = max(d if d < np.inf else b for dgm in dgms for b,d in dgm)
    mn = min(b for dgm in dgms for b,d in dgm)
    return mn, mx

def init_diagram(axis, lims):
    axis.plot([lims[0], 1.2*lims[1]], [lims[0],1.2*lims[1]], c='black', alpha=0.5, zorder=1)
    axis.plot(lims, [lims[1],lims[1]], c='black', ls=':', alpha=0.5, zorder=1)
    axis.plot([lims[1], lims[1]], [lims[1], 1.2*lims[1]], c='black', ls=':', alpha=0.5, zorder=1)

def lim_dgm(dgm, lim):
    return np.array([[b, d if d < np.inf else 1.2*lim] for b,d in dgm])

def plot_diagrams(axis, dgms, lims=None, title=None, init=True, eps=0):
    if lims is None:
        lims = get_lims(dgms)
    if init:
        init_diagram(axis, lims)
    elems = []
    for dim, dgm in enumerate(dgms):
        if len(dgm):
            d = lim_dgm(dgm, lims[1])
            elems += [axis.scatter(d[:,0], d[:,1], s=7, zorder=2, alpha=0.3, label='H%d' % dim)]
        else:
            elems += [axis.scatter([], [], s=7, zorder=2, alpha=0.3, label='H%d' % dim)]
    if init:
        axis.legend()
    if title is not None:
        axis.set_title(title)
    return lims, elems

def save_plot(dir, prefix, name, dpi=300):
    fname = os.path.join(dir,'%s_%s.png' % (prefix, name))
    print('saving %s' % fname)
    plt.savefig(fname, dpi=dpi)

def plot_histo(axis, L, histo, name='', ymax=None, stat='count'):
    if ymax is not None:
        ax.set_ylim(0, ymax)
    for dim, h in enumerate(histo):
        axis.plot(L[1:] - 1 / len(L), h, label='H%d' % dim)
    fig.suptitle('TPers histogram %s' % name)
    ax.set_xlabel('TPers')
    ax.set_ylabel(stat)
    ax.legend()
    plt.tight_layout()
