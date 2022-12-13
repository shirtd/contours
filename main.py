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

    if args.cover or args.union:
        args.plot_cover(sample)
