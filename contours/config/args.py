import numpy as np
import argparse
import os

from contours.config import COLOR, COLORS

#
# RES=8 # 16 # 32 #
# DSET='rainier_small' # 'rainier_sub' # 'northwest' #
# DIR=os.path.join('data')
# DDIR=os.path.join(DIR, DSET)
# SAMPLE='rainier_small8-sample666_1000.csv'
#
# FILE=os.path.join(DDIR, f'{DSET}{RES}.csv') # None #
# # JSON= None # os.path.join(DDIR, f'{DSET}{RES}.json')
# SAMPLE_FILE=None # os.path.join(DDIR, 'samples', SAMPLE) #
# SUB_FILE= None
#
COEF=2/np.sqrt(3)
MULT=0.7/COEF

DATA_DIR = os.path.join('data','test')
# CUTS=[200, 1000, 1400, 1800, 2500, 4500]
CUTS=[1850, 2130, 2585, 3180, 4175, 4500]
FDIR='figures'
DPI=300
PAD=1e2
LIPS=None
THRESH=None # PAD
ALPHA=None # 2e8 # None # 2e4


# PARSE
parser = argparse.ArgumentParser(prog='lipser')

parser.add_argument('file', nargs='?', help='surface file')
parser.add_argument('--gauss', action='store_true', help='generate gaussian surface')
parser.add_argument('--downsample', default=None, type=int, help='downsample')
parser.add_argument('--resolution', default=1024, type=int, help='resolution')
parser.add_argument('--key', '-k', default=None, type=str, help='program key')
parser.add_argument('--parent', default=None, help='sample parent (supersample)')
parser.add_argument('--seed', default=None, type=int, help='sample seed')

parser.add_argument('--force', action='store_true', help='force save sample')
parser.add_argument('--barcode', action='store_true')
parser.add_argument('--nosmooth', action='store_true')
parser.add_argument('--relative', action='store_true')
parser.add_argument('--write', action='store_true', help='write data')
parser.add_argument('--show', action='store_true')
parser.add_argument('--save', action='store_true', help='save figures')
parser.add_argument('--dir', default=FDIR, help='figure output directory')
parser.add_argument('--folder', default=FDIR, help='figure output directory {deprecated}')
parser.add_argument('--dpi', type=int, default=DPI, help='image dpi')

parser.add_argument('--cuts', default=CUTS, nargs='+', type=float, help='cuts')
parser.add_argument('--colors', default=COLORS, nargs='+', type=str, help='colors')
parser.add_argument('--pad', default=PAD, type=float, help='padding')
# parser.add_argument('--lips', default=LIPS, type=float, help='lipschitz constant')

parser.add_argument('--json', default=None, help='surface config {deprecated}')
# parser.add_argument('--config', default=None, help='configuration file')


# PROGRAM ARGS
parser.add_argument('--sample', action='store_true', help='sample surface')
parser.add_argument('--thresh', type=float, default=THRESH, help='cover radius')
parser.add_argument('--mult', type=float, default=MULT, help='radius mult (greedy param)')
parser.add_argument('--coef', type=float, default=COEF, help='cover coef')
parser.add_argument('--greedy', action='store_true', help='greedy sample')
parser.add_argument('--greedyfun', action='store_true', help='greedy sample by function value')
# parser.add_argument('--weight', action='store_true', help='weight greedy sample by function value')
parser.add_argument('--local', action='store_true', help='local lips')

parser.add_argument('--sample-file', default=None, help='sample file')
parser.add_argument('--sub-file', default=None, help='sample file')

# parser.add_argument('--show', action='store_true', help='show plot')
# parser.add_argument('--save', action='store_true', help='save plot')

parser.add_argument('--contours', action='store_true', help='plot contours')
parser.add_argument('--cover', action='store_true', help='plot cover')
parser.add_argument('--color', action='store_true', help='plot color')
parser.add_argument('--union', action='store_true', help='plot union')
parser.add_argument('--surf', action='store_true', help='plot surf')
parser.add_argument('--rips', action='store_true', help='do rips')
parser.add_argument('--alpha', default=ALPHA, type=float, help='convexity constant (for delaunay)')
parser.add_argument('--delaunay', action='store_true', help='do delaunay')
parser.add_argument('--voronoi', action='store_true', help='do voronoi')
parser.add_argument('--graph', action='store_true', help='plot surf')
parser.add_argument('--lips', action='store_true', help='plot lips')
parser.add_argument('--nomin', action='store_true', help='max only')
parser.add_argument('--nomax', action='store_true', help='min only')
parser.add_argument('--noim', action='store_true', help='no image persistence')
