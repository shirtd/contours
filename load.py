import matplotlib.pyplot as plt
import numpy as np
import os, sys

from contours.surface import USGSScalarFieldData, GaussianScalarFieldData
from contours.config import COLOR, KWARGS, GAUSS_ARGS, parser


if __name__ == '__main__':
    args = parser.parse_args()

    if args.gauss:
        name, folder = 'surf', os.path.join('data', 'surf')
        surf = GaussianScalarFieldData(name, folder, args.resolution, args.downsample, **GAUSS_ARGS)
    else:
        surf = USGSScalarFieldData(args.file, args.cuts, args.colors, args.pad, args.downsample)

    if args.show:
        fig, ax = surf.init_plot()
        surf_plt = surf.plot(ax, **KWARGS['surf'])
        plt.show()

    if args.save:
        surf.save()
