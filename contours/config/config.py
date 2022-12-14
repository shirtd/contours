import numpy as np

from contours.config import *


LW=0.4
SIZE=1

# TODO: make this a function
# pass args to modify defaults

# [0.05, 0.2, 0.45, 0.875, 1.09, 1.31]

KWARGS = {  'barcode'   : { 'lw' : 10},
            'surf'      : { 'zorder' : 0, 'alpha' : 0.5},
            'sample'    : { 'zorder' : 10, 'edgecolors' : 'black', 's' : SIZE, 'color' : 'black', 'alpha' : 1},
            'supsample' : { 'zorder' : 10, 'edgecolors' : 'black', 'facecolors' : 'none', 's' : SIZE*6, 'lw' : 2*LW, 'alpha' : 0},
            'subsample' : { 'zorder' : 10, 's' : SIZE*2, 'color' : 'black'},
            'cover'     : { 'zorder' : 2, 'alpha' : 0.2, 'color' : COLOR['red'], 'lw' : 1},
            'union'     : { 'zorder' : 2, 'alpha' : 1, 'color' : COLOR['red1'], 'lw' : 1},
            'graph'     : { 'zorder' : 1, 'color' : COLOR['red'], 'fade' : [1, 0.8, 0], 'lw' : LW, 's' : SIZE},
            'rips'      : { 'zorder' : 1, 'color' : COLOR['red'], 'fade' : [1, 0.8, 0.6], 'lw' : LW, 's' : SIZE},
            'delaunay'  : { 'zorder' : 1, 'color' : COLOR['red'], 'fade' : [1, 0.8, 0.6], 'lw' : LW, 's' : SIZE},
            'voronoi'   : { 'zorder' : 1, 'color' : COLOR['red'], 'fade' : [1, 0.8, 0.6], 'lw' : LW, 's' : SIZE/2},
            'min'       : { 'graph'  : { 'zorder' : 1, 'color' : COLOR['gray'], 'fade' : [1, 0.8, 0], 'lw' : LW, 's' : SIZE},
                            'rips'   : { 'zorder' : 1, 'color' : COLOR['gray'], 'fade' : [1, 0.8, 0.6], 'lw' : LW, 's' : SIZE},
                            'delaunay': { 'zorder' : 1, 'color' : COLOR['gray'], 'fade' : [1, 0.8, 0.6], 'lw' : LW, 's' : SIZE},
                            'voronoi': { 'zorder' : 1, 'color' : COLOR['gray'], 'fade' : [1, 0.8, 0.6], 'lw' : LW, 's' : SIZE/2},
                            'cover' : { 'zorder' : 2, 'alpha' : 0.2, 'color' : COLOR['red']},
                            'union' : { 'zorder' : 2, 'alpha' : 1, 'color' : COLOR['red1']}},
            'max'       : { 'graph' : { 'zorder' : 1, 'color' : COLOR['red'], 'fade' : [1, 0.8, 0], 'lw' : LW, 's' : SIZE},
                            'rips'  : { 'zorder' : 1, 'color' : COLOR['red'], 'fade' : [1, 0.8, 0.6], 'lw' : LW, 's' : SIZE},
                            'delaunay': { 'zorder' : 1, 'color' : COLOR['red'], 'fade' : [1, 0.8, 0.6], 'lw' : LW, 's' : SIZE},
                            'voronoi': { 'zorder' : 1, 'color' : COLOR['red'], 'fade' : [1, 0.8, 0.6], 'lw' : LW, 's' : SIZE/2},
                            'cover' : { 'zorder' : 2, 'alpha' : 0.2, 'color' : COLOR['blue']},
                            'union' : { 'zorder' : 2, 'alpha' : 1, 'color' : COLOR['blue1']}}}


#                     (weight,  [xpos, ypos],   [xspread, yspread])
GAUSSES = {'original': [(0.85,     [-0.25, 0.1],    [0.3, 0.3]),    # base
                        (0.6,   [-1.35, -0.1],   [0.15, 0.15]),  # small feature
                        (0.65,   [-0.85, -0.35],   [0.2, 0.2]),    # main feature 1
                        (0.75,   [-0.8, -0],     [0.4, 0.4]),    # main feature 2
                        (0.25,  [0.6, 0.0],     [0.4, 0.2]),    # bridge
                        (0.8,   [1.25, 0.3],    [0.27, 0.25])], # minor feature
           'original0':[(0.8,   [-0.2, 0.2],    [0.3, 0.3]),    # main feature
                        (0.72,  [-1.37, -0.1],  [0.15, 0.15]),  # small feature
                        (0.6,   [-0.8, -0.4],   [0.2, 0.2]),    # second feature
                        (0.7,   [-0.8, -0],     [0.4, 0.4]),    # second feature 2
                        (0.3,   [0.6, 0.0],     [0.4, 0.2]),    # bridge
                        (0.82,  [1.25, 0.2],    [0.26, 0.25])], # minor feature
           'original1':[(0.85,  [-0.1, 0.18],   [0.3, 0.3]),    # main feature
                        (0.65,  [-0.8, 0.08],   [0.4, 0.4]),    # second feature 2
                        (0.65,  [-0.8, -0.4],   [0.2, 0.2]),    # second feature
                        (0.6,   [-1.1, 0.55],   [0.15, 0.13]),  # small feature
                        (0.2,   [0.6, 0.0],     [0.4, 0.2]),    # bridge
                        (0.3,   [1., 0.1],      [0.5, 0.4])],    # bridge
            'surf1':   [(0.7,   [-0.25, 0.2],   [0.25, 0.2]),
                        (0.5,   [-1.1, 0.4],    [0.16, 0.13]),
                        (0.6,   [-0.65, -0.4],  [0.2, 0.2]),
                        (0.5,   [-0.8, -0],     [0.4, 0.4]),
                        (0.45,  [0.75, 0.2],    [0.4, 0.3]),
                        (0.45,  [1.25, 0.35],   [0.25, 0.25])],
            'surf2':   [(1,     [-0.2, 0.2],    [0.3, 0.3]),
                        (0.6,   [-1.1, 0.4],    [0.16, 0.13]),
                        (0.7,   [-0.8, -0.4],   [0.2, 0.2]),
                        (0.8,   [-0.8, -0],     [0.4, 0.4]),
                        (0.4,   [0.75, 0.2],    [0.5, 0.3]),
                        (0.8,   [1.25, 0.35],   [0.25, 0.25])]}

GAUSS_ARGS = {  'pad' : 1.5,
                'scale' : 1000,
                # 'lips' : 3.155422091834973,
                # 'lips' : 3.155422091834973,
                'lips' : 3.,
                'extents' : [[-2, 2], [-1, 1]],
                # # 'cuts' : [0.05, 0.3, 0.55, 0.8, 1.35],
                # # 'colors' : [COLOR[c] for c in ['green', 'blue', 'purple', 'yellow']],
                # TODO!
                'colors' : [COLOR[c] for c in ['blue','green','yellow','salmon','purple']],
                'cuts' : [0.05, 0.2, 0.55, 0.885, 1.15, 1.35],
                'gauss_args' : GAUSSES['original']}
                # # TODO!
                # 'cuts' : [0.05, 0.2, 0.55, 0.85, 1., 1.1],
                # 'gauss_args' : GAUSSES['original0']}

def get_config(args):
    if args.lips:
        if args.cover or args.union:
            return {'min' : {**{'visible' : not args.nomin}, **KWARGS['min'][args.mode]},
                    'max' : {**{'visible' : not args.nomax}, **KWARGS['max'][args.mode]}}
        if args.sub_file is not None:
            return {'min' : {**{'visible' : False}, **KWARGS['min'][args.mode]},
                    'max' : {**{'visible' : False}, **KWARGS['max'][args.mode]}}
        return {'min' : {**{'visible' : False}, **KWARGS['min'][args.mode]},
                'max' : {**{'visible' : False}, **KWARGS['max'][args.mode]}}
    return {'sub' : {**{'visible' : False}, **KWARGS[args.mode]}}

# CONFIG = {  'surf32' :    {'res' : 32, 'shape' : (2,1), 'pad' : (1.2, 1.55),
#                         'cuts' : [0.05, 0.3, 0.55, 0.8, 1.35],
#                         'colors' : ['green', 'blue', 'purple', 'yellow'],
#                         'labels' : ['A', 'B', 'C', 'D'],
#                         'lips' : 3.1443048369350226, 'lw' : 5,
#                         'gauss_args' : [(1,     [-0.2, 0.2],    [0.3, 0.3]),
#                                         (0.5,   [-1.3, -0.1],   [0.15, 0.15]),
#                                         (0.7,   [-0.8, -0.4],   [0.2, 0.2]),
#                                         (0.8,   [-0.8, -0],     [0.4, 0.4]),
#                                         (0.4,   [0.6, 0.0],     [0.4, 0.2]),
#                                         (0.7,   [1.25, 0.3],    [0.25, 0.25])]},
#             'rainier_sub16' : {'res' : 337, 'shape' : (1,1), 'pad' : (1.3, 1.3),
#                         'cuts' : [200, 1000, 1400, 1800, 2500, 4500],
#                         'colors' : ['blue','green','yellow','salmon','purple'],
#                         'labels' : ['A', 'B', 'C', 'D', 'E'],
#                         'min' : 265.258441, 'max' : 4379.845434, 'lw' : 1,
#                         'lips' : 46519.52591999933},
#             'rainier_super16' : {'res' : 1350, 'shape' : (1,1), 'pad' : (1.3, 1.3),
#                         'cuts' : [1200, 1800, 2000, 2500, 3100, 4500],
#                         'colors' : ['blue','green','yellow','salmon','purple'],
#                         'labels' : ['A', 'B', 'C', 'D', 'E'],
#                         'min' : 265.258441, 'max' : 4379.845434, 'lw' : 1,
#                         'lips' : 46519.52591999933},
#             'test' : {'res' : 1692, 'shape' : (1,0.6383), 'pad' : (1.3, 1.3),
#                         # 'cuts' : list(1850 + 333 * np.array([0, 0.9, 2.2, 4.20, 6.9])) + [4500],
#                         'cuts' : [1850, 2130, 2585, 3180, 4175, 4500],
#                         'colors' : ['blue','green','yellow','salmon','purple'],
#                         'labels' : ['A', 'B', 'C', 'D', 'E'],
#                         'min' : 265.258441, 'max' : 4379.845434, 'lw' : 1,
#                         'lips' : 46519.52591999933},
#             'rainier_peak' : {'res' : 230, 'shape' : (1,1), 'pad' : (1.3, 1.3),
#                         'cuts' : [1800, 2000, 2300, 2600, 3100, 4500],
#                         'colors' : ['blue','green', 'yellow', 'salmon', 'purple'],
#                         # 'colors' : ['green', 'yellow','salmon','purple'],
#                         'labels' : ['A', 'B', 'C', 'D', 'E'],
#                         'min' : 265.258441, 'max' : 4379.845434, 'lw' : 1,
#                         'lips' : 31705.27213000035},
#                         # 'lips' : 25483.938340730343},
#             'circle'  : {'res' : 256, 'weight' : 0.5, 'scale' : 2.8, 'seed' : 0,
#                         'cuts' : [0, 0.07, 0.15, 0.2, 0.27, 0.4, 0.6, 0.75, 1.3]}}
#
# CONFIG['surf32_2'] = CONFIG['surf32'].copy()
# CONFIG['surf32_2']['cuts'] = [0.05, 0.2, 0.45, 0.875, 1.09, 1.31]
# CONFIG['surf32_2']['colors'] = ['blue','green','yellow','salmon','purple']
# CONFIG['surf32_2']['labels'] = ['A', 'B', 'C', 'D', 'E']
#
# CONFIG['surf8'] = CONFIG['surf32'].copy()
# CONFIG['surf8']['res'] = 8

# print(CONFIG['test']['cuts'])
