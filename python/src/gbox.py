import struct

class Geocode(object):
    LON_BOUND = (-180, 180)
    LAT_BOUND = (-90, 90)
    SIZE = (LON_BOUND[1]-LON_BOUND[0], LAT_BOUND[1]-LAT_BOUND[0])

    def __init__(self, lon, lat, depth=32):
        self.depth = depth
        self._gpoint = (lon, lat)
        self._gbox = None
        self._gcode, self._gbox_coord = self._calcGeocode(self._gpoint, self.depth)

    def _findPosition(self, position, lbound, ubound):
        '''
        For given position, compare it to the mid point between lower bound (lbound) and
        upper bound (ubound).  If after mid point, return 1 and set new lower bound as
        mid point.  Otherwise return 0 and set upper bound as mid point.
        '''
        mid = (lbound + ubound) / 2.0
        if position > mid:
            bit = 1
            lres = mid
            ures = ubound
        else:
            bit = 0
            lres = lbound
            ures = mid

        return bit, lres, ures

    def _calcGeocode(self, loc, depth):
        '''
        Find the postion (both lon and lat) if above or below mid point of the bound,
        per _findPosition function.  Repeat for number of depth provided, producing
        an integer with the size of depth * 2.
        '''
        x, y = loc
        x_lbound, x_ubound = self.LON_BOUND
        y_lbound, y_ubound = self.LAT_BOUND

        result = 0L
        for l in xrange(depth):
            x_bit, x_lbound, x_ubound = self._findPosition(x, x_lbound, x_ubound)
            y_bit, y_lbound, y_ubound = self._findPosition(y, y_lbound, y_ubound)

            # Reverse the index
            i = depth - l - 1

            # Calculate the interleave value
            result_index = i * 2
            
            if x_bit:
                result += 1 << (result_index+1)
            
            if y_bit:
                result += 1 << result_index
        
        # Convert unsigned 64bit long into a signed version
        u64int = struct.pack("Q", result)
        s64int = struct.unpack("q", u64int)[0]

        return s64int, (x_lbound, y_lbound, x_ubound, y_ubound)

    def gpoint(self):
        return self._gpoint

    def gcode(self):
        return self._gcode

    def gbox(self):
        if self._gbox is None:
            x_lbound, y_lbound, x_ubound, y_ubound = self._gbox_coord
            self._gbox = {
                'NW': (x_lbound, y_ubound),
                'NE': (x_ubound, y_ubound),
                'SW': (x_lbound, y_ubound),
                'SE': (x_lbound, y_lbound)
            }

        return self._gbox
