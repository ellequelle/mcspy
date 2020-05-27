import numpy as np

__all__ = [
    "potential_temperature",
    "profdiff",
    "profddz",
    "logmean",
    "logmedian",
    "logquantile",
    "logstd",
    "inf2nan",
]


def potential_temperature(prs, temp, p_ref=610):
    """
    Calculate potential temperature from pressure and temperature
    vectors with a reference pressure of `p_ref`.
    """
    # acc to eq (1) in Hinson et al. 2019
    pr = p_ref / prs
    theta = temp * pr ** (0.25)
    return theta


def nan2val(x, val):
    """
    Replace nans in an array `x` with the value `val`.
    """
    return np.where(np.isnan(x), val, x)


def inf2nan(x, val=np.nan):
    """
    Replace any inf values of array with np.nan or another
    specified value `val`.
    """
    return np.where(np.isinf(x), val, x)


def profdiff(var, axis=-1):
    """
    Find the first order difference of `var` along the axis `axis`.
    """
    dvar = np.diff(var, axis=axis)
    dvar = np.moveaxis(dvar, axis, -1)
    z = np.zeros(dvar.shape[:-1])[..., None] + np.nan
    dvar = np.concatenate((dvar, z), axis=-1)
    return np.moveaxis(dvar, -1, axis)


def profddz(altitude, var, axis=-1):
    """
    Find the derivative of `var` with respect to `altitude` along
    the axis `axis`.
    """
    # calculate the derivative
    dvar = np.diff(var, axis=axis)
    daltitude = np.diff(altitude, axis=axis)
    dtdz = dvar / daltitude
    # adtdz a block of nan's on the end to keep the same size
    dtdz = np.moveaxis(dtdz, axis, -1)
    z = np.zeros(dtdz.shape[:-1])[..., None] + np.nan
    dtdz = np.concatenate((dtdz, z), axis=-1)
    return np.moveaxis(dtdz, -1, axis)


def _logop(func, name=None, doc=None):
    """
    Returns a function that evaluates the ufunc `func` in log space
    by running `exp( func( log(x) ) )`.
    This is used for functions like mean and
    """
    # wrap the function
    def logfunc(x, axis=-1, base=10):
        y = np.log(x) / np.log(base)
        y = func(y, axis=axis)
        if base == np.e:
            return np.exp(y)

        return np.power(base, y)

    # rename logfunc to match func
    logfunc.__name__ = func.__name__
    logfunc.__doc__ = func.__doc__
    if name is not None:
        logfunc.__name__ = name
    if doc is not None:
        logfunc.__doc__ = doc

    return logfunc


logmean = _logop(np.nanmean, "logmean")
logstd = _logop(np.nanstd, "logstd")
logvar = _logop(np.nanvar, "logvar")

# logmedian and logquantile don't make sense but it's
# they're here for completeness
logmedian = np.nanmedian
logmedian.__name__ = "logmedian"
logquantile = np.nanquantile
logquantile.__name__ = "logquantile"
