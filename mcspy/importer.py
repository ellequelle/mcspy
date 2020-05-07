__package__ = 'mcspy'
import gzip
import numpy as np
import pandas as pd
from .util import local_data_path

__all__ = ['collect_yearly_vars', ]
_others = ['save_prof_var', '_append_mix_dframe', 'save_mix_dframe', 'save_mix_var', 'save_prof_df', '_append_prof_var', '_append_mix_var', '_append_prof_df']

def save_prof_var(var, year, varname):
    '''Writes the profile data variable `varname` from `year`, passed in the numpy array `var` to the numpy array file "{year}/{year}_{varname}_profiles.npy".'''
    fname = local_data_path(f'DATA/{year}/{year}_{varname}_profiles.npy')
    with gzip.open(fname, 'wb') as fout:
        np.save(fout, var, False)
    print(f'wrote {fname}')

def _append_mix_dframe(mix):
    '''Append new rows onto an existing saved metadata index DataFrame.'''
    year = mix['date'].dt.year.unique()
    if year.size > 1:
        raise ValueError('append_mix_drame only works for data from a single year')
    year = year[0]
    df = pd.DataFrame()
    _append_mix_dfvars(mix) # save as individual arrays
    try:
        df = load_mix_dframe(year)
    except:
        pass
    save_mix_dframe(df.append(mix, verify_integrity=True))

def save_mix_var(var, year, varname):
    '''Writes a metadata index variable for `varname` from `year` as a numpy array to the numpy array file "{year}/{year}_{varname}_index.npy".'''
    fname = local_data_path(f'DATA/{year}/{year}_{varname}_index.npy')
    with gzip.open(fname, 'wb') as fout:
        np.save(fout, var, False)
    print(f'wrote {fname}')



def save_mix_dframe(mix):
    '''Save a metadata index DataFrame to a numpy file (numeric data) and a csv file (non-numeric data). This function saves one DataFrame per earth year.'''
    mix = mix.copy()
    mix = mix.reset_index()
    year = mix['profid'].str.slice(None, 4).iloc[0]
    fn = local_data_path(f'DATA/{year}/{year}_mixvars')
    # drop product ID
    if 'prodid' in mix:
        mix = mix.drop(columns=['prodid'])
    fname = addext(fn, '.csv.gz')
    # write profile ID column to a compressed csv file
    mix.pop('profid').to_csv(fname, index=None, header=True)
    print(f'saved {fname}')
    # interpret datetime columns as 64-bit integers
    for cc in ['date', 'UTC', 'datetime']:
        mix[cc] = mix[cc].astype(int)
    fname = addext(fn, '.npy')
    # save numeric data columns as a 2-D numpy array
    np.save(fname, mix[mix_cols].values, False)
    print(f'saved {fname}')


def save_prof_df(dfprof):
    year = dfprof['profid'].str.slice(None, 4).iloc[0]
    for vv in prof_cols:
        if vv in dfprof:
            save_prof_var(dfprof[vv].to_numpy(), year, vv)

def _append_prof_var(var, year, varname):
    '''Append profile data passed in `var` for the variable `varname` and year `year` to a numpy array file. If the file does not exist, create it.'''
    dat = var.reshape((105,-1))
    fname = local_data_path(f'DATA/{year}/{year}_{varname}_profiles.npy')
    # check whether file exists
    if not exists(fname):
        save_prof_var(var, year, varname)
    else:
        # concatenate new and existing data arrays
        oldvar = load_prof_var(year, varname)
        oldvar = np.hstack((oldvar, dat))
        # save concatenated arrays to the file
        save_prof_var(oldvar, year, varname)

def _append_mix_var(var, year, varname):
    '''Append metadata data passed in `var` for the metadata variable `varname` and year `year` to a numpy array file. If the file does not exist, create it.'''
    dat = var.reshape((105,-1))
    fname = local_data_path(f'DATA/{year}/{year}_{varname}_index.npy')
    # check whether file exists
    if not exists(fname):
        save_prof_var(var, year, varname)
    else:
        # concatenate new and existing data arrays
        oldvar = load_prof_var(year, varname)
        oldvar = np.hstack((oldvar, dat))
        # save concatenated arrays to the file
        save_prof_var(oldvar, year, varname)

def _append_prof_df(dfprof):
    '''Append the data from columns in the profile DataFrame `dfprof` to the respective data files.'''
    year = dfprof['profid'].str.slice(None, 4).iloc[0]
    for vv in prof_cols:
        if vv in dfprof:
            _append_prof_var(dfprof[vv].to_numpy(), year, vv)


def _shrink_df(df):
    '''Convert ints and floats from 64 bit to 32 bit to save space '''
    df_ = df.copy()
    for vv in df:
        if df_[vv].dtype.kind == 'i':
            df_[vv] = pd.to_numeric(df_[vv], downcast='integer')
        elif df_[vv].dtype.kind == 'u':
            df_[vv] = pd.to_numeric(df_[vv], downcast='unsigned')
        elif df_[vv].dtype.kind == 'f':
            df_[vv] = pd.to_numeric(df_[vv], downcast='float')
    return df_

def collect_yearly_vars(dfindex):
    '''Read the MCS TAB data files and save the metadata and profile data to binary files to be easily read in the future.
    This function creates yearly .npy array files with each file containing the data for one variable for the whole year. If TAB files are not found locally, it will attempt to download them from the PDS. 

This appends TAB files onto any data in already existing .npy or .csv.gz files, and so this function should only be run once when first assembling the binary files.

    Parameters
    ----------
    dfindex : DataFrame from the PDS index file loaded by `reload_index`. 
    '''
    ymms = (dfindex.start_time.dt.year*100
                + dfindex.start_time.dt.month).unique()
    for ym in ymms:
        dfi = dfindex.loc[dfindex.index.str.startswith(ym.astype(str))]
        dfmix = pd.DataFrame()
        dfprof = pd.DataFrame()
        for prodid in dfi.index:
            dfm, dfp = load_tab_file(prodid)
            dfmix = dfmix.append(_shrink_df(dfm))
            dfprof = dfprof.append(_shrink_df(dfp))
        _append_mix_dframe(dfmix)
        _append_prof_df(dfprof)
