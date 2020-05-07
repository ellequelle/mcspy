__package__ = 'mcspy'

from os.path import exists
import gzip
from .downloader import get_most_recent_index_ftp, get_most_recent_index_http
import pandas as pd
from .defs import MCS_DATA_PATH, index_columns, _index_keep_columns, qmarci_mdgm

indexing = ['dfidnex', 'lxquery', 'lxlatrng', 'lxlonrng', 'lxyear',
            'lxtempe', 'lxday', 'lximg', 'lxLsN', 'reload_index']

# convenience functions for creating logical DataFrame indexes from the metadata index DataFrame
lxquery = lambda mix, qstr: mix.index.isin(mix.query(qstr).index)
lxlatrng = lambda mix, l0, l1: lxquery(mix, f'lat > {l0} & lat < {l1}')
lxlonrng = lambda mix, l0, l1: lxquery(mix, f'lon > {l0} & lon < {l1}')
lxyear = lambda mix, yr: lxquery(mix, f'date > {yr} & date < {yr+1}')
lxtempe = lambda mix: lxquery(mix, qtempe)
lxday = lambda mix: lxquery(mix, qday)
lximg = lambda mix: lxquery(mix, qimg)
lxLsN = lambda mix, Ls, N: lxquery(mix, f'Ls > {Ls} & Ls < {Ls+N}')

def reload_index(download=False):
    '''Load the cumulative index file that lists every TAB data file in the PDS archive '''
    dftypes = {'volume_id':'string', 'path':'string', 'filename':'string',
               'start_orbit_number':'int64', 'stop_orbit_number':'int64'}
    # download index file if not found
    if not exists(MCS_DATA_PATH + 'CUMINDEX.TAB.gz') or download:
        if exists(MCS_DATA_PATH + 'CUMINDEX.TAB') and not download:
            # if uncompressed version, compress it
            with open(MCS_DATA_PATH + 'CUMINDEX.TAB', 'r') as fin:
                with gzip.open(MCS_DATA_PATH + 'CUMINDEX.TAB.gz', 'w') as fout:
                    fout.write(fin.read())
        else:
            # if cumulative index is not found, download it from pds
            try: # with ftp it's easy to find the most recent index
                get_most_recent_index_ftp(MCS_DATA_PATH + 'CUMINDEX.TAB.gz')
            except: # fall back on http if ftp doesn't work
                get_most_recent_index_http(MCS_DATA_PATH + 'CUMINDEX.TAB.gz')
    # read index file into pandas DataFrame
    dfindex = pd.read_csv(MCS_DATA_PATH + 'CUMINDEX.TAB.gz', header=None, 
                        dtype=dftypes, parse_dates=['start_time', 'stop_time'],
        names=index_columns, infer_datetime_format=True, usecols=_index_keep_columns).rename_axis(index='mcsnum')
    # make start and stop times datetimes
    for cn in ['start_time', 'stop_time']:
        dfindex[cn] = pd.to_datetime(dfindex[cn])
    # downcast integers
    for cn in ['start_orbit_number', 'stop_orbit_number']:
        dfindex[cn] = pd.to_numeric(dfindex[cn], downcast='unsigned')
    # make string columns pd.StringDtype
    for cn in ['volume_id', 'path', 'filename']:
        dfindex[cn] = dfindex[cn].astype('string')
    # set filename, what I call Product ID, to be the index
    dfindex = dfindex.set_index('filename', drop=False).rename_axis(index='prodid')
    return dfindex

dfindex = reload_index()
