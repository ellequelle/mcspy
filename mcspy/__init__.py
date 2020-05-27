__name__ = "mcspy"
__package__ = "mcspy"

from .indexing import (
    dfindex,
    lxLsN,
    lxday,
    lximg,
    lxtempe,
    reload_index,
)
from .defs import (
    MCS_DATA_PATH,
    qday,
    qnight,
    qtempe,
    qmarci_mdgm,
    qgds_MY28,
    qgds_MY34,
    lxgds_MY28,
    lxgds_MY34,
    lxday,
    lxgds,
    lxregion,
    lxtempe,
    lxmarci_mdgm,
)
from .loaders import (
    load_H2Oice,
    load_mix_dframe,
    load_mix_dframe_years,
    load_mix_var,
    load_mix_var_years,
    load_H2Oice_err,
    load_H2Ovap,
    load_H2Ovap_err,
    load_altitude,
    load_dust,
    load_dust_err,
    load_prof_var,
    load_prof_var_years,
    load_pressure,
    load_temperature,
    load_temperature_err,
    load_Ls,
    load_SZA,
    load_MY,
    load_LST,
    load_lat,
    load_lon,
)
from .parsing import parse_tab_file, load_tab_file
from .util import mcs_tab_path, calc_Ls2
from .calc import (
    potential_temperature,
    profdiff,
    nan2val,
    inf2nan,
    logmean,
    logstd,
    logvar,
)

"""
mcspy is for working with data from the [Mars Climate Sounder](https://mars.nasa.gov/mro/mission/instruments/mcs/), an instrument aboard the NASA [Mars Reconnaisance Orbiter](https://mars.nasa.gov/mro/mission/overview/).

MCS data is publicly available on the [Planetary Data System (PDS) Atmospheres node](https://pds-atmospheres.nmsu.edu) in the form of thousands of separate text files. Each text file has several hundred retrieved profiles, typically from two orbits around Mars. All of the metadata is in the same files as the profile data, meaning that in order to find profiles at a specific location or time, it is necessary to read many text files.

Working with the data in this form is inefficient, so mcspy makes it easy to download data from a range of dates, and then save the metadata and the profiles in binary numpy array files.

"""
