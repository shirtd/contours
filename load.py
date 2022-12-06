import matplotlib.pyplot as plt
import numpy as np
import os, sys

from contours.config import COLOR, KWARGS, GAUSS_ARGS
from contours.config.args import parser

from contours.program import LoadArgs


if __name__ == '__main__':
    args = LoadArgs(parser)

    surf = args.get_surface()
    if args.contours:
        args.plot_contours(surf)

    barcode_surf = None
    if args.barcode:
        args.plot_barcode(surf)

    sample = args.do_sample(surf)

    if sample is not None:
        args.plot_sample(surf, sample)
    else:
        args.plot_surface(surf)
