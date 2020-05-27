import io
import gzip
from os.path import (
    basename,
    isabs,
    exists,
)
import numpy as np
import pandas as pd
from .marsdate import utc2myls
from .downloader import get_tab_files
from .util import (
    mcs_tab_path,
    add_prof_profid,
    add_prof_rowid,
    make_profidint,
    make_rowidint,
)
from .defs import (
    MCS_DATA_PATH,
    mix_keep_cols,
    header_columns,
    data_columns,
    mix_use_cols,
    mix_tab_dtypes,
    mix_date_col_lookup,
)

__all__ = [
    "parse_tab_file",
    "load_tab_file",
]


def load_tab_file(prodid, dfindex=None, download=True, **kwargs):
    """Load the data from the raw text file. Downloads the file if it
    isn't found locally.
    Returns a DataFrame with metadata and a DataFrame with the actual
    profile data."""
    # get the absolute path
    path = mcs_tab_path(prodid, dfindex, absolute=True,)
    if not exists(path):
        # if not found, look for gzipped version
        if exists(path + ".gz"):
            path = path + ".gz"
        elif download:
            # if no compressed version, try downloading
            get_tab_files(
                prodid, dfindex,
            )
            path = path + ".gz"
    # parse the TAB file and return two DataFrames
    return parse_tab_file(path, **kwargs)


def parse_tab_file(
    fn, meta=True, data=True, mix_keep_cols=mix_keep_cols,
):
    """Given a TAB file name, parse the MCS file and return the
    metadata (location, Ls, LST, etc) and the profiles in two DataFrames.
    meta: whether to return the metadata DataFrame
    data: whether to return the profile data DataFrame
    mix_keep_cols: columns to keep in the metadata (default value is
    set above)
    """

    # read file, separating the metadata lines from the profile data lines
    (mdlines, dats,) = _read_lists(fn)

    # product ID (prodid) is the name of the TAB file
    prodid = basename(fn.replace(".gz", ""))

    mdl = {}
    for (k, (a, b),) in mix_date_col_lookup.items():
        if a in mix_use_cols and b in mix_use_cols:
            mdl[k] = [a, b]

    # read "header" lines into a DataFrame
    dfmd = pd.read_csv(
        io.StringIO("\n".join(mdlines)),
        header=None,
        names=header_columns,
        dtype=mix_tab_dtypes,
        cache_dates=True,
        infer_datetime_format=True,
        parse_dates=True,
        na_values=["-9999"],
        comment="#",
    )  # .replace(-9999,np.nan)
    """
    # replace nans in any date columns with NaT
    for k in mix_date_cols + mix_time_cols:
        if k in dfmd:
            dfmd[k].replace(np.nan, pd.NaT)
    """

    # make product ID column
    dfmd["prodid"] = prodid
    # make profile ID column and make it the dataframe index
    dfmd["profid"] = dfmd["prodid"] + ":" + dfmd.index.astype(str)
    dfmd = dfmd.set_index("profid")

    # find retrievals that are marked as "bad"
    lx = dfmd["1"].astype(bool) | (
        (dfmd["Gqual"] != 0) & (dfmd["Gqual"] != 6)
    )  # indicates bad retrievals
    # store number of retrievals in file before removing bad ones
    nlen = len(lx)
    # get profile IDs of "bad" retrievals
    badprofids = dfmd[lx].index
    # remove bad rows from the metadata index dataframe
    dfmd = dfmd[~lx]
    # remove the quality marker row
    dfmd.pop("1")

    # sometimes the none of the profiles are useful, then
    # return empty DataFrames
    if len(dfmd) == 0:
        if meta:
            return pd.DataFrame(), pd.DataFrame()
        return pd.DataFrame()

    # convert date to datetime
    dfmd["date"] = pd.to_datetime(dfmd["date"])
    # convert UTC to timedelta
    dfmd["UTC"] = pd.to_timedelta(dfmd["UTC"])
    # make a datetime column with the actual UTC time
    dfmd["datetime"] = dfmd["date"] + dfmd["UTC"]
    # use the datetime column to calculate the Mars Year and Ls for
    # each retrieval
    mycls = np.transpose(utc2myls(dfmd["datetime"]))
    df = pd.DataFrame(mycls, columns=["MY", "cLs"], index=dfmd.index)
    dfmd = dfmd.join(df)

    # drop extra columns
    dfmd = dfmd[mix_keep_cols]
    dfmd["profidint"] = make_profidint(dfmd)

    # deal with the profile data
    if data:
        # use pandas to parse the profile data
        dats = "\n".join(["\n".join(d) for d in dats])
        dats = pd.read_csv(
            io.StringIO(dats),
            header=None,
            dtype=float,
            names=data_columns,
            na_values=-9999.0,
        )

        # add a column with the profile number (number from the top
        # of the file)
        prof_num = (
            np.tile(np.array(range(nlen)), (105, 1),).transpose().flatten()
        )
        # this file has two bad profiles
        # 2006121500_DDR.TAB 4348 (34230, 15) (34020,)
        dats["prof_num"] = prof_num
        dats["prodid"] = prodid
        # make profile ID column from prof_num
        dats = add_prof_profid(dats)
        # add row ID and make it the index
        dats = add_prof_rowid(dats)
        dats = dats.set_index("rowid")

        # drop bad rows
        dats = dats[~(dats["profid"].isin(badprofids))]
        # remove quality flag column
        dats.pop("1")

        # make integer row ID
        dats["rowidint"] = make_rowidint(dats.index)

        # return DataFrames
        if meta:
            return dfmd, dats
        return dats
    return dfmd


def _read_lists(fn):
    """_read_lists is a function to help parse_mcs_file by reading
    the actual TAB file, separating the metadata rows from the profile
    data rows, and returning both sets of strings as lists
    returns
       mdlines: list of metadata lines
       dats: list of profile data lines
    """
    # read the file
    if not isabs(fn):
        fn = MCS_DATA_PATH + fn
    if fn.endswith("gz"):
        with gzip.open(fn, "rb") as fin:
            lines = fin.read().decode("ascii").replace('"', "").split("\n")
    else:
        with open(fn, "r") as fin:
            lines = fin.read().replace('"', "").split("\n")
    for ix in range(len(lines)):
        if lines[0].startswith("#"):
            lines = lines[1:]
        # if lines[ix].startswith('1, '):
        #    break
    # remove comment lines
    # lines = lines[ix+2:]
    lines = lines[2:]
    # separate out "header" lines from retrieval data
    mdlines = lines[::106]  # metadata lines
    # get data lines with profiles separated
    dats = [
        lines[slice((n * 106 + 1), ((n + 1) * 106))]
        for n in range(len(lines) // 106)
    ]
    return mdlines, dats
