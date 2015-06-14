#!/usr/bin/env python

import unittest
from gbox import Geocode
import json

class GeoBoxTestCase(unittest.TestCase):
    def setUp(self):
        loc_file = '../res/location.json'
        with open(loc_file, 'r') as fh:
            self.loc = json.load(fh)
    
    @unittest.skip('output json')
    def test01_print(self):
        result = {}
        for loc_name, data in self.loc.iteritems():
            g = Geocode(data['lon'], data['lat'])
            result[loc_name] = {
                'lon': data['lon'],
                'lat': data['lat'],
                'gpoint': g.gpoint(),
                'gcode': g.gcode(),
                'gbox': g.gbox()
            }

        print "\n\n%s" % json.dumps(result)
        

    def test10_location(self):
        for loc_name, data in self.loc.iteritems():
            g = Geocode(data['lon'], data['lat'])
            self.assertItemsEqual(g.gpoint(), data['gpoint'], "Expect gpoint from %s to match.  Expected %s; got %s" % (loc_name, data['gpoint'], g.gpoint()))
            self.assertEqual(g.gcode(), data['gcode'], "Expect gcode from %s to match.  Expected %s; got %s" % (loc_name, data['gcode'], g.gcode()))
            
            for coord, gpoint in g.gbox().iteritems():
                expected_gpoint = data['gbox'][coord]
                self.assertItemsEqual(gpoint, expected_gpoint, "Expect gbox['%s'] from %s to match.  Expected %s; got %s" % (coord, loc_name, gpoint, expected_gpoint))
            

# =================================================================
# Run
if __name__ == '__main__':
    print '''
----------------------------------------------------------------------
START UNIT TEST for %s
    ''' % __file__
    unittest.main(verbosity=2)