__package__ = "mcspy"

import gzip
import numpy as np
import pandas as pd
from .util import addext
from .defs import MCS_DATA_PATH


__all__ = [
    "load_mix_dframe",
    "load_mix_dframe_years",
    "load_mix_var",
    "load_mix_var_years",
    "load_prof_var",
    "load_prof_var_years",
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
]


def load_mix_dframe(year):
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
    # mix = pd.DataFrame(mix, columns=mix_cols)
    fname = addext(fn, ".csv.gz")
    # for vv in ['SCLK', 'Ls', 'solar_dist', 'orb_num', 'LST',
    # 'lat', 'lon', 'MY']:
    #    mix[vv] = pd.to_numeric(mix[vv], downcast='float')
    # load the index/profile ID column
    mix["profid"] = pd.read_csv(
        fname, squeeze=True, header=None, skiprows=1
    )
    # change time columns back to datetime types
    for cc in ["datetime"]:
        mix[cc] = mix[cc].astype("datetime64[ns]")
    # mix['UTC'] = mix['UTC'].astype('timedelta64[ns]')
    # make profid the index
    return mix.set_index("profid")


def load_mix_dframe_years(years=[2006, 2007, 2008, 2009, 2010]):
    """Load the metadata index files for several years and return one
    concatenated DataFrame."""
    df = pd.DataFrame()
    for yy in years:
        df = df.append(load_mix_dframe(yy))
    return df


def load_mix_var(year, varname, OLDMIX=False):
    """
    Reads a metadata index variable for `varname` from `year` as a
    numpy array from the numpy array file
    '{year}/indexdata/{year}_{varname}_index.npy'.
    """
    if OLDMIX:
        fname = (
            MCS_DATA_PATH
            + f"DATA/{year}/indexdata/{year}_{varname}_index.npy"
        )
        with gzip.open(fname, "rb") as fin:
            var = np.load(fin)
    else:
        fname = (
            MCS_DATA_PATH + f"DATA/{year}/indexdata/{year}_mixvars.npz"
        )
        with np.load(fname, allow_pickle=False) as fin:
            var = fin[varname]
    if varname in ["date", "datetime"] or "date" in varname.lower():
        var = var.astype("datetime64[ns]")
    if varname in ["UTC"]:
        var = var.astype("timedelta64[ns]")
    # print(f'loaded {fname}')
    return var


def load_mix_var_years(
    years=[2006, 2007, 2008, 2009, 2010], varname="temperature"
):
    """Loads multiple years of data for the metadata index variable
    `varname` and returns a single 1-D numpy array."""
    dat = []
    for yy in years:
        dat.append(load_mix_var(yy, varname))
    return np.concatenate(dat, axis=0)


def load_prof_var(year, varname):
    """Reads the profile data variable `varname` from `year` from
    the numpy array file "{year}/profdata/{year}_{varname}_profiles.npy"
    and returns a single 2-D array. If `varname` == "pressure", the
    returned array is shape (105,1)."""
    # handle pressure separately
    if varname == "pressure" or "varname" == "prs":
        return 610 * np.exp(-0.125 * (np.arange(105) - 9)).reshape(
            (1, 105)
        )
    fname = (
        MCS_DATA_PATH
        + f"DATA/{year}/profdata/{year}_{varname}_profiles.npy"
    )
    # load data
    with gzip.open(fname, "rb") as fout:
        var = np.load(fout).reshape((-1, 105))
    print(f"loaded {fname}")
    return var


def load_prof_var_years(
    years=[2006, 2007, 2008, 2009, 2010], varname="temperature"
):
    """Reads the profile data variable `varname` from `years`
    from the numpy array files and returns a single 2-D array.
    If `varname` == "pressure", the returned array is shape (105,1)."""
    dat = []
    # handle pressure separately
    if varname == "pressure":
        return load_prof_var(2006, varname)
    # read the data file for each year
    for yy in years:
        dat.append(load_prof_var(yy, varname))
    # concatenate the data arrays
    return np.concatenate(dat, axis=0)


# convenience functions to load several variables
load_temperature = load_prof_var_years
load_temperature_err = lambda: load_prof_var_years(varname="T_err") # noqa
load_pressure = lambda: load_prof_var_years(varname="pressure") # noqa
load_altitude = lambda: load_prof_var_years(varname="altitude") # noqa
load_H2Oice = lambda: load_prof_var_years(varname="H2Oice") # noqa
load_H2Oice_err = lambda: load_prof_var_years(varname="H2Oice_err") # noqa
load_H2Ovap = lambda: load_prof_var_years(varname="H2Ovap") # noqa
load_H2Ovap_err = lambda: load_prof_var_years(varname="H2Ovap_err") # noqa
load_dust = lambda: load_prof_var_years(varname="dust") # noqa
load_dust_err = lambda: load_prof_var_years(varname="dust_err") # noqa
load_SZA = lambda: load_mix_var_years(varname='solar_zen') # noqa
load_Ls = lambda: load_mix_var_years(varname='Ls') # noqa
load_MY = lambda: load_mix_var_years(varname='MY') # noqa
load_LST = lambda: load_mix_var_years(varname='LST') # noqa
load_lat = lambda: load_mix_var_years(varname='lat') # noqa
load_lon = lambda: load_mix_var_years(varname='lon') # noqa
load_Ls2 = lambda: load_Ls() + 360*(load_MY()-28) # noqa

