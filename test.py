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
from contours.persistence import Filtration, Diagram

plt.ion()

if __name__ == '__main__':
    args = RunSample(parser)

    # args.file = "data/surf/samples/surf8-sample322-111.csv"
    args.file = "data/surf/samples/surf8-sample1002-61.csv"


    sample = MetricSampleFile(args.file)
    args.set_args(sample)

    delaunay = sample.get_delaunay(2e4)
    voronoi = VoronoiComplex(delaunay) # , delaunay.get_boundary())

    delaunay.lips(sample, sample.config['lips'])
    voronoi.lips(sample, sample.config['lips'])

    filt = Filtration(voronoi, 'min')
    pivot = Filtration(delaunay, 'max')
    map = {s : voronoi.primal(s) for s in voronoi}
    hom =  Diagram(voronoi, filt, pivot=pivot, map=map, dual=True, verbose=True)
    barcode = hom.get_diagram(voronoi, filt, pivot, delaunay)

    fig, ax = init_barcode()
    barcode_plt = plot_barcode(ax, barcode[1], sample.cuts, sample.colors, **KWARGS['barcode'])
