#!/usr/bin/env python
#
from geobox import GeoBoxEncoder, GeoPoint

locs = {
    'roma_piramide': {
        'lat': 41.87643118161227,
        'lon': 12.481563961993402,
        'gcode': 'eagacagacctggaaaga'
    },
    'paris_louvre': {
        'lat': 48.86102675689321,
        'lon': 2.335861599932855,
        'gcode': 'eaagggatcgcacaataa'
    },
    'greenwich': {
        'lat': 51.48,
        'lon': 0,
        'gcode': 'eaaggaggaggaagaaag'
    }
}

for name, loc in locs.iteritems():
    gpoint = GeoPoint(latitude=loc['lat'], longitude=loc['lon'])

    print "{0} (box size:{1:.4f})".format(name, gpoint.hypotenuse)
    print " - code: {0:18}".format(gpoint.gcode)
    if gpoint.gcode != loc['gcode']:
        print " - err:  Mismatch %s" % loc['gcode']
    else:
        for gcode, box in gpoint.neighbors().iteritems():
            print " - near: %s" % gcode
