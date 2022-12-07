import matplotlib.pyplot as plt
import numpy as np
import argparse
import os, sys

from contours.config import COLOR, COLORS, KWARGS, GAUSS_ARGS, get_config
from contours.config.args import parser, get_tag, set_args

from contours.complex import RipsComplex, DelaunayComplex, VoronoiComplex
from contours.surface import ScalarFieldFile, MetricSampleFile


if __name__ == '__main__':
    args = parser.parse_args()

    sample = MetricSampleFile(args.file)
    tag = set_args(args, sample)
    if args.sub_file is not None:
        subsample = MetricSampleFile(args.sub_file)
        tag = f'{tag}-{len(subsample)}subsample'
    if args.rips or args.graph or args.delaunay or args.voronoi or args.barcode:
        if args.delaunay or args.voronoi:
            filter = None if args.alpha is None else (lambda f: f < args.alpha)
            complex = DelaunayComplex(sample.points, sample.radius, filter, verbose=True)
            if args.voronoi:
                complex.superlevels(sample)
                boundary = complex.get_boundary()
                complex = VoronoiComplex(complex, boundary, verbose=True)

        else:
            radius = sample.radius
            if not args.noim:
                radius *= 2 / np.sqrt(3)
            complex = RipsComplex(sample.points, radius, verbose=True)
        if args.lips:
            if args.sub_file is not None:
                complex.lips_sub(subsample, args.local)
            elif not args.voronoi:
                complex.lips(sample, sample.config['lips'], invert_min=False)
            else:
                print("! can't do lips on voronoi")
        elif not args.voronoi:
            complex.sublevels(sample)

    plot_args = [args.show, args.save, args.folder, args.color, args.dpi]

    if args.barcode:
        if args.nosmooth:
            tag += '-nosmooth'
        if args.lips:
            if args.sub_file is not None:
                sample_dgms = sample.plot_lips_sub_barcode(complex, subsample, *plot_args, smooth=not args.nosmooth, **KWARGS['barcode'])
            else:
                sample_dgms = sample.plot_lips_barcode(complex, *plot_args, smooth=not args.nosmooth, **KWARGS['barcode'])
        else:
            sample_dgms = sample.plot_barcode(complex, *plot_args, smooth=not args.nosmooth, **KWARGS['barcode'])

    if args.contours:
        if args.cover or args.union:
            if args.lips:
                sample.plot_lips_filtration(get_config(args), tag, *plot_args)
            else:
                sample.plot_cover_filtration(tag, *plot_args, **KWARGS[args.key])
        elif args.rips or args.graph or args.delaunay or args.voronoi:
            config = get_config(args)
            if args.lips and args.sub_file is not None:
                hide = {'min'} if args.nomin else {'max'} if args.nomax else {}
                sample.plot_complex_filtration(complex, config, tag, *plot_args, subsample=subsample, hide=hide)
            else:
                sample.plot_complex_filtration(complex, config, tag, *plot_args)


    else:
        fig, ax = sample.init_plot()
        if args.cover or args.union:
            sample.plot(ax, **KWARGS['sample'])
            cover_plt = sample.plot_cover(ax, args.color, **KWARGS[args.key])
        elif args.rips or args.graph or args.delaunay or args.voronoi:
            complex_plt = sample.plot_complex(ax, complex, args.color, **KWARGS[args.key])
        elif args.sub_file is not None:
            sample.plot(ax, **KWARGS['sample'])
            subsample.plot(ax, plot_color=args.color, **KWARGS['subsample'])
        else:
            sample.plot(ax, **KWARGS['sample'])

        if args.save:
            sample.save_plot(args.folder, args.dpi, tag)

        if args.show:
            print('close plot to exit')
            plt.show()
