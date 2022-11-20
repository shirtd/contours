import matplotlib.pyplot as plt
import numpy as np
import argparse
import os, sys

from contours.config import COLOR, KWARGS, parser
from contours.surface import ScalarFieldFile, MetricSampleFile
from contours.complex import RipsComplex


def get_tag(args, suffix=''):
    tag = f"{args.key}{'' if args.noim else '-im'}"
    if args.lips:
        tag = f"{tag}-lips{'-max' if args.nomin else '-min' if args.nomax else ''}"
        if args.local:
            tag += '-local'
    return f"{tag}{'-color' if args.color else ''}{suffix}"

def set_args(args, sample):
    args.parent = sample.parent if args.parent is None else args.parent
    if args.key is None:
        args.key = ( 'graph' if args.graph else 'rips' if args.rips
                else 'union' if args.union else 'cover' )
    args.folder = os.path.join(args.folder, sample.parent)
    if args.lips:
        args.folder = os.path.join(args.folder, 'lips')
    args.folder = os.path.join(args.folder, args.key, sample.name)
    return get_tag(args)

def get_config(args):
    if args.lips:
        if args.cover or args.union:
            return {'min' : {**{'visible' : not args.nomin}, **KWARGS['min'][args.key]},
                    'max' : {**{'visible' : not args.nomax}, **KWARGS['max'][args.key]}}
        if args.sub_file is not None:
            return {'min' : {**{'visible' : False}, **KWARGS['min'][args.key]},
                    'max' : {**{'visible' : False}, **KWARGS['max'][args.key]}}
        return {'min' : {**{'visible' : False, 'key' : 'min'}, **KWARGS['min'][args.key]},
                'max' : {**{'visible' : False, 'key' : 'max'}, **KWARGS['max'][args.key]}}
    return {'f' : {**{'visible' : False}, **KWARGS[args.key]}}


if __name__ == '__main__':
    args = parser.parse_args()

    sample = MetricSampleFile(args.file)
    tag = set_args(args, sample)
    if args.sub_file is not None:
        subsample = MetricSampleFile(args.sub_file)
        tag = f'{tag}-{len(subsample)}subsample'
    if args.rips or args.graph or args.barcode:
        radius = sample.radius
        if not args.noim:
            radius *= 2 / np.sqrt(3)
        rips = RipsComplex(sample.points, radius, verbose=True)
        if args.lips:
            if args.sub_file is not None:
                rips.lips_sub(subsample, args.local)
            else:
                rips.lips(sample, sample.config['lips'], invert_min=True)
        else:
            rips.sublevels(sample)

    plot_args = [args.show, args.save, args.folder, args.color, args.dpi]

    if args.barcode:
        if args.nosmooth:
            tag += '-nosmooth'
        if args.lips:
            if args.sub_file is not None:
                sample_dgms = sample.plot_lips_sub_barcode(rips, subsample, *plot_args, smooth=not args.nosmooth, **KWARGS['barcode'])
            else:
                sample_dgms = sample.plot_lips_barcode(rips, *plot_args, smooth=not args.nosmooth, **KWARGS['barcode'])
        else:
            sample_dgms = sample.plot_barcode(rips, *plot_args, smooth=not args.nosmooth, **KWARGS['barcode'])

    if args.contours:
        if args.cover or args.union:
            if args.lips:
                sample.plot_lips_filtration(get_config(args), tag, *plot_args)
            else:
                sample.plot_cover_filtration(tag, *plot_args, **KWARGS[args.key])
        elif args.rips or args.graph:
            config = get_config(args)
            if args.lips:
                if args.sub_file is None:
                    sample.plot_rips_filtration(rips, config, tag, *plot_args)
                else:
                    hide = {'min'} if args.nomin else {'max'} if args.nomax else {}
                    sample.plot_rips_filtration(rips, config, tag, *plot_args, subsample=subsample, hide=hide)
            else:
                sample.plot_rips_filtration(rips, config, tag, *plot_args)
    else:
        fig, ax = sample.init_plot()
        if args.sub_file is not None:
            sample.plot(ax, **KWARGS['supsample'])
            subsample.plot(ax, plot_color=args.color, **KWARGS['subsample'])
        else:
            sample.plot(ax, **KWARGS['sample'])

        # tag = f"{key}{color_str}" if args.cover or args.union or args.rips or args.graph else None
        if args.cover or args.union:
            cover_plt = sample.plot_cover(ax, args.color, **KWARGS[args.key])
        elif args.rips or args.graph:
            rips_plt = sample.plot_rips(ax, rips, args.color, **KWARGS[args.key])

        if args.save:
            sample.save_plot(args.folder, args.dpi, tag)

        if args.show:
            print('close plot to exit')
            plt.show()
