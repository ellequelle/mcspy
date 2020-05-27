from datetime import datetime
import numpy as np
import pandas as pd

try:
    from astropy.time import Time

    _useastropy = True
except Exception:
    _useastropy = False

__all__ = ["myls2utc", "utc2myls"]

__doc__ = """
Adapted from JavaScript version by Aymeric Spiga(?)
https://github.com/aymeric-spiga
http://www-mars.lmd.jussieu.fr/mars/time/martian_time.html

There is a mean discrepency of about -0.088 (-0.106 to -0.068)
degrees in converting to and from MY, Ls. The bulk of this error
seems to be in the determination of MY, with up to 0.01 degrees
due to the Ls-sol conversion. The highest error is for
approximately 71 > Ls > 0.
With the fix turned on (_FIX=True), the discrepency is down to
RMS < 0.00071 degrees when running myls2utc(utc2myls(x)). This was
optimized by adjusting the parameters below. Use of astropy has
negligible impact on the discrepency.
"""

_FIX = True
_off2j = -0.099773362  # -0.03837437*2.6
_off2myls = -0.065236429  # -0.03837437*1.7
_perifix = 0.003


def myls2utc(MY, Ls):
    # 1. Get julian date
    jdate = myls2jd(MY, Ls)
    # 2. Convert to Earth Gregorian date
    return jd2utc(jdate, scale="utc")


def utc2myls(time, scale="utc"):
    jdate = utc2jd(time, scale)
    return jd2myls(jdate)


def sol2ls(sol):
    year_day = 668.6  # number of sols in a martian year
    peri_day = 485.35  # perihelion date
    e_ellip = 0.09340  # orbital ecentricity
    # 2*Pi*(1-Ls(perihelion)/360) Ls(perihelion) = 250.99
    timeperi = 1.90258341759902
    rad2deg = 180 / np.pi

    zz, zanom, zdx = 10, 10, 10

    # xref: mean anomaly, zx0: eccentric anomaly, zteta: true anomaly

    zz = (sol - peri_day) / year_day
    zanom = 2 * np.pi * (zz - np.round(zz))
    xref = np.abs(zanom)

    # Solve Kepler equation zx0 - e *sin(zx0) = xref
    # Using Newton iterations
    zx0 = xref + e_ellip * np.sin(xref)
    if isscalar(sol):
        while np.abs(zdx) >= 1e-9:
            zdx = -(zx0 - e_ellip * np.sin(zx0) - xref) / (1.0 - e_ellip * np.cos(zx0))
            zx0 = zx0 + zdx
    else:
        lx = np.abs(zdx) >= 1e-9
        while np.any(lx):
            zdx = -(zx0 - e_ellip * np.sin(zx0) - xref) / (1.0 - e_ellip * np.cos(zx0))
            zx0 = zx0 + zdx
            lx = np.abs(zdx) >= 1e-9
    lx = zanom < 0
    if np.any(lx):
        zx0 = np.where(lx, -zx0, zx0)

    # Compute true anomaly zteta, now that eccentric anomaly zx0 is known
    zteta = 2 * np.arctan(
        np.sqrt((1.0 + e_ellip) / (1.0 - e_ellip)) * np.tan(zx0 / 2.0)
    )

    # compute Ls
    Ls = zteta - timeperi
    Ls = np.where(Ls < 0, Ls + 2 * np.pi, Ls)
    Ls = np.where(Ls > 2 * np.pi, Ls - 2 * np.pi, Ls)
    # if Ls < 0:
    #    Ls = Ls + 2*np.pi
    # if Ls > 2*np.pi:
    #    Ls = Ls - 2*np.pi

    # convert Ls into degrees
    Ls = rad2deg * Ls

    return Ls


def utc2jd(time, scale="utc"):
    """
    Only works with arrays if using astropy.
    """
    if _useastropy:
        try:
            return Time(time, scale=scale).jd
        except Exception:
            if isinstance(time, tuple):
                return Time(
                    dict(
                        zip(
                            ("year", "month", "day", "hour", "minute", "second",), time,
                        )
                    ),
                    format="ymdhms",
                    scale=scale,
                ).jd
            else:
                return Time(pd.to_datetime(time), scale=scale).jd

    if (
        isinstance(time, tuple)
        or isinstance(time, list)
        or isinstance(time, np.ndarray)
    ):
        d = dict(
            zip(
                ("year", "month", "day", "hour", "minute", "second", "microsecond",),
                time,
            )
        )
        if "second" in d:
            if not d["second"].is_integer():
                d["microsecond"] = d["second"] / 1e6
                d["second"] = int(d["second"])
        d = {k: int(v) for k, v in d.items() if k != "microsecond"}
        time = datetime(**d)

    jdate = pd.to_datetime(time).to_julian_date()

    return jdate


def jd2myls(jdate):
    # Convert a Julian date to corresponding "sol" and "Ls"
    jdate_ref = 2.442765667e6  # 19/12/1975 4:00:00, such that Ls=0
    # jdate_ref is also the begining of Martian Year "12"
    MY_ref = 12
    earthday = 86400
    marsday = 88775.245
    marsyear = 668.60  # number of sols in a martian year

    jdate = _tovec(jdate)

    # try shifting so error is centered on zero
    if _FIX:
        jdate = jdate - _off2myls

    """
    # calculations from GISS mars24 docs
    # https://www.giss.nasa.gov/tools/mars24/help/algorithm.html
    ## j2000 date
    # Julian centuries since 12:00 Jan 1, 2000 (UT)
    T = (utc.jd - 2451545)/36525
    if utc < datetime(1970,1,1):
        # (TT - UTC)
        dtt_utcjd = 64.184 + 59*T - 51.2*T**2 - 67.1*T**3 - 16.4*T**4
    else:
        df = load_leapsec(jdate-2400000.5, 'MJD')
    TT = utc.jd + dtt_utcjd # terrestrial time
    jdtt = utc.jd + dtt_utcjd/86400 # julian date (TT)
    dtj2000 = jdtt - 2451545 # days since J2000

    ## mars position
    M = np.mod(19.3871 + 0.52402073*dtj2000, 360) # mean anomaly
    # angle of fictitious mean sun
    alpha_FMS = np.mod(270.3871 + 0.524038496*dtj2000, 360)
    x = 0.985626*dtj2000
    PBS = (0.0071*cos(np.deg2rad(x/2.2353 + 49.409)) # perturbers
            + 0.0057*np.cos(np.deg2rad(x/2.7543 + 168.173))
            + 0.0039*np.cos(np.deg2rad(x/1.1177 + 191.837))
            + 0.0037*np.cos(np.deg2rad(x/15.7866 + 21.736))
            + 0.0021*np.cos(np.deg2rad(x/2.1354 + 15.704))
            + 0.002*np.cos(np.deg2rad(x/2.4694 + 95.528)))
    Mrad = np.deg2rad(M)
    eoc = ((10.691 + 3e-7*dtj2000)*np.sin(Mrad)
            + 0.623*np.sin(2*Mrad) # equation of center
            + 0.050*np.sin(3*Mrad) + 0.005*np.sin(4*Mrad)
            + 0.0005*np.sin(5*Mrad) + PBS)
    Ls = alpha_FMS + eoc # solar longitude
    Lsrad = np.deg2rad(Ls) # solar longitude

    ## time on mars
    #EOT = 2.861*np.sin(2*Lsrad) - 0.071*np.sin(4*Lsrad)
    #      + 0.002*np.sin(6*Lsrad) - eoc
    # time at mars prime meridian
    #MST = np.mod(24*(((jdtt - 2451549.5)/1.0274912517)
    #             + 44796 - 0.0009626), 24)
    #LMST = np.mod(MST - lon/15, 24) # local mean solar time
    #TST = MST + EOT/15 # true solar time
    #LTST = LMST + EOT/15 # local true solar time
    #subsolar_lon = MST*15 + EOT + 180 # subsolar longitude
    """

    # Start by converting given date to Julian date
    # jdate = utc2jd()

    sol = (jdate - jdate_ref) * earthday / marsday

    MY = MY_ref
    # Compute Martian Year #, along with sol value
    # sol being computed modulo the number of sols in a martian year
    if isscalar(jdate):
        while sol >= marsyear:
            sol = sol - marsyear
            MY = MY + 1
        while sol < 0.0:
            sol = sol + marsyear
            MY = MY - 1
    else:
        lx = sol >= marsyear
        while np.any(lx):  # sol >= marsyear:
            sol = np.where(lx, sol - marsyear, sol)
            MY = np.where(lx, MY + 1, MY)
            lx = sol >= marsyear
        lx = sol < 0.0
        while np.any(lx):  # sol < 0.0:
            sol = np.where(lx, sol + marsyear, sol)
            MY = np.where(lx, MY - 1, MY)
            lx = sol < 0.0

    # convert sol number to Ls
    # sols_per_MY = 668.6 # number of sols in a martian year
    # Ls = sol/sols_per_MY*360
    Ls = sol2ls(sol)

    return MY, Ls


def myls2jd(MY, Ls, return_type="float"):
    """The argument return_type only matters if using astropy."""
    _rta = ["float", "astropy"]
    if return_type.lower() not in _rta:
        ValueError(f"return_type can be one of {_rta}.")

    MY, Ls = _tovec(MY, Ls)

    sols_per_MY = 668.6  # number of sols in a martian year
    sec_per_sol = 88775.245  # sol length, in seconds
    sec_per_day = 86400  # Earth day length, in seconds
    # day_per_year = 365.2422 # number of earth days in an earth year
    ref_MY = 26
    # Julian date for April 18.7 2002, Ls = 0, beginning of Mars Year 26
    ref_jdate = 2452383.23

    # 1. Find julian date for the (beginning of) chose Mars Year
    jdate = (MY - ref_MY) * (sols_per_MY * (sec_per_sol / sec_per_day)) + ref_jdate

    # 2. Find the number of martian sols corresponding to
    #    sought Solar Longitude
    # sol = Ls/360*sols_per_MY
    sol = ls2sol(Ls)

    # small fix for Ls = 0, we get sol = 668.59987 instead of sol~0
    # lx = sol >= 668.59
    # if np.any(lx):
    #    sol = np.where(lx, sol + 0.01 - sols_per_MY, sol)
    #    #sol[lx] = sol[lx] + 0.01 - sols_per_MY

    # 3. Add up these sols to get julian date
    jdate = jdate + sol * (sec_per_sol / sec_per_day)

    # try shifting so error is centered on zero
    if _FIX:
        jdate = jdate - _off2j

    if return_type == "astropy":
        if not _useastropy:
            raise ValueError("Astropy is not available")
        return Time(jdate, format="jd", scale="utc")

    return jdate


def ls2sol(Ls):
    sols_per_MY = 668.6  # number of sols in a martian year
    peri_day = 485.35  # perihelion date (in sols)
    e_ellip = 0.09340  # orbital ecentricity
    peri_day = 485.35  # perihelion date (in sols)
    # 2*Pi*(1-Ls(perihelion)/360) Ls(perihelion) = 250.99
    timeperi = 1.90258341759902
    rad2deg = 180 / np.pi

    zteta = np.array(Ls) / rad2deg + timeperi  # true anomaly
    zx0 = 2.0 * np.arctan(
        np.tan(0.5 * zteta) / np.sqrt((1.0 + e_ellip) / (1.0 - e_ellip))
    )  # eccentric anomaly
    xref = zx0 - e_ellip * np.sin(zx0)  # xref: mean anomaly

    sol = (xref / (2.0 * np.pi)) * sols_per_MY + peri_day

    # small fix for Ls = 0, we get sol = 668.59987 instead of sol~0
    lx = sol >= 668.59
    if np.any(lx):
        if _FIX:
            sol = np.where(lx, sol + _perifix - sols_per_MY, sol)
        else:
            sol = np.where(lx, sol + 0.01 - sols_per_MY, sol)
        # sol[lx] = sol[lx] + 0.01 - sols_per_MY

    return sol


def jd2utc(jdate, scale="utc"):
    if _useastropy:
        return Time(jdate, format="jd", scale=scale).ymdhms

    # convert julian date to gregorian date
    ijj = np.floor(jdate + 0.5)
    iss = np.floor((4 * ijj - 6884477) / 146097)
    ir3 = ijj - np.floor((146097 * iss + 6884480) / 4)
    iap = np.floor((4 * ir3 + 3) / 1461)
    ir2 = ir3 - np.floor(1461 * iap / 4)
    imp = np.floor((5 * ir2 + 461) / 153)
    ir1 = ir2 - np.floor((153 * imp - 457) / 5)
    ij = ir1 + 1

    # if imp >= 13:
    #    imp = imp-12
    #    iap = iap+1
    iap = np.where(imp >= 13, iap + 1, iap)
    imp = np.where(imp >= 13, imp - 12, imp)

    year = iap + 100 * iss
    month = imp
    day = ij

    try:
        from logging import warning

        warning("Values for hour, minute, and second are untested.")
    except Exception:
        pass
    # experimental, untested
    rr = (jdate - ijj) * 24 + 12
    hour = np.floor(rr)
    mm = (rr - hour) * 60
    minute = np.floor(mm)
    second = (mm - minute) * 60

    return year, month, day, hour, minute, second


def _test_myls_utc(nt=500, plot=True, seed=None):
    myls2ls = lambda x: (np.array(x) * [[360], [1]]).sum(axis=0)  # NOQA
    tests = np.stack(
        (np.random.randint(0, 45, nt), np.random.random(nt) * 360), axis=0,
    )
    if _useastropy:
        utc = myls2utc(*tests)
        results = np.array(utc2myls(utc))
    else:
        utc = myls2utc(*tests)
        results = np.array([utc2myls(j) for j in np.transpose(utc)]).transpose()
    diffs = myls2ls(results - tests)
    diffs[diffs > 5] = diffs[diffs > 5] - 360
    diffs[diffs < -5] = 360 + diffs[diffs < -5]
    if plot:
        from matplotlib import pyplot as plt

        plt.scatter(tests[1, :], tests[0, :], c=diffs, marker=".")
        plt.colorbar(label=r"$\Delta$L$_s$")
        plt.xlabel(r"L$_s$")
        plt.ylabel("MY")

        plt.figure()
        plt.scatter(tests[1, :], diffs, c=tests[0, :], marker=".")
        plt.colorbar(label="MY")
        plt.xlabel(r"L$_s$")
        plt.ylabel(r"$\Delta$L$_s$")
        plt.show()

    return tests, utc, diffs, results


def isscalar(x):
    return not hasattr(x, "__len__")


def _tovec(*args):
    def doit(x):
        if isscalar(x) or not isinstance(x, np.ndarray):
            return np.array(x)
        return x

    if len(args) == 1:
        return doit(args[0])
    args = list(args)
    for ix in range(len(args)):
        args[ix] = doit(args[ix])
    return tuple(args)


def load_leapsec(date=None, index="date"):
    import io

    def format_lstable(lines):
        import re

        lls = []
        for ll in lines:
            try:
                ll = ll.strip()
                lls.append(
                    re.sub(
                        r"(\d+)\s+(\d+)\s+(\d{4})",
                        lambda x: "{}-{}-{}".format(*x.groups()),
                        ll,
                    )
                )
            except Exception:
                lls.append(ll)
        return "\n".join(lls)

    def check_expired(lines, date):
        try:
            for ll in lines:
                if "expire" in ll:
                    break
            ix = ll.index("on") + 3
            texp = pd.to_datetime(ll[ix:])
            if texp < datetime.now() or texp < date:
                import requests

                lsurl = "https://hpiers.obspm.fr/iers/bul/bulc/" + "Leap_Second.dat"
                print(
                    "Leapsecond table is outdated, attempting to "
                    + "fetch new table..."
                )
                print(lsurl)
                req = requests.get(lsurl)
                lines = req.text.split("\n")
        except Exception as e:
            print("Error: " + str(e))
        return lines

    if date is None:
        date = datetime.now()
    else:
        date = pd.to_datetime(date)
    lines = check_expired(leapsec.split("\n"), date)
    lines = format_lstable(lines)
    buf = io.StringIO(lines)
    df = pd.read_table(
        buf,
        skiprows=14,
        header=None,
        names=["MJD", "date", "tai_utc"],
        sep=r"\s+",
        infer_datetime_format=True,
    )
    buf.close()

    df["date"] = pd.to_datetime(df["date"], dayfirst=True)
    df = df.set_index(index)
    try:
        return df.reindex(pd.to_datetime(date), method="ffill")
    except Exception:
        pass
    return df.reindex(pd.to_datetime([date]), method="ffill")


leapsec = """#  Value of TAI-UTC in second valid beetween the initial value until
#  the epoch given on the next line. The last line reads that NO
#  leap second was introduced since the corresponding date
#  Updated through IERS Bulletin 59 issued in January 2020
#
#
#  File expires on 28 December 2020
#
#
#    MJD        Date        TAI-UTC (s)
#           day month year
#    ---    --------------   ------
#
41317.0    1  1 1972       10
41499.0    1  7 1972       11
41683.0    1  1 1973       12
42048.0    1  1 1974       13
42413.0    1  1 1975       14
42778.0    1  1 1976       15
43144.0    1  1 1977       16
43509.0    1  1 1978       17
43874.0    1  1 1979       18
44239.0    1  1 1980       19
44786.0    1  7 1981       20
45151.0    1  7 1982       21
45516.0    1  7 1983       22
46247.0    1  7 1985       23
47161.0    1  1 1988       24
47892.0    1  1 1990       25
48257.0    1  1 1991       26
48804.0    1  7 1992       27
49169.0    1  7 1993       28
49534.0    1  7 1994       29
50083.0    1  1 1996       30
50630.0    1  7 1997       31
51179.0    1  1 1999       32
53736.0    1  1 2006       33
54832.0    1  1 2009       34
56109.0    1  7 2012       35
57204.0    1  7 2015       36
57754.0    1  1 2017       37
"""
