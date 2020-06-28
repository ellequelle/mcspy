__package__ = "mcspy"

from os import makedirs
from os.path import exists
import gzip
from .downloader import (
    get_most_recent_index_ftp,
    get_most_recent_index_http,
)
from .util import lxload
import pandas as pd
from .defs import (
    MCS_DATA_PATH,
    index_columns,
    _index_keep_columns,
)

indexing = [
    "dfindex",
    "lxdfquery",
    "lxdflatrng",
    "lxdflonrng",
    "lxdfyear",
    "lxdftempe",
    "lxdfday",
    "lxdfimg",
    "lxdfLsN",
    "reload_index",
    "qday",
    "qtempe",
    "qimg",
    "qmarci_mdgm",
]


# QUERY STRINGS
# for indexing using a mix DataFrame
qday = "solar_zen < 90"
qnight = "LST <= 0.4"
qtempe = "lat < 47.8 & lat > 43 & lon > -83.3 & lon < -70"
qimg = "lat < 70 & lat > 20 & lon > -125 & lon < -60"
qmarci_mdgm = 'start_time < "2010-07-01" & start_time > "2006-11-08"'

# approximate time of planet-encircling/global dust storms
# MY 28 (2007)
qgds_MY28 = "Ls > 269 & Ls < 300 & MY == 28"

# MY 34 (2018)
qgds_MY34 = "Ls > 185 & Ls < 250 & MY == 34"


# VARIABLE-BASED INDEX FUNCTIONS
# create logical indices based on one or more input variables


@lxload("Ls2")
def lxgds_MY28(Ls2):
    return (Ls2 > 250) & (Ls2 < 300)


@lxload("Ls2")
def lxgds_MY34(Ls2):
    return (Ls2 > 185 + 360 * (34 - 28)) & (Ls2 < 250 + 360 * (34 - 28))


@lxload("solar_zen")
def lxday(SZA):
    return SZA < 90


@lxload("Ls2")
def lxgds(Ls2):
    return lxgds_MY34(Ls2) | lxgds_MY28(Ls2)


@lxload(("lat", "lon"))
def lxregion(lat, lon, minlat=-90, minlon=-180, maxlat=90, maxlon=180):
    return (lat > minlat) & (lat < maxlat) & (lon > minlon) & (lon < maxlon)


@lxload(("lat", "lon"))
def lxtempe(lat, lon):
    return lxregion(
        lat, lon, minlat=43.0, minlon=-83.3, maxlat=47.8, maxlon=-70.0
    )


@lxload("Ls2")
def lxmarci_mdgm(Ls2):
    return (Ls2 > 132.1) & (Ls2 < 832)


# MIX INDEXING FUNCTIONS
# convenience functions for creating logical DataFrame indexes from
# the metadata index DataFrame
def lxdfquery(mix, qstr):
    return mix.index.isin(mix.query(qstr).index)


def lxdfmdgm(mix):
    return lxdfquery(qmarci_mdgm)


def lxdflatrng(mix, l0, l1):
    return lxdfquery(mix, f"lat > {l0} & lat < {l1}")


def lxdflonrng(mix, l0, l1):
    return lxdfquery(mix, f"lon > {l0} & lon < {l1}")


def lxdfyear(mix, yr):
    return lxdfquery(mix, f"date > {yr} & date < {yr+1}")


def lxdftempe(mix):
    return lxdfquery(mix, qtempe)


def lxdfday(mix):
    return lxdfquery(mix, qday)


def lxdfimg(mix):
    return lxdfquery(mix, qimg)


def lxdfLsN(mix, Ls, N):
    return lxdfquery(mix, f"Ls > {Ls} & Ls < {Ls+N}")


# INDEX LOADER
# to load the index of all data files and orbit numbers
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
    if not exists(MCS_DATA_PATH + "DATA/CUMINDEX.TAB.gz") or download:
        if exists(MCS_DATA_PATH + "DATA/CUMINDEX.TAB") and not download:
            # if uncompressed version, compress it
            with open(MCS_DATA_PATH + "DATA/CUMINDEX.TAB", "r") as fin:
                with gzip.open(
                    MCS_DATA_PATH + "DATA/CUMINDEX.TAB.gz", "w"
                ) as fout:
                    fout.write(fin.read())
        else:
            print("File CUMINDEX.TAB was not found locally.")
            if not allow_download:
                return pd.DataFrame()
            a = input("Attempt to download CUMINDEX.TAB from PDS? (y/n)")
            if a.lower() != "y":
                return pd.DataFrame()
            makedirs(MCS_DATA_PATH, exist_ok=True)
            # if cumulative index is not found, download it from pds
            try:  # with ftp it's easy to find the most recent index
                get_most_recent_index_ftp(
                    MCS_DATA_PATH + "DATA/CUMINDEX.TAB.gz"
                )
            except Exception:  # fall back on http if ftp doesn't work
                get_most_recent_index_http(
                    MCS_DATA_PATH + "DATA/CUMINDEX.TAB.gz"
                )
    # read index file into pandas DataFrame
    dfindex = pd.read_csv(
        MCS_DATA_PATH + "DATA/CUMINDEX.TAB.gz",
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
