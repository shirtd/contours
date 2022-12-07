import matplotlib.pyplot as plt
import numpy as np
import argparse
import os, sys

from contours.config import COLOR, KWARGS, parser
from contours.surface import ScalarFieldFile, MetricSampleFile
from contours.complex import RipsComplex, DelaunayComplex, VoronoiComplex

FILE = 'data/rainier_sub/samples/rainier_sub32-sample1257-2000.csv'
# SUB_FILE = 'data/rainier_sub/samples/rainier_sub32-sample1257-2000.csv'

plt.ion()

if __name__ == '__main__':

    sample = MetricSampleFile(FILE)
    # subsample = MetricSampleFile(SUB_FILE)

    complex = DelaunayComplex(sample.points, sample.radius, verbose=True)
    complex.sublevels(sample)

    complex = VoronoiComplex(complex, verbose=True)
    complex.lips_sub(sample)

    # complex.lips_sub(subsample, args.local)
    # complex.lips(sample, sample.config['lips'], invert_min=True)

    # sample_dgms = sample.plot_lips_sub_barcode(complex, subsample, True, False, 'figures', True, 300, smooth=False, **KWARGS['barcode'])
    # sample_dgms = sample.plot_lips_barcode(complex, True, False, 'figures', True, 300, smooth=False, **KWARGS['barcode'])
    sample_dgms = sample.plot_barcode(complex, True, False, 'figures', True, 300, smooth=False, **KWARGS['barcode'])


    fig, ax = sample.init_plot()

    V = complex.P
    ax.scatter(V[:,0], V[:,1], c='red', s=5, zorder=5)
    E = np.array([[V[v] for v in e] for e in complex(1) if len(e) == 2])
    for e in E:
        ax.plot(e[:,0], e[:,1], color='black', zorder=2)
