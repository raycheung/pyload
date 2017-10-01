# -*- coding: utf-8 -*-
# @author: vuolter

from __future__ import absolute_import, unicode_literals

from builtins import bytes, dict, int, str

from future import standard_library

from pyload.utils.check import isiterable, ismapping

standard_library.install_aliases()


try:
    import bitmath
except ImportError:
    bitmath = None


def convert(obj, rule, func, args=(), kwargs={}, fallback=None):
    res = None
    cvargs = (rule, func, args, kwargs, fallback)
    try:
        if rule(obj):
            res = func(obj, *args, **kwargs)
        elif ismapping(obj):
            res = dict((convert(k, *cvargs), convert(v, *cvargs))
                       for k, v in obj.items())
        elif isiterable(obj):
            res = type(obj)(convert(i, *cvargs) for i in obj)
        else:
            res = obj
    except Exception as exc:
        if callable(fallback):
            fbargs = cvargs[:-1] + (exc,)
            return fallback(obj, *fbargs)
        raise
    return res


def size(value, in_unit, out_unit):
    """Convert file size."""
    in_unit = in_unit.strip()[0].upper()
    out_unit = out_unit.strip()[0].upper()

    if in_unit == out_unit:
        return value

    in_unit += 'yte' if in_unit == 'B' else 'iB'
    out_unit += 'yte' if out_unit == 'B' else 'iB'

    try:
        # Create a bitmath instance representing the input value with its
        # corresponding unit
        in_size = getattr(bitmath, in_unit)(value)
        # Call the instance method to convert it to the output unit
        out_size = getattr(in_size, 'to_' + out_unit)()
        return out_size.value

    except AttributeError:
        sizeunits = ('B', 'K', 'M', 'G', 'T', 'P', 'E')
        sizemap = dict((u, i * 10) for i, u in enumerate(sizeunits))

        in_magnitude = sizemap[in_unit]
        out_magnitude = sizemap[out_unit]

        magnitude = in_magnitude - out_magnitude
        i, d = divmod(value, 1)

        decimal = int(d * (1024 ** (abs(magnitude) // 10)))
        if magnitude >= 0:
            integer = int(i) << magnitude
        else:
            integer = int(i) >> magnitude * -1
            decimal = -decimal

        return integer + decimal


def to_bytes(obj, encoding='utf-8', errors='strict'):
    try:
        return obj.encode(encoding, errors)
    except AttributeError:
        try:
            return bytes(obj)
        except NameError:
            return str(obj)


def to_str(obj, encoding='utf-8', errors='strict'):
    try:
        return obj.decode(encoding, errors)
    except AttributeError:
        try:
            return unicode(obj)
        except NameError:
            return str(obj)


def to_dict(obj):
    """Convert object to dictionary or return default."""
    return dict((attr, getattr(obj, attr)) for attr in obj.__slots__)


def to_list(obj):
    """Convert value to a list with value inside or return default."""
    if isinstance(obj, list):
        res = obj
    elif ismapping(obj):
        res = list(obj.items())
    elif isiterable(obj, strict=False):
        res = list(obj)
    elif obj is not None:
        res = [obj]
    else:
        res = list(obj)
