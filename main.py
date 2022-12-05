import matplotlib.pyplot as plt
import numpy as np
import argparse
import os, sys

from contours.config import COLOR, COLORS, KWARGS, GAUSS_ARGS, get_config
from contours.config.args import parser, get_tag, set_args


from contours.surface import ScalarFieldFile, MetricSampleFile

def do_cover(args, sample, tag, subsample=None):
    plot_args = [args.show, args.save, args.folder, args.color, args.dpi]
    if args.cover or args.union:
        return sample.plot_lips_filtration(get_config(args), tag, *plot_args)
    return sample.plot_cover_filtration(tag, *plot_args, **KWARGS[args.mode])

def do_contours(args, complex, tag, subsample=None):
    plot_args = [args.show, args.save, args.folder, args.color, args.dpi]
    if args.lips:
        plot_args += [{'min'} if args.nomin else {'max'} if args.nomax else {}]
        if subsample is not None:
            plot_args += [subsample]
    return sample.plot_complex_filtration(complex, get_config(args), tag, *plot_args)

def do_barcode(args, complex, tag, subsample=None):
    plot_args = [args.show, args.save, args.folder, args.color, args.dpi]
    if args.nosmooth:
        tag += '-nosmooth'
        plot_args += [not args.nosmooth]
    if args.lips:
        if subsample is not None:
            return sample.plot_lips_sub_barcode(complex, subsample, *plot_args, **KWARGS['barcode'])
        return sample.plot_lips_barcode(complex, *plot_args, **KWARGS['barcode'])
    return sample.plot_barcode(complex, *plot_args, **KWARGS['barcode'])


if __name__ == '__main__':
    args = parser.parse_args()

    sample = MetricSampleFile(args.file)
    tag = set_args(args, sample)

    subsample = None
    if args.lips and args.sub_file is not None:
        subsample = MetricSampleFile(args.sub_file)
        tag = f'{tag}-{len(subsample)}sub'

    complex = None
    if args.rips or args.graph:
        complex = sample.get_rips(args.noim)
    elif args.delaunay:
        complex = sample.get_delaunay(args.alpha)
    elif args.voronoi:
        complex = sample.get_voronoi(args.alpha)


    if complex is None and args.contours:
        do_cover(args, sample, tag, subsample)
    else:
        if args.lips:
            if args.sub_file is not None:
                complex.lips_sub(subsample)
            else:
                complex.lips(sample, sample.config['lips'], invert_min=True)
        else:
            complex.sublevels(sample)

        if args.barcode:
            do_barcode(args, sample, tag, subsample)

        if args.contours:
            do_contours(args, complex, tag, subsample)

        fig, ax = sample.init_plot()
        complex_plt = sample.plot_complex(ax, complex, args.color, **KWARGS[args.mode])

        if args.save:
            sample.save_plot(args.folder, args.dpi, tag)

        if args.show:
            print('close plot to exit')
            plt.show()


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
