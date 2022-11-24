import matplotlib.pyplot as plt
import numpy as np
import os, sys

from contours.surface import USGSScalarFieldData, GaussianScalarFieldData, ScalarFieldFile
from contours.config import COLOR, KWARGS, GAUSS_ARGS, parser


if __name__ == '__main__':
    args = parser.parse_args()

    if args.gauss:
        name, folder = 'surf', os.path.join('data', 'surf')
        surf = GaussianScalarFieldData(name, folder, args.resolution, args.downsample, **GAUSS_ARGS)
        if args.write:
            surf.save()
    elif os.path.splitext(args.file)[1] == '.asc':
        surf = USGSScalarFieldData(args.file, args.cuts, args.colors, args.pad, args.downsample)
        if args.write:
            surf.save()
    else:
        surf = ScalarFieldFile(args.file, args.json)

    args.folder = os.path.join(args.folder, surf.name)
    plot_args = [args.show, args.save, args.folder, args.dpi]

    if args.barcode:
        surf_dgms = surf.plot_barcode(*plot_args, **KWARGS['barcode'])

    if args.contours:
        surf.plot_contours(*plot_args)

    sample = None
    if args.greedy:
        sample = surf.greedy_sample(args.thresh, args.mult, args.seed)
    elif args.sample_file is not None:
        sample = MetricSampleFile(args.sample_file)

    if args.sample:
        sample = surf.sample(args.thresh, sample)

    fig, ax = surf.init_plot()
    surf_plt = surf.plot(ax, **KWARGS['surf'])

    if sample is not None:
        sample.plot(ax, **KWARGS['sample'])
        sample.plot_cover(ax, **KWARGS['union' if args.union else 'cover'])
        if args.show:
            plt.pause(0.1)
        if args.write or input(f'save {sample.name} (y/*)? ') == 'y':
            sample.save(sample.get_data())
        if args.save:
            sample.save_plot(args.folder, args.dpi)
    else:
        if args.save:
            surf.save_plot(args.folder, args.dpi)
        if args.show:
            plt.show()
