import matplotlib.pyplot as plt
import numpy as np
import argparse
import os, sys

from contours.config import COLOR, COLORS, KWARGS
from contours.config.args import parser
from contours.plot import init_barcode, plot_barcode

from contours.surface import ScalarFieldFile, MetricSampleFile
from contours.program import RunSample
from contours.complex import VoronoiComplex
from contours.persistence import Filtration, Barcode, ImageFiltration

plt.ion()

if __name__ == '__main__':
    args = RunSample(parser)

    # args.file = "data/surf/samples/surf8-sample322-111.csv"
    args.file = "data/surf/samples/surf8-sample1002-61.csv"
    # args.file = "data/surf/samples/surf4-sample3261-34.csv"


    sample = MetricSampleFile(args.file)
    args.set_args(sample)

    # complex = sample.get_rips()
    # complex.sublevels(sample)
    #
    # filt = Filtration(complex, 'sub')
    # pivot = Filtration(complex, 'sub', filter=lambda s: s('dist') <= 2*sample.radius)
    # imfilt = ImageFiltration(pivot, filt)
    # hom =  Barcode(imfilt)
    # barcode = hom.get_barcode(imfilt)

    # delaunay = sample.get_rips()
    delaunay = sample.get_delaunay()
    delaunay.lips(sample, sample.config['lips'])
    voronoi = VoronoiComplex(delaunay)#, delaunay.get_boundary())

    # fig, ax = sample.init_plot()
    # sample.plot_complex(ax, delaunay, **KWARGS['max']['delaunay'])
    # sample.plot_complex(ax, voronoi, **KWARGS['min']['voronoi'])

    filt = Filtration(voronoi, 'min')
    pivot = Filtration(delaunay, 'max')
    map = {s : voronoi.dual(s) for s in delaunay}
    imfilt = ImageFiltration(pivot, filt, map, True)
    hom =  Barcode(imfilt)
    barcode = hom.get_barcode(imfilt)

    fig, ax = init_barcode()
    barcode_plt = plot_barcode(ax, barcode[1], sample.cuts, sample.colors, **KWARGS['barcode'])
