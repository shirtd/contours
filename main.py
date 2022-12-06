import matplotlib.pyplot as plt
import numpy as np
import argparse
import os, sys

from contours.config import COLOR, COLORS, KWARGS
from contours.config.args import parser

from contours.surface import ScalarFieldFile, MetricSampleFile
from contours.program import MainArgs


if __name__ == '__main__':
    args = MainArgs(parser)

    sample = MetricSampleFile(args.file)
    args.set_args(sample)
    tag = args.get_tag()

    subsample = None
    if args.lips and args.sub_file is not None:
        subsample = MetricSampleFile(args.sub_file)
        tag = f'{tag}-{len(subsample)}sub'

    complex = args.get_complex(sample)

    if complex is None and args.contours:
        args.do_cover(sample, tag, subsample)
    else:
        if args.lips:
            if args.sub_file is not None:
                complex.lips_sub(subsample)
            else:
                complex.lips(sample, sample.config['lips'], invert_min=True)
        else:
            complex.sublevels(sample)

        if args.barcode:
            args.do_barcode(sample, tag, subsample)

        if args.contours:
            args.do_contours(sample, complex, tag, subsample)

        args.plot_complex(sample, complex, tag)

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
