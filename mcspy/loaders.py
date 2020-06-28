__package__ = "mcspy"

from os.path import basename
import gzip
import numpy as np
import pandas as pd
import mcspy.util as util
from .util import addext, rowidint_to_rowid
from .defs import MCS_DATA_PATH

__all__ = [
    "load_mix_dframe",
    "load_mix_dframe_years",
    "load_mix_var",
    "load_mix_var_years",
    "load_prof_var",
    "load_prof_var_years",
    "load_calc_var",
    "load_calc_var_years",
    "load_H2Oice",
    "load_H2Oice_err",
    "load_H2Ovap",
    "load_H2Ovap_err",
    "load_altitude",
    "load_dust",
    "load_dust_err",
    "load_pressure",
    "load_temperature",
    "load_temperature_err",
    "load_Ls",
    "load_Ls2",
    "load_SZA",
    "load_MY",
    "load_LST",
    "load_lat",
    "load_lon",
]


def load_mix_dframe(year, quiet=False):
    """Load and recreate a metadata index DataFrame from a numpy file
    and a csv file. This function is the opposite of save_mix_dframe.
    returns: the metadata index DataFrame
    """
    fn = MCS_DATA_PATH + f"DATA/{year}/indexdata/{year}_mixvars"
    # fname = addext(fn, '.npy')
    fname = addext(fn, ".npz")
    # load the numeric data and make a new DataFrame
    with np.load(fname, mmap_mode="c") as _mix:
        mix = pd.DataFrame(dict(_mix.items()))
    if not quiet:
        print(f"loaded {fname}")
    # mix = pd.DataFrame(mix, columns=mix_cols)
    fname = addext(fn, ".csv.gz")
    # for vv in ['SCLK', 'Ls', 'solar_dist', 'orb_num', 'LST',
    # 'lat', 'lon', 'MY']:
    #    mix[vv] = pd.to_numeric(mix[vv], downcast='float')
    # load the index/profile ID column
    mix["profid"] = pd.read_csv(fname, squeeze=True, header=None, skiprows=1)
    if not quiet:
        print(f"loaded {fname}")
    # change time columns back to datetime types
    for cc in ["datetime"]:
        mix[cc] = mix[cc].astype("datetime64[ns]")
    # mix['UTC'] = mix['UTC'].astype('timedelta64[ns]')
    # make profid the index
    return mix.set_index("profid")


@util.allyearsdec
def load_mix_dframe_years(years=None, quiet=False):
    """Load the metadata index files for several years and return one
    concatenated DataFrame."""
    df = pd.DataFrame()
    for yy in years:
        if not quiet:
            print(f"Loading {yy} index...")
        df = df.append(load_mix_dframe(yy))
    return df


def load_mix_var(year, varname, OLDMIX=False, quiet=False):
    """
    Reads a metadata index variable for `varname` from `year` as a
    numpy array from the numpy array file
    '{year}/indexdata/{year}_{varname}_index.npy'.
    """
    if OLDMIX:
        fname = (
            MCS_DATA_PATH + f"DATA/{year}/indexdata/{year}_{varname}_index.npy"
        )
        with gzip.open(fname, "rb") as fin:
            var = np.load(fin)
    else:
        try:
            fname = MCS_DATA_PATH + f"DATA/{year}/indexdata/{year}_mixvars.npz"
            with np.load(fname, allow_pickle=False) as fin:
                var = fin[varname]
        except KeyError:
            var = load_mix_var(year, varname, True)
    if varname in ["date", "datetime"] or "date" in varname.lower():
        var = var.astype("datetime64[ns]")
    if varname in ["UTC"]:
        var = var.astype("timedelta64[ns]")
    if not quiet:
        print(f"loaded {fname}")
    return var


def load_mix_vars(
    year, varnames, OLDMIX=False, quiet=False, output_tuple=True
):
    """
    Reads a metadata index variable for `varname` from `year` as a
    numpy array from the numpy array file
    '{year}/indexdata/{year}_{varname}_index.npy'.
    """
    vars = {}
    if OLDMIX:
        print("OLDMIX only works with load_mix_var.")
        return {}
    else:
        try:
            fname = MCS_DATA_PATH + f"DATA/{year}/indexdata/{year}_mixvars.npz"
            with np.load(fname, allow_pickle=False) as fin:
                for name in varnames:
                    vars[name] = fin[name]
        except KeyError as e:
            print(e)
            return
            for name in varnames:
                vars[name] = load_mix_var(year, name, True)
    for name in varnames:
        if name in ["date", "datetime"] or "date" in name.lower():
            vars[name] = vars[name].astype("datetime64[ns]")
        if name in ["UTC"]:
            vars[name] = vars[name].astype("timedelta64[ns]")
    if not quiet:
        print(f"loaded {fname}")
    if output_tuple:
        return tuple(vars.values())
    return vars


def load_prof_dframe(year):
    """
    Loads the profile data from `year` and returns a DataFrame.
    """
    from glob import glob

    fname = MCS_DATA_PATH + f"DATA/{year}/profdata/{year}_*_profiles.npy"
    varnames = [basename(x)[5:-13] for x in glob(fname)]
    df = pd.DataFrame()
    for vn in varnames:
        df[vn] = load_prof_var(year, vn).flatten()
    df["rowid"] = rowidint_to_rowid(df["rowidint"])
    return df.set_index("rowid").sort_values("rowidint")


@util.allyearsdec
def load_mix_var_years(years=None, varname="Ls", quiet=False):
    """Loads multiple years of data for the metadata index variable
    `varname` and returns a single 1-D numpy array."""
    dat = []
    for yy in years:
        dat.append(load_mix_var(yy, varname, quiet=quiet))
    return np.concatenate(dat, axis=0)


@util.allyearsdec
def load_mix_vars_years(
    years=None, varnames=["Ls"], quiet=False, output_tuple=False
):
    """Loads multiple years of data for the metadata index variable
    `varname` and returns a single 1-D numpy array."""
    dat = {}
    for yy in years:
        odat = load_mix_vars(yy, varnames, quiet=quiet, output_tuple=False)
        for name in varnames:
            dat.setdefault(name, [])
            dat[name].append(odat[name])
    for name in varnames:
        dat[name] = np.concatenate(dat[name], axis=0)
    if output_tuple:
        return tuple(dat.values())
    return dat


def load_prof_var(year, varname, quiet=False):
    """Reads the profile data variable `varname` from `year` from
    the numpy array file "{year}/profdata/{year}_{varname}_profiles.npy"
    and returns a single 2-D array. If `varname` == "pressure", the
    returned array is shape (105,1)."""
    # handle pressure separately
    if varname == "pressure" or "varname" == "prs":
        return 610 * np.exp(-0.125 * (np.arange(105) - 9)).reshape((1, 105))
    fname = (
        MCS_DATA_PATH + f"DATA/{year}/profdata/{year}_{varname}_profiles.npy"
    )
    # load data
    with gzip.open(fname, "rb") as fout:
        var = np.load(fout).reshape((-1, 105))
    if not quiet:
        print(f"loaded {fname}")
    return var


def load_calc_var(year, varname, quiet=False):
    """Reads the calculated profile variable `varname` from `year` from the
    numpy array file "{year}/calcdata/{year}_{varname}_profiles.npy" and
    returns a single 2-D array. If `varname` == "pressure", the returned array
    is shape (105,1)."""
    # handle pressure separately
    if varname == "pressure" or "varname" == "prs":
        return 610 * np.exp(-0.125 * (np.arange(105) - 9)).reshape((1, 105))
    fname = (
        MCS_DATA_PATH + f"DATA/{year}/calcdata/{year}_{varname}_profiles.npy"
    )
    # load data
    with gzip.open(fname, "rb") as fout:
        var = np.load(fout).reshape((-1, 105))
    if not quiet:
        print(f"loaded {fname}")
    return var


@util.allyearsdec
def load_prof_var_years(years=None, varname="temperature", quiet=False):
    """Reads the profile data variable `varname` from `years`
    from the numpy array files and returns a single 2-D array.
    If `varname` == "pressure", the returned array is shape (105,1)."""
    dat = []
    if not quiet:
        print(f"Loading {varname}...")
    # handle pressure separately
    if varname == "pressure":
        return load_prof_var(2006, varname, quiet)
    # read the data file for each year
    for yy in years:
        dat.append(load_prof_var(yy, varname, quiet))
    # concatenate the data arrays
    return np.concatenate(dat, axis=0)


@util.allyearsdec
def load_calc_var_years(years=None, varname="temperature", quiet=False):
    """Reads the calculated profile variable `varname` from `years`
    from the numpy array files and returns a single 2-D array.
    If `varname` == "pressure", the returned array is shape (105,1)."""
    dat = []
    if not quiet:
        print(f"Loading {varname}...")
    # handle pressure separately
    if varname == "pressure":
        return load_calc_var(2006, varname, quiet)
    # read the data file for each year
    for yy in years:
        dat.append(load_calc_var(yy, varname, quiet))
    # concatenate the data arrays
    return np.concatenate(dat, axis=0)


# convenience functions to load several variables
load_temperature = load_prof_var_years
load_temperature_err = lambda: load_prof_var_years(varname="T_err")  # noqa
load_pressure = lambda: load_prof_var_years(varname="pressure")  # noqa
load_altitude = lambda: load_prof_var_years(varname="altitude")  # noqa
load_H2Oice = lambda: load_prof_var_years(varname="H2Oice")  # noqa
load_H2Oice_err = lambda: load_prof_var_years(varname="H2Oice_err")  # noqa
load_H2Ovap = lambda: load_prof_var_years(varname="H2Ovap")  # noqa
load_H2Ovap_err = lambda: load_prof_var_years(varname="H2Ovap_err")  # noqa
load_dust = lambda: load_prof_var_years(varname="dust")  # noqa
load_dust_err = lambda: load_prof_var_years(varname="dust_err")  # noqa
load_SZA = lambda: load_mix_var_years(varname="solar_zen")  # noqa
load_Ls = lambda: load_mix_var_years(varname="Ls")  # noqa
load_MY = lambda: load_mix_var_years(varname="MY")  # noqa
load_LST = lambda: load_mix_var_years(varname="LST")  # noqa
load_lat = lambda: load_mix_var_years(varname="lat")  # noqa
load_lon = lambda: load_mix_var_years(varname="lon")  # noqa
load_Ls2 = lambda: load_Ls() + 360 * (load_MY() - 28)  # noqa
