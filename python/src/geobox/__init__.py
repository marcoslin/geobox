'''
Author: Marcos Lin
Created On: 12 Aug 2013

The purpose of this library is to create a geo proximity representation

Inpired by GeoPrint
    https://github.com/michelp/xodb
    ** Under tools/geoprint.py

* The first implementation is a simple porting from GeoPrint.  Later version
  should convert the ID from DNA to an Integer

'''
import json
from collections import namedtuple
from operator import neg, mod
from math import radians as rads
from math import (
    asin,
    atan2,
    cos,
    degrees,
    log10,
    pi,
    sin,
    sqrt,
)

interval = namedtuple("interval", "min max")

alphabet = 'gatc'
decodemap = dict((k, i) for (i, k) in enumerate(alphabet))


class GeoBoxEncoder(object):
    EARTH_RADIUS = 6378100
    DEFAULT_PRECISION = 18

    @classmethod
    def encode(cls, latitude, longitude, precision=None, box=False):
        """Encode the given latitude and longitude into a geobox_id that
        contains 'precision' characters.

        If radians is True, input parameters are in radians, otherwise
        they are degrees.  Example::

        >>> c = (7.0625, -95.677068)
        >>> h = encode(*c)
        >>> h
        'watttatcttttgctacgaagt'

        >>> r = rads(c[0]), rads(c[1])
        >>> h2 = encode(*r, radians=True)
        >>> h == h2
        True
        """
        if precision is None:
            precision = cls.DEFAULT_PRECISION

        if longitude < 0:
            geobox_id = ['w']
            loni = interval(-180.0, 0.0)
        else:
            geobox_id = ['e']
            loni = interval(0.0, 180.0)

        lati = interval(-90.0, 90.0)

        while len(geobox_id) < precision:
            ch = 0
            mid = (loni.min + loni.max) / 2
            if longitude > mid:
                ch |= 2
                loni = interval(mid, loni.max)
            else:
                loni = interval(loni.min, mid)

            mid = (lati.min + lati.max) / 2
            if latitude > mid:
                ch |= 1
                lati = interval(mid, lati.max)
            else:
                lati = interval(lati.min, mid)

            geobox_id.append(alphabet[ch])
        result = ''.join(geobox_id)
        if box:
            return (result, (lati[0], loni[0]), (lati[1], loni[1]))
        return result

    @classmethod
    def decode(cls, geobox_id, box=False):
        """Decode a geobox_id, returning the latitude and longitude.  These
        coordinates should approximate the input coordinates within a
        degree of error returned by 'error()'

        >>> c = (7.0625, -95.677068)
        >>> h = encode(*c)
        >>> c2 = decode(h)
        >>> e = error(h)
        >>> abs(c[0] - c2[0]) <= e
        True
        >>> abs(c[1] - c2[1]) <= e
        True

        If radians is True, results are in radians instead of degrees.

        >>> c2 = decode(h, radians=True)
        >>> e = error(h, radians=True)
        >>> abs(rads(c[0]) - c2[0]) <= e
        True
        >>> abs(rads(c[1]) - c2[1]) <= e
        True
        """
        lati = interval(-90.0, 90.0)
        first = geobox_id[0]
        if first == 'w':
            loni = interval(-180.0, 0.0)
        elif first == 'e':
            loni = interval(0.0, 180.0)

        geobox_id = geobox_id[1:]

        for c in geobox_id:
            cd = decodemap[c]
            if cd & 2:
                loni = interval((loni.min + loni.max) / 2, loni.max)
            else:
                loni = interval(loni.min, (loni.min + loni.max) / 2)
            if cd & 1:
                lati = interval((lati.min + lati.max) / 2, lati.max)
            else:
                lati = interval(lati.min, (lati.min + lati.max) / 2)
        lat = (lati.min + lati.max) / 2
        lon = (loni.min + loni.max) / 2

        if box:
            return ((lat, lon), (lati[0], loni[0]), (lati[1], loni[1]))
        return lat, lon

    @classmethod
    def neighbors(cls, geobox_id, bearing=True, box=False):
        '''
        Return the surrounding
        '''
        results = set()
        precision = len(geobox_id)
        spacing = 180 / (2.0 ** (precision - 1))
        ctr = cls.decode(geobox_id)
        dirs = ['N', 'S', 'E', 'NE', 'SE', 'W', 'NW', 'SW']
        i = 0
        for direction_lat in (0, 1, -1):
            for direction_long in (0, 1, -1):
                if direction_lat == 0 and direction_long == 0:
                    continue
                lat = ctr[0] + (direction_lat * spacing)
                lon = ctr[1] + (direction_long * spacing)
                h = cls.encode(lat, lon, precision=precision, box=box)
                if bearing:
                    h = (dirs[i], h)
                results.add(h)
                i += 1
        return results

    @classmethod
    def haversine(cls, latLngA, latLngB):
        """
        Calculate the great circle distance between two points
        on the earth (specified in decimal degrees)
        """
        lat1, lon1 = latLngA
        lat2, lon2 = latLngB

        # convert decimal degrees to radians
        lon1, lat1, lon2, lat2 = map(rads, [lon1, lat1, lon2, lat2])
        # haversine formula
        dlon = lon2 - lon1
        dlat = lat2 - lat1
        a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
        c = 2 * asin(sqrt(a))
        # Return distance in meter
        return cls.EARTH_RADIUS * c


class GeoPoint(object):
    '''
    Used to represent a point
    '''
    _lat = None
    _lng = None
    _geobox_id = None
    _box = None
    _precision = None

    @classmethod
    def encode_geobox_id(cls, latitude, longitude, precision=None, box=False):
        if precision is None:
            precision = GeoBoxEncoder.DEFAULT_PRECISION
        return GeoBoxEncoder.encode(latitude, longitude, precision, box)

    def __init__(self, latitude=None, longitude=None, geobox_id=None, precision=None, build_box=True):
        # Either latitude/longitude or geobox_id must be provided
        if geobox_id is None:
            if latitude is None or longitude is None:
                raise ValueError("Either geobox_id or latitude/longitude must be provided to create a GeoPoint")

            self._lat = latitude
            self._lng = longitude

            if precision is None:
                self._precision = GeoBoxEncoder.DEFAULT_PRECISION
            else:
                self._precision = precision

            geobox = self.encode_geobox_id(latitude, longitude, self._precision, box=True)

            self._geobox_id = geobox[0]
            latLng_SW = geobox[1]
            latLng_NE = geobox[2]
        else:
            latlng, latLng_SW, latLng_NE = GeoBoxEncoder.decode(geobox_id, box=True)
            self._geobox_id = geobox_id
            self._lat = latlng[0]
            self._lng = latlng[1]
            if precision is None:
                self._precision = len(geobox_id)
            else:
                self._precision = precision

        # Create box if needed
        if build_box:
            self._box = self._build_box(latLng_SW=latLng_SW, latLng_NE=latLng_NE, precision=precision)

    # Private methods
    def _build_box(self, latLng_SW, latLng_NE, precision=None):
        '''
        Based on latLng of SW and NE points returned from the GeoBoxEncoder, create
        a box that is represented by a dictionary of 4 GeoPoints: NW, NE, SE, SW
        '''
        if precision is None:
            precision = self._precision

        latLng_SE = (latLng_SW[0], latLng_NE[1])
        latLng_NW = (latLng_NE[0], latLng_SW[1])

        # Build the result
        box = dict()
        box['SW'] = self.__class__(latitude=latLng_SW[0], longitude=latLng_SW[1], precision=precision, build_box=False)
        box['NE'] = self.__class__(latitude=latLng_NE[0], longitude=latLng_NE[1], precision=precision, build_box=False)
        box['SE'] = self.__class__(latitude=latLng_SE[0], longitude=latLng_SE[1], precision=precision, build_box=False)
        box['NW'] = self.__class__(latitude=latLng_NW[0], longitude=latLng_NW[1], precision=precision, build_box=False)

        return box

    # Define Properties
    @property
    def latitude(self):
        return self._lat

    @property
    def longitude(self):
        return self._lng

    @property
    def precision(self):
        return self._precision

    @property
    def gcode(self):
        return self._geobox_id

    @property
    def latlng(self):
        return (self._lat, self._lng)

    @property
    def box(self):
        return self._box

    @property
    def hypotenuse(self):
        box = self._box
        return self.distance(box['NE'], box['SW'])

    # Methods
    def neighbors(self):
        '''
        Create a dictionary with 8 entries, representing the boxes surronding the current one.
        '''
        nb = {}
        for geobox in GeoBoxEncoder.neighbors(self._geobox_id, box=True):
            # Ignoring the heading contained in geobox[0]
            geobox_id, latLng_SW, latLng_NE = geobox[1]
            nb[geobox_id] = self._build_box(latLng_SW, latLng_NE)
        return nb

    def distance_from(self, geopoint):
        return self.distance(self, geopoint)

    @classmethod
    def distance(cls, geopointA, geopointB):
        '''
        Calculate the great circle distance between two points
        using haversine
        '''
        lat1, lon1 = geopointA.latlng
        lat2, lon2 = geopointB.latlng

        # convert decimal degrees to radians
        lon1, lat1, lon2, lat2 = map(rads, [lon1, lat1, lon2, lat2])
        # haversine formula
        dlon = lon2 - lon1
        dlat = lat2 - lat1
        a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
        c = 2 * asin(sqrt(a))
        # Return distance in meter
        return GeoBoxEncoder.EARTH_RADIUS * c


class GeoPointEncoder(json.JSONEncoder):
    '''
    Basic Encoder designed to convert datetime object into ISODATE
    '''
    def default(self, obj):
        if isinstance(obj, GeoPoint):
            return {
                    'geobox_id': obj.geobox_id,
                    'latitude': obj.latitude,
                    'longitude': obj.longitude
                    }
        else:
            return super(GeoPointEncoder, self).default(obj)
