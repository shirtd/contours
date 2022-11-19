from scipy.spatial import KDTree
import matplotlib.pyplot as plt
import numpy.linalg as la
import numpy as np
import os

from contours.util import lmap, format_float
from contours.config import COLOR


def init_barcode(figsize=(14,5), hide_ticks=False, ylim=None):
    fig, ax = plt.subplots(1, 1, figsize=figsize)
    if hide_ticks:
        ax[1].set_xticks([])
    if ylim is not None:
        ax[1].set_ylim(*ylim)
    ax.set_yticks([])
    plt.tight_layout()
    return fig, ax

def init_barcodes(figsize=(14,9), hide_ticks=False, ylim=None):
    fig, ax = plt.subplots(2, 1, sharex=True, figsize=figsize)
    if hide_ticks:
        ax[1].set_xticks([])
    if ylim is not None:
        ax[1].set_ylim(*ylim)
    plt.tight_layout()
    return fig, ax

def get_fig(shape, mult=10):
    return plt.subplots(figsize=(mult*shape[0], mult*shape[1]))

def reset_plot(ax, scale=None, clear=True):
    if clear:
        ax.cla()
    ax.axis('off')
    ax.axis('equal')
    if scale is not None:
        ax.set_xlim(-scale, scale)
        ax.set_ylim(-scale, scale)

# def init_surface(shape, pad=1.3, mult=10, extents=None):
#     fig, ax = get_fig((shape[0] / shape[1], 1), mult)
#     ax.axis('scaled')
#     if extents is None:
#         l = np.array(shape) * np.array(pad)
#         ax.set_xlim(-l[0],l[0])
#         ax.set_ylim(-l[1],l[1])
#     else:
#         l = np.array(extents) * 1.3
#         ax.set_xlim(*extents[0])
#         ax.set_ylim(*extents[1])
#     ax.invert_yaxis()
#     ax.axis('off')
#     plt.tight_layout()
#     return fig, ax

def init_surface(extents, pad=1000, mult=12):
    extents = [[a-pad,b+pad] for a,b in extents]
    dx = abs(extents[0][0] - extents[0][1])
    dy = abs(extents[1][0] - extents[1][1])
    fig, ax = get_fig((1, dy/dx), mult)
    # fig, ax = plt.subplots()
    ax.invert_yaxis()
    ax.axis('off')
    ax.axis('scaled')
    ax.set_xlim(*extents[0])
    ax.set_ylim(*extents[1])
    plt.tight_layout()
    return fig, ax

def plot_barcode(ax, dgm, cuts, colors, lw=5, thresh=0, *args, **kwargs):
    ax.set_xlim(cuts[0], cuts[-1])
    dgm = np.array([p for p in dgm if p[1]-p[0] > thresh and p[1] != np.inf])
    if not len(dgm):
        return None
    for i, (birth, death) in enumerate(dgm):
        for (a,b), c in zip(zip(cuts[:-1], cuts[1:]), colors):
            if a < birth and death <= b:
                ax.plot([birth, death], [i, i], c=c, lw=lw)
            elif birth < a and death > a and death <= b:
                ax.plot([a, death], [i, i], c=c, lw=lw)
            elif birth > a and birth < b and death > b:
                ax.plot([birth, b], [i, i], c=c, lw=lw)
            elif birth <= a and b < death:
                ax.plot([b, a], [i, i], c=c, lw=lw)
            # if death == np.inf:
            #       ax.plot([lim, lim+0.1], [i, i], c='black', linestyle='dotted')
    ax.get_yaxis().set_visible(False)
    plt.tight_layout()
    return ax

def get_color(f, cuts, colors, default=None):
    if default is None:
        default = colors[0]
    for (a,b), c in zip(zip(cuts[:-1],cuts[1:]), colors):
        if a <= f < b:
            return c
    return default

def get_cut(f, cuts, colors, default=-1):
    for i, (a,b) in enumerate(zip(cuts[:-1],cuts[1:])):
        if a <= f < b:
            return i
    return default

def plot_surface(ax, surf, cuts, colors, zorder=0, xlim=(-3,3), ylim=(-2,2), init=False, contour_color=None, alpha=0.5, invert=False):
    if invert:
        contour_kw = {'colors' : [colors[0]]+ colors} if contour_color is None else {'color' : contour_color}
    else:
        contour_kw = {'colors' : colors + [colors[-1]]}
        if contour_color is not None:
            contour_kw = {'color' : contour_color}
    res = {'surface' : ax.contourf(*surf.grid, surf.surface, levels=cuts, colors=colors, zorder=zorder, alpha=alpha),
            'contours' : ax.contour(*surf.grid, surf.surface, levels=cuts, zorder=zorder, **contour_kw)}
    if init:
        init_surface(ax, xlim, ylim)
    return res

def plot_rainier(ax, surf, cuts, colors, alpha=0.5, zorder=0):
    res = {'surface' : ax.contourf(*surf.grid, surf.surface, levels=cuts, colors=colors, alpha=alpha, zorder=0),
            'contours' : ax.contour(*surf.grid, surf.surface, levels=cuts, colors=colors, zorder=0)}
    ax.axis('off')
    ax.axis('scaled')
    plt.tight_layout()
    return res

def plot_points(ax, points, visible=True, **kwargs):
    p = ax.scatter(points[:,0], points[:,1], **kwargs)
    p.set_visible(visible)
    return p

def plot_balls(ax, P, F, alpha=0.2, color=None, colors=None, zorder=None, zorders=None, **kwargs):
    colors = [color for _ in F] if colors is None else colors
    zorders = [zorder for _ in F] if zorders is None else zorders
    balls = []
    for p,f,c,z in zip(P, F, colors, zorders):
        s = plt.Circle(p, f, alpha=alpha, facecolor=c, edgecolor='none', zorder=z, **kwargs)
        balls.append(s)
        ax.add_patch(s)
    return balls

def plot_poly(ax, P, T, visible=True, color=None, color_list=None, **kwargs):
    if color_list is None:
        color_list = [color for _ in T]
    tp = {t : plt.Polygon(P[t,:], facecolor=c, edgecolor='none', **kwargs) for c,t in zip(color_list,T)}
    lmap(lambda t: ax.add_patch(t), tp.values())
    if not visible:
        for t,p in tp.items():
            p.set_visible(False)
    return tp

def plot_edges(ax, P, E, visible=True, color=None, color_list=None, **kwargs):
    if color_list is None:
        color_list = [color for _ in E]
    ep = {e : ax.plot(P[e,0], P[e,1], color=c, **kwargs)[0] for c,e in zip(color_list,E)}
    if not visible:
        for e,p in ep.items():
            p.set_visible(False)
    return ep

def plot_rips(ax, complex, color=COLOR['red'], edge_color=COLOR['black'], visible=True, fade=[1, 0.3, 0.15], # [1, 0.6, 0.3],
                                        dim=2, zorder=1, alpha=1, s=9, tri_colors=None, edge_colors=None, lw=0.1):
    edge_kw = {'color' : edge_color} if edge_colors is None else {'color_list' : edge_colors}
    tri_kw = {'color' : color} if tri_colors is None else {'color_list' : tri_colors}
    return {1 : plot_edges(ax, complex.P, complex(1), visible, alpha=alpha*fade[1], zorder=zorder+1, lw=lw, **edge_kw),
            2 : plot_poly(ax, complex.P, complex(2), visible, alpha=alpha*fade[2], zorder=zorder, **tri_kw)}

def plot_rips_filtration(ax, rips, levels, keys, name, dir='figures', save=True, wait=0.5, dpi=300, hide={}):
    rips_plt = {k : plot_rips(ax, rips, **v) for k,v in keys.items()}
    if save and not os.path.exists(dir):
        print(f'making directory {dir}')
        os.makedirs(dir)
    for i, t in enumerate(levels):
        for d in (1,2):
            for s in rips(d):
                for k,v in rips_plt.items():
                    if not (k in hide and hide[k]):
                        if s.data[k] <= t:
                            rips_plt[k][d][s].set_visible(not keys[k]['visible'])
        if wait is not None:
            plt.pause(wait)
        if save:
            # t_str = np.format_float_scientific(t, trim='-')
            fname = os.path.join(dir, f'{name}{format_float(t)}.png')
            print(f'saving {fname}')
            plt.savefig(fname, dpi=dpi, transparent=True)
    return rips_plt

def plot_offset_filtration(ax, sample, constant, levels, keys, name, dir='figures', save=True, wait=0.5, dpi=300, hide={}):
    if 'min' in hide and hide['min'] and 'min' in keys:
        keys['min']['visible'] = False

    offset_plt = {  'max' : plot_balls(ax, sample, 2 * sample.function/constant, **keys['max']),
                    'min' : plot_balls(ax, sample, 2 * sample.function/constant, **keys['min'])}
    if save and not os.path.exists(dir):
        print(f'making directory {dir}')
        os.makedirs(dir)
    for i, t in enumerate(levels):
        for j,f in enumerate(sample.function):
            fs = {'max' : (t - f) / constant, 'min' : (f - t) / constant}
            for k,v in offset_plt.items():
                if not (k in hide and hide[k]):
                    v[j].set_radius(fs[k] if fs[k] > 0 else 0)
        if wait is not None:
            plt.pause(wait)
        if save:
            # t_str = np.format_float_scientific(t, trim='-')
            fname = os.path.join(dir, f'{name}{int(t*100)}.png')
            print(f'saving {fname}')
            plt.savefig(fname, dpi=dpi, transparent=True)
    return offset_plt

def plot_sfa(ax, sample, levels, kw, name, dir='figures', save=True, wait=0.5, dpi=300, colors=None):
    offset_plt = plot_balls(ax, sample, np.ones(len(sample)) * sample.radius/2, **kw)
    if save and not os.path.exists(dir):
        print(f'making directory {dir}')
        os.makedirs(dir)
    for i, t in enumerate(levels):
        for j,f in enumerate(sample.function):
            if f <= t:
                offset_plt[j].set_visible(True)
        if wait is not None:
            plt.pause(wait)
        if save:
            # t_str = np.format_float_scientific(t, trim='-')
            fname = os.path.join(dir, f'{name}{int(t*100)}.png')
            print(f'saving {fname}')
            plt.savefig(fname, dpi=dpi, transparent=True)
    return offset_plt


def get_sample(fig, ax, S, thresh, P=None, color=COLOR['pink1']):
    if P is not None:
        plot_points(ax, P, color='black', zorder=3, s=5)
        plot_balls(ax, P, np.ones(len(P))*thresh/2, alpha=1., color='gray', zorder=2)
        P = list(P)
    else:
        P = []
    T = KDTree(S[:,:2])
    def onclick(event):
        p = S[T.query(np.array([event.xdata,event.ydata]))[1]]
        ax.add_patch(plt.Circle(p, thresh/2, color=color, zorder=3, alpha=1))
        ax.scatter(p[0], p[1], c='black', zorder=4, s=5)
        plt.pause(0.1)
        P.append(p)
    cid = fig.canvas.mpl_connect('button_press_event', onclick)
    plt.show()
    fig.canvas.mpl_disconnect(cid)
    P = sorted(P, key=lambda x: x[1])
    return np.vstack(P) if len(P) else None

def get_subsample(fig, ax, S, thresh, P, sub_file=None, color=COLOR['pink1']):
    cover_plt = plot_balls(ax, P, np.ones(len(P))*thresh/2, alpha=0.5, color='gray', zorder=2)
    T = KDTree(P[:,:2])
    Q = [] if sub_file is None else list(np.loadtxt(sub_file, dtype=int))
    for idx in Q:
        ax.scatter(P[idx,0],P[idx,1],marker='*',zorder=5,color='black')
        cover_plt[idx].set_color(color)
        cover_plt[idx].set_alpha(1)
        cover_plt[idx].set_zorder(3)
    def onclick(event):
        idx = T.query(np.array([event.xdata,event.ydata]))[1]
        cover_plt[idx].set_color(color)
        cover_plt[idx].set_alpha(1)
        cover_plt[idx].set_zorder(3)
        ax.scatter(P[idx,0],P[idx,1], marker='*',zorder=4)
        plt.pause(0.1)
        Q.append(int(idx))
    cid = fig.canvas.mpl_connect('button_press_event', onclick)
    plt.show()
    fig.canvas.mpl_disconnect(cid)
    return sorted(Q)
