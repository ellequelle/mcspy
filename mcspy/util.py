__package__ = "mcspy"

import numpy as np
from .defs import MCS_DATA_PATH
import pandas as pd

__all__ = [
    "add_prof_profid",
    "add_prof_prsnum",
    "local_data_path",
    "add_prof_rowid",
    "addext",
    "mcs_tab_path",
    "make_profidint",
    "profidint_to_profid",
    "make_rowidint",
    "rowidint_to_rowid",
    "calc_Ls2",
    "allyearsdec",
    "lxload",
]


def calc_Ls2(Ls, MY):
    return Ls + 360 * (MY - 28)


def local_data_path(pth, ext=""):
    from pathlib import Path

    pth = Path(addext(pth, ext))
    if pth.is_absolute():
        return str(pth)
    # if pth.parts[0] == 'DATA':
    pth = MCS_DATA_PATH / pth
    return str(pth)


def mcs_tab_path(prodids, dfindex=None, volume=False, absolute=False):
    """Guess the file path for the .TAB file with a given product ID
    (prodid). Prodids can be either a single string or a Series
    of strings."""
    isstring = False
    if dfindex is None:
        if isinstance(prodids, str):
            prodids = [prodids]
            isstring = True
        if not isinstance(prodids, pd.Series):
            prodids = pd.Series(prodids, dtype=str)
        path = (
            "DATA/"
            + prodids.str[:4]
            + "/"
            + prodids.str[:6]
            + "/"
            + prodids.str[:8]
            + "/"
            + prodids
        )
    else:
        df = dfindex.loc[prodids]
        path = "DATA/" + df["path"] + "/" + df["filename"]
    if volume:
        # volume is for downloading the file from PDS
        if dfindex is None:
            raise ValueError("dfindex is needed for volume.")
        path = df["volume_id"] + "/" + path
    ret = path
    if absolute:
        ret = MCS_DATA_PATH + path
    if isstring:
        return ret[0]
    return ret


def add_prof_prsnum(prof):
    if "prsnum" in prof:
        return prof
    p = prof.copy()
    p.insert(
        1,
        "prsnum",
        (np.log(p["pressure"] / 610) / -0.125 + 10).round().astype(int),
    )
    return p


def add_prof_rowid(prof):
    if "rowid" in prof:
        return prof
    pp = prof.copy()
    pp = add_prof_profid(add_prof_prsnum(pp))
    pp["rowid"] = (pp.profid + ":" + pp.prsnum.astype(str)).astype("string")
    return pp


def add_prof_profid(prof):
    if "profid" in prof:
        return prof
    pp = prof.copy()
    pp["profid"] = (pp["prodid"] + ":" + pp.prof_num.astype(str)).astype(
        "string"
    )
    return pp


def make_prodidint(ix):
    """
    Make a integer version of prodid.
    ix: a series or a DataFrame with a column or index named "prodid"

    returns: pandas integer Series of profidint
    """
    ix = ix.copy()
    # make an integer version of profile ID
    # date identifies the data file, multipy by 1e4 to allow
    # up to 9999 profiles per data file
    # profile number in the data file
    if isinstance(ix, pd.DataFrame):
        if "prodid" not in ix:
            ix = ix.reset_index()
        ix = ix["prodid"]
    elif not isinstance(ix, pd.Series):
        ix = pd.Series(ix)
    ix = ix.str.slice(None, 10).astype(int)
    return ix.values


def prodidint_to_prodid(pidi):
    if not isinstance(pidi, (pd.Series)):
        pidi = pd.Series(pidi, name="profid")
    pidi = pidi.astype(str).astype("string") + "_DDR.TAB"
    return pidi


def make_profidint(mix):
    """
    Make a integer version of profid.
    mix: a series or a DataFrame with a column or index named "profid"

    returns: pandas integer Series of profidint
    """
    mix = mix.copy()
    # make an integer version of profile ID
    # date identifies the data file, multipy by 1e4 to allow
    # up to 9999 profiles per data file
    # profile number in the data file
    if isinstance(mix, pd.DataFrame):
        if "profid" not in mix:
            mix = mix.reset_index()
        mix = mix["profid"]
    elif not isinstance(mix, pd.Series):
        mix = pd.Series(mix)
    mix = mix.str.slice(None, 10).astype(int) * 10000 + mix.str.slice(
        19, None
    ).astype(int)
    return mix.values


def profidint_to_profid(pidi):
    """
    Make profid index from profidint. This is the inverse
    of make_profidint_mix_df.
    pidi: integer arraylike or pandas Series

    returns: pandas Series of profid strings
    """
    if not isinstance(pidi, (pd.Series)):
        pidi = pd.Series(pidi, name="profid")
    pidi = pidi.astype(str).astype("string")
    date = pidi.str.slice(None, 10)
    profnum = pidi.str.slice(10, None)
    profnum = profnum.str.replace("0", " ").str.lstrip().str.replace(" ", "0")
    profnum[~profnum.str.isnumeric()] = "0"
    profid = (date + "_DDR.TAB:" + profnum).astype("string")
    profid.name = "profid"
    return profid


def make_rowidint(prof):
    rid = pd.Series(prof)
    rowidint = rid.str[:10].astype(int)
    rid2 = rid.str[19:].str.split(":")
    rid2a = rid2.apply(lambda x: x[0]).astype(int)
    rid2b = rid2.apply(lambda x: x[1]).astype(int)
    rowidint = rowidint * 10000 + rid2a
    rowidint = rowidint * 1000 + rid2b
    return rowidint.values


def rowidint_to_rowid(rowidint):
    if not isinstance(rowidint, pd.Series):
        rowidint = pd.Series(rowidint)
    rownum = rowidint % 1000
    profnum = rowidint // 1000 % 10000
    prodidint = rowidint // 1000 // 10000
    rid = (
        prodidint.astype(str)
        + "_DDR.TAB:"
        + profnum.astype(str)
        + ":"
        + rownum.astype(str)
    )
    rid.name = "rowid"
    return rid.astype("string")


def addext(fn, ext):
    """Add a file extension to a filename if it doesn't already exist."""
    if not fn.endswith(ext):
        return fn + ext
    return fn


# decorator for _years functions
def allyearsdec(f):
    ays = (
        2006,
        2007,
        2008,
        2009,
        2010,
        2011,
        2012,
        2013,
        2014,
        2015,
        2016,
        2017,
        2018,
        2019,
    )

    def func(years=None, **kwargs):
        if years is None:
            return f(years=ays, **kwargs)
        else:
            return f(years=years, **kwargs)

    func.__doc__ = f.__doc__
    func.__name__ = f.__name__
    return func


class lxload(object):
    def __init__(self, load_var_name, load_var_type="mix"):
        """
        load_var_name: the name of the variable to load as an argument.
        load_var_type: which kind of variable, options: ['mix', 'prof'].
        """
        self.varname = load_var_name
        self.vartype = load_var_type

    def __call__(self, f):
        def func(*args, **kwargs):
            if len(args) > 0:
                return f(*args, **kwargs)
            elif self.vartype == "mix":
                from .loaders import load_mix_vars_years

                if isinstance(self.varname, str):
                    self.varname = [self.varname]
                var = load_mix_vars_years(
                    varnames=self.varname, output_tuple=True
                )
            elif self.vartype == "prof":
                from .loaders import load_prof_var_years

                var = [load_prof_var_years(varname=self.varname)]
            print(var, kwargs)
            return f(*var, **kwargs)

        func.__name__ = f.__name__
        func.__doc__ = f.__doc__
        return func
