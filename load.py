import matplotlib.pyplot as plt
import numpy as np
import os, sys

from contours.config import COLOR, KWARGS, GAUSS_ARGS
from contours.config.args import parser

from contours.program import RunSurface


if __name__ == '__main__':
    args = RunSurface(parser)

    surf = args.get_surface()
    if args.contours:
        args.plot_contours(surf)

    if args.barcode:
        barcode = surf.get_barcode()
        args.plot_barcode(surf, barcode, **KWARGS['barcode'])

    sample = args.do_sample(surf)

    if sample is not None:
        args.plot_sample(surf, sample)
    else:
        args.plot_surface(surf)
