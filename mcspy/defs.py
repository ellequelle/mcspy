__package__ = 'mcspy'
from os import getenv
from os.path import exists
from configparser import ConfigParser

__all__ = ['qday', 'qregion', 'qtempe', 'qimg', 'qmarci_mdgm',
 'MCS_DATA_PATH', 'PDS_ROOT_URL', 'header_columns', 'index_columns', 
 '_index_keep_columns', 'data_columns', 'mix_keep_cols',
    'mix_cols', 'prof_cols', 'set_config']


qday = 'LST > 0.4'
qnight = 'LST <= 0.4'
qregion = 'lat < 50 & lat > 30 & lon > -91 & lon < -60'
qtempe = 'lat < 47.8 & lat > 43 & lon > -83.3 & lon < -70'
qimg = 'lat < 70 & lat > 20 & lon > -125 & lon < -60'
qmarci_mdgm = 'start_time < "2010-07-01" & start_time > "2006-11-08"'

_default_config = ({
    'mcs_data_path':getenv('HOME')+'/mcsdata',
    'most_recent_known_mrom':'MROM_2158',
    })

def set_config(key, value):
    config = ConfigParser(defaults=_default_config)
    config.read(getenv('HOME')+'/.mcspy')
    config.set('DEFAULT', key, value)
    with open(getenv('HOME')+'/.mcspy', 'w') as fout:
        config.write(fout)

# load cfg file
if exists(getenv('HOME') + '/.mcspy'):
    config = ConfigParser(defaults=_default_config)
    config.read(getenv('HOME')+'/.mcspy')
else:
    MCS_DATA_PATH = getenv('HOME')+'/mcsdata'
    config = ConfigParser(defaults=_default_config)
    with open(getenv('HOME')+'/.mcspy', 'w') as fout:
        config.write(fout)
        
MCS_DATA_PATH = config['DEFAULT']['mcs_data_path']
_most_recent_known_mrom = config['DEFAULT']['most_recent_known_mrom']

header_columns = ['1', 'date', 'UTC', 'SCLK', 'Ls', 'Solar_dist',
    'Orb_num', 'Gqual', 'Solar_lat', 'Solar_lon', 'Solar_zen',
    'LST', 'lat', 'lon', 'Profile_rad', 'Profile_alt', 'Limb_ang',
    'Are_rad', 'Surf_lat', 'Surf_lon', 'Surf_rad', 'T_surf',
    'T_surf_err', 'T_near_surf', 'T_near_surf_err', 'Dust_column',
    'Dust_column_err', 'H2Ovap_column', 'H2Ovap_column_err',
    'H2Oice_column', 'H2Oice_column_err', 'CO2ice_column',
    'CO2ice_column_err', 'p_surf', 'p_surf_err', 'p_ret_alt',
    'p_ret', 'p_ret_err', 'Rqual', 'P_qual', 'T_qual', 'Dust_qual',
    'H2Ovap_qual', 'H2Oice_qual', 'CO2ice_qual', 'surf_qual',
    'Obs_qual', 'Ref_SCLK_0', 'Ref_SCLK_1', 'Ref_SCLK_2',
    'Ref_SCLK_3', 'Ref_SCLK_4', 'Ref_SCLK_5', 'Ref_SCLK_6',
    'Ref_SCLK_7', 'Ref_SCLK_8', 'Ref_SCLK_9', 'Ref_Date_0',
    'Ref_UTC_0', 'Ref_Date_1', 'Ref_UTC_1', 'Ref_Date_2',
    'Ref_UTC_2', 'Ref_Date_3', 'Ref_UTC_3', 'Ref_Date_4',
    'Ref_UTC_4', 'Ref_Date_5', 'Ref_UTC_5', 'Ref_Date_6',
    'Ref_UTC_6', 'Ref_Date_7', 'Ref_UTC_7', 'Ref_Date_8',
    'Ref_UTC_8', 'Ref_Date_9', 'Ref_UTC_9']
index_columns = ['volume_id', 'path', 'filename',
    'product_creation_time', 'start_time', 'stop_time',
    'spacecraft_clock_start_count', 'spacecraft_clock_stop_count',
    'start_orbit_number', 'stop_orbit_number']
_index_keep_columns = ['volume_id', 'path', 'filename',
    'start_time', 'stop_time', 'start_orbit_number',
    'stop_orbit_number']
data_columns = ['1', 'pressure', 'temperature', 'T_err', 'dust',
    'dust_err', 'H2Ovap', 'H2Ovap_err', 'H2Oice', 'H2Oice_err',
    'CO2ice', 'CO2ice_err', 'altitude', 'lat', 'lon']
mix_keep_cols = ['date', 'UTC', 'SCLK', 'Ls', 'Solar_dist',
    'Orb_num', 'LST', 'lat', 'lon', 'datetime', 'MY', 'cLs']
mix_cols = ['date', 'UTC', 'SCLK', 'Ls', 'Solar_dist',
    'Orb_num', 'LST', 'lat', 'lon', 'datetime', 'MY']
prof_cols = ['temperature', 'T_err', 'dust', 'dust_err',
    'H2Ovap', 'H2Ovap_err', 'H2Oice', 'H2Oice_err',
    'altitude', 'lat', 'lon']

