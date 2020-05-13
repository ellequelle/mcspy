__package__ = "mcspy"

from os import makedirs
from os.path import exists
import gzip
from .downloader import (
    get_most_recent_index_ftp,
    get_most_recent_index_http,
)
import pandas as pd
from .defs import (
    MCS_DATA_PATH,
    index_columns,
    _index_keep_columns,
    qmarci_mdgm,
    qtempe,
    qday,
    qimg,
)

indexing = [
    "dfidnex",
    "lxquery",
    "lxlatrng",
    "lxlonrng",
    "lxyear",
    "lxtempe",
    "lxday",
    "lximg",
    "lxLsN",
    "reload_index",
]


# convenience functions for creating logical DataFrame indexes from
# the metadata index DataFrame
def lxquery(mix, qstr):
    return mix.index.isin(mix.query(qstr).index)


def lxmdgm(mix):
    return lxquery(qmarci_mdgm)


def lxlatrng(mix, l0, l1):
    return lxquery(mix, f"lat > {l0} & lat < {l1}")


def lxlonrng(mix, l0, l1):
    return lxquery(mix, f"lon > {l0} & lon < {l1}")


def lxyear(mix, yr):
    return lxquery(mix, f"date > {yr} & date < {yr+1}")


def lxtempe(mix):
    return lxquery(mix, qtempe)


def lxday(mix):
    return lxquery(mix, qday)


def lximg(mix):
    return lxquery(mix, qimg)


def lxLsN(mix, Ls, N):
    return lxquery(mix, f"Ls > {Ls} & Ls < {Ls+N}")


def reload_index(download=False, allow_download=True):
    """Load the cumulative index file that lists every TAB data
    file in the PDS archive """
    dftypes = {
        "volume_id": "string",
        "path": "string",
        "filename": "string",
        "start_orbit_number": "int64",
        "stop_orbit_number": "int64",
    }
    # download index file if not found
    if not exists(MCS_DATA_PATH + "CUMINDEX.TAB.gz") or download:
        if exists(MCS_DATA_PATH + "CUMINDEX.TAB") and not download:
            # if uncompressed version, compress it
            with open(MCS_DATA_PATH + "CUMINDEX.TAB", "r") as fin:
                with gzip.open(
                    MCS_DATA_PATH + "CUMINDEX.TAB.gz", "w"
                ) as fout:
                    fout.write(fin.read())
        else:
            print("File CUMINDEX.TAB was not found locally.")
            if not allow_download:
                return pd.DataFrame()
            a = input(
                "Attempt to download CUMINDEX.TAB from PDS? (y/n)"
            )
            if a.lower() != "y":
                return pd.DataFrame()
            makedirs(MCS_DATA_PATH, exist_ok=True)
            # if cumulative index is not found, download it from pds
            try:  # with ftp it's easy to find the most recent index
                get_most_recent_index_ftp(
                    MCS_DATA_PATH + "CUMINDEX.TAB.gz"
                )
            except Exception:  # fall back on http if ftp doesn't work
                get_most_recent_index_http(
                    MCS_DATA_PATH + "CUMINDEX.TAB.gz"
                )
    # read index file into pandas DataFrame
    dfindex = pd.read_csv(
        MCS_DATA_PATH + "CUMINDEX.TAB.gz",
        header=None,
        dtype=dftypes,
        parse_dates=["start_time", "stop_time"],
        names=index_columns,
        infer_datetime_format=True,
        usecols=_index_keep_columns,
    ).rename_axis(index="mcsnum")
    # make start and stop times datetimes
    for cn in ["start_time", "stop_time"]:
        dfindex[cn] = pd.to_datetime(dfindex[cn])
    # downcast integers
    for cn in ["start_orbit_number", "stop_orbit_number"]:
        dfindex[cn] = pd.to_numeric(dfindex[cn], downcast="unsigned")
    # make string columns pd.StringDtype
    for cn in ["volume_id", "path", "filename"]:
        dfindex[cn] = dfindex[cn].astype("string")
    # set filename, what I call Product ID, to be the index
    dfindex = dfindex.set_index("filename", drop=False).rename_axis(
        index="prodid"
    )
    return dfindex


dfindex = reload_index(allow_download=False)
