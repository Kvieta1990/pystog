from __future__ import (absolute_import, division, print_function)
import json

from pystog import StoG
from pystog.io import get_cli_args, parse_cli_args


def pystog_cli(kwargs=None):
    if not kwargs:
        args = get_cli_args()
        if args.json:
            print("loading config from '%s'" % args.json)
            with open(args.json, 'r') as f:
                kwargs = json.load(f)

        else:
            kwargs = parse_cli_args(args)

    # Merge S(Q) files
    stog = StoG(**kwargs)
    stog.read_all_data(skiprows=3)
    stog.merge_data()
    stog.write_out_merged_sq()

    if "PlotFlag" in kwargs:
        if kwargs["PlotFlag"]:
            stog.plot_merged_sq()

    # Initial S(Q) -> g(r) transform
    stog.transform_merged()
    stog.write_out_merged_gr()

    if "PlotFlag" in kwargs:
        if kwargs["PlotFlag"]:
            stog.plot_gr(
                ylabel=stog.real_space_function,
                title="Merged %s" % stog.real_space_function)

    # TODO: Add the lowR minimizer here
    # print stog.get_lowR_mean_square()

    # Set the S(Q) and g(r) if no Fourier Filter
    r = stog.df_gr_master[stog.gr_title].values
    q = stog.df_sq_master[stog.sq_title].values
    sq = stog.df_sq_master[stog.sq_title].values
    gr_out = stog.df_gr_master[stog.gr_title].values

    # Apply Fourier Filter
    if "FourierFilter" in kwargs:
        q, sq, r, gr_out = stog.fourier_filter()

    # Apply Lorch Modification
    if kwargs["LorchFlag"]:
        r, gr_out = stog.apply_lorch(q, sq, r)

    # Apply final scale number
    stog._add_keen_fq(q, sq)
    stog._add_keen_gr(r, gr_out)

    if "PlotFlag" in kwargs:
        if kwargs["PlotFlag"]:
            stog.plot_summary_sq()
            stog.plot_summary_gr()
