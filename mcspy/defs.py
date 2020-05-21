__package__ = "mcspy"

from os import getenv
from os.path import exists
from collections import OrderedDict
from configparser import ConfigParser

__all__ = [
    "qday",
    "qregion",
    "qtempe",
    "qimg",
    "qmarci_mdgm",
    "MCS_DATA_PATH",
    "header_columns",
    "index_columns",
    "_index_keep_columns",
    "data_columns",
    "mix_keep_cols",
    "mix_cols",
    "prof_cols",
    "set_config",
]


# query strings
qday = "solar_zen < 90"
qnight = "LST <= 0.4"
qregion = "lat < 50 & lat > 30 & lon > -91 & lon < -60"
qtempe = "lat < 47.8 & lat > 43 & lon > -83.3 & lon < -70"
qimg = "lat < 70 & lat > 20 & lon > -125 & lon < -60"
qmarci_mdgm = 'start_time < "2010-07-01" & start_time > "2006-11-08"'
qgds_MY28 = "Ls > 269 & Ls < 300 & MY == 28"


# default configureation for config file ~/.mcspy
_default_config = {
    "mcs_data_path": getenv("HOME") + "/mcsdata",
    "most_recent_known_mrom": "MROM_2158",
}

MCS_DATA_PATH = None


def set_config(key, value):
    config = ConfigParser(defaults=_default_config)
    config.read(getenv("HOME") + "/.mcspy")
    config.set("DEFAULT", key, value)
    with open(getenv("HOME") + "/.mcspy", "w") as fout:
        config.write(fout)


# load cfg file
if exists(getenv("HOME") + "/.mcspy"):
    config = ConfigParser(defaults=_default_config)
    config.read(getenv("HOME") + "/.mcspy")
else:
    MCS_DATA_PATH = getenv("HOME") + "/mcsdata/"
    config = ConfigParser(defaults=_default_config)
    with open(getenv("HOME") + "/.mcspy", "w") as fout:
        config.write(fout)

MCS_DATA_PATH = config["DEFAULT"]["mcs_data_path"]

if not MCS_DATA_PATH.endswith("/"):
    MCS_DATA_PATH = MCS_DATA_PATH + "/"
_most_recent_known_mrom = config["DEFAULT"]["most_recent_known_mrom"]


header_columns = [
    "1",
    "date",
    "UTC",
    "SCLK",
    "Ls",
    "solar_dist",
    "orb_num",
    "Gqual",
    "solar_lat",
    "solar_lon",
    "solar_zen",
    "LST",
    "lat",
    "lon",
    "profile_rad",
    "profile_alt",
    "limb_ang",
    "are_rad",
    "surf_lat",
    "surf_lon",
    "surf_rad",
    "T_surf",
    "T_surf_err",
    "T_near_surf",
    "T_near_surf_err",
    "dust_column",
    "Dust_column_err",
    "H2Ovap_column",
    "H2Ovap_column_err",
    "H2Oice_column",
    "H2Oice_column_err",
    "CO2ice_column",
    "CO2ice_column_err",
    "p_surf",
    "p_surf_err",
    "p_ret_alt",
    "p_ret",
    "p_ret_err",
    "Rqual",
    "P_qual",
    "T_qual",
    "dust_qual",
    "H2Ovap_qual",
    "H2Oice_qual",
    "CO2ice_qual",
    "surf_qual",
    "obs_qual",
    "ref_sclk_0",
    "ref_sclk_1",
    "ref_sclk_2",
    "ref_sclk_3",
    "ref_sclk_4",
    "ref_sclk_5",
    "ref_sclk_6",
    "ref_sclk_7",
    "ref_sclk_8",
    "ref_sclk_9",
    "ref_date_0",
    "ref_utc_0",
    "ref_date_1",
    "ref_utc_1",
    "ref_date_2",
    "ref_utc_2",
    "ref_date_3",
    "ref_utc_3",
    "ref_date_4",
    "ref_utc_4",
    "ref_date_5",
    "ref_utc_5",
    "ref_date_6",
    "ref_utc_6",
    "ref_date_7",
    "ref_utc_7",
    "ref_date_8",
    "ref_utc_8",
    "ref_date_9",
    "ref_utc_9",
]

index_columns = [
    "volume_id",
    "path",
    "filename",
    "product_creation_time",
    "start_time",
    "stop_time",
    "spacecraft_clock_start_count",
    "spacecraft_clock_stop_count",
    "start_orbit_number",
    "stop_orbit_number",
]

_index_keep_columns = [
    "volume_id",
    "path",
    "filename",
    "start_time",
    "stop_time",
    "start_orbit_number",
    "stop_orbit_number",
]

data_columns = [
    "1",
    "pressure",
    "temperature",
    "T_err",
    "dust",
    "dust_err",
    "H2Ovap",
    "H2Ovap_err",
    "H2Oice",
    "H2Oice_err",
    "CO2ice",
    "CO2ice_err",
    "altitude",
    "lat",
    "lon",
]

mix_tab_ref_dt_cols = [
    "ref_date_0",
    "ref_utc_0",
    "ref_date_1",
    "ref_utc_1",
    "ref_date_2",
    "ref_utc_2",
    "ref_date_3",
    "ref_utc_3",
    "ref_date_4",
    "ref_utc_4",
    "ref_date_5",
    "ref_utc_5",
    "ref_date_6",
    "ref_utc_6",
    "ref_date_7",
    "ref_utc_7",
    "ref_date_8",
    "ref_utc_8",
    "ref_date_9",
    "ref_utc_9",
]

mix_tab_ref_sclk_cols = [
    "ref_sclk_0",
    "ref_sclk_1",
    "ref_sclk_2",
    "ref_sclk_3",
    "ref_sclk_4",
    "ref_sclk_5",
    "ref_sclk_6",
    "ref_sclk_7",
    "ref_sclk_8",
    "ref_sclk_9",
]

mix_tab_int_cols = [
    "orb_num",
    "Gqual",
    "Rqual",
    "P_qual",
    "T_qual",
    "dust_qual",
    "H2Ovap_qual",
    "H2Oice_qual",
    "CO2ice_qual",
    "surf_qual",
    "obs_qual",
]

mix_tab_real_cols = [
    "SCLK",
    "Ls",
    "solar_dist",
    "solar_lat",
    "solar_lon",
    "solar_zen",
    "LST",
    "lat",
    "lon",
    "profile_rad",
    "profile_alt",
    "limb_ang",
    "are_rad",
    "surf_lat",
    "surf_lon",
    "surf_rad",
    "T_surf",
    "T_surf_err",
    "T_near_surf",
    "T_near_surf_err",
    "dust_column",
    "Dust_column_err",
    "H2Ovap_column",
    "H2Ovap_column_err",
    "H2Oice_column",
    "H2Oice_column_err",
    "CO2ice_column",
    "CO2ice_column_err",
    "p_surf",
    "p_surf_err",
    "p_ret_alt",
    "p_ret",
    "p_ret_err",
] + mix_tab_ref_sclk_cols

mix_tab_dtypes = dict()
mix_tab_dtypes.update({n: "int" for n in mix_tab_int_cols})
mix_tab_dtypes.update({n: "float" for n in mix_tab_real_cols})

mix_date_col_lookup = {
    "datetime": ["date", "UTC"],
    "ref_datetime_0": ["ref_date_0", "ref_utc_0"],
    "ref_datetime_1": ["ref_date_1", "ref_utc_1"],
    "ref_datetime_2": ["ref_date_2", "ref_utc_2"],
    "ref_datetime_3": ["ref_date_3", "ref_utc_3"],
    "ref_datetime_4": ["ref_date_4", "ref_utc_4"],
    "ref_datetime_5": ["ref_date_5", "ref_utc_5"],
    "ref_datetime_6": ["ref_date_6", "ref_utc_6"],
    "ref_datetime_7": ["ref_date_7", "ref_utc_7"],
    "ref_datetime_8": ["ref_date_8", "ref_utc_8"],
    "ref_datetime_9": ["ref_date_9", "ref_utc_9"],
}

mix_date_cols = (
    ["date", "datetime"]
    + mix_tab_ref_dt_cols[0::2]
    + list(mix_date_col_lookup.keys())
)

mix_time_cols = ["UTC"] + mix_tab_ref_dt_cols[1::2]
mix_new_cols = ["datetime", "MY"]

mix_data_cols = [
    "date",
    "UTC",
    "SCLK",
    "Ls",
    "solar_dist",
    "orb_num",
    "solar_lat",
    "solar_lon",
    "solar_zen",
    "LST",
    "lat",
    "lon",
    "profile_rad",
    "profile_alt",
    "limb_ang",
    "are_rad",
    "surf_lat",
    "surf_lon",
    "surf_rad",
    "T_surf",
    "T_surf_err",
    "T_near_surf",
    "T_near_surf_err",
    "dust_column",
    "Dust_column_err",
    "H2Ovap_column",
    "H2Ovap_column_err",
    "H2Oice_column",
    "H2Oice_column_err",
    "CO2ice_column",
    "CO2ice_column_err",
    "p_surf",
    "p_surf_err",
    "p_ret_alt",
    "p_ret",
    "p_ret_err",
]

mix_qual_cols = [
    "Rqual",
    "P_qual",
    "T_qual",
    "dust_qual",
    "H2Ovap_qual",
    "H2Oice_qual",
    "CO2ice_qual",
    "surf_qual",
    "obs_qual",
    "Gqual",
]

mix_use_cols = [
    "datetime",
    "MY",
    "SCLK",
    "Ls",
    "solar_dist",
    "orb_num",
    "solar_lat",
    "solar_lon",
    "solar_zen",
    "LST",
    "lat",
    "lon",
    "profile_rad",
    "profile_alt",
    "limb_ang",
    "are_rad",
    "surf_lat",
    "surf_lon",
    "surf_rad",
    "T_surf",
    "T_surf_err",
    "T_near_surf",
    "T_near_surf_err",
    "dust_column",
    "Dust_column_err",
    "H2Ovap_column",
    "H2Ovap_column_err",
    "H2Oice_column",
    "H2Oice_column_err",
    "CO2ice_column",
    "CO2ice_column_err",
    "p_surf",
    "p_surf_err",
    "p_ret_alt",
    "p_ret",
    "p_ret_err",
] + mix_qual_cols

mix_keep_cols = mix_use_cols
mix_cols = mix_use_cols + ['profidint']

prof_cols = [
    "temperature",
    "T_err",
    "dust",
    "dust_err",
    "H2Oice",
    "H2Oice_err",
    "altitude",
    "lat",
    "lon",
    "rowidint",
]

mix_descriptions = dict(
    rad_qual_description=OrderedDict(((None, "Radiance Quality Flag"),)),
    p_qual_description=OrderedDict(
        (
            (None, "Pressure retrieval quality flag."),
            (0, "0 = successful pressure retrieval."),
            (
                9,
                (
                    "9 = pressure not retrieved, pressure scale is based "
                    + "on climatological surface pressure."
                ),
            ),
        )
    ),
    T_qual_description=OrderedDict(
        (
            (None, "Vertical extent of the temperature retrieval."),
            (
                0,
                (
                    "0 = successful limb and nadir retrieval (coverage "
                    + "to the surface)."
                ),
            ),
            (
                1,
                (
                    "1 = successful limb and surface retrieval (no near "
                    + "surface atmosphere)."
                ),
            ),
            (
                2,
                (
                    "2 = successful limb retrieval (no surface or near "
                    + "surface atmosphere)."
                ),
            ),
            (
                3,
                (
                    "3 = truncated limb retrieval (profile stops well above "
                    + "the surface)."
                ),
            ),
        )
    ),
    dust_qual_description=OrderedDict(
        (
            (None, "Vertical extent of the dust retrieval."),
            (2, "2 = successful limb retrieval (full dust profile)."),
            (
                3,
                (
                    "3 = truncated limb retrieval (profile stops well above "
                    + "the surface)."
                ),
            ),
            (9, "9 = dust not retrieved."),
        )
    ),
    H2Ovap_qual_description=OrderedDict(
        (
            (None, "Water vapor retrieval quality flag."),
            (9, "9 = not retrieved."),
        )
    ),
    H2Oice_qual_description=OrderedDict(
        (
            (None, "Vertical extent of the water ice retrieval."),
            (2, "2 = successful limb retrieval (full water ice profile).",),
            (
                3,
                (
                    "3 = truncated limb retrieval (profile stops well above "
                    + "the surface)."
                ),
            ),
            (9, "9 = water ice not retrieved."),
        )
    ),
    CO2ice_qual_description=OrderedDict(
        ((None, "CO2 ice retrieval quality flag."), (9, "9 = not retrieved."),)
    ),
    surf_qual_description=OrderedDict(
        ((None, "Surface/near surface retrieval quality flag."),)
    ),
    obs_qual_description=OrderedDict(
        (
            (
                None,
                (
                    "Quality and viewing direction of the observations used "
                    + "for the retrieval."
                ),
            ),
            (
                0,
                (
                    "0 = Standard observations, forward in-track viewing (178 "
                    + "deg <= Azimuth <= 182 deg), retrieved in 1-D."
                ),
            ),
            (
                1,
                (
                    "1 = Limb staring observations (reduced calibration "
                    + "quality), forward in-track viewing (178 <= Azimuth "
                    + "<= 182 deg), retrieved in 1-D."
                ),
            ),
            (
                2,
                (
                    "2 = Standard observations, right forward off-track "
                    + "viewing (182 deg < Azimuth < 260 deg), retrieved "
                    + "in 1-D."
                ),
            ),
            (
                3,
                (
                    "3 = Standard observations, right cross-track viewing "
                    + "(260 deg <= Azimuth < 290 deg), retrieved in 1-D."
                ),
            ),
            (
                4,
                (
                    "4 = Standard observations, left forward off-track "
                    + "viewing (90 deg < Azimuth < 178 deg), retrieved in 1-D."
                ),
            ),
            (
                5,
                (
                    "5 = Standard observations, left cross-track "
                    + "viewing (Azimuth "
                    + "= 90 deg), retrieved in 1-D."
                ),
            ),
            (
                6,
                (
                    "6 = Standard observations, left aft off-track viewing (2 "
                    + "deg < Azimuth < 90 deg), retrieved in 1-D."
                ),
            ),
            (
                7,
                (
                    "7 = Standard observations, aft in-track viewing (-4 deg "
                    + "<= Azimuth <= 2 deg), retrieved in 1-D."
                ),
            ),
            (
                10,
                (
                    "10 = Standard observations, forward in-track viewing "
                    + "(178 deg <= Azimuth <= 182 deg), retrieved in 2-D."
                ),
            ),
            (
                11,
                (
                    "11 = Limb staring observations (reduced calibration "
                    + "quality), forward in-track viewing (178 <= Azimuth "
                    + "<= 182 deg), retrieved in 2-D."
                ),
            ),
            (
                17,
                (
                    "17 = Standard observations, aft in-track viewing (-4 "
                    + "deg <= Azimuth <= 2 deg), retrieved in 2-D."
                ),
            ),
        )
    ),
)
