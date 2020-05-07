__package__ = 'mcspy'

from .defs import MCS_DATA_PATH


__all__ = ['add_prof_profid', 'add_prof_prsnum', 'local_data_path',
     'add_prof_rowid', 'addext', 'mcs_tab_path']

def local_data_path(pth, ext=''):
    from pathlib import Path
    from os.path import isabs
    pth = Path(addext(pth, ext))
    if pth.is_absolute():
        return str(pth)
    if pth.parts[0] == 'DATA':
        pth = MCS_DATA_PATH / pth
    return str(pth)


def mcs_tab_path(prodids, dfindex, volume=False,
                     absolute=False):
    '''Guess the file path for the .TAB file with a given product ID (prodid). Prodids can be either a single string or a Series of strings.'''
    df = dfindex.loc[prodids]
    path = 'DATA/'+df['path']+'/'+df['filename']
    if volume:
        # volume is for downloading the file from PDS
        path = df['volume_id']+'/' + path
    if absolute:
        return MCS_DATA_PATH + path
    return path

def add_prof_prsnum(prof):
    if 'prsnum' in prof:
        return prof
    p = prof.copy()
    p.insert(1, 'prsnum', (np.log(p['pressure']/610)/-.125+10).round().astype(int))
    return p

def add_prof_rowid(prof):
    if 'rowid' in prof:
        return prof
    pp = prof.copy()
    pp = add_prof_profid(add_prof_prsnum(pp))
    pp['rowid'] = (pp.profid + ':' + pp.prsnum.astype(str)).astype('string')
    return pp

def add_prof_profid(prof):
    if 'profid' in prof:
        return prof
    pp = prof.copy()
    pp['profid'] = (pp['prodid'] + ':' + pp.prof_num.astype(str)).astype('string')
    return pp

def addext(fn, ext):
    '''Add a file extension to a filename if it doesn't already exist.'''
    if not fn.endswith(ext):
        return fn+ext
    return fn
