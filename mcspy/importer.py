__package__ = "mcspy"
import gzip
from os import makedirs
from os.path import exists, dirname
import numpy as np
import pandas as pd
from .loaders import (
    load_mix_var,
    load_prof_var,
    load_mix_dframe,
    load_prof_dframe,
)
from .util import local_data_path, addext
from .parsing import load_tab_file
from .defs import mix_cols, prof_cols, MCS_DATA_PATH

__all__ = [
    "collect_yearly_vars",
    "find_missing_tab_files",
    "import_downloaded_files",
    "check_mix_data",
    "sort_prof_data",
    "sort_mix_data",
]
_others = [
    "save_prof_var",
    "_append_mix_dframe",
    "save_mix_dframe",
    "save_mix_var",
    "save_prof_df",
    "_append_prof_var",
    "_append_mix_var",
    "_append_prof_df",
    "_load_tab_files",
]


def save_prof_var(var, year, varname):
    """Writes the profile data variable `varname` from `year`, passed
    in the numpy array `var` to the numpy array file "{year}/profdata/
    {year}_{varname}_profiles.npy"."""
    fname = local_data_path(
        f"DATA/{year}/profdata/{year}_{varname}_profiles.npy"
    )
    if not exists(dirname(fname)):
        makedirs(dirname(fname))
    with gzip.open(fname, "wb") as fout:
        np.save(fout, var, False)
    print(f"wrote {fname}")


def _append_mix_dframe(mix):
    """Append new rows onto an existing saved metadata index DataFrame."""
    if len(mix) == 0:
        return
    year = mix["datetime"].dt.year.unique()
    if year.size > 1:
        raise ValueError(
            "append_mix_drame only works for data from a single year"
        )
    year = year[0]
    df = pd.DataFrame()
    _append_mix_dfvars(mix)  # save as individual arrays
    fn = local_data_path(f"DATA/{year}/indexdata/{year}_mixvars")
    if exists(addext(fn, ".npz")) and exists(addext(fn, ".csv.gz")):
        df = load_mix_dframe(year)
    else:
        df = pd.DataFrame()
    save_mix_dframe(df.append(mix, verify_integrity=True))


def save_mix_var(var, year, varname):
    """Writes a metadata index variable for `varname` from `year` as
    a numpy array to the numpy array file
    '{year}/indexdata/{year}_{varname}_index.npy'."""
    fname = local_data_path(
        f"DATA/{year}/indexdata/{year}_{varname}_index.npy"
    )
    if varname in ["datetime"]:
        var = var.astype(int)
    if not exists(dirname(fname)):
        makedirs(dirname(fname))
    with gzip.open(fname, "wb") as fout:
        np.save(fout, var, False)
    print(f"wrote {fname}")


def save_mix_dframe(mix):
    """Save a metadata index DataFrame to a numpy file (numeric data)
    and a csv file (non-numeric data). This function saves one
    DataFrame per earth year."""
    mix = mix.copy()
    mix = mix.reset_index()  # index becomes "profid" column
    year = mix["profid"].str.slice(None, 4).iloc[0]
    fn = local_data_path(f"DATA/{year}/indexdata/{year}_mixvars")
    # drop product ID
    if "prodid" in mix:
        mix = mix.drop(columns=["prodid"])
    fname = addext(fn, ".csv.gz")
    # write profile ID column to a compressed csv file
    mix.pop("profid").to_csv(fname, index=None, header=True)
    print(f"saved {fname}")
    # interpret datetime columns as 64-bit integers
    # save numeric data columns as a 2-D numpy array
    for cc in ["datetime"]:
        mix[cc] = mix[cc].astype(int)
    np.savez_compressed(fn, **{n: mix[n].to_numpy() for n in mix.columns})
    # fname = addext(fn, '.npy')
    # np.save(fname, mix[mix_cols].values, False)
    print(f"saved {fname}, {mix.shape}")


def save_prof_df(dfprof):
    year = dfprof["profid"].str.slice(None, 4).iloc[0]
    for vv in prof_cols:
        if vv in dfprof:
            save_prof_var(dfprof[vv].to_numpy(), year, vv)


def _append_prof_var(var, year, varname):
    """Append profile data passed in `var` for the variable `varname`
    and year `year` to a numpy array file. If the file does not exist,
    create it."""
    if len(var) == 0:
        return
    dat = var.reshape((-1, 105))
    fname = local_data_path(
        f"DATA/{year}/profdata/{year}_{varname}_profiles.npy"
    )
    # check whether file exists
    if not exists(fname):
        save_prof_var(var, year, varname)
    else:
        # concatenate new and existing data arrays
        oldvar = load_prof_var(year, varname).flatten()
        print(oldvar.shape, dat.shape)
        oldvar = np.hstack((oldvar.flatten(), dat.flatten()))
        # save concatenated arrays to the file
        save_prof_var(oldvar, year, varname)
        print(f"prof {varname}, {year}, {oldvar.shape}")


def _append_mix_var(var, year, varname):
    """Append metadata data passed in `var` for the metadata variable
    `varname` and year `year` to a numpy array file. If the file does
    not exist, create it."""
    if len(var) == 0:
        return
    dat = var
    fname = local_data_path(
        f"DATA/{year}/indexdata/{year}_{varname}_index.npy"
    )
    # check whether file exists
    if not exists(fname):
        save_mix_var(var, year, varname)
    else:
        # concatenate new and existing data arrays
        oldvar = load_mix_var(year, varname)
        oldvar = np.concatenate((oldvar, dat))
        # save concatenated arrays to the file
        save_mix_var(oldvar, year, varname)
        print(f"mix {varname}, {year}, {oldvar.shape}")


def _append_mix_dfvars(df):
    if len(df) == 0:
        return
    year = df["datetime"].dt.year.unique()
    year = year[0]
    mix = df
    for vv in mix_cols:
        if vv in mix:
            _append_mix_var(mix[vv].to_numpy(), year, vv)


def _append_prof_df(dfprof):
    """Append the data from columns in the profile DataFrame `dfprof`
    to the respective data files."""
    if len(dfprof) == 0:
        return
    year = dfprof["profid"].str.slice(None, 4).iloc[0]
    for vv in prof_cols:
        if vv in dfprof:
            _append_prof_var(dfprof[vv].to_numpy(), year, vv)


def _shrink_df(df):
    """Convert ints and floats from 64 bit to 32 bit to save space """
    df_ = df.copy()
    for vv in df:
        if df_[vv].dtype.kind == "i":
            df_[vv] = pd.to_numeric(df_[vv], downcast="integer")
        elif df_[vv].dtype.kind == "u":
            df_[vv] = pd.to_numeric(df_[vv], downcast="unsigned")
        elif df_[vv].dtype.kind == "f":
            df_[vv] = pd.to_numeric(df_[vv], downcast="float")
    return df_


def find_existing_tab_files(year="*", PATHS=False, ABSOLUTE=False):
    """
    Find all existing .TAB or .TAB.gz files in the current MCS_DATA_PATH.
    By default, returns the product ID (filename) for each file

    PATHS: return the file paths
    ABSOLUTE: return the absolute file paths (if False, returns paths
        relative to MCS_DATA_PATH). Ignored if PATHS is false.
    """
    from pathlib import Path

    pth = Path(MCS_DATA_PATH) / "DATA"
    allfiles = list(pth.glob(f"{year}/**/*TAB")) + list(
        pth.glob(f"{year}/**/*TAB.gz")
    )
    if PATHS:
        if ABSOLUTE:
            return [x.absolute().as_posix() for x in allfiles]
        return [x.relative_to(MCS_DATA_PATH).as_posix() for x in allfiles]
    # last 3 characters are ".gz"
    return [x.name[:-3] for x in allfiles]


def _get_missing_prodids(year):
    """
    Compare avaliable TAB files to prodids in the {year}_profidint_index.npy
    file and return a list of product ID's of files not represented in binary
    data files.
    """
    prodids = pd.Series(find_existing_tab_files()).str[:10]
    prodids = prodids[prodids.str.startswith(str(year))].astype(int)
    mixprodids = pd.Series(
        pd.unique(
            np.trunc(load_mix_var(str(year), "profidint") / 1e4).astype(int)
        )
    )
    return (
        prodids.loc[~prodids.isin(mixprodids)].astype(str) + "_DDR.TAB"
    ).tolist()


def check_index_profiles(year, raise_for_false=True):
    """
    Check index and profile ID variables for consistency. Make sure sizes and
    values match.
    """
    err = None
    msg = ""
    profids = load_mix_var(str(year), "profidint")
    rowids = load_prof_var(str(year), "rowidint")
    if profids.shape[0] != rowids.shape[0]:
        msg = "Index and profile sizes do not match."
        err = IndexError
    lx = profids == (rowids[:, 0] / 1e3).astype(int)
    if not lx.all():
        msg = "Profile ID's and row ID's are inconsistent."
        err = ValueError
    if not (np.sort(profids) == profids).all():
        msg = "Profile ID's are not sorted."
        err = AssertionError
    if not (np.sort(rowids) == rowids).all():
        msg = "Row ID's are not sorted."
        err = AssertionError
    if err is None:
        return True
    if raise_for_false:
        raise (err(msg))


def _get_new_prodids(year):
    file_prodids = (
        pd.Series(find_existing_tab_files(str(year))).str[:10].astype(int)
    )
    try:
        imported_prodids = pd.Series(
            pd.unique(load_mix_var(year, "profidint") // 10000)
        )
    except FileNotFoundError:
        imported_prodids = pd.Series(dtype=int)
    return file_prodids[~file_prodids.isin(imported_prodids)]


def import_downloaded_files(year):
    new_prodids = _get_new_prodids(year)
    ymms = (new_prodids // 1000).unique()
    for ym in ymms:
        pids = new_prodids[new_prodids // 1000 == ym].astype(str) + "_DDR.TAB"
        dfm, dfp = _load_tab_files(pids.tolist())
        if len(dfm) == 0 and len(dfp) == 0:
            continue
        if len(dfm) != len(dfp)//105:
            raise ValueError("Index and profile data shapes don't match.")
        _append_mix_dframe(dfm)
        _append_prof_df(dfp)
    print("Sorting index data...")
    sort_mix_data(year)
    print("Sorting profile data...")
    sort_prof_data(year)
    return check_index_profiles(year)


def sort_mix_data(year):
    _mix = load_mix_dframe(year)
    mix = _mix.sort_values("profidint")
    if (_mix.values == mix.values).all():
        return
    save_mix_dframe(mix)
    for vv in mix_cols:
        if vv in mix:
            save_mix_var(mix[vv], year, vv)


def sort_prof_data(year):
    rowidint = load_prof_var(year, 'rowidint')
    ix = np.argsort(rowidint.flatten()).reshape(-1, 105)
    save_prof_var(rowidint.flatten()[ix], year, 'rowidint')
    for vv in prof_cols:
        if vv == 'rowidint':
            continue
        try:
            var = load_prof_var(year, vv)
        except:
            continue
        prof = var.flatten()[ix]
        save_prof_var(prof, year, vv)

        
def find_missing_tab_files(dfindex):
    """
    List product ID's of any TAB files listed in dfindex that are not available
    locally.
    """
    from os import stat
    from os.path import exists
    from .util import mcs_tab_path

    missing_prodids = []
    # loop through rows
    for prodid in dfindex.index:
        fn = mcs_tab_path(prodid, dfindex, absolute=True)
        tf = False  # assume does not exist
        if not exists(fn):  # try both .TAB and .TAB.gz
            fn = fn + ".gz"
        if exists(fn):  # this should be the correct name if it exists
            tf = stat(fn).st_size > 5e3  # make sure it's a reasonable size
        if not tf:  # if it does not exist or is unreasonably small
            missing_prodids.append(prodid)  # add file to missing list
    return missing_prodids


def collect_yearly_vars(dfindex, MIX=True, PROF=True):
    """Read the MCS TAB data files and save the metadata and profile
    data to binary files to be easily read in the future.

    This function creates yearly .npy array files with each file
    containing the data for one variable for the whole year. If TAB
    files are not found locally, it will attempt to download them from
    the PDS.

    This appends TAB files onto any data in already existing .npy or
    .csv.gz files, and so this function should only be run once when
    first assembling the binary files.

    Parameters
    ----------
    dfindex : DataFrame from the PDS index file loaded by `reload_index`.
    """
    # read max 10 days at a time between saves
    # loading files gets slower as the dataframes increase in size
    ymms = (
        dfindex.start_time.dt.year * 1000
        + dfindex.start_time.dt.month * 10
        + dfindex.start_time.dt.day // 10
    ).unique()
    for ym in ymms:
        dfi = dfindex.loc[dfindex.index.str.startswith(ym.astype(str))]
        dfmix, dfprof = _load_tab_files(dfi.index, dfindex, MIX=MIX, PROF=PROF)
        if MIX:
            _append_mix_dframe(dfmix)
        if PROF:
            _append_prof_df(dfprof)


def _load_tab_files(prodids, dfindex=None, MIX=True, PROF=True):
    dfmix = []
    dfprof = []
    dfmix = pd.DataFrame()
    dfprof = pd.DataFrame()
    for prodid in prodids:
        dfm, dfp = load_tab_file(prodid, dfindex)
        xpt = [prodid]
        if MIX:
            dfmix = dfmix.append(_shrink_df(dfm), verify_integrity=True)
            # dfmix.append(_shrink_df(dfm).reset_index().set_index('profidint'))
            xpt += [dfmix.index.nunique()]
        if PROF:
            dfprof = dfprof.append(_shrink_df(dfp), verify_integrity=True)
            # dfprof.append(_shrink_df(dfp).reset_index().set_index('rowidint'))
            xpt += [dfprof.index.nunique()]
        print(*xpt)
    # if MIX:
    #    dfmix = pd.concat(dfmix).set_index('profid')
    # if PROF:
    #    dfprof = pd.concat(dfprof).set_index('profid')
    return dfmix, dfprof
