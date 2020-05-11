__package__ = 'mcspy'
from os import makedirs, unlink
from os.path import dirname
import gzip
from ftplib import FTP
from requests import get
from .util import mcs_tab_path, addext
from .defs import _most_recent_known_mrom

__all__ = ['get_tab_files', 'get_most_recent_index_http', 'get_most_recent_index_ftp']

PDS_ATMOS_HOST = 'atmos.nmsu.edu'
PDS_SERVER_PATH = '/PDS/data/'
PDS_ROOT_URL = f'{PDS_ATMOS_HOST}{PDS_SERVER_PATH}'

def get_tab_files(prodids, dfindex, overwrite=False, use_ftp=False):
    '''Given one or more product IDs (prodids), download .TAB data files from the PDS.'''
    if isinstance(prodids, str):
        prodids = [prodids]
    for prodid in prodids:
        # get the file path as it is stored on the PDS
        path = mcs_tab_path(prodid, dfindex, volume=True)
        # get the local file path, not including the volume
        localpath = mcs_tab_path(prodid, dfindex, volume=False,
                                      absolute=True)
        # make sure directory exists
        makedirs(dirname(localpath), exist_ok=True)
        if use_ftp:
            get_tab_file_ftp(PDS_SERVER_PATH + '/' + path, addext(localpath, '.gz'))
        else:
            get_tab_file_http(PDS_ROOT_URL + '/' + path, addext(localpath, '.gz'))
    print('Done')

def ftp_login():
    '''Convenience function to return an FTP object connected to the PDS atmos server.'''
    passwd = input('Email (as a "password" for PDS ftp server): ')
    print(f'Connecting to {PDS_ATMOS_HOST}...')
    return FTP(PDS_ATMOS_HOST, user='anonymous', passwd=passwd)

def get_tab_file_http(server_filepath, local_filepath):
    '''Download the specified file using HTTP. '''
    print(f'Downloading {server_filepath}...')
    try:
        with gzip.open(addext(local_filepath, '.gz'), 'w') as fout:
            r = get('http://' + server_filepath)
            # check response
            r.raise_for_status()
            # save as gzip'ed file
            fout.write(r.content)
    except Exception as e:
        unlink(addext(local_filepath, '.gz'))
        raise Exception from e

def get_tab_file_ftp(server_filepath, local_filepath):
    '''Download the specified file using FTP. '''
    with ftp_login() as ftp:
        with gzip.open(local_filepath, 'w') as fout:
            print(f'Downloading {server_filepath}...')
            ftp.retrbinary('RETR {server_filepath}', fout.write)

def get_most_recent_index_ftp(local_filepath='CUMINDEX.TAB.gz'):
    '''Find and download the most recent CUMINDEX.TAB file using FTP.'''
    with ftp_login() as ftp:
        mromlist = ftp.nlst('/PDS/data/MROM_2*')
        mromlist.sort()
        ftp.cwd(mromlist[-1]+'/INDEX')
        with gzip.open(addext(local_filepath, '.gz'), 'w') as fout:
            print('Downloading '+ftp.pwd()+'/CUMINDEX.TAB')
            ftp.retrbinary('RETR CUMINDEX.TAB', fout.write)
            
def get_most_recent_index_http(local_filepath='CUMINDEX.TAB.gz'):
    '''Assume this is the most recent file since it's difficult to search with HTTP. '''
    r = get(PDS_ROOT_URL + _most_recent_known_mrom + '/INDEX/CUMINDEX.TAB')
    r.raise_for_status()
    with gzip.open(MCS_DATA_PATH + 'CUMINDEX.TAB.gz', 'w') as fout:
        fout.write(r.content)
