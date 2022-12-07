import matplotlib.pyplot as plt
import numpy as np
import argparse
import os, sys

from contours.config import COLOR, COLORS, KWARGS
from contours.config.args import parser

from contours.surface import ScalarFieldFile, MetricSampleFile
from contours.program import RunSample


if __name__ == '__main__':
    args = RunSample(parser)

    sample = MetricSampleFile(args.file)
    args.set_args(sample)

    complex = args.get_complex(sample)
    subsample = args.get_subsample()

    if args.contours:
        args.plot_contours(sample, complex, subsample)

    if args.barcode:
        if args.lips:
            barcode = sample.get_barcode(complex, not args.nosmooth, 'min', 'max')
        else:
            barcode = sample.get_barcode(complex, not args.nosmooth)
        args.plot_barcode(sample, barcode, **KWARGS['barcode'])

    if complex is not None:
        args.plot_complex(sample, complex)


    # else:
    #     fig, ax = sample.init_plot()
    #     if args.cover or args.union:
    #         sample.plot(ax, **KWARGS['sample'])
    #         cover_plt = sample.plot_cover(ax, args.color, **KWARGS[args.mode])
    #     elif args.rips or args.graph or args.delaunay or args.voronoi:
    #         complex_plt = sample.plot_complex(ax, complex, args.color, **KWARGS[args.mode])
    #     elif args.sub_file is not None:
    #         sample.plot(ax, **KWARGS['sample'])
    #         subsample.plot(ax, plot_color=args.color, **KWARGS['subsample'])
    #     else:
    #         sample.plot(ax, **KWARGS['sample'])
    #
    #     if args.save:
    #         sample.save_plot(args.folder, args.dpi, tag)
    #
    #     if args.show:
    #         print('close plot to exit')
    #         plt.show()
