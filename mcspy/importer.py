__package__ = 'mcspy'
import gzip
from os import makedirs
from os.path import exists, dirname
import numpy as np
import pandas as pd
from .loaders import load_mix_var, load_prof_var, load_mix_dframe
from .util import local_data_path, addext
from .parsing import load_tab_file
from .defs import mix_cols, prof_cols

__all__ = ['collect_yearly_vars', ]
_others = ['save_prof_var', '_append_mix_dframe', 'save_mix_dframe', 'save_mix_var', 'save_prof_df', '_append_prof_var', '_append_mix_var', '_append_prof_df']

def save_prof_var(var, year, varname):
    '''Writes the profile data variable `varname` from `year`, passed in the numpy array `var` to the numpy array file "{year}/profdata/{year}_{varname}_profiles.npy".'''
    fname = local_data_path(f'DATA/{year}/profdata/{year}_{varname}_profiles.npy')
    if not exists(dirname(fname)):
        makedirs(dirname(fname))
    with gzip.open(fname, 'wb') as fout:
        np.save(fout, var, False)
    print(f'wrote {fname}')

def _append_mix_dframe(mix):
    '''Append new rows onto an existing saved metadata index DataFrame.'''
    year = mix['datetime'].dt.year.unique()
    if year.size > 1:
        raise ValueError('append_mix_drame only works for data from a single year')
    year = year[0]
    df = pd.DataFrame()
    _append_mix_dfvars(mix) # save as individual arrays
    fn = local_data_path(f'DATA/{year}/indexdata/{year}_mixvars')
    if exists(addext(fn, '.npz')) and exists(addext(fn, '.csv.gz')):
        df = load_mix_dframe(year)
    else:
        df = pd.DataFrame()
    save_mix_dframe(df.append(mix, verify_integrity=True))

def save_mix_var(var, year, varname):
    '''Writes a metadata index variable for `varname` from `year` as a numpy array to the numpy array file "{year}/indexdata/{year}_{varname}_index.npy".'''
    fname = local_data_path(f'DATA/{year}/indexdata/{year}_{varname}_index.npy')
    if varname in ['datetime']:
        var = var.astype(int)
    if not exists(dirname(fname)):
        makedirs(dirname(fname))
    with gzip.open(fname, 'wb') as fout:
        np.save(fout, var, False)
    print(f'wrote {fname}')

def save_mix_dframe(mix):
    '''Save a metadata index DataFrame to a numpy file (numeric data) and a csv file (non-numeric data). This function saves one DataFrame per earth year.'''
    mix = mix.copy()
    mix = mix.reset_index()
    year = mix['profid'].str.slice(None, 4).iloc[0]
    fn = local_data_path(f'DATA/{year}/indexdata/{year}_mixvars')
    # drop product ID
    if 'prodid' in mix:
        mix = mix.drop(columns=['prodid'])
    fname = addext(fn, '.csv.gz')
    # write profile ID column to a compressed csv file
    mix.pop('profid').to_csv(fname, index=None, header=True)
    print(f'saved {fname}')
    # interpret datetime columns as 64-bit integers
    # save numeric data columns as a 2-D numpy array
    for cc in ['datetime']:
        mix[cc] = mix[cc].astype(int)
    np.savez_compressed(fn, **{n:mix[n].to_numpy() for n in mix.columns})
    #fname = addext(fn, '.npy')
    #np.save(fname, mix[mix_cols].values, False)
    print(f'saved {fname}, {mix.shape}')

def save_prof_df(dfprof):
    year = dfprof['profid'].str.slice(None, 4).iloc[0]
    for vv in prof_cols:
        if vv in dfprof:
            save_prof_var(dfprof[vv].to_numpy(), year, vv)

def _append_prof_var(var, year, varname):
    '''Append profile data passed in `var` for the variable `varname` and year `year` to a numpy array file. If the file does not exist, create it.'''
    dat = var.reshape((-1,105))
    fname = local_data_path(f'DATA/{year}/profdata/{year}_{varname}_profiles.npy')
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
        print(f'prof {varname}, {year}, {oldvar.shape}')

def _append_mix_var(var, year, varname):
    '''Append metadata data passed in `var` for the metadata variable `varname` and year `year` to a numpy array file. If the file does not exist, create it.'''
    dat = var
    fname = local_data_path(f'DATA/{year}/indexdata/{year}_{varname}_index.npy')
    # check whether file exists
    if not exists(fname):
        save_mix_var(var, year, varname)
    else:
        # concatenate new and existing data arrays
        oldvar = load_mix_var(year, varname)
        oldvar = np.concatenate((oldvar, dat))
        # save concatenated arrays to the file
        save_mix_var(oldvar, year, varname)
        print(f'mix {varname}, {year}, {oldvar.shape}')

def _append_mix_dfvars(df):
    year = df['datetime'].dt.year.unique()
    year = year[0]
    for vv in mix_cols:
        if vv in df:
            _append_mix_var(df[vv].to_numpy(), year, vv)

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

def collect_yearly_vars(dfindex, MIX=True, PROF=True):
    '''Read the MCS TAB data files and save the metadata and profile data to binary files to be easily read in the future.
    This function creates yearly .npy array files with each file containing the data for one variable for the whole year. If TAB files are not found locally, it will attempt to download them from the PDS. 

This appends TAB files onto any data in already existing .npy or .csv.gz files, and so this function should only be run once when first assembling the binary files.

    Parameters
    ----------
    dfindex : DataFrame from the PDS index file loaded by `reload_index`. 
    '''
    # read max 10 days at a time between saves
    # loading files gets slower as the dataframes increase in size
    ymms = (dfindex.start_time.dt.year*1000
                + dfindex.start_time.dt.month*10
                + dfindex.start_time.dt.day//10).unique()
    for ym in ymms:
        dfi = dfindex.loc[dfindex.index.str.startswith(ym.astype(str))]
        if MIX:
            dfmix = pd.DataFrame()
        if PROF:
            dfprof = pd.DataFrame()
        for prodid in dfi.index:
            dfm, dfp = load_tab_file(prodid, dfindex)
            xpt = [prodid]
            if MIX:
                dfmix = dfmix.append(_shrink_df(dfm), verify_integrity=True)
                xpt += [dfmix.index.nunique()]
            if PROF:
                dfprof = dfprof.append(_shrink_df(dfp),
                                verify_integrity=True)
                xpt += [dfprof.index.nunique()]
            print(*xpt)
        if MIX:
            _append_mix_dframe(dfmix)
        if PROF:
            _append_prof_df(dfprof)
